from flask import Flask, request, jsonify, send_file
import os
from transformers import pipeline
import speech_recognition as sr
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# directory where app.py is located
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# transformer model for text generation
chatbot = pipeline('text-generation', model='gpt2')

# Sample data
available_slots = ["08:00 - 09:00", "10:00 - 11:00", "13:00 - 14:00"]
doctors = ["Dr. Myeni", "Dr. Masuvhe", "Dr. Lee", "Dr. Mangoato"]

# Database connection configuration
def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='your_username',  # MySQL USERNAME 
        password='your_password',  # MySQL password
        database='chatbot_db'
    )

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
    elif "book appointment" in user_message.lower():
        
        
        user_initials = request.json['initials']
        surname = request.json['surname']
        user_id = request.json['user_id']  # Assuming user_id is passed in the request
        chosen_doctor = "Dr. Myeni"  # put the doctor chosen by the user
        chosen_day = "2024-10-30"  # put the chosen day
        chosen_time = "10:00 - 11:00"  # Put the chosen time
        reminder_set = True  # Set based on our user preference

        # Save every information to our database
        try:
            connection = create_connection()
            cursor = connection.cursor()
            sql = """INSERT INTO appointments (user_initials, surname, user_id, doctor_assigned, chosen_day, chosen_time, reminder_set)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (user_initials, surname, user_id, chosen_doctor, chosen_day, chosen_time, reminder_set))
            connection.commit()
            bot_response = f"Your appointment with {chosen_doctor} has been booked on {chosen_day} at {chosen_time}."
        except Error as e:
            bot_response = f"An error occurred while booking the appointment: {str(e)}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        # our chatbot  generate a response for other queries
        response = chatbot(user_message, max_length=50, num_return_sequences=1)
        bot_response = response[0]['generated_text'].strip()

    return jsonify({"response": bot_response})

@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    # this is our Fuction that will convert speech to text
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
