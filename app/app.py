
import re  
import os
from status import TaskStatus
# from task_table import TaskTable
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__) 

app.secret_key = 'abcdefgh'
  
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'cs353hw4db'
  
mysql = MySQL(app)  

@app.route('/')

@app.route('/login', methods =['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = % s AND password = % s', (username, password, ))
        user = cursor.fetchone()
        if user:              
            session['loggedin'] = True
            session['userid'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return redirect(url_for('task'))
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message = message)


@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            message = 'Choose a different username!'
  
        elif not username or not password or not email:
            message = 'Please fill out the form!'

        else:
            cursor.execute('INSERT INTO User (id, username, email, password) VALUES (NULL, % s, % s, % s)', (username, email, password,))
            mysql.connection.commit()
            message = 'User successfully created!'

    elif request.method == 'POST':

        message = 'Please fill all the fields!'
    return render_template('register.html', message = message)

@app.route('/task/done/<int:task_id>', methods =['POST'])
def done_task(task_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE Task SET status = %s, done_time = now() WHERE id = %s', (TaskStatus.DONE.value, task_id,))
    mysql.connection.commit()
    return redirect(url_for('task'))

@app.route('/task/update/<int:task_id>', methods =['POST'])
def update_task(task_id):
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cursor.execute('UPDATE Task SET status = %s, done_time = now() WHERE id = %s', (TaskStatus.DONE.value, task_id,))
    # mysql.connection.commit()
    return "kudur"
    # return redirect(url_for('task'))

@app.route('/task/delete/<int:task_id>', methods =['POST'])
def delete_task(task_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM Task WHERE id = %s', (task_id,))
    mysql.connection.commit()
    return redirect(url_for('task'))

@app.route('/task', methods =['GET', 'POST', 'DELETE'])
def task(message = ''):
    form = {
            "title": '',
            "description": '',
            "due_date": '',
            "task_type": '',
        }
    
    if (request.method == 'POST' and 'title' in request.form and 'description' in request.form and 'due-date' in request.form and 'task-type' in request.form
        and request.form['due-date'] != '' and request.form['title'] != '' and request.form['description'] != ''):
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due-date']
        task_type = request.form['task-type']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO Task (id, title, description, status, deadline, creation_time, done_time, user_id, task_type) VALUES (NULL, % s, % s, %s, % s, now(), NULL, %s, %s)', (title, description, TaskStatus.TODO.value, due_date, session['userid'], task_type))
        mysql.connection.commit()
        message = 'Task successfully created!'
        return redirect(url_for('task'))
    elif request.method == 'POST':
        form = {
            "title": request.form['title'],
            "description": request.form['description'],
            "due_date": request.form['due-date'],
            "task_type": request.form['task-type'],
        }
        message = 'Please fill all the fields!'
        # return task(message)
    
    # get task types from db
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM TaskType')
    task_types = cursor.fetchall()   
    
    # get todo tasks from db
    cursor.execute('SELECT * FROM Task WHERE status = %s ORDER BY deadline', (TaskStatus.TODO.value,))
    task_todo = cursor.fetchall()
    
    # get done tasks from db  
    cursor.execute('SELECT * FROM Task WHERE status = %s ORDER BY done_time DESC', (TaskStatus.DONE.value,))
    task_done = cursor.fetchall()
    
    task_headers = {
        'Mark': ' ',
        'title': 'Title',
        'description': 'Description',
        'status': 'Status',
        'deadline': "Deadline",
        'creation_time': "Created At",
        'done_time': 'Done At',
        'task_type': 'Category',
        'update': 'Update',
        'Delete': ' '
    }
    
    return render_template('task.html', task_types = task_types, task_headers = task_headers, task_todo = task_todo, form = form, task_done = task_done, message = message)

@app.route('/analysis', methods =['GET', 'POST'])
def analysis():
    return "Analysis page"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
