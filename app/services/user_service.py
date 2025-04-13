from app import db
from app.models.user import User
from werkzeug.exceptions import BadRequest, NotFound
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def get_all_users(sort='created_at', order='desc', page=1, per_page=5):
        try:
            query = User.query

            # Apply sorting
            sort_column = getattr(User, sort)
            if order == 'desc':
                query = query.order_by(db.desc(sort_column))
            else:
                query = query.order_by(db.asc(sort_column))

            # Execute query
            users = query.all()
            print(f"Query result: {users}")
            
            return users, len(users)
        except Exception as e:
            print(f"Service error: {str(e)}")
            raise

    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFound(f'User {user_id} not found')
        return user

    @staticmethod
    def create_user(data):
        if User.query.filter_by(username=data['username']).first():
            raise BadRequest('Username already exists')
        
        if User.query.filter_by(email=data['email']).first():
            raise BadRequest('Email already exists')

        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user(user_id, data):
        user = UserService.get_user_by_id(user_id)
        
        if 'username' in data and data['username'] != user.username:
            if User.query.filter_by(username=data['username']).first():
                raise BadRequest('Username already exists')

        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                raise BadRequest('Email already exists')

        for key, value in data.items():
            setattr(user, key, value)
        
        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        user = UserService.get_user_by_id(user_id)
        db.session.delete(user)
        db.session.commit()