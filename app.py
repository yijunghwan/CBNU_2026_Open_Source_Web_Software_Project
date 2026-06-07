from flask import Flask, render_template
from config import Config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect, text

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


def ensure_schema_updates():
    inspector = inspect(db.engine)
    table_names = set(inspector.get_table_names())

    if 'users' in table_names:
        with db.engine.begin() as connection:
            try:
                connection.execute(
                    text("ALTER TABLE users DROP CHECK check_valid_club_member")
                )
            except Exception:
                # 제약식이 없거나 DB 엔진 문법 차이가 있는 경우 무시
                pass

            try:
                connection.execute(
                    text(
                        "ALTER TABLE users "
                        "ADD CONSTRAINT check_valid_club_member "
                        "CHECK ((role_level < 10) OR (belonging_club != 'N') OR (role_level >= 40))"
                    )
                )
            except Exception:
                # 이미 동일 제약식이 있거나 일부 DB에서 CHECK를 강제하지 않으면 무시
                pass

    if 'clubs' not in table_names:
        return

    column_names = {column['name'] for column in inspector.get_columns('clubs')}
    if 'post_types_json' in column_names:
        return

    with db.engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE clubs "
                "ADD COLUMN post_types_json TEXT"
            )
        )


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
        ensure_schema_updates()
    app.run(debug=True, port=5001)