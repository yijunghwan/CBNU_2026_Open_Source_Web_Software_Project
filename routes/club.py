from flask import Blueprint

# 동아리 관련 기능 네임스페이스 ('/club')
club_bp = Blueprint('club', __name__, url_prefix='/club')


# 회장 관리 페이지 전용으로 따로 만들어야ㅏㄹ듯