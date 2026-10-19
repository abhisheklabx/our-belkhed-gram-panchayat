import os
import json
from flask import Flask, session, g, request
from config import Config
from models.database import db
from models.models import User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Load translations into memory cache
    translations_cache = {}
    translations_dir = os.path.join(app.root_path, 'translations')
    for lang in ['mr', 'hi', 'en']:
        fpath = os.path.join(translations_dir, f"{lang}.json")
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                translations_cache[lang] = json.load(f)
        else:
            translations_cache[lang] = {}

    # Context processors and global helpers
    @app.before_request
    def load_user_and_language():
        # Language handling: session -> param -> cookie -> default 'mr'
        req_lang = request.args.get('lang')
        if req_lang in ['mr', 'hi', 'en']:
            session['lang'] = req_lang
        elif 'lang' not in session:
            session['lang'] = 'mr'

        g.lang = session.get('lang', 'mr')
        g.t = translations_cache.get(g.lang, translations_cache.get('en', {}))

        # User handling
        user_id = session.get('user_id')
        if user_id:
            g.user = db.session.get(User, user_id)
        else:
            g.user = None

    @app.context_processor
    def inject_globals():
        def t(key, default=''):
            return g.t.get(key, default or key)

        return {
            'current_lang': g.lang,
            'current_user': g.user,
            'config': app.config,
            't': t
        }

    # Security & CORS Headers
    @app.after_request
    def set_security_headers(response):
        frontend_url = os.getenv('FRONTEND_URL', '')
        if frontend_url:
            response.headers['Access-Control-Allow-Origin'] = frontend_url
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'

        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    # Register Blueprints
    from routes.public import public_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    print("Starting Our Belkhed Server on http://127.0.0.1:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
