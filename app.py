from flask import Flask, render_template
from config import Config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect, text

from models import Club, ClubBoard, promotionBoard, db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

from routes.auth import auth_bp
from routes.mypage import mypage_bp
from routes.club import club_bp
from routes.meeting import meeting_bp
from routes.board import board_bp
from routes.promtion import promotion_bp

app.register_blueprint(auth_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(club_bp)
app.register_blueprint(meeting_bp)
app.register_blueprint(board_bp)
app.register_blueprint(promotion_bp)


#일종의 전역변수 navbar_clubs를 템플릿에서 사용할 수 있도록 하는 용도 (보안을위해 민감 정보는 넣으면 안됨) 즉 db에서 동아리 목록을 그냥 주는거임 랜딩페이지에서 부터
@app.context_processor
def inject_navbar_clubs():
    try:
        clubs = Club.query.order_by(Club.name.asc()).all()#동아리 이름 전부 가져와라
    except SQLAlchemyError:#db 접속오류나면 빈 리스트로 처리 코파일럿이 추천함 솔직히
        clubs = []
    return {'navbar_clubs': clubs}

@app.route('/')
def main():
    # 최근 공계 계시글 5개 가져오기
    public_posts = (
        ClubBoard.query
        .filter(ClubBoard.is_public == 1)
        .order_by(ClubBoard.created_at.desc())
        .limit(5)
        .all()
    )
    
    promotion_posts = (
        promotionBoard.query
        .order_by(promotionBoard.created_at.desc())
        .limit(5)
        .all()
    )  # 홍보게시판 글 5개 가져오기
    return render_template('main.html', public_posts=public_posts, promotion_posts=promotion_posts)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() #대충 db테이블을 만들어주는 역할 models/__init__.py ->여기에 db 객체 있음 단, 테이블이 변해버리는등의 경우는 드랍했다가 다시해야함 따로 수정하거나
        
    app.run(debug=True, port=5001) 