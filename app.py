from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name: row['column_name']
    return conn

def init_db():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    # Drop tables if they exist
    c.execute('DROP TABLE IF EXISTS tasks')
    c.execute('DROP TABLE IF EXISTS users')
    # Create the users table
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    # Create the tasks table with a foreign key to users
    c.execute('''
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT t.id, t.name, t.description, t.status, u.username
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
    ''')
    tasks = c.fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/users')
def users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('users.html', users=users)

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, email) VALUES (?, ?)', (username, email))
        conn.commit()
        conn.close()
        return redirect(url_for('users'))
    return render_template('create_user.html')

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        status = request.form['status']
        user_id = request.form['user_id']
        conn = get_db_connection()
        conn.execute('INSERT INTO tasks (name, description, status, user_id) VALUES (?, ?, ?, ?)', 
                     (name, description, status, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        conn = get_db_connection()
        users = conn.execute('SELECT id, username FROM users').fetchall()
        conn.close()
        return render_template('add_task.html', users=users)

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        status = request.form['status']
        user_id = request.form['user_id']
        conn.execute('UPDATE tasks SET name = ?, description = ?, status = ?, user_id = ? WHERE id = ?',
                     (name, description, status, user_id, task_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    users = conn.execute('SELECT id, username FROM users').fetchall()
    conn.close()
    return render_template('edit_task.html', task=task, users=users)

@app.route('/delete/<int:task_id>', methods=['GET'])
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()  # Ensure database is initialized before starting the app
    app.run(debug=True)
