from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from functools import wraps

auth_bp = Blueprint('auth_bp', __name__)

mongo = None  # Placeholder for the MongoDB client

def init_mongo(db_client):
    global mongo
    mongo = db_client

def authenticate_user(username, password):
    user = mongo.db.users.find_one({"username": username})
    if user and check_password_hash(user['password'], password):
        return True
    return False

def basic_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not authenticate_user(auth.username, auth.password):
            return jsonify({"error": "Authentication failed"}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/protected')
@basic_auth_required
def protected():
    return jsonify({"message": "protected endpoint"})
