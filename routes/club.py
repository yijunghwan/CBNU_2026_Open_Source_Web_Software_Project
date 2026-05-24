from flask import Blueprint, request, session, jsonify, render_template, redirect, url_for
from models import db, User, Club, ClubApplication

# 동아리 관련 기능 네임스페이스 ('/club')
club_bp = Blueprint('club', __name__, url_prefix='/club')


# 동아리 가입시에 라우터
@club_bp.route('/apply', methods=['GET', 'POST'])
def apply_club():
    # 로그인 확인
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(user_id=user_id).first()

    #접근 제한
    if user.role_level >= 10 or user.belonging_club != 'N':
        return "이미 동아리에 소속되어 있어 가입 신청을 할 수 없습니다.", 403

    #접근제한(이미 신청한 동아리가 있는지)
    existing_app = ClubApplication.query.filter_by(user_pk=user.id).first()
    if existing_app:
        return "이미 가입 심사 대기 중인 동아리가 있습니다. 결과를 기다려주세요.", 400


    if request.method == 'GET':
        # DB에서 동아리 목록을 싹 다 긁어와서 HTML에 던져버린다.
        clubs = Club.query.all()
        return render_template('apply.html', user=user, clubs=clubs)



    if request.method == 'POST':
        # 프론트엔드에서 날아온 데이터 받기
        club_id = request.form.get('club_id')
        memo = request.form.get('memo')

        # 새로운 가입 신청서(ClubApplication) 객체 생성
        new_app = ClubApplication(
            user_pk=user.id,
            club_id=int(club_id),
            status='PENDING', # 기본값 '대기중'
            memo=memo         # 유저가 적은 코멘트
        )
        
        try:
            db.session.add(new_app)
            db.session.commit()
            return jsonify({"success": True, "message": "성공적으로 가입 신청이 접수되었습니다!"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": "서버 오류로 신청에 실패했습니다."}), 500
        



