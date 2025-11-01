from flask import Flask, render_template, request, Response
from dotenv import load_dotenv
import os, requests, json

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    def stream():
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistralai/mistral-7b-instruct",  # Free, good model
            "stream": True,
            "messages": [
                {"role": "system", "content": "You are Jimmy AI, a friendly helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        }

        with requests.post(url, headers=headers, json=payload, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        content = line[6:]
                        if content == "[DONE]":
                            break
                        try:
                            data_json = json.loads(content)
                            delta = data_json["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield f"data: {delta}\n\n"
                        except Exception:
                            continue

    return Response(stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)
