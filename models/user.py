from models import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    #로그인 및 인증 정보
    user_id = db.Column(db.String(50), unique=True, nullable=False)   # 로그인 ID
    password = db.Column(db.String(255), nullable=False)                # 해시 비밀번호
    
    #인적사항 
    student_id = db.Column(db.String(20), unique=True, nullable=False)  # 학번
    name = db.Column(db.String(50), nullable=False)                     # 이름
    age = db.Column(db.Integer, default=0, nullable=False)              # 나이
    phone = db.Column(db.String(20), nullable=False)                    # 연락처
    grade = db.Column(db.Integer, nullable=False)                      # 학년 (1, 2, 3, 4)
    admission_year = db.Column(db.Integer, nullable=False)             # 입학년도 2022->이런식으로 4글자 연도만 들어가게할듯?
    address = db.Column(db.String(255), default= 'N', nullable=False)                # 주소 ->일딴 비어두면
    email = db.Column(db.String(255), nullable=False)                  # 이메일 ->추후 정보늘때 타입체크 필수
    belonging_club = db.Column(db.String(50), default='N', nullable=False)            # 소속동아리
    
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