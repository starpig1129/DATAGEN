#!/usr/bin/env python3
"""
開發環境一鍵啟動腳本
同時啟動後端 WebSocket 服務和前端開發伺服器
"""

import asyncio
import subprocess
import sys
import os
import webbrowser
import time
from typing import List, Optional


class DevServerManager:
    """開發伺服器管理器"""

    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.running = False

    async def start_backend(self) -> subprocess.Popen:
        """啟動後端 WebSocket 服務"""
        print("🚀 啟動後端 WebSocket 服務...")
        try:
            # 切換到 backend 目錄
            backend_dir = os.path.join(os.path.dirname(__file__), "backend")
            process = subprocess.Popen(
                [sys.executable, "app/main.py"],
                cwd=backend_dir,
                # stdout=subprocess.PIPE,  # 註解掉以顯示後端日誌
                # stderr=subprocess.PIPE,
                # text=True,
                # bufsize=1,
                # universal_newlines=True
            )
            print(f"✅ 後端服務已啟動 (PID: {process.pid})")
            return process
        except Exception as e:
            print(f"❌ 後端服務啟動失敗: {e}")
            raise

    async def start_frontend(self) -> subprocess.Popen:
        """啟動前端開發伺服器"""
        print("🚀 啟動前端開發伺服器...")
        try:
            # 切換到 frontend 目錄
            frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            print(f"✅ 前端服務已啟動 (PID: {process.pid})")
            return process
        except Exception as e:
            print(f"❌ 前端服務啟動失敗: {e}")
            raise

    def open_browser(self, delay: float = 3.0):
        """打開瀏覽器"""
        def _open_browser():
            time.sleep(delay)  # 等待服務器啟動
            print(f"🌐 自動打開瀏覽器: http://localhost:3000")
            webbrowser.open("http://localhost:3000")

        import threading
        browser_thread = threading.Thread(target=_open_browser, daemon=True)
        browser_thread.start()

    async def monitor_processes(self):
        """監控進程狀態"""
        while self.running:
            if self.backend_process and self.backend_process.poll() is not None:
                print("⚠️  後端服務已停止")
                break
            if self.frontend_process and self.frontend_process.poll() is not None:
                print("⚠️  前端服務已停止")
                break
            await asyncio.sleep(1)

    async def start_all(self):
        """啟動所有服務"""
        print("🎯 開始啟動開發環境...")
        print("=" * 50)

        self.running = True

        try:
            # 並發啟動後端和前端服務
            backend_task = asyncio.create_task(self.start_backend())
            frontend_task = asyncio.create_task(self.start_frontend())

            self.backend_process = await backend_task
            self.frontend_process = await frontend_task

            print("=" * 50)
            print("🎉 所有服務已啟動！")
            print("📊 後端服務: http://localhost:5001")
            print("🌐 前端開發伺服器: http://localhost:3000")
            print("=" * 50)

            # 打開瀏覽器
            self.open_browser()

            # 監控進程
            await self.monitor_processes()

        except KeyboardInterrupt:
            print("\n⚠️  收到中斷信號，正在關閉服務...")
        except Exception as e:
            print(f"\n❌ 啟動過程中發生錯誤: {e}")
        finally:
            await self.stop_all()

    async def stop_all(self):
        """停止所有服務"""
        print("\n🛑 正在關閉所有服務...")
        self.running = False

        processes_to_stop = []

        if self.backend_process:
            processes_to_stop.append(("後端 WebSocket", self.backend_process))
        if self.frontend_process:
            processes_to_stop.append(("前端", self.frontend_process))

        for name, process in processes_to_stop:
            try:
                print(f"正在停止 {name} 服務 (PID: {process.pid})...")
                process.terminate()

                # 等待進程結束
                try:
                    await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, process.wait
                        ),
                        timeout=10.0
                    )
                    print(f"✅ {name} 服務已停止")
                except asyncio.TimeoutError:
                    print(f"⚠️  {name} 服務無回應，正在強制終止...")
                    process.kill()
                    process.wait()
                    print(f"✅ {name} 服務已強制終止")

            except Exception as e:
                print(f"❌ 停止 {name} 服務時發生錯誤: {e}")

        print("🎯 開發環境已完全關閉")


async def main():
    """主函數"""
    # 檢查是否在正確的目錄
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ 錯誤: 請在專案根目錄運行此腳本")
        print("當前目錄:", os.getcwd())
        return

    # 檢查依賴
    print("🔍 檢查專案依賴...")

    # 檢查後端依賴
    backend_requirements = os.path.join("backend", "requirements.txt")
    if not os.path.exists(backend_requirements):
        print("⚠️  警告: 找不到 backend/requirements.txt")
    else:
        print("✅ 後端依賴檔案存在")

    # 檢查前端依賴
    frontend_package = os.path.join("frontend", "package.json")
    if not os.path.exists(frontend_package):
        print("⚠️  警告: 找不到 frontend/package.json")
    else:
        print("✅ 前端依賴檔案存在")

    print("=" * 50)

    # 創建管理器並啟動服務
    manager = DevServerManager()
    await manager.start_all()


if __name__ == "__main__":
    # 設置事件循環策略 (Windows 兼容)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 再見！")
    except Exception as e:
        print(f"\n❌ 發生未預期的錯誤: {e}")
        sys.exit(1)