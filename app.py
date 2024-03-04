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
from flask import flash





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

# Get all trades from the database
trades = trades_collection.find()

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

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_info = mongo.db.users.find_one({"username": request.form.get('username')})
        if user_info is not None:
            user = User(username=user_info['username'], password=user_info['password'])
            if user and user.check_password(request.form.get('password')):
                login_user(user, remember=True)
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
            login_user(User(username=username, password=password), remember=True)
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
            
            # Read the CSV into a DataFrame
            df = pd.read_csv(filepath)
            
            # Add the 'visible_id' column
            df['visible_id'] = range(1, len(df) + 1)
            
            # Reorder columns to make 'visible_id' the first column
            cols = ['visible_id'] + [col for col in df.columns if col != 'visible_id']
            df = df[cols]

            print(df)
            
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
    # group trades by token
    grouptrades = trades_collection.aggregate([
        {
            "$group": {
                "_id": "$Token",
                "netQuantity": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$Transaction", "BUY"]},
                            "$Quantity",
                            {"$multiply": ["$Quantity", -1]}
                        ]
                    }
                }
            }
        }
    ])

    grouptrades_list = list(grouptrades)

    print("grouptrades: ", grouptrades_list)

    print("trades: ", trades)
    return render_template('dashboard.html', section="Dashboard", grouptrades=grouptrades_list)

@app.route('/taxes')
@login_required
def taxes():
    # group trades by token and get profit of each, where profit will have "+" before the number and "-" if it is a loss
    grouptrades = trades_collection.aggregate([
        {
            "$group": {
                "_id": "$Token",
                "profit": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$Transaction", "SELL"]},
                            {"$multiply": ["$Quantity", "$Price"]},
                            {"$multiply": ["$Quantity", -1, "$Price"]}
                        ]
                    }
                }
            }
        }
    ])
    grouptrades_list = list(grouptrades)
    for trade in grouptrades_list:
        trade['profit'] = "{:,.2f}".format(trade['profit'])
    print("grouptrades: ", grouptrades_list)
    return render_template('taxes.html', section="Taxes", grouptrades=grouptrades_list)

@app.route('/insights')
@login_required
def insights():
    return render_template('insights.html', section="Insights")

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
        visible_id = request.form.get('visible_id')
        field = request.form.get('field')
        new_value = request.form.get('new_value')

        try:
            visible_id = int(visible_id)  # Convert visible_id to int
            
            # Update operation here; adjust the field's data type conversion as necessary
            update_result = trades_collection.update_one(
                {"visible_id": visible_id},
                {"$set": {field: new_value}}
            )
            
            if update_result.modified_count > 0:
                flash('Record updated successfully.', 'success')
            else:
                flash('No record found with the given Visible ID, or no change needed.', 'info')
        except ValueError:
            flash('Invalid Visible ID format. Please enter a valid number.', 'error')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')

        return redirect(url_for('edit'))
    
    # GET request to show the form
    return render_template('edit.html')




@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/search_results', methods=['POST'])
def search_results():
    search_query = request.form['search_query']
    results_cursor = trades_collection.find({"Token": {"$regex": search_query, "$options": "i"}})
    # Convert cursor to list and remove the first field from each document
    results = []
    for doc in results_cursor:
        doc_dict = dict(doc)
        if doc_dict:
            # Remove the first key-value pair
            first_key = list(doc_dict.keys())[0]
            doc_dict.pop(first_key)
        results.append(doc_dict)
    
    return render_template('search_results.html', results=results)

@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == "Delete Document":
            visible_id_str = request.form.get('visible_id')
            try:
                visible_id = int(visible_id_str)
                result = trades_collection.delete_one({"visible_id": visible_id})
                if result.deleted_count > 0:
                    flash('Document deleted successfully.', 'success')
                else:
                    flash('No document found with the given Visible ID.', 'warning')
            except ValueError:
                flash('Invalid Visible ID format. Please enter a valid number.', 'error')
            except Exception as e:
                flash(f'Error deleting document: {str(e)}', 'error')
        
        elif action == "Delete All":
            trades_collection.delete_many({})
            flash('All documents deleted successfully.', 'success')
        
        return redirect('/delete')
    
    return render_template('delete.html')



@app.route('/view_db')
def view_db():
    # Fetch all documents from the collection
    documents = list(trades_collection.find())
    # Render a template, passing in the documents
    return render_template('view_db.html', documents=documents)

if __name__ == '__main__':
    app.run(debug=True, port=3000)