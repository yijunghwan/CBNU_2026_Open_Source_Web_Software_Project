from models import db

class User(db.Model):
    __tablename__ = 'users'
    
    __table_args__ = (
        db.CheckConstraint(
            "(role_level < 10) OR (belonging_club != 'N') OR (role_level >= 40)", 
            name='check_valid_club_member'
        ),
    )# 혹시 모를 버그 방지용
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 로그인 및 인증 정보
    user_id = db.Column(db.String(50), unique=True, nullable=False)   
    password = db.Column(db.String(255), nullable=False)                
    
    # 인적사항 
    student_id = db.Column(db.String(20), unique=True, nullable=False)  
    name = db.Column(db.String(50), nullable=False)                     
    age = db.Column(db.Integer, default=0, nullable=False)              
    phone = db.Column(db.String(20), default='N', nullable=False)    
    grade = db.Column(db.Integer, nullable=False)                      
    admission_year = db.Column(db.Integer, default=0, nullable=False)             
    address = db.Column(db.String(255), default='N', nullable=False)                
    email = db.Column(db.String(255), default='N', nullable=False)                  
    belonging_club = db.Column(db.String(50), default='N', nullable=False)
    off = db.Column(db.Integer, default=0, nullable=False) #휴학시 1
    
    

    # 0: 비동아리원(GUEST) / 10: 동아리원 / 20: 간부 / 30: 회장 / 40: 조교 및 개발자(ADMIN)
    role_level = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
            return (
                f"<User(\n"
                f"  id={self.id},\n"
                f"  user_id='{self.user_id}',\n"
                f"  student_id='{self.student_id}',\n"
                f"  name='{self.name}',\n"
                f"  age={self.age},\n"
                f"  phone='{self.phone}',\n"
                f"  grade={self.grade},\n"
                f"  admission_year={self.admission_year},\n"
                f"  address='{self.address}',\n"
                f"  email='{self.email}',\n"
                f"  belonging_club='{self.belonging_club}',\n"
                f"  role_level={self.role_level}\n"
                f")>"
            )