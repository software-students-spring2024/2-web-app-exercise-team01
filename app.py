from flask import Flask, request, jsonify, render_template
from flask import redirect
from flask_pymongo import PyMongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PW = os.getenv("DB_PW")

app = Flask(__name__)

uri = f"mongodb+srv://{DB_USER}:{DB_PW}@sweproject2.v6vtrh6.mongodb.net/?retryWrites=true&w=majority&appName=SWEProject2"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

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

@app.route('/upload')
def upload():
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