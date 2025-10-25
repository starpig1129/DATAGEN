"""應用程式設定和組態管理。"""

import os
from pathlib import Path
from dotenv import load_dotenv
import yaml

# 載入環境變數
load_dotenv()

# 指向 backend/config/ 目錄
BASE_DIR = Path(__file__).resolve().parent

# 應用程式設定
APP_TITLE = "多代理數據分析系統 API"
APP_DESCRIPTION = "提供後端 API 服務"
APP_VERSION = "1.0.0"

# API 金鑰和環境變數
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')

# 工作目錄
WORKING_DIRECTORY = os.getenv('WORKING_DIRECTORY', './data')

# Conda 相關路徑
CONDA_ENV = os.getenv('CONDA_ENV', 'base')

# ChromeDriver 路徑
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', './chromedriver/chromedriver')


class AgentModelsConfig:
    """從 YAML 檔案載入代理模型組態的類別。"""

    def __init__(self, config_path: Path = BASE_DIR / 'agent_models.yaml'):
        """初始化組態，載入 YAML 檔案。

        Args:
            config_path: YAML 組態檔案的路徑。

        Raises:
            FileNotFoundError: 如果組態檔案不存在。
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Configuration file not found: {config_path}") from e

    @property
    def agents(self):
        """取得代理組態。"""
        return self._config.get('agents', {})

    def get_agent_config(self, agent_name: str):
        """取得特定代理的組態。

        Args:
            agent_name: 代理名稱。

        Returns:
            代理組態字典，如果未找到則為空字典。
        """
        return self.agents.get(agent_name, {})

    def get_provider(self, agent_name: str):
        """取得特定代理的提供者。

        Args:
            agent_name: 代理名稱。

        Returns:
            提供者名稱，如果未找到則為 None。
        """
        agent_config = self.get_agent_config(agent_name)
        return agent_config.get('provider')

    def get_model_config(self, agent_name: str):
        """取得特定代理的模型組態。

        Args:
            agent_name: 代理名稱。

        Returns:
            模型組態字典，如果未找到則為空字典。
        """
        agent_config = self.get_agent_config(agent_name)
        return agent_config.get('model_config', {})


# 建立全局實例
AGENT_MODELS = AgentModelsConfig()