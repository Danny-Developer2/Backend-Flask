from flask import render_template, Blueprint, flash, redirect, url_for, request, jsonify
from app.services.user_service import UserService
from werkzeug.exceptions import NotFound
from flask_login import login_required
from app.models.collection import Collection
from datetime import datetime
from flask_login import login_user, login_required, logout_user
from app.models.user import User
from app.extensions import db
from datetime import timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


web = Blueprint('web', __name__)


@web.route('/users')
@login_required  # Add this decorator
@jwt_required()
def users_list():
    try:
        users = UserService.get_all_users()[0]
        return render_template('users/list.html', users=users)
    except Exception as e:
        flash(str(e), 'danger')
        return render_template('users/list.html', users=[])

@web.route('/users/add', methods=['GET'])
def users_add():
    return render_template('users/add.html')

@web.route('/users/create', methods=['POST'])
def users_create():
    try:
        data = request.get_json()
        user = UserService.create_user(data)
        flash('User created successfully', 'success')
        return jsonify({'status': 'success', 'message': 'User created successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    
    
@web.route('/users/<int:id>/edit', methods=['GET'])
def users_edit(id):
    try:
        user = UserService.get_user_by_id(id)
        return render_template('users/edit.html', user=user)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('web.users_list'))

@web.route('/users/<int:id>/update', methods=['POST'])
def users_update(id):
    try:
        data = request.get_json()
        user = UserService.update_user(id, data)
        flash('User updated successfully', 'success')
        return jsonify({'status': 'success', 'message': 'User updated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    
    
    
# ... existing routes ...

@web.route('/users/<int:id>/delete', methods=['POST'])
def users_delete(id):
    try:
        UserService.delete_user(id)
        return jsonify({
            'status': 'success',
            'message': 'User deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
        

@web.route('/collections/import', methods=['GET','POST'])
def collections_import():
    if request.method == 'GET':
        collections = Collection.query.all() 
        return render_template('collections/list.html',collections=collections)
    try:
        data = request.json
        
        # Limpiar datos existentes
        Collection.query.delete()
        
        # Insertar nuevos registros
        for item in data:
            collection = Collection(
                client_id=str(item.get('ID Cliente')),
                client_name=item.get('Nombre del Cliente'),
                phone=item.get('Teléfono'),
                email=item.get('Correo Electrónico'),
                due_date=datetime.strptime(item.get('Fecha de Vencimiento'), '%Y-%m-%d').date() if item.get('Fecha de Vencimiento') else None,
                amount=float(str(item.get('Monto Adeudado', '0')).replace('$', '').replace(',', '')),
                days_overdue=int(item.get('Días de Mora', 0)),
                status=item.get('Estatus de Cobranza'),
                last_management=datetime.strptime(item.get('Última Gestión'), '%Y-%m-%d').date() if item.get('Última Gestión') else None,
                observations=item.get('Observaciones')
            )
            db.session.add(collection)
        
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Datos importados correctamente'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    


@web.route('/collections/delete-all', methods=['POST'])
def collections_delete_all():
    try:
        Collection.query.delete()
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Todos los registros han sido eliminados'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
        


@web.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            user = User.query.filter_by(username=data.get('username')).first()
            
            if not user:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid username or password'
                }), 401
                
            if not user.is_active:
                return jsonify({
                    'status': 'error',
                    'message': 'Usuario desactivado. Contacte a soporte.'
                }), 403
                
            if not user.check_password(data.get('password')):
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid username or password'
                }), 401
                
            # Create JWT token
            access_token = create_access_token(
                identity=str(user.id),
                expires_delta=timedelta(hours=1)
            )
            
            login_user(user, remember=data.get('remember', False))
            
            # Create response before setting cookie
            response = jsonify({
                'status': 'success',
                'message': 'Login successful',
                'user': user.to_dict()
            })
            
            # Set JWT token in HTTP-only cookie
            response.set_cookie(
                'access_token',
                value=access_token,
                httponly=True,
                secure=False,  # Cambiar a True en producción con HTTPS
                samesite='Lax',
                max_age=3600  # 1 hora en segundos
            )
            
            return response
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
            
    return render_template('users/login.html')

@web.route('/logout')
@login_required
def logout():
    response = redirect(url_for('web.login'))
    response.delete_cookie('access_token')
    response.delete_cookie('session')
    logout_user()
    flash('You have been logged out.', 'info')
    return response


# ... existing imports ...

@web.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate input
            if not all(k in data for k in ['username', 'email', 'password']):
                return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
            
            if not User.is_valid_username(data['username']):
                return jsonify({'status': 'error', 'message': 'Invalid username format'}), 400
                
            if not User.is_valid_email(data['email']):
                return jsonify({'status': 'error', 'message': 'Invalid email format'}), 400
                
            # Check if user already exists
            if User.find_by_username(data['username']):
                return jsonify({'status': 'error', 'message': 'Username already exists'}), 400
                
            if User.find_by_email(data['email']):
                return jsonify({'status': 'error', 'message': 'Email already exists'}), 400
                
            # Create new user
            user = User(
                username=data['username'],
                email=data['email'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', '')
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'User registered successfully',
                'user': user.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
            
    return render_template('users/register.html')