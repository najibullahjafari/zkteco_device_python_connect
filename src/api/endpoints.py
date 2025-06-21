from datetime import datetime
from flask import Flask, jsonify, request
from core import zk  # Assuming core.py is in the same directory

app = Flask(__name__)


@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        conn = zk.connect()
        users = conn.get_users()
        conn.disconnect()
        return jsonify([{'uid': user.uid, 'name': user.name, 'privilege': user.privilege} for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/<int:uid>', methods=['DELETE'])
def delete_user(uid):
    try:
        conn = zk.connect()
        conn.delete_user(uid)
        conn.disconnect()
        return jsonify({"status": "deleted"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/<int:uid>', methods=['GET'])
def get_user(uid):
    try:
        conn = zk.connect()
        user = conn.get_user(uid)
        conn.disconnect()
        if user:
            return jsonify({'uid': user.uid, 'name': user.name, 'privilege': user.privilege})
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    try:
        conn = zk.connect()
        attendance = conn.get_attendance()
        conn.disconnect()
        return jsonify([{'user_id': att.user_id, 'timestamp': att.timestamp, 'status': att.status} for att in attendance])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/users', methods=['POST'])
def api_insert_user():
    try:
        data = request.get_json()
        conn = zk.connect()
        conn.set_user(
            uid=data.get('uid'),
            name=data.get('name'),
            privilege=data.get('privilege'),
            password=data.get('password'),
            group_id=data.get('group_id'),
            user_id=data.get('user_id')
        )
        conn.disconnect()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/attendance/<int:user_id>/<string:date>', methods=['GET'])
def get_attendance_by_user_and_date(user_id, date):
    try:
        conn = zk.connect()
        attendance = conn.get_attendance()
        conn.disconnect()
        # Filter by user_id and date (date format: YYYY-MM-DD)
        filtered = [
            {'user_id': att.user_id, 'timestamp': str(
                att.timestamp), 'status': att.status}
            for att in attendance
            if str(att.user_id) == str(user_id) and str(att.timestamp).startswith(date)
        ]
        return jsonify(filtered)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
