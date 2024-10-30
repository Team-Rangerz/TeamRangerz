import numpy
import tensorflow
from transformers import pipeline


from flask import Flask, request, jsonify, send_file
import os
from transformers import pipeline
import speech_recognition as sr

app = Flask(__name__)

# Get the current directory where app.py is located
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Load the transformer model for text generation
chatbot = pipeline('text-generation', model='gpt2')

# Sample data
available_slots = ["08:00 - 09:00", "10:00 - 11:00", "13:00 - 14:00"]
doctors = ["Dr. Myeni", "Dr. Masuvhe", "Dr. Lee", "Dr. Mangoato"]

@app.route('/')
def home():
    return send_file(os.path.join(APP_ROOT, 'index.html'))

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json['message']
    print(f"User message: {user_message}")  # Debugging

    # Response logic
    if "available slots" in user_message.lower():
        bot_response = "Here are the available slots:\n" + "\n".join(available_slots)
    elif "cancel" in user_message.lower():
        bot_response = "Your appointment has been canceled."
    elif "doctors" in user_message.lower():
        bot_response = "Here are the available doctors:\n" + "\n".join(doctors)
    elif any(symptom in user_message.lower() for symptom in ["chills", "fever", "headache", "cough"]):
        bot_response = "It seems you might have a fever. Here are some home remedies: Drink warm fluids, rest, and consider over-the-counter medications."
    else:
        # Use the chatbot to generate a response for other queries
        response = chatbot(user_message, max_length=50, num_return_sequences=1)
        bot_response = response[0]['generated_text'].strip()

    return jsonify({"response": bot_response})

@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    # This function will convert speech to text
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your message...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"Recognized text: {text}")  # Debugging
            return jsonify({"text": text})
        except sr.UnknownValueError:
            return jsonify({"text": "Sorry, I could not understand the audio."})
        except sr.RequestError:
            return jsonify({"text": "Could not request results from Google Speech Recognition service."})

if __name__ == '__main__':
    app.run(debug=True)