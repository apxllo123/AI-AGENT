# iPad 10th Gen + Google Colab Setup

Use this if you only have an iPad. Your iPad is the screen/UI; Colab provides the compute.

## 1. Open Colab

Go to <https://colab.research.google.com> in Safari.

## 2. Clone your repo

Run this in a Colab cell:

```bash
!git clone https://github.com/apxllo123/AI-AGENT.git
%cd AI-AGENT
```

If you are testing files from a zip, upload the zip to Colab instead and unzip it.

## 3. Install dependencies

```bash
!pip install -r requirements.txt
!npm install
```

## 4. Train the tiny model

Fast test:

```bash
!python train.py --quick
```

Better training:

```bash
!python train.py --steps 1500 --batch-size 32 --n-embd 128 --n-layer 4 --n-head 4
```

Training creates:

```text
artifacts/model.pt
artifacts/bpe.pkl
python-service/artifacts/model.pt
python-service/artifacts/bpe.pkl
```

## 5. Create a public URL for the web app

Colab does not automatically give a public web URL. One simple option is ngrok:

```bash
!pip install pyngrok
```

```python
from pyngrok import ngrok
public_url = ngrok.connect(8080)
print(public_url)
```

> ngrok may ask for a free auth token. If it does, create one at ngrok.com and run `ngrok.set_auth_token("YOUR_TOKEN")` before `ngrok.connect(8080)`.

## 6. Start the full app

Run this in a Colab cell and keep it running:

```bash
!chmod +x start_agent.sh
!./start_agent.sh
```

Open the ngrok URL from step 5 in Safari on your iPad.

## API-only test

If you only want to test the Python API:

```bash
!PORT=8081 python python-service/app.py
```

Then in another cell:

```bash
!curl -X POST http://127.0.0.1:8081/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"calculate 9*9"}'
```

## Alternatives to ngrok

- Cloudflare Tunnel
- GitHub Codespaces port forwarding
- Replit
- Render
- Railway

## Tips

- Add better examples to `data/tiny_data.txt`.
- Use a consistent format:

```text
User: question here
Assistant: answer here
```

- A tiny from-scratch model is for learning. Use the agent tools and optional Ollama/cloud model for stronger answers.
