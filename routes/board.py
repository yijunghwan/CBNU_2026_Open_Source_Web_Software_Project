import json
from urllib.parse import urlparse

from flask import Blueprint, request, session, jsonify
from flask import render_template, redirect, url_for
from models import db, User, Club, ClubBoard, Comment

board_bp = Blueprint('board', __name__, url_prefix='/board')


def _get_filter_type():
	return str((request.args.get('post_type') or 'all')).strip()


def _can_access_write_page():
	if session.get('board_write_entry') == 'myclub':
		return True

	referer = request.referrer or ''
	if not referer:
		return False

	try:
		parsed = urlparse(referer)
		if parsed.path in ('/board/myclub', '/board/myClub'):
			session['board_write_entry'] = 'myclub'
			return True
		return False
	except Exception:
		return False


def _get_login_user():
	user_id = session.get('id')
	if not user_id:
		return None
	return User.query.filter_by(user_id=user_id).first()


def _load_post_types(club):
	try:
		loaded = json.loads(club.post_types_json or '[]')
	except (TypeError, ValueError, json.JSONDecodeError):
		loaded = []

	post_types = []
	for item in loaded:
		text = str(item).strip()
		if text and text not in post_types:
			post_types.append(text)

	return post_types


def _apply_post_type_filter(query, selected_post_type):
	if selected_post_type == 'all':
		return query
	if selected_post_type == 'free':
		return query.filter((ClubBoard.post_type == '') | (ClubBoard.post_type.is_(None)))
	return query.filter(ClubBoard.post_type == selected_post_type)


def _paginate_query(query, page, per_page=10):
	if page < 1:
		page = 1

	total = query.count()
	total_pages = (total + per_page - 1) // per_page

	if total_pages < 1:
		total_pages = 1

	if page > total_pages:
		page = total_pages

	posts = (
		query
		.limit(per_page)
		.offset((page - 1) * per_page)
		.all()
	)

	return posts, page, total_pages, total


@board_bp.route('/myClub', methods=['GET'])
@board_bp.route('/myclub', methods=['GET'])
def myclub():
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	selected_post_type = _get_filter_type()
	page = request.args.get('page', 1, type=int)
	session['board_write_entry'] = 'myclub'

	if user.belonging_club == 'N':
		return render_template(
			'board_list.html',
			page_title='내 동아리 게시판',
			scope='myclub',
			club_name='N',
			available_post_types=[],
			selected_post_type=selected_post_type,
			posts=[],
			page=1,
			total_pages=1,
			total_posts=0,
			message='소속 동아리가 없습니다.'
		)

	club = Club.find_by_name(user.belonging_club)
	available_post_types = _load_post_types(club) if club else []

	posts_query = (
		ClubBoard.query
		.filter_by(club_name=user.belonging_club)
	)

	posts_query = _apply_post_type_filter(posts_query, selected_post_type) \
		.order_by(ClubBoard.is_notice.desc(), ClubBoard.created_at.desc())

	posts, page, total_pages, total_posts = _paginate_query(posts_query, page)

	return render_template(
		'board_list.html',
		page_title='내 동아리 게시판',
		scope='myclub',
		club_name=user.belonging_club,
		available_post_types=available_post_types,
		selected_post_type=selected_post_type,
		posts=posts,
		page=page,
		total_pages=total_pages,
		total_posts=total_posts,
		message=''
	)


@board_bp.route('/<int:post_id>', methods=['GET'])
def board_post(post_id):
    user = _get_login_user()
    if not user:
        return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

    post = ClubBoard.query.get_or_404(post_id)

    is_my_club_post = user.belonging_club == post.club_name
    is_public_post = post.is_public == 1
    if (not is_my_club_post) and (not is_public_post):
        return "이 게시글을 볼 권한이 없습니다.", 403

    comment_page = request.args.get('comment_page', 1, type=int)

    comments_query = (
        Comment.query
        .filter_by(post_id=post.id)
        .order_by(Comment.created_at.asc())
    )

    comments, comment_page, comment_total_pages, comment_total = (
        _paginate_query(comments_query, comment_page, per_page=10)
    )

    return render_template(
        'board_post.html',
        post=post,
        comments=comments,
        comment_page=comment_page,
        comment_total_pages=comment_total_pages,
        comment_total=comment_total,
        user=user,
        message=request.args.get('message', ''),
        message_type=request.args.get('type', 'info')
    )


@board_bp.route('/my-posts', methods=['GET'])
def my_posts():
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	posts = (
		ClubBoard.query
		.filter_by(author_pk=user.id)
		.order_by(ClubBoard.created_at.desc())
		.all()
	)

	return render_template(
		'board_my_posts.html',
		user=user,
		posts=posts,
		message=request.args.get('message', ''),
		message_type=request.args.get('type', 'info')
	)


@board_bp.route('/anterclub/<string:club_name>', methods=['GET'])
@board_bp.route('/anotherclub/<string:club_name>', methods=['GET'])
def anterclub(club_name):
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	selected_post_type = _get_filter_type()
	page = request.args.get('page', 1, type=int)

	if user.belonging_club == club_name:
		return redirect(url_for('board.myclub'))

	club = Club.find_by_name(club_name)
	available_post_types = _load_post_types(club) if club else []

	posts_query = (
		ClubBoard.query
		.filter(ClubBoard.club_name == club_name, ClubBoard.is_public == 1)
	)

	posts_query = _apply_post_type_filter(posts_query, selected_post_type) \
		.order_by(ClubBoard.is_notice.desc(), ClubBoard.created_at.desc())

	posts, page, total_pages, total_posts = _paginate_query(posts_query, page)

	return render_template(
		'board_list.html',
		page_title=f'{club_name} 게시판',
		scope='anotherclub',
		club_name=club_name,
		available_post_types=available_post_types,
		selected_post_type=selected_post_type,
		posts=posts,
		page=page,
		total_pages=total_pages,
		total_posts=total_posts,
		message=''
	)


@board_bp.route('/all', methods=['GET'])
def all_board():
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	selected_post_type = _get_filter_type()
	page = request.args.get('page', 1, type=int)

	posts_query = (
		ClubBoard.query
		.filter(ClubBoard.is_public == 1)
	)

	posts_query = _apply_post_type_filter(posts_query, selected_post_type) \
		.order_by(ClubBoard.created_at.desc())

	posts, page, total_pages, total_posts = _paginate_query(posts_query, page)

	custom_types = (
		db.session.query(ClubBoard.post_type)
		.filter(ClubBoard.post_type.isnot(None), ClubBoard.post_type != '')
		.distinct()
		.all()
	)
	available_post_types = [row[0] for row in custom_types]

	return render_template(
		'board_list.html',
		page_title='전체 공개 게시판',
		scope='all',
		club_name='ALL',
		available_post_types=available_post_types,
		selected_post_type=selected_post_type,
		posts=posts,
		page=page,
		total_pages=total_pages,
		total_posts=total_posts,
		message=''
	)


@board_bp.route('/writePost', methods=['POST', 'GET'])
def write_post():
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	if user.belonging_club == 'N':
		return jsonify({'success': False, 'message': '동아리 소속 사용자만 글을 작성할 수 있습니다.'}), 403

	club = Club.find_by_name(user.belonging_club)
	if not club:
		return jsonify({'success': False, 'message': '소속 동아리를 찾을 수 없습니다.'}), 404

	if not _can_access_write_page():
		return redirect(url_for('board.myclub', message='글쓰기는 내 동아리 게시판에서만 접근할 수 있습니다.', type='error'))

	if request.method == 'GET':
		return render_template(
			'board_write.html',
			club_name=club.name,
			post_types=_load_post_types(club),
			can_notice=(user.role_level >= 20),
			message=request.args.get('message', ''),
			message_type=request.args.get('type', 'info')
		)

	payload = request.get_json(silent=True) if request.is_json else request.form
	title = str((payload.get('title') or '')).strip()
	content = str((payload.get('content') or '')).strip()
	post_type = str((payload.get('post_type') or '')).strip()

	if not title:
		if request.is_json:
			return jsonify({'success': False, 'message': '제목을 입력하세요.'}), 400
		return redirect(url_for('board.write_post', message='제목을 입력하세요.', type='error'))
	if not content:
		if request.is_json:
			return jsonify({'success': False, 'message': '내용을 입력하세요.'}), 400
		return redirect(url_for('board.write_post', message='내용을 입력하세요.', type='error'))

	allowed_post_types = _load_post_types(club)
	if post_type and post_type not in allowed_post_types:
		if request.is_json:
			return jsonify({
				'success': False,
				'message': '허용되지 않은 글 유형입니다.',
				'allowed_post_types': allowed_post_types,
			}), 400
		return redirect(url_for('board.write_post', message='허용되지 않은 글 유형입니다.', type='error'))

	is_public_raw = payload.get('is_public', 0)
	is_notice_raw = payload.get('is_notice', 0)

	try:
		is_public = int(is_public_raw)
		is_notice = int(is_notice_raw)
	except (TypeError, ValueError):
		if request.is_json:
			return jsonify({'success': False, 'message': 'is_public/is_notice 값이 올바르지 않습니다.'}), 400
		return redirect(url_for('board.write_post', message='공개/공지 값이 올바르지 않습니다.', type='error'))

	if is_public not in (0, 1):
		if request.is_json:
			return jsonify({'success': False, 'message': 'is_public은 0 또는 1만 가능합니다.'}), 400
		return redirect(url_for('board.write_post', message='공개 여부 값이 올바르지 않습니다.', type='error'))
	if is_notice not in (0, 1):
		if request.is_json:
			return jsonify({'success': False, 'message': 'is_notice는 0 또는 1만 가능합니다.'}), 400
		return redirect(url_for('board.write_post', message='공지 여부 값이 올바르지 않습니다.', type='error'))
	if is_notice == 1 and user.role_level < 20:
		if request.is_json:
			return jsonify({'success': False, 'message': '공지글은 간부 이상만 작성할 수 있습니다.'}), 403
		return redirect(url_for('board.write_post', message='공지글은 간부 이상만 작성할 수 있습니다.', type='error'))

	new_post = ClubBoard(
		title=title,
		content=content,
		author_pk=user.id,
		club_name=club.name,
		is_public=is_public,
		is_notice=is_notice,
		post_type=post_type,
	)

	try:
		db.session.add(new_post)
		db.session.commit()
	except Exception:
		db.session.rollback()
		if request.is_json:
			return jsonify({'success': False, 'message': '게시글 저장 중 오류가 발생했습니다.'}), 500
		return redirect(url_for('board.write_post', message='게시글 저장 중 오류가 발생했습니다.', type='error'))

	if not request.is_json:
		session.pop('board_write_entry', None)
		return redirect(url_for('board.myclub', message='게시글이 등록되었습니다.', type='success'))

	return jsonify({
		'success': True,
		'message': '게시글이 등록되었습니다.',
		'post_id': new_post.id,
		'club_name': new_post.club_name,
		'post_type': new_post.post_type,
	}), 201


@board_bp.route('/editPost/<int:Post_id>', methods=['POST', 'GET'])
def edit_post(Post_id):
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	post = ClubBoard.query.get_or_404(Post_id)
	if post.author_pk != user.id:
		return "본인이 작성한 글만 수정할 수 있습니다.", 403

	club = Club.find_by_name(post.club_name)
	allowed_post_types = _load_post_types(club) if club else []
	can_notice = user.role_level >= 20

	if request.method == 'GET':
		return render_template(
			'board_edit.html',
			post=post,
			post_types=allowed_post_types,
			can_notice=can_notice,
			message=request.args.get('message', ''),
			message_type=request.args.get('type', 'info')
		)

	payload = request.get_json(silent=True) if request.is_json else request.form
	title = str((payload.get('title') or '')).strip()
	content = str((payload.get('content') or '')).strip()
	post_type = str((payload.get('post_type') or '')).strip()

	if not title or not content:
		if request.is_json:
			return jsonify({'success': False, 'message': '제목과 내용을 모두 입력하세요.'}), 400
		return redirect(url_for('board.edit_post', Post_id=Post_id, message='제목과 내용을 모두 입력하세요.', type='error'))

	if post_type and post_type not in allowed_post_types:
		if request.is_json:
			return jsonify({'success': False, 'message': '허용되지 않은 글 유형입니다.'}), 400
		return redirect(url_for('board.edit_post', Post_id=Post_id, message='허용되지 않은 글 유형입니다.', type='error'))

	try:
		is_public = int(payload.get('is_public', 0))
		is_notice = int(payload.get('is_notice', 0))
	except (TypeError, ValueError):
		if request.is_json:
			return jsonify({'success': False, 'message': '공개/공지 값이 올바르지 않습니다.'}), 400
		return redirect(url_for('board.edit_post', Post_id=Post_id, message='공개/공지 값이 올바르지 않습니다.', type='error'))

	if is_public not in (0, 1) or is_notice not in (0, 1):
		if request.is_json:
			return jsonify({'success': False, 'message': '공개/공지 값은 0 또는 1만 가능합니다.'}), 400
		return redirect(url_for('board.edit_post', Post_id=Post_id, message='공개/공지 값은 0 또는 1만 가능합니다.', type='error'))

	if is_notice == 1 and not can_notice:
		if request.is_json:
			return jsonify({'success': False, 'message': '공지글은 간부 이상만 설정할 수 있습니다.'}), 403
		return redirect(url_for('board.edit_post', Post_id=Post_id, message='공지글은 간부 이상만 설정할 수 있습니다.', type='error'))

	try:
		post.title = title
		post.content = content
		post.post_type = post_type
		post.is_public = is_public
		post.is_notice = is_notice
		db.session.commit()
	except Exception:
		db.session.rollback()
		if request.is_json:
			return jsonify({'success': False, 'message': '게시글 수정 중 오류가 발생했습니다.'}), 500
		return redirect(url_for('board.edit_post', Post_id=Post_id, message='게시글 수정 중 오류가 발생했습니다.', type='error'))

	if request.is_json:
		return jsonify({'success': True, 'message': '게시글이 수정되었습니다.'}), 200
	return redirect(url_for('board.board_post', post_id=Post_id, message='게시글이 수정되었습니다.', type='success'))


@board_bp.route('/deletePost/<int:Post_id>', methods=['POST'])
def delete_post(Post_id):
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	post = ClubBoard.query.get_or_404(Post_id)
	if post.author_pk != user.id:
		return "본인이 작성한 글만 삭제할 수 있습니다.", 403

	try:
		db.session.delete(post)
		db.session.commit()
	except Exception:
		db.session.rollback()
		return redirect(url_for('board.edit_post', Post_id=Post_id, message='게시글 삭제 중 오류가 발생했습니다.', type='error'))

	return redirect(url_for('board.my_posts', message='게시글이 삭제되었습니다.', type='success'))


@board_bp.route('/comment/<int:Post_id>', methods=['POST'])
def write_comment(Post_id):
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	post = ClubBoard.query.get_or_404(Post_id)
	is_my_club_post = user.belonging_club == post.club_name
	is_public_post = post.is_public == 1
	if (not is_my_club_post) and (not is_public_post):
		return "이 게시글에 댓글을 작성할 권한이 없습니다.", 403

	content = str((request.form.get('content') or '')).strip()
	if not content:
		return redirect(url_for('board.board_post', post_id=Post_id, message='댓글 내용을 입력하세요.', type='error'))

	try:
		comment = Comment(post_id=Post_id, author_pk=user.id, content=content)
		db.session.add(comment)
		db.session.commit()
	except Exception:
		db.session.rollback()
		return redirect(url_for('board.board_post', post_id=Post_id, message='댓글 작성 중 오류가 발생했습니다.', type='error'))

	return redirect(url_for('board.board_post', post_id=Post_id, message='댓글이 등록되었습니다.', type='success'))


@board_bp.route('/editComment/<int:Comment_id>', methods=['POST', 'GET'])
def edit_comment(Comment_id):
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	comment = Comment.query.get_or_404(Comment_id)
	if comment.author_pk != user.id:
		return "본인이 작성한 댓글만 수정할 수 있습니다.", 403

	if request.method == 'GET':
		return render_template(
			'comment_edit.html',
			comment=comment,
			message=request.args.get('message', ''),
			message_type=request.args.get('type', 'info')
		)

	content = str((request.form.get('content') or '')).strip()
	if not content:
		return redirect(url_for('board.edit_comment', Comment_id=Comment_id, message='댓글 내용을 입력하세요.', type='error'))

	try:
		comment.content = content
		db.session.commit()
	except Exception:
		db.session.rollback()
		return redirect(url_for('board.edit_comment', Comment_id=Comment_id, message='댓글 수정 중 오류가 발생했습니다.', type='error'))

	return redirect(url_for('board.board_post', post_id=comment.post_id, message='댓글이 수정되었습니다.', type='success'))


@board_bp.route('/deleteComment/<int:Comment_id>', methods=['POST'])
def delete_comment(Comment_id):
	user = _get_login_user()
	if not user:
		return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

	comment = Comment.query.get_or_404(Comment_id)
	if comment.author_pk != user.id:
		return "본인이 작성한 댓글만 삭제할 수 있습니다.", 403

	post_id = comment.post_id
	try:
		db.session.delete(comment)
		db.session.commit()
	except Exception:
		db.session.rollback()
		return redirect(url_for('board.edit_comment', Comment_id=Comment_id, message='댓글 삭제 중 오류가 발생했습니다.', type='error'))

	return redirect(url_for('board.board_post', post_id=post_id, message='댓글이 삭제되었습니다.', type='success'))