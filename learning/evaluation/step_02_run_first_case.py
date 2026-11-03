# 课程：step_02_first_real_run.md；访问范围：默认列表/预览不请求模型；显式--run会调用真实模型。
"""G1-02：正式HTTP入口的单案例真实效果采集，包装器只记录并转发原调用。"""

import argparse
import asyncio
import hashlib
import json
import logging
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import httpx

from main import app
from app.services.llm_service import llm_service


ROOT = Path(__file__).resolve().parents[2]


def parse_arguments(raw: str):
    """记录模型参数；解析失败保留原文，不替业务代码修参数。"""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {"unparsed": raw}


def check_tool_policy(expected: dict, model_calls: list[dict], executed_tools: list[dict], prior_tool_results: list[dict] | None = None) -> dict[str, bool]:
    """根据当前规则核对真实轨迹；optional未调用时只接受前轮匹配的工具证据。

    prior_tool_results由多轮采集器提供，仅含同一会话前面轮次的工具结果。
    这里不判断最终回答语义，也不把允许复用理解成允许无依据猜测。
    知识库required案例可用nonempty_query检查参数结构；查询含义仍需另行审核。
    """
    policy = expected.get("tool_policy", "required")
    proposed = [call for item in model_calls for call in item.get("proposed_tools", [])]
    complete = bool(model_calls) and all(item["status"] == "completed" for item in model_calls)
    if policy == "none":
        return {"no_tool_calls": complete and not proposed and not executed_tools}

    target = expected["required_tool_call"]
    argument_match = expected.get("argument_match", "exact")
    if argument_match not in ("exact", "nonempty_query"):
        raise ValueError("argument_match只支持exact或nonempty_query。")
    if argument_match == "nonempty_query" and (policy != "required" or target["name"] != "search_knowledge_base"):
        raise ValueError("nonempty_query仅用于required的search_knowledge_base案例。")
    def matches_call(item):
        if item["name"] != target["name"]:
            return False
        arguments = item["arguments"]
        if argument_match == "nonempty_query":
            return (isinstance(arguments, dict) and set(arguments) == {"query"}
                    and isinstance(arguments["query"], str) and bool(arguments["query"].strip()))
        return arguments == target["arguments"]
    def matches_facts(item):
        return "error_type" not in item and all(
            key in item.get("result", {}) and item["result"][key] == value
            for key, value in expected["tool_result_fields"].items()
        )
    matching = [item for item in executed_tools if matches_call(item)]
    if policy == "required":
        return {"required_tool_and_arguments": bool(matching),
                "tool_result_facts": any(matches_facts(item) for item in matching)}
    if policy != "optional":
        raise ValueError("未知tool_policy。")
    if proposed or executed_tools:
        return {"optional_tool_calls_valid": complete and bool(executed_tools) and
                len(proposed) == len(executed_tools) and
                all(matches_call(item) for item in proposed) and
                all(matches_call(item) and matches_facts(item) for item in executed_tools)}
    history = [item for item in (prior_tool_results or []) if matches_call(item)]
    return {"history_evidence_available": complete and bool(history) and matches_facts(history[-1])}


async def collect_case(case: dict, conversation_id: str | None = None, prior_tool_results: list[dict] | None = None) -> dict:
    """执行一轮HTTP请求。多轮入口可传共享会话ID；单轮默认创建独立ID。"""
    expected = case["expected"]
    tool_policy = expected.get("tool_policy", "required")
    if tool_policy not in ("required", "none", "optional"):
        raise ValueError("tool_policy只支持required、none或optional。")
    if tool_policy == "none" and (expected.get("required_tool_call") is not None or expected.get("tool_result_fields")):
        raise ValueError("不调用工具时，required_tool_call应为null或省略，tool_result_fields应为空或省略。")
    report = {
        "case_id": case["id"], "baseline": "formal_native_agent",
        "case_version": case.get("case_version", 1), "grading_policy_version": 3,
        "started_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "model": llm_service.model, "expected": case["expected"],
        "model_calls": [], "executed_tools": [], "http": None,
        "human_review": {"status": "pending", "reason": "最终事实、否定和额外编造需核对。"},
        "task_verdict": "pending", "estimated_cost": None,
    }
    request = dict(case["request"])
    request["conversation_id"] = conversation_id or (request["conversation_id"] + "-" + uuid4().hex[:8])
    report["request"] = request
    real_create = llm_service.client.chat.completions.create
    real_execute = llm_service._execute_tool

    async def record_create(*args, **kwargs):
        entry = {"input_message_count": len(kwargs["messages"]), "status": "started"}
        report["model_calls"].append(entry)
        start = time.perf_counter()
        try:
            response = await real_create(*args, **kwargs)
            message = response.choices[0].message
            entry.update(status="completed", proposed_tools=[{
                "id": call.id, "name": call.function.name,
                "arguments": parse_arguments(call.function.arguments),
            } for call in (message.tool_calls or [])])
            entry["usage"] = response.usage.model_dump() if response.usage else None
            return response
        except BaseException as error:
            entry.update(status="error", error_type=type(error).__name__,
                         http_status=getattr(error, "status_code", None))
            raise
        finally:
            entry["elapsed_seconds"] = round(time.perf_counter() - start, 3)

    def record_execute(name, arguments):
        entry = {"name": name, "arguments": parse_arguments(arguments)}
        report["executed_tools"].append(entry)
        start = time.perf_counter()
        try:
            result = real_execute(name=name, arguments=arguments)
            entry["result"] = result
            return result
        except Exception as error:
            entry["error_type"] = type(error).__name__
            raise
        finally:
            entry["elapsed_seconds"] = round(time.perf_counter() - start, 3)

    start = time.perf_counter()
    api_logger = logging.getLogger("app.api.chat")
    previous_disabled = api_logger.disabled
    api_logger.disabled = True  # 报告仅记异常类型，避免打印供应商异常正文。
    try:
        with (
            patch.object(llm_service.client.chat.completions, "create", new=record_create),
            patch.object(llm_service, "_execute_tool", new=record_execute),
        ):
            async with asyncio.timeout(90):
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://local-eval") as client:
                    response = await client.request(case["method"], case["path"], json=request)
                    report["http"] = {"status": response.status_code, "body": response.json()}
    except Exception as error:
        report["execution_error"] = {"type": type(error).__name__, "status": getattr(error, "status_code", None)}
    finally:
        api_logger.disabled = previous_disabled
        report["elapsed_seconds"] = round(time.perf_counter() - start, 3)
    report["checks"] = {
        "http_ok": report["http"] is not None and report["http"]["status"] == expected["http_status"],
    }
    report["checks"].update(check_tool_policy(
        expected, report["model_calls"], report["executed_tools"], prior_tool_results,
    ))
    if not all(report["checks"].values()):
        report["task_verdict"] = "failed_or_incomplete"
    return report


async def collect_dialogue(case: dict) -> dict:
    """main传入含turns的案例；同一新会话依次执行各轮，保留逐轮结果及汇总。

    turns每项包含message和expected。HTTP调用失败则停止后续轮次，避免在前提
    未建立时继续假装完成多轮。模型/工具行为失败也保留，不只看最后一句。
    """
    turns = case["turns"]
    if not turns:
        raise ValueError("多轮案例的turns不能为空。")
    conversation_id = case["request"]["conversation_id"] + "-" + uuid4().hex[:8]
    report = {
        "case_id": case["id"], "baseline": "formal_native_agent",
        "case_version": case.get("case_version", 1), "grading_policy_version": 3,
        "started_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "model": llm_service.model, "conversation_id": conversation_id,
        "turns": [], "model_calls": [], "executed_tools": [],
        "human_review": {"status": "pending", "reason": "需要逐轮核对答案和对话连续性。"},
        "task_verdict": "pending", "estimated_cost": None,
    }
    start = time.perf_counter()
    for number, turn in enumerate(turns, start=1):
        turn_case = {
            "id": f"{case['id']}_turn_{number}", "method": case["method"], "path": case["path"],
            "case_version": case.get("case_version", 1),
            "request": {"conversation_id": conversation_id, "message": turn["message"]},
            "expected": turn["expected"],
        }
        result = await collect_case(turn_case, conversation_id=conversation_id,
                                    prior_tool_results=report["executed_tools"])
        result["turn_index"] = number
        report["turns"].append(result)
        report["model_calls"].extend(dict(item, turn_index=number) for item in result["model_calls"])
        report["executed_tools"].extend(dict(item, turn_index=number) for item in result["executed_tools"])
        if result["http"] is None or result["http"]["status"] != 200:
            report["stop_reason"] = f"第{number}轮HTTP未成功，后续轮次未执行。"
            break
    report["elapsed_seconds"] = round(time.perf_counter() - start, 3)
    report["checks"] = {
        "all_turns_executed": len(report["turns"]) == len(turns),
        "all_turns_mechanical_checks": all(all(turn["checks"].values()) for turn in report["turns"]),
    }
    if not all(report["checks"].values()):
        report["task_verdict"] = "failed_or_incomplete"
    return report


def case_description(case: dict) -> str:
    """只读列表描述：单轮显示问题，多轮按顺序列出各轮问题。"""
    if "turns" in case:
        return " → ".join(turn["message"] for turn in case["turns"])
    return case["request"]["message"]


def select_case(cases: list[dict], case_id: str | None = None) -> dict:
    """cases来自案例JSON，case_id来自命令行；返回选中的案例给main。

    不指定ID仍选第一条。未知/重复ID明确报错，防止悄悄执行错误案例。
    """
    if not cases:
        raise ValueError("案例列表为空。")
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("案例ID重复，请为每条案例设置唯一id。")
    if case_id is None:
        return cases[0]
    for case in cases:
        if case["id"] == case_id:
            return case
    raise ValueError(f"找不到案例ID：{case_id}；可选ID：{', '.join(ids)}")


def main(argv: list[str] | None = None) -> None:
    """读取命令行选择一条案例；列表/预览只读，不调用模型。

    argv通常为None，由argparse读取终端参数；离线检查可显式传入参数列表。
    """
    parser = argparse.ArgumentParser(description="从正式HTTP入口运行一条真实效果案例。")
    parser.add_argument("--case-id", help="案例ID；省略时保持原行为，执行第一条。")
    display = parser.add_mutually_exclusive_group()
    display.add_argument("--list-cases", action="store_true", help="只显示已有案例ID和问题，不请求模型。")
    display.add_argument("--show-case", action="store_true", help="只预览选中案例和预期，不请求模型。")
    display.add_argument("--run", action="store_true", help="显式运行选定案例，访问真实模型并保存报告。")
    args = parser.parse_args(argv)
    try:
        cases = json.loads((ROOT / "learning/evaluation/cases/agent_baseline.json").read_text(encoding="utf-8"))["cases"]
        case = select_case(cases, args.case_id)
    except (ValueError, KeyError) as error:
        parser.error(str(error))
    if args.list_cases:
        for item in cases:
            print(f"{item['id']}：{case_description(item)}")
        return
    if args.show_case or not args.run:
        print(json.dumps(case, ensure_ascii=False, indent=2))
        return
    print("本次执行案例：", case["id"])
    report = asyncio.run(collect_dialogue(case) if "turns" in case else collect_case(case))
    report["git_head"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    from app.core.config import get_settings
    settings = get_settings()
    report["runtime_backends"] = {"orders": settings.order_storage_backend,
                                  "knowledge": settings.knowledge_retrieval_backend}
    # 记录实际代码/知识版本；不读取.env，不把密钥写入报告。
    report["source_sha256"] = {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted([ROOT / "main.py", ROOT / "requirements.txt", *list((ROOT / "app").rglob("*.py")), *list((ROOT / "data/knowledge").glob("*.md"))])
    }
    folder = ROOT / "learning/evaluation/results"
    folder.mkdir(exist_ok=True)
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d_%H%M%S_%f")
    output = folder / f"{stamp}_{case['id']}.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("报告：", output)
    print("模型调用入口次数：", len(report["model_calls"]))
    print("实际执行工具次数：", len(report["executed_tools"]))
    print("机械检查：", report["checks"])
    for turn in report.get("turns", [report]):
        if "turn_index" in turn:
            print(f"第{turn['turn_index']}轮检查：", turn["checks"])
        print("HTTP响应：", turn["http"])
        print("执行异常：", turn.get("execution_error"))
    if "stop_reason" in report:
        print("停止原因：", report["stop_reason"])
    print("最终事实审核：pending；本脚本不把包含某个字符串直接判为通过。")


if __name__ == "__main__":
    main()
