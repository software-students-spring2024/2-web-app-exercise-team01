from flask import Flask, request, jsonify, render_template, url_for
from flask import redirect
from flask import jsonify
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import pandas as pd
from werkzeug.utils import secure_filename


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
trades_collection = mongo.db.csv

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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'csv'}

app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure UPLOAD_FOLDER exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            df = pd.read_csv(filepath)
            
            # Convert DataFrame to dictionary for MongoDB
            records = df.to_dict(orient='records')
            
            # Insert records into MongoDB - trades collection
            result = trades_collection.insert_many(records)
            
            # Cleanup after saving to database
            os.remove(filepath)
            
            return jsonify({"success": True, "filename": filename, "documents_inserted": len(result.inserted_ids)}), 200
        return jsonify({"error": "Invalid file or upload failed"}), 400
    else:
        # GET request - render the upload page
        return render_template('upload.html', section="Upload")

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', section="Dashboard")

@app.route('/taxes')
@login_required
def taxes():
    return render_template('taxes.html', section="Taxes")

@app.route('/insights')
@login_required
def insights():
    return render_template('insights.html', section="Insights")

@app.route('/edit')
@login_required
def edit():
    return render_template('edit.html')

@app.route('/delete')
@login_required
def delete():
    return render_template('delete.html')

@app.route('/search')
def search():
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True, port=3000)






if __name__ == "__main__":
    app.run(debug=True)
