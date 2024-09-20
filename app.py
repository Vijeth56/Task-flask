from flask import Flask, render_template, request, jsonify
from datetime import datetime
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config.from_object('config.Config')

mysql = MySQL(app)

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")


@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    description = data.get('description')
    deadline_str = data.get('deadline')  

    
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO task(description, status, deadline) VALUES(%s, %s, %s)",
                   (description, "assigned", deadline))
    mysql.connection.commit()
    new_task_id = cursor.lastrowid  
    cursor.close()

    return jsonify(success=True, task={
        'id': new_task_id,
        'description': description,
        'status': "assigned",
        'deadline': deadline.strftime('%Y-%m-%d') if deadline else None
    })


@app.route('/tasks/<status>', methods=['POST'])
def move_task(status):
    data = request.json
    task_id = data.get('id')
    
    if status not in ["assigned", "in-progress", "done"]:
        return jsonify(success=False), 400

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE task SET status=%s WHERE id=%s", (status, task_id))
    mysql.connection.commit()
    
    if cursor.rowcount > 0:
        cursor.close()
        return jsonify(success=True)
    
    cursor.close()
    return jsonify(success=False), 400

def get_tasks():
    cursor = mysql.connection.cursor()
    
    tasks = {
        "assigned": [],
        "in-progress": [],
        "done": []
    }
    
    for status in tasks.keys():
        cursor.execute("SELECT id, description, status, deadline FROM task WHERE status=%s", (status,))
        result = cursor.fetchall()
        for row in result:
            tasks[status].append({
                'id': row[0],
                'description': row[1],
                'status': row[2],
                'deadline': row[3].strftime('%Y-%m-%d') if row[3] else None
            })

    cursor.close()
    return tasks  # Return the dictionary of tasks directly

@app.route('/tasks-data', methods=['GET'])
def tasks_data():
    return jsonify(get_tasks())  


# delete task 
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM task WHERE id=%s", (task_id,))
    mysql.connection.commit()
    
    if cursor.rowcount > 0:
        cursor.close()
        return jsonify(success=True)
    
    cursor.close()
    return jsonify(success=False), 404

# teams page 
@app.route("/teams", methods=['GET'])
def teams():
    return render_template("teams.html")

@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    if username:
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user(username) VALUES(%s)", (username,))
        mysql.connection.commit()
        cursor.close()
        return jsonify(success=True)
    return jsonify(success=False), 400

@app.route('/users-data', methods=['GET'])
def users_data():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, username FROM user")
    users = cursor.fetchall()
    cursor.close()

    
    user_list = [{'id': user[0], 'username': user[1]} for user in users]
    return jsonify(user_list)

if __name__ == "__main__":
    app.run(debug=True)
