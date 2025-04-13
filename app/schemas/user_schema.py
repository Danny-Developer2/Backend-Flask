from app import api
from flask_restx import fields

user_input_model = api.model('UserInput', {
    'username': fields.String(required=True, description='Username', min_length=3, max_length=80),
    'email': fields.String(required=True, description='User email', max_length=120),
    'is_active': fields.Boolean(description='User status', default=True)
})

user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='User identifier'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='User email'),
    'created_at': fields.DateTime(description='Creation date'),
    'is_active': fields.Boolean(description='User status')
})

response_model = api.model('Response', {
    'status': fields.String(description='Response status'),
    'message': fields.String(description='Response message'),
    'data': fields.Raw(description='Response data')
})