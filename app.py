from flask import Flask
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

# 전역 데이터베이스 초기화 결합
db.init_app(app)


from routes.auth import auth_bp
from routes.mypage import mypage_bp

app.register_blueprint(auth_bp)
app.register_blueprint(mypage_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True, port=5001)