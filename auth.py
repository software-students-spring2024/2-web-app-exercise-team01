# auth.py
from flask import Blueprint, request, render_template, redirect, url_for, flash
from extensions import login_manager, bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


# Initialize Blueprint for auth routes
auth = Blueprint('auth', __name__)

# Setup Flask-Bcrypt for password hashing
bcrypt = Bcrypt()

# MongoDB setup
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PW = os.getenv("DB_PW")
uri = f"mongodb+srv://{DB_USER}:{DB_PW}@sweproject2.v6vtrh6.mongodb.net/?retryWrites=true&w=majority&appName=SWEProject2"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.your_database_name  
users_collection = db.users  

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({"_id": user_id})
    if not user:
        return None
    return User(user_id)

# Registration route
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if username already exists
        user_exists = users_collection.find_one({"username": username})
        if user_exists:
            flash('Username already exists')
            return redirect(url_for('auth.register'))

        # Hash the password
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert new user into the database
        users_collection.insert_one({"username": username, "password": hashed_pw})

        return redirect(url_for('auth.login'))
    return render_template('register.html')

# Login route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users_collection.find_one({"username": username})
        if user and bcrypt.check_password_hash(user['password'], password):
            user_obj = User(str(user['_id']))  # Ensure string conversion if using ObjectId
            login_user(user_obj)
            return redirect(url_for('main.dashboard'))  # Adjust the redirect as needed
        else:
            flash('Invalid login credentials')
    return render_template('login.html')

# Logout route
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
