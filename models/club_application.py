from models import db

class ClubApplication(db.Model):
    __tablename__ = 'club_applications'
    

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)#id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)#user_id
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=False)#club_id
    status = db.Column(db.String(20), default='PENDING', nullable=False)#현재 상태 (PENDING, REJECTED)-> 이렇게 두개만둘듯? 대기중 / 거절 (통과는 바로 users 건들이고 삭제되는방식으로)
    

    memo = db.Column(db.String(255), default='심사중입니다', nullable=False)#아마 필요상 추가한것(반려 사유 적으면 좋을듯)

    @classmethod
    def find_pendings_by_club(cls, target_club_id):
        return cls.query.filter_by(club_id=target_club_id, status='PENDING').all()

   
    def __repr__(self):
        return (
            f"<ClubApplication(\n"
            f"  id={self.id},\n"
            f"  user={self.user_id},\n"
            f"  club={self.club_id},\n"
            f"  status='{self.status}',\n"
            f"  memo='{self.memo}'\n"
            f")>"
        )