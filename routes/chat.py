from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from extensions import db, socketio
from models import ChatMessage, User
from flask_socketio import emit, join_room
import os
import secrets
from werkzeug.utils import secure_filename
from config import Config

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/')
@login_required
def index():
    # Load recent 50 messages
    messages = ChatMessage.query.order_by(ChatMessage.timestamp.asc()).limit(50).all()
    message_data = []
    for m in messages:
        message_data.append({
            'username': m.author.username,
            'content': m.content,
            'type': m.message_type,
            'is_me': m.user_id == current_user.id
        })
    return render_template('chat/index.html', messages=message_data)

@chat_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify(error='No file part'), 400
    file = request.files['file']
    ftype = request.form.get('type', 'image') # 'image' or 'audio'
    
    if file.filename == '':
        return jsonify(error='No selected file'), 400
        
    if file:
        filename = secure_filename(file.filename)
        # Create unique name
        unique_name = secrets.token_hex(8) + "_" + filename
        
        # Ensure upload dir exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
        file.save(file_path)
        
        # URL for client
        file_url = f"/static/uploads/{unique_name}"
        
        # Save to DB
        msg = ChatMessage(user_id=current_user.id, message_type=ftype, content=file_url)
        db.session.add(msg)
        current_user.points += 1
        db.session.commit()
        
        # Emit to all clients
        socketio.emit('new_message', {
            'username': current_user.username,
            'content': file_url,
            'type': ftype
        })
        
        return jsonify(success=True, url=file_url)

@socketio.on('send_message')
def handle_send_message(data):
    if not current_user.is_authenticated:
        return
    text = data.get('content')
    if text:
        msg = ChatMessage(user_id=current_user.id, message_type='text', content=text)
        db.session.add(msg)
        current_user.points += 1
        db.session.commit()
        
        emit('new_message', {
            'username': current_user.username,
            'content': text,
            'type': 'text'
        }, broadcast=True)
