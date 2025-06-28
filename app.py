from flask import Flask, request, jsonify, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
import werkzeug
from parser_utils import extract_text
from rag_utils import load_vector_db, retrieve_chunks, chunk_and_store
import shutil
import gc


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
    extracted_text = extract_text(save_path, mimetype)
    vector_folder = os.path.join('vectors', user.uuid)
    vector_path = os.path.join(vector_folder, f"{filename}.faiss")
    chunk_and_store(extracted_text, vector_path, metadata={"filename": filename})
    print("Extracted text:", extracted_text[:500])  # for dev check
    return jsonify({"message": "Upload successful"})

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    query = data.get('query')
    uuid_input = data.get('uuid')

    user = User.query.filter_by(uuid=session['uuid']).first()
    if not user:
        return jsonify({"error": "Invalid user"}), 400

    vector_folder = os.path.join('vectors', user.uuid)
    if not os.path.exists(vector_folder):
        return jsonify({"error": "No vectors found"}), 400

    results = []
    for vec_file in os.listdir(vector_folder):
        if vec_file.endswith(".faiss"):
            vec_path = os.path.join(vector_folder, vec_file)
            try:
                vectordb = load_vector_db(vec_path)
                chunk_tuples = retrieve_chunks(vectordb, query)  # returns list of (Document, score)
                results.extend(chunk_tuples)
            except Exception as e:
                print(f"Error loading vector DB from {vec_path}: {e}")
                continue

    # Sort by score (lower is better with similarity_search_with_score)
    results = sorted(results, key=lambda x: x[1])

    # Extract top 10 contents
    top_chunks = [doc.page_content for doc, score in results[:10]]
    if vectordb:
        del vectordb
        gc.collect()

    return jsonify({"chunks": top_chunks})

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
        # Delete the uploaded file (e.g., PDF)
        if os.path.exists(file.path):
            os.remove(file.path)

        # Delete the vector folder: e.g. vectors/<uuid>/<filename>.pdf.faiss/
        vector_folder = os.path.join('vectors', user.uuid, f"{file.filename}.faiss")
        if os.path.exists(vector_folder):
            shutil.rmtree(vector_folder)
            print(f"[✓] Deleted vector folder: {vector_folder}")

    except Exception as e:
        print(f"[!] Delete error: {e}")

    db.session.delete(file)
    db.session.commit()
    return jsonify({"message": "File and vector index deleted"})

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
