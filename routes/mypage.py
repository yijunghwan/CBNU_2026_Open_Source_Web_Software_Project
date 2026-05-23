from flask import Blueprint, render_template, session, redirect, url_for
from models import User, ClubApplication, Club, db

mypage_bp = Blueprint('mypage', __name__)

@mypage_bp.route('/mypage')
def my_page():
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return 1 #사용자의 정보르 못불러옴 비정상황

    # [공통 데이터] 플레이스홀더 (내가 쓴 글/댓글)
    posts = []
    comments = []

    # 권한별 분기 및 전용 HTML 렌더링
    if user.role_level >= 30:
        # [회장/관리자] 동아리 총원 집계 후 회장 전용 페이지 반사
        member_count = User.query.filter_by(belonging_club=user.belonging_club).count()
        return render_template('mypage_30.html', user=user, posts=posts, comments=comments, count=member_count)
        
    elif user.role_level >= 10:
        # [간부/일반 부원] 동아리 총원 집계 후 부원 전용 페이지 반사
        member_count = User.query.filter_by(belonging_club=user.belonging_club).count()
        return render_template('mypage_10.html', user=user, posts=posts, comments=comments, count=member_count)
        
    else:
        # [비동아리원] 가입 신청 상태 확인 후 비동아리원 전용 페이지 반사
        application = ClubApplication.query.filter_by(user_id=user.id).first()
        applying_club_name = Club.query.get(application.club_id).name if application else None
        
        return render_template('mypage_0.html', user=user, posts=posts, comments=comments, 
                               application=application, club_name=applying_club_name)