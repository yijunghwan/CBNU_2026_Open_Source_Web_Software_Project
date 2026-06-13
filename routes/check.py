#사용자 정보 가져오기
def get_user_info(id):
    user = User.query.filter_by(user_id=user_id).first()
    return user

#로그인 여부 함수
def c_login():
    user_id = session.get('id')
    if user_id is None:
        return user_id
       
#권한 10 확인
def c_10(id):
    if user_id is None:
        return None

#권한 20 확인
def c_20(id):

#권한 30 확인
def c_30(id):

#권한 40 확인
def c_40(id):

#동아리 확인
def c_club(id):

#아직 완성X