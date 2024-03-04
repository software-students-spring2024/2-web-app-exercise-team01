from flask import Flask, request, jsonify, render_template
from flask import redirect
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PW = os.getenv("DB_PW")

app = Flask(__name__)
app.secret_key = os.urandom(12)
app.config["MONGO_URI"] = f"mongodb+srv://{DB_USER}:{DB_PW}@sweproject2.v6vtrh6.mongodb.net/sweproject2?retryWrites=true&w=majority&appName=SWEProject2"
mongo = PyMongo(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

'''
CREATE TEMPLATES AND RENDER THEM DEPENDING ON THE ENDPOINT
ISNTEAD OF USING JAVASCRIPT TO INSERT CONTENT
'''

class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.username = username
        self.password = password

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(username):
    print("load user username: ", username)
    user_info = mongo.db.users.find_one({"username": username})
    if user_info is not None:
        return User(username=user_info['username'], password=user_info['password'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_info = mongo.db.users.find_one({"username": request.form.get('username')})
        if user_info is not None:
            user = User(username=user_info['username'], password=user_info['password'])
            if user and user.check_password(request.form.get('password')):
                login_user(user)
                return redirect('/dashboard')
        return 'Invalid credentials'
    else:
        if current_user.is_authenticated:
            return redirect('/dashboard')
        else:
            return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect('/dashboard')
    else:
        return redirect('/login')
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = mongo.db.users.find_one({"username": username})
        if existing_user is None:
            hashed_password = generate_password_hash(password)
            mongo.db.users.insert_one({"username": username, "password": hashed_password})
            login_user(User(username=username, password=password))
            return redirect('/dashboard')
        else:
            return 'Username already exists'
    else:
        if current_user.is_authenticated:
            return redirect('/dashboard')
        else:
            return render_template('signup.html')

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