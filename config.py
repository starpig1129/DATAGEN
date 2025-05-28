"""
多代理數據分析系統配置文件
包含所有服務的配置參數
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ServerConfig:
    """服務器配置"""
    host: str = "0.0.0.0"
    port: int = 5001
    debug: bool = False
    workers: int = 4
    timeout: int = 120

@dataclass
class WebSocketConfig:
    """WebSocket 配置"""
    host: str = "localhost"
    port: int = 8765
    ping_interval: int = 30
    ping_timeout: int = 10
    max_connections: int = 100

@dataclass
class DatabaseConfig:
    """數據庫配置"""
    upload_folder: str = "data_storage"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: set = None
    settings_file: str = "./settings.json"

    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = {
                'txt', 'csv', 'json', 'pdf', 'xlsx', 'xls', 
                'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 
                'md', 'py', 'js', 'html', 'css'
            }

@dataclass
class RealtimeConfig:
    """實時更新配置"""
    enable_websocket: bool = True
    enable_sse: bool = True
    metrics_interval: int = 30  # 秒
    health_check_interval: int = 60  # 秒
    auto_reconnect: bool = True
    max_reconnect_attempts: int = 10
    reconnect_interval: int = 5000  # 毫秒

@dataclass
class AgentConfig:
    """代理配置"""
    max_concurrent_agents: int = 3
    agent_timeout: int = 60000  # 毫秒
    retry_failed_tasks: bool = True
    save_intermediate_results: bool = True
    enable_debugging: bool = False

@dataclass
class CacheConfig:
    """緩存配置"""
    enable_cache: bool = True
    max_cache_size: int = 100 * 1024 * 1024  # 100MB
    cache_ttl: int = 3600  # 秒
    data_retention_limit: int = 100
    auto_cleanup: bool = True
    cleanup_interval: int = 300  # 秒

@dataclass
class SecurityConfig:
    """安全配置"""
    enable_cors: bool = True
    cors_origins: list = None
    api_rate_limit: str = "100/hour"
    require_auth: bool = False
    secret_key: str = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173"
            ]
        if self.secret_key is None:
            self.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

class SystemConfig:
    """系統主配置類"""
    
    def __init__(self):
        # 從環境變數載入配置
        self.server = ServerConfig(
            host=os.environ.get('FLASK_HOST', '0.0.0.0'),
            port=int(os.environ.get('FLASK_PORT', 5001)),
            debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
            workers=int(os.environ.get('WORKERS', 4)),
            timeout=int(os.environ.get('TIMEOUT', 120))
        )
        
        self.websocket = WebSocketConfig(
            host=os.environ.get('WS_HOST', 'localhost'),
            port=int(os.environ.get('WS_PORT', 8765)),
            ping_interval=int(os.environ.get('WS_PING_INTERVAL', 30)),
            ping_timeout=int(os.environ.get('WS_PING_TIMEOUT', 10)),
            max_connections=int(os.environ.get('WS_MAX_CONNECTIONS', 100))
        )
        
        self.database = DatabaseConfig(
            upload_folder=os.environ.get('UPLOAD_FOLDER', 'data_storage'),
            max_file_size=int(os.environ.get('MAX_FILE_SIZE', 100 * 1024 * 1024)),
            settings_file=os.environ.get('SETTINGS_FILE', './settings.json')
        )
        
        self.realtime = RealtimeConfig(
            enable_websocket=os.environ.get('ENABLE_WEBSOCKET', 'True').lower() == 'true',
            enable_sse=os.environ.get('ENABLE_SSE', 'True').lower() == 'true',
            metrics_interval=int(os.environ.get('METRICS_INTERVAL', 30)),
            health_check_interval=int(os.environ.get('HEALTH_CHECK_INTERVAL', 60)),
            auto_reconnect=os.environ.get('AUTO_RECONNECT', 'True').lower() == 'true',
            max_reconnect_attempts=int(os.environ.get('MAX_RECONNECT_ATTEMPTS', 10)),
            reconnect_interval=int(os.environ.get('RECONNECT_INTERVAL', 5000))
        )
        
        self.agent = AgentConfig(
            max_concurrent_agents=int(os.environ.get('MAX_CONCURRENT_AGENTS', 3)),
            agent_timeout=int(os.environ.get('AGENT_TIMEOUT', 60000)),
            retry_failed_tasks=os.environ.get('RETRY_FAILED_TASKS', 'True').lower() == 'true',
            save_intermediate_results=os.environ.get('SAVE_INTERMEDIATE_RESULTS', 'True').lower() == 'true',
            enable_debugging=os.environ.get('ENABLE_DEBUGGING', 'False').lower() == 'true'
        )
        
        self.cache = CacheConfig(
            enable_cache=os.environ.get('ENABLE_CACHE', 'True').lower() == 'true',
            max_cache_size=int(os.environ.get('MAX_CACHE_SIZE', 100 * 1024 * 1024)),
            cache_ttl=int(os.environ.get('CACHE_TTL', 3600)),
            data_retention_limit=int(os.environ.get('DATA_RETENTION_LIMIT', 100)),
            auto_cleanup=os.environ.get('AUTO_CLEANUP', 'True').lower() == 'true',
            cleanup_interval=int(os.environ.get('CLEANUP_INTERVAL', 300))
        )
        
        self.security = SecurityConfig(
            enable_cors=os.environ.get('ENABLE_CORS', 'True').lower() == 'true',
            api_rate_limit=os.environ.get('API_RATE_LIMIT', '100/hour'),
            require_auth=os.environ.get('REQUIRE_AUTH', 'False').lower() == 'true'
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'server': {
                'host': self.server.host,
                'port': self.server.port,
                'debug': self.server.debug,
                'workers': self.server.workers,
                'timeout': self.server.timeout
            },
            'websocket': {
                'host': self.websocket.host,
                'port': self.websocket.port,
                'ping_interval': self.websocket.ping_interval,
                'ping_timeout': self.websocket.ping_timeout,
                'max_connections': self.websocket.max_connections
            },
            'database': {
                'upload_folder': self.database.upload_folder,
                'max_file_size': self.database.max_file_size,
                'allowed_extensions': list(self.database.allowed_extensions),
                'settings_file': self.database.settings_file
            },
            'realtime': {
                'enable_websocket': self.realtime.enable_websocket,
                'enable_sse': self.realtime.enable_sse,
                'metrics_interval': self.realtime.metrics_interval,
                'health_check_interval': self.realtime.health_check_interval,
                'auto_reconnect': self.realtime.auto_reconnect,
                'max_reconnect_attempts': self.realtime.max_reconnect_attempts,
                'reconnect_interval': self.realtime.reconnect_interval
            },
            'agent': {
                'max_concurrent_agents': self.agent.max_concurrent_agents,
                'agent_timeout': self.agent.agent_timeout,
                'retry_failed_tasks': self.agent.retry_failed_tasks,
                'save_intermediate_results': self.agent.save_intermediate_results,
                'enable_debugging': self.agent.enable_debugging
            },
            'cache': {
                'enable_cache': self.cache.enable_cache,
                'max_cache_size': self.cache.max_cache_size,
                'cache_ttl': self.cache.cache_ttl,
                'data_retention_limit': self.cache.data_retention_limit,
                'auto_cleanup': self.cache.auto_cleanup,
                'cleanup_interval': self.cache.cleanup_interval
            },
            'security': {
                'enable_cors': self.security.enable_cors,
                'cors_origins': self.security.cors_origins,
                'api_rate_limit': self.security.api_rate_limit,
                'require_auth': self.security.require_auth
            }
        }
    
    def validate(self) -> list:
        """驗證配置有效性"""
        errors = []
        
        # 驗證端口範圍
        if not (1 <= self.server.port <= 65535):
            errors.append(f"無效的服務器端口: {self.server.port}")
        
        if not (1 <= self.websocket.port <= 65535):
            errors.append(f"無效的 WebSocket 端口: {self.websocket.port}")
        
        # 驗證文件大小
        if self.database.max_file_size <= 0:
            errors.append("最大文件大小必須大於 0")
        
        # 驗證時間間隔
        if self.realtime.metrics_interval <= 0:
            errors.append("指標間隔必須大於 0")
        
        if self.realtime.health_check_interval <= 0:
            errors.append("健康檢查間隔必須大於 0")
        
        # 驗證代理配置
        if self.agent.max_concurrent_agents <= 0:
            errors.append("最大併發代理數必須大於 0")
        
        if self.agent.agent_timeout <= 0:
            errors.append("代理超時時間必須大於 0")
        
        # 驗證緩存配置
        if self.cache.max_cache_size <= 0:
            errors.append("最大緩存大小必須大於 0")
        
        if self.cache.cache_ttl <= 0:
            errors.append("緩存 TTL 必須大於 0")
        
        return errors
    
    def get_frontend_config(self) -> Dict[str, Any]:
        """獲取前端需要的配置"""
        return {
            'apiBaseUrl': f"http://{self.server.host}:{self.server.port}",
            'wsUrl': f"ws://{self.websocket.host}:{self.websocket.port}",
            'maxFileSize': self.database.max_file_size,
            'allowedExtensions': list(self.database.allowed_extensions),
            'enableRealtime': self.realtime.enable_websocket,
            'autoReconnect': self.realtime.auto_reconnect,
            'maxReconnectAttempts': self.realtime.max_reconnect_attempts,
            'reconnectInterval': self.realtime.reconnect_interval
        }

# 創建全域配置實例
config = SystemConfig()

def load_config_from_file(file_path: str) -> SystemConfig:
    """從文件載入配置"""
    import json
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 更新環境變數
        for section, values in data.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    env_key = f"{section.upper()}_{key.upper()}"
                    os.environ[env_key] = str(value)
        
        # 重新創建配置實例
        return SystemConfig()
        
    except FileNotFoundError:
        print(f"配置文件不存在: {file_path}")
        return config
    except json.JSONDecodeError as e:
        print(f"配置文件格式錯誤: {e}")
        return config
    except Exception as e:
        print(f"載入配置文件失敗: {e}")
        return config

def save_config_to_file(config_instance: SystemConfig, file_path: str) -> bool:
    """保存配置到文件"""
    import json
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_instance.to_dict(), f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存配置文件失敗: {e}")
        return False

def print_config_summary(config_instance: SystemConfig = None):
    """打印配置摘要"""
    if config_instance is None:
        config_instance = config
    
    print("=" * 60)
    print("系統配置摘要")
    print("=" * 60)
    print(f"🌐 Flask 服務器:    {config_instance.server.host}:{config_instance.server.port}")
    print(f"🔌 WebSocket 服務器: {config_instance.websocket.host}:{config_instance.websocket.port}")
    print(f"📁 上傳目錄:       {config_instance.database.upload_folder}")
    print(f"📏 最大文件大小:    {config_instance.database.max_file_size // (1024*1024)} MB")
    print(f"⚡ 實時更新:       {'啟用' if config_instance.realtime.enable_websocket else '禁用'}")
    print(f"🤖 最大併發代理:    {config_instance.agent.max_concurrent_agents}")
    print(f"💾 緩存:          {'啟用' if config_instance.cache.enable_cache else '禁用'}")
    print(f"🔒 CORS:          {'啟用' if config_instance.security.enable_cors else '禁用'}")
    print(f"🐛 調試模式:       {'啟用' if config_instance.server.debug else '禁用'}")
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="系統配置管理")
    parser.add_argument("--validate", action="store_true", help="驗證當前配置")
    parser.add_argument("--summary", action="store_true", help="顯示配置摘要")
    parser.add_argument("--export", help="導出配置到文件")
    parser.add_argument("--import", dest="import_file", help="從文件導入配置")
    
    args = parser.parse_args()
    
    current_config = config
    
    if args.import_file:
        current_config = load_config_from_file(args.import_file)
        print(f"已從 {args.import_file} 載入配置")
    
    if args.validate:
        errors = current_config.validate()
        if errors:
            print("❌ 配置驗證失敗:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("✅ 配置驗證通過")
    
    if args.summary:
        print_config_summary(current_config)
    
    if args.export:
        if save_config_to_file(current_config, args.export):
            print(f"✅ 配置已導出到 {args.export}")
        else:
            print(f"❌ 配置導出失敗")
    
    if not any([args.validate, args.summary, args.export, args.import_file]):
        print_config_summary(current_config)