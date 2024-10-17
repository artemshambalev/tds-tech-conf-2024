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
