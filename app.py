import os
import sklearn

APP_ROOT = os.path.dirname(os.path.abspath(__file__))  # Gets the directory where the current file is located


from flask import Flask, request, jsonify, send_file
import mysql.connector
import os

#Code for symptom classifier training with TF-IDF and Logistic Regression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

# Sample dataset for symptoms and doctor specialties
symptom_data = ["chills", "cough", "stomach ache", "joint pain"]
doctor_specialty = ["fever specialist", "respiratory specialist", "digestive specialist", "pain management specialist"]

# Vectorization and model setup
vectorizer = TfidfVectorizer()
X_train = vectorizer.fit_transform(symptom_data)
y_train = np.array(doctor_specialty)

model = LogisticRegression()
model.fit(X_train, y_train)

def assign_doctor(symptom_input):
    X_test = vectorizer.transform([symptom_input])
    return model.predict(X_test)[0]


app = Flask(__name__)

# Database connection configuration
db_config = {
    'user': 'root',  
    'password': '',  
    'host': 'localhost',
    'database': 'chatbot_db' 
}

# Initialize user chat data
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

@app.route('/')
def home():
    # Send the index.html file located in the same directory as app.py
    return send_file(os.path.join(APP_ROOT, 'index.html'))

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json['message'].lower()

    # Step 1: User greets the bot
    if not user_data["greeted"] and any(greet in user_message for greet in ["hi", "hello", "hey"]):
        user_data["greeted"] = True
        bot_response = "Hello! Could you please provide your details in this format: Initials, Surname, and ID Number?"

    # Step 2: User provides details
    elif user_data["greeted"] and not user_data["details_provided"]:
        if "," in user_message:
            initials, surname, id_number = map(str.strip, user_message.split(",", 2))
            user_data.update({"details_provided": True, "\n initials": initials, "surname": surname, "id_number": id_number})
            bot_response = f"Thank you, {initials} {surname}. How may I assist you today?"
        else:
            bot_response = "Please provide your details in the correct format: Initials, Surname, and ID Number."

    # Step 3: User mentions feeling unwell
    elif user_data["details_provided"] and not user_data["feeling_unwell"] and any(
        phrase in user_message for phrase in ["i'm sick", "i'm not feeling okay", "i'm not well", "not feeling well"]):
        user_data["feeling_unwell"] = True
        bot_response = "I'm sorry to hear that. Could you please tell me your symptoms?"

    # Step 4: User provides symptoms and the bot assigns a doctor based on category
    elif user_data["feeling_unwell"] and not user_data["symptoms_provided"]:
        # Check symptoms and assign appropriate doctor
        fever_symptoms = ["chills", "feeling cold", "shivering", "body aches", "headaches"]
        respiratory_symptoms = ["cough", "sore throat", "shortness of breath", "wheezing"]
        digestive_symptoms = ["nausea", "vomiting", "stomach ache", "diarrhea"]
        pain_symptoms = ["back pain", "joint pain", "muscle pain", "headache"]

        if any(symptom in user_message for symptom in fever_symptoms):
            doctor_assigned, category = "Dr. Smith", "fever specialist"
        elif any(symptom in user_message for symptom in respiratory_symptoms):
            doctor_assigned, category = "Dr. Johnson", "respiratory specialist"
        elif any(symptom in user_message for symptom in digestive_symptoms):
            doctor_assigned, category = "Dr. Lee", "digestive specialist"
        elif any(symptom in user_message for symptom in pain_symptoms):
            doctor_assigned, category = "Dr. Davis", "pain management specialist"
        else:
            bot_response = "Could you specify your symptoms?"
            return jsonify({"response": bot_response})

        user_data.update({"symptoms_provided": True, "doctor_assigned": doctor_assigned, "doctor_category": category})
        bot_response = f"Thank you for sharing. It seems you need a {category}. I will assign you to {doctor_assigned}."

    # Step 5: User asks for available slots
    elif user_data["doctor_assigned"] and "available slots" in user_message:
        bot_response = f"{user_data['doctor_assigned']} is available Monday to Friday. Please pick a day."

    # Step 6: User picks a day
    elif user_data["doctor_assigned"] and any(day in user_message for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]):
        user_data["chosen_day"] = user_message.capitalize()
        bot_response = f"Available slots for {user_data['chosen_day']}:\n1. 09:00 - 10:00\n2. 11:00 - 12:00\n3. 14:00 - 15:00\n4. 16:00 - 17:00"

    # Step 7: User picks a time slot
    elif "09:00" in user_message or "11:00" in user_message or "14:00" in user_message or "16:00" in user_message:
        user_data.update({"chosen_time": user_message, "appointment_confirmed": True})
        bot_response = (
            f"Thank you! Your appointment has been set with {user_data['doctor_assigned']} on "
            f"{user_data['chosen_day']} at {user_data['chosen_time']}. "
            "Would you like to cancel the appointment or keep it?"
        )

    # Step 8: User decides to cancel or keep the appointment
    elif user_data["appointment_confirmed"] and "cancel" in user_message:
        user_data["appointment_cancelled"] = True
        bot_response = "Your appointment has been cancelled."

    elif user_data["appointment_confirmed"] and not user_data["appointment_cancelled"] and "keep" in user_message:
        bot_response = "Would you like to be reminded about your appointment?"

    # Step 9: User decides on receiving a reminder
    elif user_data["appointment_confirmed"] and not user_data["appointment_cancelled"] and "remind" in user_message:
        user_data["reminder_set"] = True
        bot_response = "A reminder has been set for your appointment. Thank you!"

        # Save appointment to the database
        save_appointment_to_db()

    # Default response
    else:
        bot_response = "Hello! How can I assist you today?"

    return jsonify({"response": bot_response})

# Function to save appointment to the MySQL database
def save_appointment_to_db():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO appointments (user_initials, surname, id_number, doctor, day, time, reminder)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (
        user_data["initials"],
        user_data["surname"],
        user_data["id_number"],
        user_data["doctor_assigned"],
        user_data["chosen_day"],
        user_data["chosen_time"],
        user_data["reminder_set"]
    ))
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
