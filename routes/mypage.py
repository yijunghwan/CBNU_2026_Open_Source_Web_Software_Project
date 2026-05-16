from flask import Blueprint, render_template, session, redirect, url_for
from models import User, ClubApplication, Club

mypage_bp = Blueprint('mypage', __name__)

@mypage_bp.route('/mypage')
def my_page():
    user_id = session.get('id')  # 로그인한 id 가져오기
    
    #로그인 안 되어 있으면 로그인 페이지로 튕겨버리기
    if not user_id:
        return redirect(url_for('auth.login')) # 로그인 안 했을때 예최처리

    #DB에서 유저의 전체 정보 가져오기
    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return redirect(url_for('auth.login'))
    
    # 4. [추가 기능] 혹시 이 유저가 현재 동아리 가입 신청 중인지 확인하기
    # (승인되면 삭제되기로 했으니, 여기 데이터가 있다면 '대기' 또는 '반려' 상태임)
    application = ClubApplication.query.filter_by(user_id=user.id).first()
    
    # 신청 정보가 있다면 해당 동아리 이름도 가져오기
    applying_club_name = None
    if application:
        club = Club.query.get(application.club_id)
        applying_club_name = club.name

    # 5. render_template을 통해 HTML 종이에 데이터를 비벼서 보내기
    return render_template('my_page.html', 
                           user=user, 
                           application=application, 
                           club_name=applying_club_name)