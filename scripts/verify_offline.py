"""离线验证入口：使用假配置，并阻止 socket 连接，绝不调用真实模型。"""
import argparse
import os
from pathlib import Path
import runpy
import socket
import sys
import unittest
from unittest.mock import patch

_original_connect = socket.socket.connect
_original_socketpair = socket.socketpair


def local_socketpair(*args, **kwargs):
    # Windows asyncio builds its internal wake-up pipe with a loopback pair.
    # Only this standard-library operation may temporarily use connect.
    with patch.object(socket.socket, 'connect', _original_connect):
        return _original_socketpair(*args, **kwargs)

BASE_DEMOS = [
    'learning.steps_01_20.step_09_first_test',
    'learning.steps_01_20.step_10_parameterized_test',
    'learning.steps_01_20.step_11_mock_model_test',
    'learning.steps_01_20.step_13_fastapi_test',
    'learning.steps_01_20.step_18_tool_safety_test',
    'learning.rag.step_03_load_documents',
    'learning.rag.step_04_split_documents',
    'learning.rag.step_05_retrieve_top_one',
    'learning.rag.step_06_show_all_scores',
    'learning.rag.step_07_build_prompt',
    'learning.rag.step_07b_03_missing_context',
    'learning.rag.step_07b_04_untrusted_context',
    'learning.rag.step_07b_05_answer_and_sources',
    'learning.rag.step_09_reliable_refusal',
    'learning.rag.step_10_sources',
    'learning.rag.step_11_rag_api',
    'learning.rag.step_12_route_regression',
    'learning.rag.step_13_knowledge_tool',
    'learning.rag.step_14_agent_knowledge_loop',
    'learning.rag.step_15a_keyword_limit',
    'learning.rag.step_15b_embedding_concept',
    'learning.rag.step_15c_cosine_similarity',
    'learning.rag.step_15d_recall_at_k',
    'learning.rag.step_15d_precision_at_k',
    'learning.rag.step_15e_rerank',
    'learning.rag.step_15f_hallucination_cases',
    'learning.rag.step_16h_01_ngram_eval_baseline',
    'learning.rag.step_17a_no_answer_eval',
    'learning.rag.step_17c_01_threshold_tradeoff',
    'learning.rag.step_17c_02_holdout_eval',
    'learning.rag.step_17e_evidence_audit',
    'learning.rag.step_17g_rag_branch_recap',
]
FRAMEWORK_DEMOS = [
    'learning.frameworks.step_19d_langchain_tool_object',
    *['learning.frameworks.' + name for name in (
        'step_20a_langgraph_state', 'step_20b_langgraph_node', 'step_20c_langgraph_edge',
        'step_20d_conditional_route', 'step_20e_checkpoint', 'step_20f_interrupt_resume',
        'step_20g_node_failure', 'step_20h_message_reducer', 'step_20j_native_graph_comparison',
        'step_20k_graph_conversation', 'step_20l_http_graph_demo', 'step_20m_knowledge_tool',
    )],
]


def configure_dummy_environment() -> None:
    # Environment takes precedence over .env. Never read a contributor's real key in tests.
    os.environ.update(LLM_API_KEY='test-only', LLM_BASE_URL='https://example.invalid/v1',
                      LLM_MODEL='local-test', DASHSCOPE_API_KEY='test-only',
                      EMBEDDING_PROVIDER='dashscope', EMBEDDING_MODEL='text-embedding-v2',
                      EMBEDDING_DIMENSIONS='1536', LANGSMITH_TRACING='false',
                      LANGCHAIN_TRACING_V2='false', LANGCHAIN_TRACING='false')
    for key in ('LANGSMITH_API_KEY', 'LANGCHAIN_API_KEY'):
        os.environ.pop(key, None)


def blocked(*args, **kwargs):
    raise AssertionError('离线检查禁止网络连接；请为外部响应增加模拟。')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=('base', 'framework'), default='base')
    parser.add_argument('--tests-only', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    configure_dummy_environment()
    with (patch.object(socket.socket, 'connect', blocked),
          patch.object(socket, 'create_connection', blocked),
          patch.object(socket, 'socketpair', local_socketpair)):
        suite = unittest.defaultTestLoader.discover(
            'tests' if args.suite == 'base' else 'learning/frameworks',
            pattern='test_*.py', top_level_dir='.',
        )
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)
        if args.tests_only:
            return
        demos = list(BASE_DEMOS if args.suite == 'base' else FRAMEWORK_DEMOS)
        if args.suite == 'base':
            demos.extend('learning.context.' + p.stem for p in sorted((root / 'learning/context').glob('step_*.py')))
        for module in demos:
            print(f'\n验证 {module}', flush=True)
            with patch.object(sys, 'argv', [module]):
                try:
                    runpy.run_module(module, run_name='__main__', alter_sys=True)
                except SystemExit as error:
                    if error.code not in (None, 0, False):
                        raise
        print(f'OFFLINE_OK suite={args.suite} tests={result.testsRun} demos={len(demos)}')


if __name__ == '__main__':
    main()
