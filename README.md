# Welcome to Singularity Notes! 🌌

A fully automated blog delivering bite-sized posts on the latest astronomy discoveries—created by AI and driven by cutting-edge research. The blog is online at [**singularitynotes.com**](https://singularitynotes.com) and every 2 days there's a new post!

- 🤝 If you want to contribute, please follow the project's [**contribution guide**](contributing.md).

## 🛠️ Development setup (Linux)

1. Install Python environment with [**Poetry ≥ 2.1**](https://python-poetry.org/)

   ```shell
   poetry install
   eval $(poetry env activate)
   ```

   or with the Python [**venv**](https://docs.python.org/3/library/venv.html) module

   ```shell
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Create an `.env` file in the working directory and set the [**OpenAI key**](https://platform.openai.com/docs/api-reference/introduction)

   ```env
   OPENAI_API_KEY = ""
   ```

3. Launch the web app locally with

   ```shell
   poe app
   ```

4. Create new posts by

   - setting the parameters in `config.yaml`
   - running

     ```shell
     poe pipe
     ```

## 🏙️ Structure of the repo

- `src/` contains all the files related to the pipeline, which performs the following steps:
  1. `get_arxiv_articles.py`: Fetch articles from [**Arxiv**](https://arxiv.org/)
  2. `select_best_article.py`: Select the most interesting article
  3. `create_raw_post.py`: Create a raw markdown post
  4. `setup_post.py`: Setup the post in Hugo
- `test/` contains unit tests
- `app/` contains the Hugo configuration files
