import os
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

@app.route('/api/version', methods=['GET'])
def get_version():
    return jsonify({'version': '1.2.0'})

@app.route('/api/todos', methods=['GET'])
def get_todos():
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM todos ORDER BY id")
        todos = cursor.fetchall()
    return jsonify(todos)

@app.route('/api/todos', methods=['POST'])
def add_todo():
    data = request.json
    title = data.get('title')
    if not title:
        return jsonify({'error': 'عنوان الزامی است'}), 400

    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO todos (title) VALUES (%s) RETURNING id", (title,))
        new_id = cursor.fetchone()[0]
        conn.commit()
    return jsonify({'message': 'تسک اضافه شد', 'id': new_id}), 201

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.json
    title = data.get('title')
    completed = data.get('completed')

    if title is None or completed is None:
        return jsonify({'error': 'title و completed الزامی هستند'}), 400

    with conn.cursor() as cursor:
        cursor.execute("UPDATE todos SET title = %s, completed = %s WHERE id = %s", (title, completed, todo_id))
        conn.commit()
    return jsonify({'message': 'تسک ویرایش شد'})

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
        conn.commit()
    return jsonify({'message': 'تسک حذف شد'})

@app.route('/api/todos/<int:todo_id>/toggle', methods=['PATCH'])
def toggle_todo(todo_id):
    with conn.cursor() as cursor:
        cursor.execute("UPDATE todos SET completed = NOT completed WHERE id = %s", (todo_id,))
        conn.commit()
    return jsonify({'message': 'وضعیت تسک تغییر کرد'})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
