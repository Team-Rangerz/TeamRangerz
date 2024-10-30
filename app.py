import os
import openai
from flask import Flask, request, jsonify, send_file
import mysql.connector

app = Flask(__name__)

# Set up OpenAI API key
openai.api_key = 'sk-Tv-UYlJcHWwrfwEFDjCQb64en5wki1wLU514bV2la-T3BlbkFJiKNTmuwuRVXUaW4c58t2q3NU5JrLN2iZiD3ofFccoA'

# Database connection configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'chatbot_db'
}

# Initialize user session data
user_data = {
    "greeted": False,
    "details_provided": False,
    "feeling_unwell": False,
    "symptoms_provided": False,
    "doctor_assigned": False,
    "appointment_confirmed": False,
    "appointment_cancelled": False,
    "reminder_set": False
}

# Root route to serve the index page
@app.route('/')
def home():
    APP_ROOT = 'C:/Users/User/Documents/Chatbot'  # Use the real path to your project directory

    return send_file(os.path.join(APP_ROOT, 'index.html'))

# Endpoint for chatbot responses
@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json['message']

    # Call OpenAI API for response
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_message}
            ],
            max_tokens=150
        )
        bot_response = response.choices[0].message['content'].strip()
    except Exception as e:
        bot_response = f"I'm having trouble connecting to my knowledge source. Error: {str(e)}"

    return jsonify({"response": bot_response})

# Function to save appointment to the MySQL database
def save_appointment_to_db():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO appointments (user_initials, surname, id_number, doctor, day, time, reminder)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (
        user_data.get("initials"),
        user_data.get("surname"),
        user_data.get("id_number"),
        user_data.get("doctor_assigned"),
        user_data.get("chosen_day"),
        user_data.get("chosen_time"),
        user_data.get("reminder_set")
    ))
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
