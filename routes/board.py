from flask import Blueprint, request, session, jsonify
from flask import render_template, redirect, url_for
from models import db, User, ClubBoard, Comment

board_bp = Blueprint('board', __name__, url_prefix='/board') #'board' 네임스페이스 정의 (이 파일의 모든 주소 앞에 자동으로 /auth가 붙음)

def _get_login_user():
	user_id = session.get('id')
	if not user_id:
		return None
	return User.query.filter_by(user_id=user_id).first()

@board_bp.route('/myClub', methods=['GET'])#자기 자신 동아리 게시판 조회
@board_bp.route('/myclub', methods=['GET'])
def myclub():
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	if user.belonging_club == 'N':
		return render_template(
			'board_list.html',
			page_title='내 동아리 게시판',
			scope='myclub',
			club_name='N',
			posts=[],
			message='소속 동아리가 없습니다.'
		)

	posts = (
		ClubBoard.query
		.filter_by(club_name=user.belonging_club)
		.order_by(ClubBoard.is_notice.desc(), ClubBoard.created_at.desc())
		.all()
	)

	return render_template(
		'board_list.html',
		page_title='내 동아리 게시판',
		scope='myclub',
		club_name=user.belonging_club,
		posts=posts,
		message=''
	)


@board_bp.route('/<int:post_id>', methods=['GET'])#게시글 상세 조회
def board_post(post_id):
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	post = ClubBoard.query.get_or_404(post_id)

	is_my_club_post = user.belonging_club == post.club_name
	is_public_post = post.is_public == 1
	if (not is_my_club_post) and (not is_public_post):
		return "이 게시글을 볼 권한이 없습니다.", 403

	comments = (
		Comment.query
		.filter_by(post_id=post.id)
		.order_by(Comment.created_at.asc())
		.all()
	)

	return render_template('board_post.html', post=post, comments=comments)


@board_bp.route('/anterclub/<string:club_name>', methods=['GET'])#타 동아리 게시판 조회(기존 오타 경로 호환)
@board_bp.route('/anotherclub/<string:club_name>', methods=['GET'])
def anterclub(club_name):
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	if user.belonging_club == club_name:
		return redirect(url_for('board.myclub'))

	posts = (
		ClubBoard.query
		.filter(ClubBoard.club_name == club_name, ClubBoard.is_public == 1)
		.order_by(ClubBoard.is_notice.desc(), ClubBoard.created_at.desc())
		.all()
	)

	return render_template(
		'board_list.html',
		page_title=f'{club_name} 게시판',
		scope='anotherclub',
		club_name=club_name,
		posts=posts,
		message=''
	)

@board_bp.route('/all', methods=['GET'])#전체 게시판 조회
def all_board():
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	posts = (
		ClubBoard.query
		.filter(ClubBoard.is_public == 1)
		.order_by(ClubBoard.is_notice.desc(), ClubBoard.created_at.desc())
		.all()
	)

	return render_template(
		'board_list.html',
		page_title='전체 공개 게시판',
		scope='all',
		club_name='ALL',
		posts=posts,
		message=''
	)

@board_bp.route('/writePost', methods=['POST', 'GET'])#게시글 작성
def write_post():
	return "글 작성 기능은 다음 단계에서 구현 예정입니다.", 501

@board_bp.route('/editPost/<int:Post_id>', methods=['POST', 'GET'])#게시글 수정
def edit_post(Post_id):
	return "글 수정 기능은 다음 단계에서 구현 예정입니다.", 501

@board_bp.route('/deletePost/<int:Post_id>', methods=['POST'])#게시글 삭제
def delete_post(Post_id):
	return "글 삭제 기능은 다음 단계에서 구현 예정입니다.", 501

@board_bp.route('/comment/<int:Post_id>', methods=['POST'])#댓글 작성
def write_comment(Post_id):
	return "댓글 작성 기능은 다음 단계에서 구현 예정입니다.", 501

@board_bp.route('/editComment/<int:Comment_id>', methods=['POST', 'GET'])#댓글 수정
def edit_comment(Comment_id):
	return "댓글 수정 기능은 다음 단계에서 구현 예정입니다.", 501

@board_bp.route('/deleteComment/<int:Comment_id>', methods=['POST'])#댓글 삭제
def delete_comment(Comment_id):
	return "댓글 삭제 기능은 다음 단계에서 구현 예정입니다.", 501