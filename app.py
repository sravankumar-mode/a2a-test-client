from flask import Flask, render_template, request, session
import requests
import uuid
import os

app = Flask(__name__)
app.secret_key = "98fe1f123afdd39031ef35a1c534faedb24812613f3fa8e8be36b514c6609e21"

ORCHESTRATOR_URL = "https://orchestrator-agent-164647869041.us-central1.run.app"

@app.route("/", methods=["GET", "POST"])
def index():
    
    if request.method == "GET":
        # 🔄 Reset everything on page refresh
        session.clear()

    if "session_id" not in session:
        session["session_id"] = f"user-session-{uuid.uuid4()}"
    session_id = session["session_id"]

    # 🧠 Init message history
    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":
        user_input = request.form["message"]
        task_id = f"test-task-{uuid.uuid4()}"

        payload = {
            "jsonrpc": "2.0",
            "id": task_id,
            "method": "tasks/send",
            "params": {
                "id": task_id,
                "sessionId": session_id,
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

            history = data.get("result", {}).get("history", [])
            agent_turns = [h for h in history if h.get("role") == "agent"]
            if agent_turns and "parts" in agent_turns[0]:
                response_text = agent_turns[0]["parts"][0]["text"]
            else:
                response_text = "(No agent response found.)"
        except Exception as e:
            response_text = f"Error: {str(e)}"

        # ➕ Append user input and agent response to history
        session["chat_history"].append({"user": user_input, "agent": response_text})
        session.modified = True

    return render_template("index.html", chat_history=session.get("chat_history", []))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
