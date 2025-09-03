# Welcome to Singularity Notes! 🌌

A fully automated blog delivering bite-sized posts on the latest astronomy discoveries—created by AI and driven by cutting-edge research. The blog is online at [**singularitynotes.com**](https://singularitynotes.com) and every 2 days there's a new post!

- 🤝 If you want to contribute follow [**this**](contributing.md) guide.
- 🔎 If you want to try out the app locally, follow the instructions from below.

## 🛠️ Installation

1. Install Python environment with [**Poetry**](https://python-poetry.org/)

   ```shell
   poetry install
   ```

   or with the Python _venv_ module

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

### ✨ Create new posts

1. Set the parameters in `config.yaml`
2. Create a new post with

   ```shell
   poe pipe
   ```
