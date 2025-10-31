# DATAGEN (Previously AI-Data-Analysis-MultiAgent)

![DATAGEN Banner](./docs/DATAGEN.jpg "DATAGEN Banner")

## About DATAGEN
DATAGEN is a powerful brand name that represents our vision of leveraging artificial intelligence technology for data generation and analysis. The name combines "DATA" and "GEN"(generation), perfectly embodying the core functionality of this project - automated data analysis and research through a multi-agent system.

Visit us at [DATAGEN Digital](https://datagen.digital/)(website under development) to learn more about our vision and services.

![System Architecture](./docs/Architecture.png)
## Overview

DATAGEN is an advanced AI-powered data analysis and research platform that utilizes multiple specialized agents to streamline tasks such as data analysis, visualization, and report generation. Our platform leverages cutting-edge technologies including LangChain, OpenAI's GPT models, and LangGraph to handle complex research processes, integrating diverse AI architectures for optimal performance.

## Key Features

### Intelligent Analysis Core
- **Advanced Hypothesis Engine**
  - AI-driven hypothesis generation and validation
  - Automated research direction optimization
  - Real-time hypothesis refinement
- **Enterprise Data Processing**
  - Robust data cleaning and transformation
  - Scalable analysis pipelines
  - Automated quality assurance
- **Dynamic Visualization Suite**
  - Interactive data visualization
  - Custom report generation
  - Automated insight extraction

### Advanced Technical Architecture
- **Multi-Agent Intelligence** 
  - Specialized agents for diverse tasks
  - Intelligent task distribution
  - Real-time coordination and optimization
- **Smart Memory Management**
  - State-of-the-art Note Taker agent
  - Efficient context retention system
  - Seamless workflow integration
- **Adaptive Processing Pipeline**
  - Dynamic workflow adjustment
  - Automated resource optimization
  - Real-time performance monitoring

## Why DATAGEN Stands Out

DATAGEN revolutionizes data analysis through its innovative multi-agent architecture and intelligent automation capabilities:

1. **Advanced Multi-Agent System**
   - Specialized agents working in harmony
   - Intelligent task distribution and coordination
   - Real-time adaptation to complex analysis requirements

2. **Smart Context Management**
   - Pioneering Note Taker agent for state tracking
   - Efficient memory utilization and context retention
   - Seamless integration across analysis phases

3. **Enterprise-Grade Performance**
   - Robust and scalable architecture
   - Consistent and reliable outcomes
   - Production-ready implementation

## System Requirements

- Python 3.10 or higher

## Installation

1. Clone the repository:
```bash
git clone https://github.com/starpig1129/DATAGEN.git
```
2. Create and activate a Conda virtual environment:
```bash
conda create -n datagen python=3.10
conda activate datagen
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Set up environment variables:
**Rename `.env Example` to `.env` and fill all the values**
```sh
# Your data storage path(required)
DATA_STORAGE_PATH =./data/

# Conda environment name(required)
CONDA_ENV = datagen

# ChromeDriver executable path(required)
CHROMEDRIVER_PATH =./chromedriver-linux64/chromedriver

# Firecrawl API key (optional)
# Note: If this key is missing, query capabilities may be reduced
FIRECRAWL_API_KEY = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# OpenAI API key (optional)
OPENAI_API_KEY = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Anthropic API key (optional)
ANTHROPIC_API_KEY = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Google API key (optional)
GOOGLE_API_KEY = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# LangChain API key (optional)
# Used for monitoring the processing
LANGCHAIN_API_KEY = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
## Usage

### Using Python Script

You can run the system  using main.py:

1. Place your data file (e.g., YourDataName.csv) in the data directory

2. Modify the user_input variable in the main() function of main.py:
```python
user_input = '''
datapath:YourDataName.csv
Use machine learning to perform data analysis and write complete graphical reports
'''
```

ˇ. Run the script:
```bash
python main.py
```

## Main Components

- `hypothesis_agent`: Generates research hypotheses
- `process_agent`: Supervises the entire research process
- `visualization_agent`: Creates data visualizations
- `code_agent`: Writes data analysis code
- `searcher_agent`: Conducts literature and web searches
- `report_agent`: Writes research reports
- `quality_review_agent`: Performs quality reviews
- `note_agent`: Records the research process

## Workflow

The system uses LangGraph to create a state graph that manages the entire research process. The workflow includes the following steps:

1. Hypothesis generation
2. Human choice (continue or regenerate hypothesis)
3. Processing (including data analysis, visualization, search, and report writing)
4. Quality review
5. Revision as needed

### Agent Model Configuration

Users can customize each agent's language model provider and model configuration by editing the `config/agent_models.yaml` file. This allows for optimization of model selection and parameters based on different agent requirements.

Here's an example structure of `config/agent_models.yaml`:

```yaml
agents:
  hypothesis_agent:
    provider: openai
    model_config:
      model: gpt-5-nano
      temperature: 1.0
  note_agent:
    provider: google
    model_config:
      model: gemini-2.5-pro
      temperature: 1.0
  code_agent:
    provider: anthropic
    model_config:
      model: claude-haiku-4-5
      temperature: 1.0
```

- **provider**: Specifies the language model provider to use (e.g., openai, google, anthropic, ollama, groq)
- **model_config**: Contains model-specific configuration parameters
  - `model`: The specific model name to use
  - `temperature`: Controls the randomness of model output (range: 0.0-2.0)

## Notes

- Ensure you have sufficient API credits, as the system will make multiple API calls.
- The system may take some time to complete the entire research process, depending on the complexity of the task.
- **WARNING**: The agent system may modify the data being analyzed. It is highly recommended to backup your data before using this system.

## Current Issues and Solutions
1. NoteTaker Efficiency Improvement
2. Overall Runtime Optimization
3. Refiner needs to be better
## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=starpig1129/DATAGEN&type=Date)](https://star-history.com/#starpig1129/DATAGEN&Date)

## Other Projects
Here are some of my other notable projects:
### ShareLMAPI
ShareLMAPI is a local language model sharing API that uses FastAPI to provide interfaces, allowing different programs or device to share the same local model, thereby reducing resource consumption. It supports streaming generation and various model configuration methods.
- GitHub: [ShareLMAPI](https://github.com/starpig1129/ShareLMAPI)
### PigPig: Advanced Multi-modal LLM Discord Bot: 
A powerful Discord bot based on multi-modal Large Language Models (LLM), designed to interact with users through natural language. 
It combines advanced AI capabilities with practical features, offering a rich experience for Discord communities.
- GitHub: [ai-discord-bot-PigPig](https://github.com/starpig1129/ai-discord-bot-PigPig)
