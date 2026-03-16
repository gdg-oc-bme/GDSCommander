# GDSCommander

A discord bot that assists members in GDSC related inquiries and can give relevant information.


## Run with Docker

```bash
docker build -t gdscommander .
docker run --env-file .env gdscommander
```

*Note: Running the GDSCommander bot happens on DigitalOcean, to see your changes on the bot, please open a pull request.*

## Local development (uv)

Dependencies are declared in `pyproject.toml` and locked in `uv.lock`. Install and run in the project venv:

```sh
uv sync
uv run python setup.py
```

Add a dependency: edit `pyproject.toml` under `[project].dependencies`, then run `uv lock` and `uv sync`. Commit both `pyproject.toml` and `uv.lock`.

## Environment Variables

Environment variables are stored in a `.env` file. **NEVER COMMIT THIS FILE. IT SHOULD BE LOCAL**.

`.env.example` is an example for what the `.env` file should look like. It contains the name of the required environment variables.

To run the bot you need to replace `TOKEN=very_secret_value` with an actual token.


*Note: If you are contributing to this project you will most likely be using a token for a test bot rather than our production token.*

## Feedback

If you have any feedback, please reach out to us on our [Discord](https://discord.gg/VAwkGyHmw9) and let us know!
