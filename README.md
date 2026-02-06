# Welcome to Singularity Notes! 🌌

Singularity Notes is a fully automated blog delivering bite-sized posts on the latest astronomy discoveries, powered by AI. The blog is online at [**singularitynotes.com**](https://singularitynotes.com).

🤝 If you want to contribute, please follow the project's [**contribution guide**](contributing.md).

## 🛠️ Development setup (Linux)

1. Install Python environment with [**uv**](https://docs.astral.sh/uv/)

   ```shell
   uv sync --all-extras
   ```

2. Create an `.env` file in the working directory and set the [**OpenAI key**](https://platform.openai.com/docs/api-reference/introduction)

   ```env
   OPENAI_API_KEY = ""
   ```

## 🚀 Usage

- Launch the web app locally

  ```shell
  poe app
  ```

- Adjust the [config.yaml](config.yaml)

- Create a new post

  ```shell
  poe pipe
  ```
