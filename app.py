from flask import Flask, render_template, request
import requests
import uuid
import json
import os

app = Flask(__name__)

ORCHESTRATOR_URL = "https://orchestrator-agent-164647869041.us-central1.run.app"

@app.route("/", methods=["GET", "POST"])
def index():
    response_text = None
    if request.method == "POST":
        user_input = request.form["message"]
        task_id = f"test-task-{uuid.uuid4()}"
        payload = {
            "jsonrpc": "2.0",
            "id": task_id,
            "method": "tasks/send",
            "params": {
                "id": task_id,
                "message": {
                    "role": "user",
                    "parts": [
                        {"type": "text", "text": user_input}
                    ]
                }
            }
        }

        try:
            res = requests.post(ORCHESTRATOR_URL, json=payload)
            data = res.json()
            # Safely navigate and extract agent reply
            history = data.get("result", {}).get("history", [])
            agent_turns = [h for h in history if h.get("role") == "agent"]
            if agent_turns and "parts" in agent_turns[0]:
                response_text = agent_turns[0]["parts"][0]["text"]
            else:
                response_text = "(No agent response found.)"
        except Exception as e:
            response_text = f"Error: {str(e)}"

    return render_template("index.html", response=response_text)


# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)