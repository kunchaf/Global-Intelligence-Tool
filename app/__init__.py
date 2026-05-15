from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Load configurations
    app.config.from_pyfile('../config.py')

    from .routes import bp

    app.register_blueprint(bp)
    return app