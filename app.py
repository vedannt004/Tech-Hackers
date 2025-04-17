from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, User, Issue
import os

app = Flask(__name__)
app = Flask(__name__, static_folder='../static', static_url_path='/static')
CORS(app)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///govgenie.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create DB tables
with app.app_context():
    db.create_all()

# Serve HTML files
@app.route('/')
def index():
    return send_from_directory('../', 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory('../', filename)

# Routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    user = User(email=data['email'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if user:
        return jsonify({'message': 'Login successful'})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/issues/create', methods=['POST'])
def create_issue():
    title = request.form['title']
    description = request.form['description']
    category = request.form['category']
    photo = request.files.get('photo')

    filename = ''
    if photo:
        filename = photo.filename
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    issue = Issue(title=title, description=description, category=category, photo=filename)
    db.session.add(issue)
    db.session.commit()
    return jsonify({'message': 'Issue submitted'})

@app.route('/api/issues/all')
def get_issues():
    issues = Issue.query.all()
    return jsonify([
        {
            'id': i.id,
            'title': i.title,
            'description': i.description,
            'category': i.category,
            'photo': i.photo,
            'status': i.status,
            'votes': i.votes
        } for i in issues
    ])

@app.route('/api/issues/upvote/<int:issue_id>', methods=['POST'])
def upvote(issue_id):
    issue = Issue.query.get(issue_id)
    if not issue:
        return jsonify({'message': 'Issue not found'}), 404
    issue.votes += 1
    db.session.commit()
    return jsonify({'message': 'Upvoted', 'votes': issue.votes})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
