from flask import Flask, request, jsonify, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
import werkzeug
from parser_utils import extract_text

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = 'your_super_secret_key'  # 🔒 Replace with a secure key

# --- Config ---
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rag.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB upload limit

# --- CORS Setup for React Frontend ---
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

# --- DB Setup ---
db = SQLAlchemy(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_org = db.Column(db.Boolean, default=False)
    uuid = db.Column(db.String(36), unique=True, nullable=False)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    path = db.Column(db.String(300), nullable=False)
    mimetype = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- Initialization ---
with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()

# --- Helpers ---
def allowed_file(filename, content_type):
    ext = os.path.splitext(filename)[1].lower()
    allowed_exts = ['.pdf', '.docx', '.txt']
    allowed_mimes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
    return ext in allowed_exts and content_type in allowed_mimes

# --- Routes ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400
    user = User(
        email=data['email'],
        password=generate_password_hash(data['password']),  # 🔐 Hashed
        is_org=data.get('is_organization', False),
        uuid=str(uuid.uuid4())
    )
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    session['uuid'] = user.uuid
    return jsonify({"uuid": user.uuid, "message": "Signup successful"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401
    session['user_id'] = user.id
    session['uuid'] = user.uuid
    return jsonify({"uuid": user.uuid, "message": "Login successful"})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route('/whoami', methods=['GET'])
def whoami():
    if 'uuid' not in session:
        return jsonify({"loggedIn": False})
    return jsonify({"loggedIn": True, "uuid": session['uuid']})

@app.route('/upload', methods=['POST'])
def upload():
    if 'uuid' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.filter_by(uuid=session['uuid']).first()
    file = request.files.get('file')
    if not user or not file:
        return jsonify({"error": "Unauthorized or file missing"}), 400

    mimetype = file.mimetype
    if not allowed_file(file.filename, mimetype):
        return jsonify({"error": "Invalid file type"}), 400

    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], user.uuid)
    os.makedirs(user_folder, exist_ok=True)

    filename = werkzeug.utils.secure_filename(file.filename)
    save_path = os.path.join(user_folder, filename)
    file.save(save_path)

    db.session.add(File(filename=filename, path=save_path, mimetype=mimetype, user_id=user.id))
    db.session.commit()
    return jsonify({"message": "Upload successful"})

@app.route('/list-files', methods=['GET'])
def list_files():
    if 'uuid' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = User.query.filter_by(uuid=session['uuid']).first()
    files = File.query.filter_by(user_id=user.id).all()
    return jsonify([f.filename for f in files])

@app.route('/delete-file', methods=['POST'])
def delete_file():
    if 'uuid' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    user = User.query.filter_by(uuid=session['uuid']).first()
    file = File.query.filter_by(filename=data['filename'], user_id=user.id).first()
    if not file:
        return jsonify({"error": "File not found"}), 404

    try:
        os.remove(file.path)
    except Exception:
        pass

    db.session.delete(file)
    db.session.commit()
    return jsonify({"message": "File deleted"})

# --- Serve React Static Build (Optional) ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(f"frontend/build/{path}"):
        return send_from_directory('frontend/build', path)
    else:
        return send_from_directory('frontend/build', 'index.html')

# --- Run ---
if __name__ == "__main__":
    app.run(debug=True)
