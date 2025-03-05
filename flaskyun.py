from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import os

app = Flask(__name__)
CORS(app)  # Allow React Native to call this API

# Dictionary to store chat history per user (or session)
chat_histories = {}
MAX_HISTORY_LENGTH = 10  # Stores last 6 messages (3 user, 3 bot)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    user_id = data.get('user_id', 'default')  # Unique user ID for tracking conversation

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Initialize user history if not present
    if user_id not in chat_histories:
        chat_histories[user_id] = [{"role": "system", "content": "You are a helpful assistant."}]

    # Append user's message
    chat_histories[user_id].append({"role": "user", "content": user_message})

    # Keep only the last MAX_HISTORY_LENGTH messages
    chat_histories[user_id] = chat_histories[user_id][-MAX_HISTORY_LENGTH:]

    try:
        # Send the trimmed conversation history
        response = ollama.chat(
            model='dolphin-mistral',
            messages=chat_histories[user_id]
        )

        bot_reply = response['message']['content']
        
        # Append bot's response to history
        chat_histories[user_id].append({"role": "assistant", "content": bot_reply})

        # Again, trim to maintain the recent history
        chat_histories[user_id] = chat_histories[user_id][-MAX_HISTORY_LENGTH:]

        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Get the PORT from Render, default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)
