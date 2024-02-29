from flask import Flask, request, jsonify, render_template
from flask import redirect
# from dotenv import load_dotenv

app = Flask(__name__)



'''
CREATE TEMPLATES AND RENDER THEM DEPENDING ON THE ENDPOINT
ISNTEAD OF USING JAVASCRIPT TO INSERT CONTENT
'''

@app.route('/')

def home():
    return redirect('/dashboard')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/taxes')
def taxes():
    return render_template('taxes.html')

@app.route('/insights')
def insights():
    return render_template('insights.html')


if __name__ == '__main__':
    app.run(debug=True, port=3000)