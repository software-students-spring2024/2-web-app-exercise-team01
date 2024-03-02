from flask import Flask, request, jsonify, render_template, url_for
from flask import redirect
from flask import jsonify
from flask_pymongo import PyMongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
import pandas as pd
from werkzeug.utils import secure_filename


load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PW = os.getenv("DB_PW")

app = Flask(__name__)

uri = f"mongodb+srv://{DB_USER}:{DB_PW}@sweproject2.v6vtrh6.mongodb.net/?retryWrites=true&w=majority&appName=SWEProject2"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

init_mongo(client)

app.register_blueprint(auth_bp, url_prefix='/auth')

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

'''
CREATE TEMPLATES AND RENDER THEM DEPENDING ON THE ENDPOINT
ISNTEAD OF USING JAVASCRIPT TO INSERT CONTENT
'''

@app.route('/')
def home():
    return redirect('/dashboard')

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

            # Read the file into a pandas DataFrame
            df = pd.read_csv(filepath)

            # Here you can process the DataFrame df as needed
            # For example, printing it to the console or performing operations on it
            print(df)

            # Optionally, after processing, you might want to store the DataFrame in MongoDB
            # This step depends on the structure of your DataFrame and the MongoDB collection's schema

            return jsonify({"success": True, "filename": filename}), 200
        return jsonify({"error": "Invalid file or upload failed"}), 400
    else:
        # GET request - render the upload page
        return render_template('upload.html', section="Upload")



@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', section="Dashboard")

@app.route('/taxes')
def taxes():
    return render_template('taxes.html', section="Taxes")

@app.route('/insights')
def insights():
    return render_template('insights.html', section="Insights")

@app.route('/edit')
def edit():
    return render_template('edit.html')

@app.route('/delete')
def delete():
    return render_template('delete.html')


if __name__ == '__main__':
    app.run(debug=True, port=3000)






if __name__ == "__main__":
    app.run(debug=True)
