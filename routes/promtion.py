from flask import Blueprint, request, session
from flask import render_template, redirect, url_for

from models import db, User, promotionBoard


promotion_bp = Blueprint('promotion', __name__, url_prefix='/promotion')
PROMOTION_LIST_PER_PAGE = 20

def get_login_user():
    user_id = session.get('id')
    if not user_id:
        return None
    return User.query.filter_by(user_id=user_id).first()


@promotion_bp.route('/list', methods=['GET'])
def list_posts():
    user = get_login_user()
    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1

    posts_query = (
        promotionBoard.query
        .order_by(promotionBoard.created_at.desc())
    )

    total_posts = posts_query.count()
    per_page = PROMOTION_LIST_PER_PAGE
    total_pages = max(1, (total_posts + per_page - 1) // per_page)
    if page > total_pages:
        page = total_pages

    posts = (
        posts_query
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )

    return render_template(
        'promotion_list.html',
        page_title='홍보게시판',
        user=user,
        posts=posts,
        per_page=PROMOTION_LIST_PER_PAGE,
        page=page,
        total_pages=total_pages,
        total_posts=total_posts,
        message=request.args.get('message', ''),
    )


@promotion_bp.route('/write', methods=['GET', 'POST'])
def write_post():
    user = get_login_user()
    if not (user and user.role_level >= 30):
        return redirect(url_for('promotion.list_posts', message='회장 이상만 홍보글을 작성할 수 있습니다.'))

    if request.method == 'GET':
        return render_template(
            'promotion_write.html',
            page_title='홍보글 작성',
            message=request.args.get('message', ''),
        )

    title = (request.form.get('title') or '').strip()
    content = (request.form.get('content') or '').strip()
    if not title or not content:
        return redirect(url_for('promotion.write_post', message='제목과 내용을 모두 입력하세요.'))

    new_post = promotionBoard(
        title=title,
        content=content,
        author_pk=user.id,
        club_name=user.belonging_club or 'N',
        is_notice=0,
    )

    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('promotion.list_posts', message='홍보글이 등록되었습니다.'))


@promotion_bp.route('/<int:post_id>', methods=['GET'])
def post_detail(post_id):
    post = promotionBoard.query.get_or_404(post_id)
    user = get_login_user()
    return render_template(
        'promotion_post.html',
        post=post,
        user=user,
        message=request.args.get('message', ''),
    )


@promotion_bp.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    user = get_login_user()
    if not (user and user.role_level >= 30):
        return redirect(url_for('promotion.list_posts', message='권한이 없습니다.'))

    post = promotionBoard.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('promotion.list_posts', message='홍보글이 삭제되었습니다.'))



