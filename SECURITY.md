# Security Policy

AI-AGENT is a learning/personal-assistant project. Please use it responsibly.

## Do not commit secrets

Never commit:

- API keys
- ngrok tokens
- passwords
- private conversations
- private training data
- `.env` files

Use `.env.example` as a template and keep real secrets local.

## Reporting issues

If you find a security problem, open a GitHub issue with enough detail to reproduce it, but do not post private tokens or exploit payloads.

## The server needs a token

`POST /chat`, `GET /memory`, `POST /memory/clear`, and `GET /conversations` need
`ACCESS_TOKEN`. The server makes a temporary token when the variable is empty.
Set a long random `ACCESS_TOKEN` before you publish the port with a tunnel or on
a host. `ALLOWED_ORIGINS` limits the pages that may call the API from another
origin.

## Tool safety

Agent tools should be explicit, understandable, and limited. Avoid adding tools that can damage files, leak data, or run unsafe commands without confirmation.
