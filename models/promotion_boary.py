from datetime import datetime
from models import db

#홍보 게시판 db
class promotionBoard(db.Model):
    __tablename__ = 'promotion_board'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 제목 및 내용
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False) 
    # 작성자 (users.id 외래키)
    author_pk = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 작성 시간
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # 소속 동아리
    club_name = db.Column(db.String(50), nullable=False)

    # 공지 여부
    is_notice = db.Column(db.Integer, default=0, nullable=False)

    # 작성자 관계
    author = db.relationship('User', backref=db.backref('promotion_posts', lazy=True))

