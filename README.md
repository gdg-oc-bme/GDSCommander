# GDSCommander

A discord bot that assists members in GDSC related inquiries and can give relevant information.

## Deployment

Run locally (requires [uv](https://docs.astral.sh/uv/), Python 3.10 or 3.11):

```bash
uv sync
uv run python setup.py
```

*Note: Running the GDSCommander bot happens on DigitalOcean, to see your changes on the bot, please open a pull request.*

## Dependencies (uv)

Dependencies are declared in `pyproject.toml` and locked in `uv.lock`. Install and run in the project venv:

```sh
uv sync   # create .venv and install from lock
uv run python setup.py  # run bot (uses .venv)
```

Add a dependency: edit `pyproject.toml` under `[project].dependencies`, then run `uv lock` and `uv sync`. Commit both `pyproject.toml` and `uv.lock`.

## Environment Variables

Environment variables are stored in a `.env` file. **NEVER COMMIT THIS FILE. IT SHOULD BE LOCAL**.

`.env.example` is an example for what the `.env` file should look like. It contains the name of the required environment variables.

To run the bot you need to replace `TOKEN=very_secret_value` with an actual token.


*Note: If you are contributing to this project you will most likely be using a token for a test bot rather than our production token.*

## Feedback

If you have any feedback, please reach out to us on our [Discord](https://discord.gg/VAwkGyHmw9) and let us know!
