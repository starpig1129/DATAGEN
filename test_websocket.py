#!/usr/bin/env python3
"""
WebSocket 連接測試腳本
用於驗證修復後的 WebSocket 服務器功能
"""

import asyncio
import websockets
import json
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    """測試 WebSocket 連接"""
    uri = "ws://localhost:8765"
    
    try:
        logger.info(f"嘗試連接到 {uri}")
        
        async with websockets.connect(uri) as websocket:
            logger.info("WebSocket 連接成功！")
            
            # 發送初始化消息
            init_message = {
                "type": "init",
                "clientId": "test_client",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await websocket.send(json.dumps(init_message))
            logger.info("已發送初始化消息")
            
            # 接收歡迎消息
            welcome_response = await websocket.recv()
            welcome_data = json.loads(welcome_response)
            logger.info(f"收到歡迎消息: {welcome_data['type']}")
            
            # 接收系統狀態消息
            status_response = await websocket.recv()
            status_data = json.loads(status_response)
            logger.info(f"收到系統狀態: {status_data['type']}")
            
            # 發送 ping 測試
            ping_message = {
                "type": "ping",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await websocket.send(json.dumps(ping_message))
            logger.info("已發送 ping 消息")
            
            # 接收 pong 回應
            pong_response = await websocket.recv()
            pong_data = json.loads(pong_response)
            logger.info(f"收到 pong 回應: {pong_data['type']}")
            
            # 請求系統狀態
            status_request = {
                "type": "request_status",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await websocket.send(json.dumps(status_request))
            logger.info("已請求系統狀態")
            
            # 接收狀態回應
            status_response = await websocket.recv()
            status_data = json.loads(status_response)
            logger.info(f"收到狀態回應: {status_data['data']}")
            
            logger.info("✅ WebSocket 連接測試成功！")
            
    except ConnectionRefusedError:
        logger.error("❌ WebSocket 連接被拒絕，請確保服務器正在運行")
    except Exception as e:
        logger.error(f"❌ WebSocket 測試失敗: {e}")

def main():
    """主函數"""
    logger.info("開始 WebSocket 連接測試")
    asyncio.run(test_websocket_connection())

if __name__ == "__main__":
    main()