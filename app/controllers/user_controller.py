from flask_restx import Resource
from app.services.user_service import UserService
from app.schemas.user_schema import user_input_model, user_model, response_model
from http import HTTPStatus
from flask import request
from app import api
from werkzeug.exceptions import BadRequest

ns = api.namespace('users', description='Users operations', path='/api/v1/users')

@ns.route('/')
class UserList(Resource):
    @ns.doc('list_users')
    @ns.response(HTTPStatus.OK, 'Success', response_model)
    @ns.param('is_active', 'Filter by user status (true/false)')
    @ns.param('sort', 'Sort field (username, email, created_at)')
    @ns.param('order', 'Sort order (asc/desc)')
    @ns.param('page', 'Page number')
    @ns.param('per_page', 'Items per page')
    def get(self):
        """List all users with filtering, sorting and pagination"""
        try:
            # Get query parameters
            is_active = request.args.get('is_active')
            sort = request.args.get('sort', 'created_at')
            order = request.args.get('order', 'desc')
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 10)), 100)

            # Validate parameters
            if sort not in ['username', 'email', 'created_at']:
                raise BadRequest('Invalid sort field')
            if order not in ['asc', 'desc']:
                raise BadRequest('Invalid sort order')
            
            # Process is_active parameter
            if is_active is not None:
                is_active = is_active.lower() == 'true'
            
            # Get paginated users
            users, total = UserService.get_all_users(
                is_active=is_active,
                sort=sort,
                order=order,
                page=page,
                per_page=per_page
            )

            return {
                'status': 'success',
                'message': 'Users retrieved successfully',
                'data': {
                    'users': [user.to_dict() for user in users],
                    'pagination': {
                        'total': total,
                        'page': page,
                        'per_page': per_page,
                        'pages': (total + per_page - 1) // per_page
                    }
                }
            }
        except BadRequest as e:
            return {'status': 'error', 'message': str(e)}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @ns.doc('create_user')
    @ns.expect(user_input_model)
    @ns.response(HTTPStatus.CREATED, 'User created', response_model)
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation error')
    def post(self):
        """Create a new user with validation"""
        try:
            if not request.is_json:
                raise BadRequest('Content-Type must be application/json')

            data = api.payload
            if not data:
                raise BadRequest('No input data provided')

            # Validate email format
            if not UserService.validate_email(data.get('email', '')):
                raise BadRequest('Invalid email format')

            # Validate username format
            if not UserService.validate_username(data.get('username', '')):
                raise BadRequest('Username must be 3-80 characters and alphanumeric')

            user = UserService.create_user(data)
            
            return {
                'status': 'success',
                'message': 'User created successfully',
                'data': user.to_dict()
            }, HTTPStatus.CREATED
        except BadRequest as e:
            return {'status': 'error', 'message': str(e)}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, HTTPStatus.BAD_REQUEST

@ns.route('/<int:id>')
@ns.param('id', 'The user identifier')
class UserResource(Resource):
    @ns.doc('get_user')
    @ns.response(HTTPStatus.OK, 'Success', response_model)
    @ns.response(HTTPStatus.NOT_FOUND, 'User not found')
    def get(self, id):
        """Get a specific user by ID"""
        try:
            user = UserService.get_user_by_id(id)
            return {
                'status': 'success',
                'message': 'User retrieved successfully',
                'data': user.to_dict()
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, HTTPStatus.NOT_FOUND

    @ns.doc('update_user')
    @ns.expect(user_input_model)
    @ns.response(HTTPStatus.OK, 'User updated', response_model)
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation error')
    @ns.response(HTTPStatus.NOT_FOUND, 'User not found')
    def put(self, id):
        """Update a user with validation"""
        try:
            if not request.is_json:
                raise BadRequest('Content-Type must be application/json')

            data = api.payload
            if not data:
                raise BadRequest('No input data provided')

            # Validate email if provided
            if 'email' in data and not UserService.validate_email(data['email']):
                raise BadRequest('Invalid email format')

            # Validate username if provided
            if 'username' in data and not UserService.validate_username(data['username']):
                raise BadRequest('Username must be 3-80 characters and alphanumeric')

            user = UserService.update_user(id, data)
            
            return {
                'status': 'success',
                'message': 'User updated successfully',
                'data': user.to_dict()
            }
        except BadRequest as e:
            return {'status': 'error', 'message': str(e)}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, HTTPStatus.NOT_FOUND

    @ns.doc('delete_user')
    @ns.response(HTTPStatus.OK, 'User deleted', response_model)
    @ns.response(HTTPStatus.NOT_FOUND, 'User not found')
    def delete(self, id):
        """Delete a user"""
        try:
            UserService.delete_user(id)
            return {
                'status': 'success',
                'message': 'User deleted successfully'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, HTTPStatus.NOT_FOUND