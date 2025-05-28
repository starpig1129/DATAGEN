#!/usr/bin/env python3
"""
多代理數據分析系統啟動腳本
同時運行 Flask API 服務器和 WebSocket 實時更新服務器
"""

import os
import sys
import time
import signal
import subprocess
import threading
import argparse
from typing import List, Optional

class ServerManager:
    """服務器管理器 - 負責啟動和管理多個服務器進程"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.running = False
        
    def start_flask_server(self, host: str = "0.0.0.0", port: int = 5001, debug: bool = False):
        """啟動 Flask API 服務器"""
        print(f"🚀 啟動 Flask API 服務器 http://{host}:{port}")
        
        env = os.environ.copy()
        env['FLASK_APP'] = 'app.py'
        env['FLASK_ENV'] = 'development' if debug else 'production'
        
        if debug:
            # 開發模式
            cmd = [sys.executable, 'app.py']
        else:
            # 生產模式使用 gunicorn
            cmd = [
                'gunicorn', 
                '--bind', f'{host}:{port}',
                '--workers', '4',
                '--worker-class', 'gevent',
                '--timeout', '120',
                'app:app'
            ]
        
        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append(process)
            
            # 啟動輸出監控線程
            monitor_thread = threading.Thread(
                target=self._monitor_process_output,
                args=(process, "Flask API"),
                daemon=True
            )
            monitor_thread.start()
            
            return process
            
        except FileNotFoundError as e:
            print(f"❌ 啟動 Flask 服務器失敗: {e}")
            if 'gunicorn' in str(e):
                print("💡 提示: 請安裝 gunicorn: pip install gunicorn gevent")
            return None
    
    def start_websocket_server(self, host: str = "localhost", port: int = 8765):
        """啟動 WebSocket 實時更新服務器"""
        print(f"🔌 啟動 WebSocket 服務器 ws://{host}:{port}")
        
        cmd = [
            sys.executable, 
            'websocket_server.py',
            '--host', host,
            '--port', str(port)
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append(process)
            
            # 啟動輸出監控線程
            monitor_thread = threading.Thread(
                target=self._monitor_process_output,
                args=(process, "WebSocket"),
                daemon=True
            )
            monitor_thread.start()
            
            return process
            
        except Exception as e:
            print(f"❌ 啟動 WebSocket 服務器失敗: {e}")
            return None
    
    def start_frontend_server(self, host: str = "localhost", port: int = 3000):
        """啟動前端開發服務器（如果需要）"""
        frontend_dir = "vue-frontend"
        
        if not os.path.exists(frontend_dir):
            print("⚠️  前端目錄不存在，跳過前端服務器啟動")
            return None
            
        print(f"🎨 啟動前端開發服務器 http://{host}:{port}")
        
        # 檢查 package.json 是否存在
        package_json = os.path.join(frontend_dir, "package.json")
        if not os.path.exists(package_json):
            print("⚠️  package.json 不存在，跳過前端服務器啟動")
            return None
        
        cmd = ["npm", "run", "dev", "--", "--host", host, "--port", str(port)]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append(process)
            
            # 啟動輸出監控線程
            monitor_thread = threading.Thread(
                target=self._monitor_process_output,
                args=(process, "Frontend"),
                daemon=True
            )
            monitor_thread.start()
            
            return process
            
        except FileNotFoundError:
            print("❌ npm 未找到，請確保 Node.js 已安裝")
            return None
        except Exception as e:
            print(f"❌ 啟動前端服務器失敗: {e}")
            return None
    
    def _monitor_process_output(self, process: subprocess.Popen, name: str):
        """監控進程輸出"""
        while process.poll() is None and self.running:
            try:
                line = process.stdout.readline()
                if line:
                    print(f"[{name}] {line.rstrip()}")
            except Exception as e:
                print(f"❌ 監控 {name} 輸出失敗: {e}")
                break
    
    def start_all(self, 
                 flask_host: str = "0.0.0.0", 
                 flask_port: int = 5001,
                 ws_host: str = "localhost", 
                 ws_port: int = 8765,
                 frontend_host: str = "localhost",
                 frontend_port: int = 3000,
                 debug: bool = False,
                 start_frontend: bool = False):
        """啟動所有服務器"""
        
        self.running = True
        
        print("=" * 60)
        print("🚀 多代理數據分析系統啟動中...")
        print("=" * 60)
        
        
        # 啟動 Flask API 服務器
        flask_process = self.start_flask_server(flask_host, flask_port, debug)
        if not flask_process:
            print("❌ Flask 服務器啟動失敗")
            return False
        
        time.sleep(2)  # 等待 Flask 服務器啟動
        
        # 啟動 WebSocket 服務器
        ws_process = self.start_websocket_server(ws_host, ws_port)
        if not ws_process:
            print("⚠️  WebSocket 服務器啟動失敗，但系統仍可運行")
        
        time.sleep(2)  # 等待 WebSocket 服務器啟動
        
        # 啟動前端服務器（可選）
        if start_frontend:
            frontend_process = self.start_frontend_server(frontend_host, frontend_port)
            time.sleep(3)  # 等待前端服務器啟動
        
        # 顯示啟動信息
        print("\n" + "=" * 60)
        print("✅ 系統啟動完成!")
        print("=" * 60)
        print(f"📡 API 服務器:     http://{flask_host}:{flask_port}")
        if ws_process:
            print(f"🔌 WebSocket 服務器: ws://{ws_host}:{ws_port}")
        if start_frontend:
            print(f"🎨 前端服務器:     http://{frontend_host}:{frontend_port}")
        print("=" * 60)
        print("📝 日誌輸出:")
        print("   - 按 Ctrl+C 停止所有服務器")
        print("   - 瀏覽器訪問 API 服務器開始使用系統")
        print("=" * 60)
        
        return True
    
    def stop_all(self):
        """停止所有服務器"""
        print("\n🛑 正在停止所有服務器...")
        
        self.running = False
        
        for i, process in enumerate(self.processes):
            if process and process.poll() is None:
                print(f"停止進程 {i+1}...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"強制終止進程 {i+1}")
                    process.kill()
                except Exception as e:
                    print(f"停止進程 {i+1} 時發生錯誤: {e}")
        
        self.processes.clear()
        print("✅ 所有服務器已停止")
    
    def wait_for_interrupt(self):
        """等待中斷信號"""
        try:
            while self.running and any(p.poll() is None for p in self.processes):
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n收到中斷信號...")
        finally:
            self.stop_all()

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="多代理數據分析系統啟動器")
    
    parser.add_argument("--flask-host", default="0.0.0.0", 
                       help="Flask 服務器主機地址 (默認: 0.0.0.0)")
    parser.add_argument("--flask-port", type=int, default=5001,
                       help="Flask 服務器端口 (默認: 5001)")
    parser.add_argument("--ws-host", default="localhost",
                       help="WebSocket 服務器主機地址 (默認: localhost)")
    parser.add_argument("--ws-port", type=int, default=8765,
                       help="WebSocket 服務器端口 (默認: 8765)")
    parser.add_argument("--frontend-host", default="localhost",
                       help="前端服務器主機地址 (默認: localhost)")
    parser.add_argument("--frontend-port", type=int, default=3000,
                       help="前端服務器端口 (默認: 3000)")
    parser.add_argument("--debug", action="store_true",
                       help="啟用調試模式")
    parser.add_argument("--with-frontend", action="store_true",
                       help="同時啟動前端開發服務器")
    parser.add_argument("--api-only", action="store_true",
                       help="僅啟動 API 服務器")
    
    args = parser.parse_args()
    
    # 創建服務器管理器
    manager = ServerManager()
    
    # 設置信號處理器
    def signal_handler(signum, frame):
        print(f"\n收到信號 {signum}")
        manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.api_only:
            # 僅啟動 API 服務器
            print("🚀 僅啟動 API 服務器模式")
            flask_process = manager.start_flask_server(
                args.flask_host, 
                args.flask_port, 
                args.debug
            )
            if flask_process:
                print(f"✅ API 服務器已啟動: http://{args.flask_host}:{args.flask_port}")
                manager.wait_for_interrupt()
        else:
            # 啟動完整系統
            if manager.start_all(
                flask_host=args.flask_host,
                flask_port=args.flask_port,
                ws_host=args.ws_host,
                ws_port=args.ws_port,
                frontend_host=args.frontend_host,
                frontend_port=args.frontend_port,
                debug=args.debug,
                start_frontend=args.with_frontend
            ):
                manager.wait_for_interrupt()
            else:
                print("❌ 系統啟動失敗")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ 啟動過程中發生錯誤: {e}")
        manager.stop_all()
        sys.exit(1)

if __name__ == "__main__":
    main()