from flask import Flask
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

# 전역 데이터베이스 초기화 결합
db.init_app(app)


from routes.auth import auth_bp#이정환 네임스페이스 ('auth')는 로그인/회원가입/로그아웃 기능 담당
from routes.mypage import mypage_bp#이정환 네임스페이스 ('mypage')는 마이페이지 기능 담당
from routes.club import club_bp#이정환 네임스페이스 ('club')는 동아리관리 기능 담당

app.register_blueprint(auth_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(club_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True, port=5001)