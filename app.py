from flask import Flask, render_template
from config import Config
from sqlalchemy.exc import SQLAlchemyError

from models import Club, ClubBoard, db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

from routes.auth import auth_bp
from routes.mypage import mypage_bp
from routes.club import club_bp
from routes.meeting import meeting_bp
from routes.board import board_bp

app.register_blueprint(auth_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(club_bp)
app.register_blueprint(meeting_bp)
app.register_blueprint(board_bp)


#일종의 전역변수 navbar_clubs를 템플릿에서 사용할 수 있도록 하는 용도 (보안을위해 민감 정보는 넣으면 안됨)
@app.context_processor
def inject_navbar_clubs():
    try:
        clubs = Club.query.order_by(Club.name.asc()).all()
    except SQLAlchemyError:
        clubs = []
    return {'navbar_clubs': clubs}

@app.route('/')
def main():
    public_posts = (
        ClubBoard.query
        .filter(ClubBoard.is_public == 1)
        .order_by(ClubBoard.created_at.desc())
        .limit(5)
        .all()
    )
    return render_template('main.html', public_posts=public_posts)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)