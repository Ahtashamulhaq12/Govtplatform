from flask import Flask
from config import Config
from extensions import db, login_manager, bcrypt, socketio

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Register blueprints here
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.elections import elections_bp
    from routes.polls import polls_bp
    from routes.reviews import reviews_bp
    from routes.chat import chat_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(elections_bp)
    app.register_blueprint(polls_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(chat_bp)

    with app.app_context():
        import models
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, log_output=True, allow_unsafe_werkzeug=True)
