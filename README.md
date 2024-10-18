# TDS TechConf Agents DEMO

This is a demo project for the TDS TechConf 2024. It is a simple project that demonstrates how to use the LLM Agents.

## Pre-requisites

- Python 3.12 or higher. I suggest using [pyenv](https://github.com/pyenv/pyenv) for managing Python versions.
- Ollama. You can install from brew: `brew install ollama` or from the [official website](https://ollama.com/).
- For Jira example, you'll need to have a Jira account and a Jira API token. You can create a token [here](https://id.atlassian.com/manage-profile/security/api-tokens).

## Models

For this demo, I used `llama3` and `mxbai-embed-large` models.

You can download them using ollama, but make sure tham ollama is running (`ollama serve`):

```bash
ollama pull llama3.1:8b
ollama pull mxbai-embed-large
```

## Installation

Install python libraries using pip

```bash
pip install -r ./requirements.txt
```

## Configuration

Make sure to provide environment variables when you run the app:

- `OLLAMA_MODEL` - Ollama model to use ("llama3.1:8b" is default)
- `JIRA_EMAIL` - Your Jira email
- `JIRA_TOKEN` - Your Jira token
- `JIRA_PROJECT_KEY` - Two(three?)-letter jira project code
- `UNITY_PROJECT_PATH` - Path to your Unity project (without trailing `/`, like `../FlappyBirdClone`)

## Running 

1. Make sure that ollama has all the models and running (`ollama serve`)
2. Run the app `streamlit run ./Intro.py`
3. Enjoy
