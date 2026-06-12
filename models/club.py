from models import db

class Club(db.Model):
    __tablename__ = 'clubs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)#id
    name = db.Column(db.String(50), unique=True, nullable=False)      # 동아리 이름 
    post_types_json = db.Column(
        db.Text,
        nullable=False,
        default='[]'
    )#동아리별 게시글 유형 리스트 여기에 있는거 기준으로 해당도아리의 게시글 작성시 유형 선택할수 있게함

    @classmethod
    def find_by_name(cls, club_name):
        return cls.query.filter_by(name=club_name).first()

    def __repr__(self):
        return f"<Club id={self.id} name='{self.name}'>"