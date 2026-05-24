from flask import Blueprint, jsonify, render_template, session, redirect, url_for, request
from models import User, ClubApplication, Club, db

mypage_bp = Blueprint('mypage', __name__, url_prefix='/user')


@mypage_bp.route('/mypage')
def my_page():
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return 1 #사용자의 정보를 못불러옴 비정상 상황

    #추후 여기에 내가 쓴글 관련 데이터도 받아와야함
    posts = []
    comments = []

    # 권한별 분기 및 전용 HTML 렌더링
    if user.role_level >= 30:
        member_count = User.query.filter_by(belonging_club=user.belonging_club).count()#동아리 정보 출력을 위하여
        return render_template('mypage_30.html', user=user, posts=posts, comments=comments, count=member_count)
        
    elif user.role_level >= 10:
        member_count = User.query.filter_by(belonging_club=user.belonging_club).count()#동아리 정보 출력을 위하여2
        return render_template('mypage_10.html', user=user, posts=posts, comments=comments, count=member_count)
        
    else:
        application = ClubApplication.query.filter_by(user_pk=user.id).first()#가입 신청내역 출력을 위하여
        applying_club_name = Club.query.get(application.club_id).name if application else None#가입 신청한 동아리가 있으면 이름을, 없으면 None을 넘겨줌 프론트엔드에서 none이면 가입 신청내역 없다고 해야할듯
        
        return render_template('mypage_0.html', user=user, posts=posts, comments=comments, 
                               application=application, club_name=applying_club_name)



# 비동아리원(0) 전용 동아리 가입 신청
@mypage_bp.route('/apply_0', methods=['GET', 'POST'])
def apply_club_0():
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(user_id=user_id).first()

    if user.role_level >= 10 or user.belonging_club != 'N':
        return "이미 동아리에 소속되어 있어 가입 신청을 할 수 없습니다.", 403

    existing_app = ClubApplication.query.filter_by(user_pk=user.id).first()
    if existing_app:
        return "이미 가입 심사 대기 중인 동아리가 있습니다. 결과를 기다려주세요.", 400

    if request.method == 'GET':
        clubs = Club.query.all()
        return render_template('apply.html', user=user, clubs=clubs)

    club_id = request.form.get('club_id')
    memo = request.form.get('memo')

    new_app = ClubApplication(
        user_pk=user.id,
        club_id=int(club_id),
        status='PENDING',
        memo=memo
    )

    try:
        db.session.add(new_app)
        db.session.commit()
        return jsonify({"success": True, "message": "성공적으로 가입 신청이 접수되었습니다!"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "서버 오류로 신청에 실패했습니다."}), 500


# 비동아리원전용 가입 신청 취소
@mypage_bp.route('/cancel_apply_0', methods=['POST'])
def cancel_apply_0():
    user_id = session.get('id')
    if not user_id:
        return jsonify({"success": False, "message": "로그인이 필요합니다."}), 401

    user = User.query.filter_by(user_id=user_id).first()

    # 방어 로직: 비동아리원(0)만 접근 허용
    if user.role_level != 0:
        return jsonify({"success": False, "message": "잘못된 접근입니다."}), 403

    application = ClubApplication.query.filter_by(user_pk=user.id).first()
    
    if not application:
        return jsonify({"success": False, "message": "취소할 가입 신청 내역이 없습니다."}), 404

    try:
        db.session.delete(application)  
        db.session.commit()             
        return jsonify({"success": True, "message": "가입 신청이 정상적으로 취소되었습니다."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "서버 오류로 취소에 실패했습니다."}), 500



# 동아리원/간부 전용 동아리 탈퇴
@mypage_bp.route('/leave_club_10', methods=['POST'])
def leave_club_10():
    user_id = session.get('id')
    if not user_id:
        return jsonify({"success": False, "message": "로그인이 필요합니다."}), 401

    user = User.query.filter_by(user_id=user_id).first()

    # 방어 로직: 아예 비동아리원이면 탈퇴할 동아리도 없음
    if user.role_level == 0 or user.belonging_club == 'N':
        return jsonify({"success": False, "message": "소속된 동아리가 없습니다."}), 400

    # 방어 로직: 회장(Level 30 이상)은 직위 해제 전까지 탈퇴 불가!
    if user.role_level >= 30:
        return jsonify({"success": False, "message": "회장은 동아리를 바로 탈퇴할 수 없습니다. 직위를 먼저 위임하세요."}), 403

    # 핵심 연산: 동아리 소속을 'N'으로 바꾸고 권한을 0(비동아리원)으로 강등
    try:
        old_club = user.belonging_club # 탈퇴 메시지용으로 잠시 저장
        
        user.belonging_club = 'N'
        user.role_level = 0
        
        db.session.commit() # 변경사항 DB 저장
        return jsonify({"success": True, "message": f"{old_club} 동아리에서 정상적으로 탈퇴되었습니다."}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "서버 오류로 탈퇴 처리에 실패했습니다."}), 500