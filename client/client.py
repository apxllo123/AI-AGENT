# client/client.py
import json
import urllib.request
import urllib.parse

SERVER_URL = "http://127.0.0.1:5000"  # change to your deployed URL


def chat(prompt, max_new_tokens=40):
    url = SERVER_URL + "/chat"

    data = {"prompt": prompt, "max_new_tokens": max_new_tokens}
    json_data = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=json_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["reply"]


if __name__ == "__main__":
    while True:
        try:
            prompt = input("You: ").strip()
            if prompt.lower() in ("quit", "exit", "bye"):
                print("Bye!")
                break

            reply = chat(prompt, max_new_tokens=60)
            print("Agent:", reply[:120] + "..." if len(reply) > 120 else reply)

        except KeyboardInterrupt:
            print("\nBye!")
            break
