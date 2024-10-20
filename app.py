from flask import Flask, request, jsonify, send_file
import os

app = Flask(__name__)

# Get the current directory where app.py is located
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def home():
    # Send the index.html file located in the same directory as app.py
    return send_file(os.path.join(APP_ROOT, 'index.html'))

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json['message']

    # Example bot response logic
    if "available slots" in user_message.lower():
        bot_response = "Here are the available slots:\n1. 08:00 - 09:00\n2. 10:00 - 11:00\n3. 13:00 - 14:00"
    elif "2" in user_message:
        bot_response = "Your appointment at 10:00 has been scheduled. Please tell me your symptoms."
    elif any(symptom in user_message.lower() for symptom in ["chills", "feeling cold", "shivering", "shaking", "body aches", "headaches"]):
        bot_response = "It seems you have a fever. I will assign you to a specific doctor for fever."
    else:
        bot_response = "Hello! How can I assist you today?"

    return jsonify({"response": bot_response})

if __name__ == '__main__':
    app.run(debug=True)
