"""启动两个独立Python进程，每个进程内访问计数接口两次，无网络端口。"""

import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """无参数；收集两个子进程的PID和计数，确认彼此不共享内存。"""
    code = """
import json
from fastapi.testclient import TestClient
from learning.web_basics.step_01_hello import app
with TestClient(app) as client:
    responses = [client.get('/counter'), client.get('/counter')]
    assert all(response.status_code == 200 for response in responses)
    print('COUNTER_RESULT=' + json.dumps([response.json() for response in responses]))
"""
    processes = []
    try:
        for _ in range(2):
            processes.append(subprocess.Popen(
                [sys.executable, "-X", "utf8", "-c", code],
                cwd=Path(__file__).resolve().parents[2],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            ))
        outputs = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=30)
            if process.returncode != 0:
                raise RuntimeError(stderr)
            line = next(line for line in stdout.splitlines() if line.startswith('COUNTER_RESULT='))
            records = json.loads(line.split('=', 1)[1])
            assert [record['count'] for record in records] == [1, 2]
            # Windows虚拟环境启动器PID可能与实际Python解释器PID不同。
            assert records[0]['pid'] == records[1]['pid']
            outputs.append(records)
            print('独立进程的两次响应：', records)
        assert outputs[0][0]['pid'] != outputs[1][0]['pid']
        print('检查通过：不同进程分别从0开始计数，都返回1、2。')
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
                process.communicate()


if __name__ == '__main__':
    main()
