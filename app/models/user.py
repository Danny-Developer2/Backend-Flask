from datetime import datetime
from app.extensions import db
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import re

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    last_login = db.Column(db.DateTime, nullable=True)
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    deleted_at = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @hybrid_property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @hybrid_property
    def is_deleted(self):
        return self.deleted_at is not None

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username, deleted_at=None).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email, deleted_at=None).first()

    @classmethod
    def search(cls, term):
        return cls.query.filter(
            db.or_(
                cls.username.ilike(f'%{term}%'),
                cls.email.ilike(f'%{term}%'),
                cls.first_name.ilike(f'%{term}%'),
                cls.last_name.ilike(f'%{term}%')
            ),
            cls.deleted_at.is_(None)
        ).all()

    @staticmethod
    def is_valid_email(email):
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def is_valid_username(username):
        if not username:
            return False
        pattern = r'^[a-zA-Z0-9_]{3,80}$'
        return bool(re.match(pattern, username))

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
        self.is_active = False
        db.session.commit()

    def restore(self):
        self.deleted_at = None
        self.is_active = True
        db.session.commit()

    def to_dict(self, include_private=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'is_deleted': self.is_deleted,
            'last_login': self.last_login.isoformat() if self.last_login else None  # Add this
        }
        
        if include_private:
            data.update({
                'first_name': self.first_name,
                'last_name': self.last_name,
                'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
            })
        
        return data

    def __repr__(self):
        return f'<User {self.username}>'