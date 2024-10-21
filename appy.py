from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Initialize SQLite database
def init_sqlite_db():
    conn = sqlite3.connect('chatbotdb.db')
    print("Opened database successfully")

    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)')
    print("Table created successfully")
    conn.close()

# Initialize the DB
init_sqlite_db()

# Serve the signup.html file directly from the CHATBOT folder
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Insert data into the database
        conn = sqlite3.connect('chatbotdb.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        conn.close()

        flash('Signup successful!')
        return redirect(url_for('signup'))

    return send_from_directory(directory=os.getcwd(), path='signup.html')


if __name__ == '__main__':
    app.run(debug=True)
