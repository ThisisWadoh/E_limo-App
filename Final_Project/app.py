from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, send_from_directory
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()  # Load environment variables

app = Flask(__name__)
app.secret_key = "your_secret_key"

user_database = {}

# Database connection
try: 
    db = mysql.connector.connect(
        host = os.getenv("DB_HOST"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        database = os.getenv("DB_NAME")
    )
    print("Database connection successful")

except mysql.connector .Error as err:
    print(f"Error: {err}")
    exit(1)

# Route to load home page
@app.route('/')
def home():
    return render_template("index.html")

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Validation
        if not email or '@' not in email:
            flash("A valid email address is required.", 'error')
            return render_template('login.html')
        if not password:
            flash("Password is required.", 'error')
            return render_template('login.html')

        # Check if user exists
        user = user_database.get(email)
        if not user or user['password'] != password:
            flash("Invalid email or password.", 'error')
            return render_template('login.html')

        flash("Login successful! Welcome back.", 'success')
        return redirect(url_for('home'))  # Redirect to the homepage or dashboard

    return render_template('login.html')

# Registration Route 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        owner_name = request.form.get('owner_name')
        crop = request.form.get('crop')
        location = request.form.get('location')
        planting_date = request.form.get('planting_date')
        soil_type = request.form.get('soil_type')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validation
        errors = []
        if not owner_name:
            errors.append("Farm owner's name is required.")
        if not crop:
            errors.append("Crop planted is required.")
        if not location:
            errors.append("Location is required.")
        if not planting_date:
            errors.append("Date of planting is required.")
        if not soil_type:
            errors.append("Soil type is required.")
        if not email or '@' not in email:
            errors.append("A valid email address is required.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")

        # If errors exist, flash them and reload the page
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')

        # Check if email already exists
        if email in user_database:
            flash("An account with this email already exists.", 'error')
            return render_template('register.html')

        # Save user in the simulated database
        user_database[email] = {
            "owner_name": owner_name,
            "crop": crop,
            "location": location,
            "planting_date": planting_date,
            "soil_type": soil_type,
            "password": password
        }

        flash("Registration successful! You can now login.", 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Services Route
@app.route('/services')
def services():
    return render_template('services.html')

# About Route
@app.route('/about')
def about():
    return render_template('about.html')

# Contacts Route
@app.route('/contact')
def contact():
    return render_template('contact.html')


# Serving favicon in Flask
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Flask route
@app.route('/api/irrigate', methods=['POST'])
def control_irrigation():
    data = request.json
    action = data.get('action')  # 'start' or 'stop'
    crop = data.get('crop')

# Validate input
    if not action or not crop:
        return jsonify({"status": "Error", "message": "Missing 'action' or 'crop' in the request"}), 400
    
    return jsonify({"message": f"Irrigation {action} for {crop} started"})

    
    # Logic to determine irrigation status based on thresholds
    cursor = db.cursor()
    cursor.execute("SELECT * FROM crop_water_requirements WHERE crop=%s", (crop,))
    result = cursor.fetchone()
    cursor.close()

    if not result:
        return jsonify({"status": "Error", "message": "Crop not found"}), 404
    
    if action == 'start':
        # Send command to microcontroller
        return jsonify({"status": "Success", "message": "Irrigation started"})
    elif action == 'stop':
        # Send command to microcontroller
        return jsonify({"status": "Success", "message": "Irrigation stopped"})
    else:
        return jsonify({"status": "Error", "message": "Invalid action"}), 400

if __name__ == '__main__':
    app.run(debug=True)

