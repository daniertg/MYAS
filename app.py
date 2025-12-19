#!/usr/bin/env python3
"""
Theoryma MYSQL Auto User - Web Management Tool
For Linux VPS with MySQL installed
Coded by Febrian Dani Ritonga
"""

from flask import Flask, render_template, request, jsonify
import subprocess
import re
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ===== MySQL Command Executor =====
def run_mysql_command(sql):
    """Execute MySQL command using sudo mysql"""
    try:
        result = subprocess.run(
            ['/usr/bin/sudo', '/usr/bin/mysql', '-e', sql],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, '', 'Command timeout'
    except Exception as e:
        return False, '', str(e)

def run_mysql_query(sql):
    """Execute MySQL query and return results"""
    try:
        result = subprocess.run(
            ['/usr/bin/sudo', '/usr/bin/mysql', '-N', '-e', sql],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr
    except Exception as e:
        return False, '', str(e)

# ===== Password Validation =====
def validate_password(password):
    """Validate password meets MySQL policy"""
    if len(password) < 8:
        return False, "Password harus minimal 8 karakter"
    if not re.search(r'[A-Z]', password):
        return False, "Password harus mengandung huruf besar"
    if not re.search(r'[a-z]', password):
        return False, "Password harus mengandung huruf kecil"
    if not re.search(r'[0-9]', password):
        return False, "Password harus mengandung angka"
    if not re.search(r'[^a-zA-Z0-9]', password):
        return False, "Password harus mengandung karakter spesial"
    return True, "OK"

# ===== Routes =====
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    """Test MySQL connection"""
    success, output, error = run_mysql_query("SELECT 1;")
    if success:
        return jsonify({'success': True, 'message': 'MySQL connection successful'})
    return jsonify({'success': False, 'error': error})

@app.route('/api/databases', methods=['GET'])
def list_databases():
    """List all databases"""
    success, output, error = run_mysql_query("SHOW DATABASES;")
    if success:
        databases = [db for db in output.split('\n') if db and db not in ['information_schema', 'performance_schema', 'mysql', 'sys']]
        return jsonify({'success': True, 'databases': databases})
    return jsonify({'success': False, 'error': error})

@app.route('/api/users', methods=['GET'])
def list_users():
    """List all MySQL users"""
    success, output, error = run_mysql_query("SELECT User, Host FROM mysql.user;")
    if success:
        users = []
        for line in output.split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2 and parts[0] not in ['root', 'mysql.sys', 'mysql.session', 'mysql.infoschema', 'debian-sys-maint']:
                    users.append({'user': parts[0], 'host': parts[1]})
        return jsonify({'success': True, 'users': users})
    return jsonify({'success': False, 'error': error})

@app.route('/api/user/<username>/<host>/grants', methods=['GET'])
def get_user_grants(username, host):
    """Get grants for specific user"""
    sql = f"SHOW GRANTS FOR '{username}'@'{host}';"
    success, output, error = run_mysql_query(sql)
    if success:
        grants = output.split('\n') if output else []
        return jsonify({'success': True, 'grants': grants})
    return jsonify({'success': False, 'error': error})

@app.route('/api/create-user', methods=['POST'])
def create_user():
    """Create new MySQL user and optionally database"""
    data = request.json
    
    db_name = data.get('database', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    host = data.get('host', 'localhost').strip()
    create_db = data.get('create_database', True)
    
    if not username:
        return jsonify({'success': False, 'error': 'Username diperlukan'})
    
    if not password:
        return jsonify({'success': False, 'error': 'Password diperlukan'})
    
    valid, msg = validate_password(password)
    if not valid:
        return jsonify({'success': False, 'error': msg})
    
    if host == '' or host == 'localhost':
        host = 'localhost'
    elif host == '0' or host == '%':
        host = '%'
    
    sql_commands = []
    
    if create_db and db_name:
        sql_commands.append(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;")
    
    sql_commands.append(f"CREATE USER IF NOT EXISTS '{username}'@'{host}' IDENTIFIED BY '{password}';")
    
    if db_name:
        sql_commands.append(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{username}'@'{host}';")
    
    sql_commands.append("FLUSH PRIVILEGES;")
    
    full_sql = ' '.join(sql_commands)
    success, output, error = run_mysql_command(full_sql)
    
    if success:
        return jsonify({
            'success': True, 
            'message': f'User {username}@{host} berhasil dibuat' + (f' dengan database {db_name}' if db_name else '')
        })
    return jsonify({'success': False, 'error': error})

@app.route('/api/create-database', methods=['POST'])
def create_database():
    """Create new database"""
    data = request.json
    db_name = data.get('database', '').strip()
    
    if not db_name:
        return jsonify({'success': False, 'error': 'Nama database diperlukan'})
    
    sql = f"CREATE DATABASE IF NOT EXISTS `{db_name}`;"
    success, output, error = run_mysql_command(sql)
    
    if success:
        return jsonify({'success': True, 'message': f'Database {db_name} berhasil dibuat'})
    return jsonify({'success': False, 'error': error})

@app.route('/api/delete-database', methods=['POST'])
def delete_database():
    """Delete database"""
    data = request.json
    db_name = data.get('database', '').strip()
    
    if not db_name:
        return jsonify({'success': False, 'error': 'Nama database diperlukan'})
    
    sql = f"DROP DATABASE IF EXISTS `{db_name}`;"
    success, output, error = run_mysql_command(sql)
    
    if success:
        return jsonify({'success': True, 'message': f'Database {db_name} berhasil dihapus'})
    return jsonify({'success': False, 'error': error})

@app.route('/api/delete-user', methods=['POST'])
def delete_user():
    """Delete MySQL user"""
    data = request.json
    username = data.get('username', '').strip()
    host = data.get('host', 'localhost').strip()
    
    if not username:
        return jsonify({'success': False, 'error': 'Username diperlukan'})
    
    sql = f"DROP USER IF EXISTS '{username}'@'{host}'; FLUSH PRIVILEGES;"
    success, output, error = run_mysql_command(sql)
    
    if success:
        return jsonify({'success': True, 'message': f'User {username}@{host} berhasil dihapus'})
    return jsonify({'success': False, 'error': error})

@app.route('/api/grant-privileges', methods=['POST'])
def grant_privileges():
    """Grant privileges to user"""
    data = request.json
    username = data.get('username', '').strip()
    host = data.get('host', 'localhost').strip()
    database = data.get('database', '').strip()
    privileges = data.get('privileges', 'ALL PRIVILEGES')
    
    if not username or not database:
        return jsonify({'success': False, 'error': 'Username dan database diperlukan'})
    
    sql = f"GRANT {privileges} ON `{database}`.* TO '{username}'@'{host}'; FLUSH PRIVILEGES;"
    success, output, error = run_mysql_command(sql)
    
    if success:
        return jsonify({'success': True, 'message': f'Privileges granted to {username}@{host} on {database}'})
    return jsonify({'success': False, 'error': error})

@app.route('/api/revoke-privileges', methods=['POST'])
def revoke_privileges():
    """Revoke privileges from user"""
    data = request.json
    username = data.get('username', '').strip()
    host = data.get('host', 'localhost').strip()
    database = data.get('database', '').strip()
    privileges = data.get('privileges', 'ALL PRIVILEGES')
    
    if not username or not database:
        return jsonify({'success': False, 'error': 'Username dan database diperlukan'})
    
    sql = f"REVOKE {privileges} ON `{database}`.* FROM '{username}'@'{host}'; FLUSH PRIVILEGES;"
    success, output, error = run_mysql_command(sql)
    
    if success:
        return jsonify({'success': True, 'message': f'Privileges revoked from {username}@{host} on {database}'})
    return jsonify({'success': False, 'error': error})

@app.route('/api/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    data = request.json
    username = data.get('username', '').strip()
    host = data.get('host', 'localhost').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username dan password diperlukan'})
    
    valid, msg = validate_password(password)
    if not valid:
        return jsonify({'success': False, 'error': msg})
    
    sql = f"ALTER USER '{username}'@'{host}' IDENTIFIED BY '{password}'; FLUSH PRIVILEGES;"
    success, output, error = run_mysql_command(sql)
    
    if success:
        return jsonify({'success': True, 'message': f'Password untuk {username}@{host} berhasil diubah'})
    return jsonify({'success': False, 'error': error})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
