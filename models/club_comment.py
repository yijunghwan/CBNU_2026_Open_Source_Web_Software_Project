from datetime import datetime
from models import db

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 어느 게시글의 댓글인지 (posts.id 외래키)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    # 작성자 (users.id 외래키)
    author_pk = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 댓글 내용
    content = db.Column(db.Text, nullable=False)

    # 작성 시간
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 관계 정의
    author = db.relationship('User', backref=db.backref('comments', lazy=True))

    def __repr__(self):
        return f"<Comment(id={self.id}, post_id={self.post_id}, author_pk={self.author_pk})>"
