from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime

app = Flask(__name__)
CORS(app)

# 密钥
SECRET_KEY = 'your-secret-key-here'

# 硬编码用户（内存模式，无需MongoDB）
USERS = {
    'teacher': {
        'password': '123456',
        'role': 'teacher',
        'username': 'teacher'
    }
}

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "用户名和密码不能为空"}), 400

    if MONGODB_AVAILABLE:
        if users_collection.find_one({"username": username}):
            return jsonify({"success": False, "message": "该用户名已被注册"}), 409

        hashed_password = generate_password_hash(password)
        class_name = request.form.get('class_name', '')
        student_id = request.form.get('student_id', '')
        new_user = {
            "username": username,
            "password": hashed_password,
            "role": "teacher",
            "class_name": class_name,
            "student_id": student_id,
            "created_at": datetime.datetime.utcnow()
        }

        try:
            users_collection.insert_one(new_user)
            return jsonify({"success": True, "message": "注册成功，请登录"}), 201
        except Exception as e:
            print(f"注册错误: {e}")
            return jsonify({"success": False, "message": "注册失败，请稍后重试"}), 500
    else:
        if username in memory_users:
            return jsonify({"success": False, "message": "该用户名已被注册"}), 409
        
        memory_users[username] = {
            "username": username,
            "password": generate_password_hash(password),
            "role": "teacher",
            "class_name": class_name,
            "student_id": student_id
        }
        return jsonify({"success": True, "message": "注册成功，请登录（内存模式）"}), 201

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请提供JSON格式的数据'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        user = USERS.get(username)
        if not user or user['password'] != password:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
        
        token = jwt.encode({
            'username': username,
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': {
                'username': username,
                'role': user['role'],
                'token': token
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)