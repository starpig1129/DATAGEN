import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Set up API keys and environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
# Get working directory from environment variable
WORKING_DIRECTORY = os.getenv('WORKING_DIRECTORY', './data')
# Get Conda-related paths from environment variables
CONDA_ENV = os.getenv('CONDA_ENV', 'base')
# Get ChromeDriver
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', './chromedriver/chromedriver')