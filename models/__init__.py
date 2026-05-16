from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


from .user import User
from .club import Club
from .club_application import ClubApplication

#약간 서브트리의 루트노드 느낌임 
#규칙~:N은 일단 비어있다는뜻임


