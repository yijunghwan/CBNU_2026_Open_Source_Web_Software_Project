from models import db

class Club(db.Model):
    __tablename__ = 'clubs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)#id
    name = db.Column(db.String(50), unique=True, nullable=False)      # 동아리 이름 
    post_types_json = db.Column(
        db.Text,
        nullable=False,
        default='[]'
    )

    @classmethod
    def find_by_name(cls, club_name):
        return cls.query.filter_by(name=club_name).first()

    def __repr__(self):
        return f"<Club id={self.id} name='{self.name}'>"