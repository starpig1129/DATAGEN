import asyncio
import sys
import os

import typer

from src.system import MultiAgentSystem
from websocket_server import run_websocket_server

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

app = typer.Typer()


@app.command()
def run():
    """運行多代理系統進行數據分析"""
    system = MultiAgentSystem()

    # 示例使用
    user_input = '''
    datapath:OnlineSalesData.csv
    Use machine learning to perform data analysis and write complete graphical reports
    '''
    system.run(user_input)


@app.command()
def websocket(
    host: str = typer.Option("localhost", help="WebSocket 伺服器主機位址"),
    port: int = typer.Option(8765, help="WebSocket 伺服器端口")
):
    """啟動 WebSocket 伺服器"""
    typer.echo(f"啟動 WebSocket 伺服器在 ws://{host}:{port}")
    asyncio.run(run_websocket_server(host, port))


if __name__ == "__main__":
    app()
