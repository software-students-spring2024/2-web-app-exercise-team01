from flask import Flask, request, jsonify, render_template
from flask import redirect
from flask_pymongo import PyMongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PW = os.getenv("DB_PW")

app = Flask(__name__)

uri = f"mongodb+srv://{DB_USER}:{DB_PW}@sweproject2.v6vtrh6.mongodb.net/?retryWrites=true&w=majority&appName=SWEProject2"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['SWEProject2']

# Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

'''
CREATE TEMPLATES AND RENDER THEM DEPENDING ON THE ENDPOINT
ISNTEAD OF USING JAVASCRIPT TO INSERT CONTENT
'''

class User(UserMixin):
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def check_password(self, password):
        return check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id):
    user_info = db.users.find_one({"_id": user_id})
    if user_info is not None:
        return User(email=user_info['email'], password=user_info['password'])
    return None

@app.route('/login', methods=['POST'])
def login():
    user_info = db.users.find_one({"email": request.form.get('email')})
    if user_info is not None:
        user = User(email=user_info['email'], password=user_info['password'])
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect('/dashboard')
    return 'Invalid credentials'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/')
@login_required
def home():
    return redirect('/dashboard')

@app.route('/upload')
@login_required
def upload():
    return render_template('upload.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/taxes')
@login_required
def taxes():
    return render_template('taxes.html')

@app.route('/insights')
@login_required
def insights():
    return render_template('insights.html')

@app.route('/edit')
@login_required
def edit():
    return render_template('edit.html')

@app.route('/delete')
@login_required
def delete():
    return render_template('delete.html')

if __name__ == '__main__':
    app.run(debug=True, port=3000)