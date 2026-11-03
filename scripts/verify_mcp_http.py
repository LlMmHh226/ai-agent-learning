"""本机HTTP MCP往返检查；使用动态端口，不使用模型，不连接外部服务。"""
import os
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import time
from unittest.mock import patch


def main():
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    env = os.environ.copy()
    env['MCP_HTTP_PORT'] = str(port)
    env['ORDER_STORAGE_BACKEND'] = 'demo'
    env['PYTHONUTF8'] = '1'
    process = subprocess.Popen(
        [sys.executable, '-X', 'utf8', '-m', 'learning.mcp.step_21g_http_server'],
        cwd=Path(__file__).resolve().parents[1], env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
    )
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError('本地MCP HTTP服务启动失败。')
            with socket.socket() as probe:
                probe.settimeout(0.3)
                try:
                    probe.connect(('127.0.0.1', port))
                except OSError:
                    time.sleep(0.1)
                    continue
                break
        else:
            raise RuntimeError('本地MCP HTTP服务未在限时内就绪。')
        with patch.dict(os.environ, {'MCP_HTTP_PORT':str(port)}):
            runpy.run_module('learning.mcp.step_21g_http_client', run_name='__main__', alter_sys=True)
        print('MCP_HTTP_OK：本机工具发现与订单查询通过。')
    finally:
        if process.poll() is None:
            process.terminate()
        try:
            process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)


if __name__ == '__main__':
    main()
