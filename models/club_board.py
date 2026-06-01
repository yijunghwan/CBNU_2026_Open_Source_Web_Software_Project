from datetime import datetime
from models import db

class ClubBoard(db.Model):
    __tablename__ = 'club_board'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 제목 및 내용
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)  # HTML 포함 가능하도록 Text 타입 사용

    # 작성자 (users.id 외래키)
    author_pk = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 작성 시간
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 소속 동아리: 동아리명 또는 (공용 게시판)
    club_name = db.Column(db.String(50), nullable=False)

    # 공개 여부: 0=전체공개 / 10=로그인유저 / 20=동아리원만
    is_public = db.Column(db.Integer, default=0, nullable=False)

    # 공지 여부: 0=일반글 / 1=공지(최상단 고정)
    is_notice = db.Column(db.Integer, default=0, nullable=False)

    # 글 유형: 'FREE' / 'QNA' / 'STUDY' / 'PROJECT'
    post_type = db.Column(db.String(20), default='FREE', nullable=False)

    # 관계 정의: post.author.name 으로 작성자 접근 가능
    author = db.relationship('User', backref=db.backref('posts', lazy=True))

    # 댓글 관계: post.comments 로 댓글 목록 접근 가능
    comments = db.relationship('Comment', backref=db.backref('post', lazy=True), lazy=True, cascade='all, delete-orphan')#댓글이라 cascade='all, delete-orphan'로 같이 삭제됨

    def __repr__(self):
        return f"<ClubBoard(id={self.id}, title='{self.title}', club_name='{self.club_name}', post_type='{self.post_type}')>"