from flask import Flask, send_from_directory, jsonify
from config import Config
from models import db
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

from routes.auth import auth_bp
from routes.mypage import mypage_bp
from routes.club import club_bp

app.register_blueprint(auth_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(club_bp)

# ─── React 빌드 파일 서빙 ───────────────────────────────────────────────────
REACT_BUILD_DIR = os.path.join(os.path.dirname(__file__), 'static', 'react_build')

# /assets/* → React 빌드 번들 파일 서빙
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(REACT_BUILD_DIR, 'assets'), filename)

# API 경로(/auth/*, /user/*, /club/*)는 각 Blueprint가 먼저 처리.
# 나머지 모든 URL → React SPA(index.html) 반환
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    return send_from_directory(REACT_BUILD_DIR, 'index.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)