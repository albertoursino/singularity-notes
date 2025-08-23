# Welcome to Singularity Notes! 🌌

A fully automated blog delivering bite-sized articles on the latest astronomy discoveries—crafted by AI and driven by cutting-edge research.

## 🛠️ Installation

1. Install Python environment

   ```shell
   python -m venv .venv
   pip install -r requirements.txt
   ```

2. Create an `.env` file in the working directory and set the OpenAI key

   ```env
   OPENAI_API_KEY = ""
   ```

## 🚀 Quickstart

Launch the app with

```shell
poe app
```

### ✨ Create new articles

1. Set the parameters in `config.yaml`
2. Create a new post with

   ```shell
   poe pipe
   ```
