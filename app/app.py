
import re  
import os
from status import TaskStatus
from functions import *
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

# List of endpoints that should be excluded from the login check
EXCLUDED_ENDPOINTS = ['/login', '/register']

@app.before_request
def require_login():
    if request.endpoint not in EXCLUDED_ENDPOINTS and not is_user_loggedin():
        # Check if the user is already on the login page
        if request.endpoint != 'login' and request.endpoint != 'register':
            # Check if the request is for a static file
            if not request.path.startswith('/static'):
                return redirect(url_for('login'))
    
def is_user_loggedin():
    return 'userid' in session and 'loggedin' in session and session['loggedin'] == True

@app.route('/')

@app.route('/login', methods =['GET', 'POST'])
def login():
    message = request.args.get('message')

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

@app.route('/logout', methods =['GET', 'POST'])
def logout():
    # clean session vars
    session['loggedin'] = False
    session['userid'] = None
    session['username'] = None
    session['email'] = None
    
    return redirect('/')

@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if not username or not password or not email:
            message = 'Please fill out the form!'
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM User WHERE username = % s', (username, ))
            account = cursor.fetchone()
            
            if account:
                message = 'Choose a different username!'
            else:
                cursor.execute('INSERT INTO User (id, username, email, password) VALUES (NULL, % s, % s, % s)', (username, email, password,))
                mysql.connection.commit()
                message = 'User successfully created!'
                return redirect(url_for('login', message = message))

    elif request.method == 'POST':
        message = 'Please fill all the fields!'
    return render_template('register.html', message = message)

@app.route('/task/done/<int:task_id>', methods =['POST'])
def done_task(task_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE Task SET status = %s, done_time =  CONVERT_TZ(now(), \'UTC\',  \'Europe/Istanbul\') WHERE id = %s AND user_id = %s', (TaskStatus.DONE.value, task_id, session['userid'],))
    mysql.connection.commit()
    
    return redirect(url_for('task'))

@app.route('/task/delete/<int:task_id>', methods =['POST'])
def delete_task(task_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM Task WHERE id = %s', (task_id,))
    mysql.connection.commit()
    
    return redirect(url_for('task'))

@app.route('/task', methods =['GET', 'POST', 'DELETE'])
def task(message = ''):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    update_task_id = None
    update_task = None
    message = request.args.get('message')
    
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
        
        cursor.execute('INSERT INTO Task (id, title, description, status, deadline, creation_time, done_time, user_id, task_type) VALUES (NULL, % s, % s, %s, % s, CONVERT_TZ(now(), \'UTC\',  \'Europe/Istanbul\'), NULL, %s, %s)', (title, description, TaskStatus.TODO.value, due_date, session['userid'], task_type))
        mysql.connection.commit()
        message = 'Task successfully created!'
        return redirect(url_for('task', message = message))
    elif (request.method == 'POST' and 'update-task-id' in request.form):
        update_task_id = request.form['update-task-id']
        
        cursor.execute('SELECT * FROM Task WHERE id = %s', (update_task_id,))
        update_task = cursor.fetchone()
        update_task["deadline"] = convert_to_datetime(update_task["deadline"])
    elif request.method == 'POST' and update_task_id == None:
        # if user tried to create a task but failed due to something, store their previous inputs
        form = {
            "title": request.form['title'],
            "description": request.form['description'],
            "due_date": request.form['due-date'],
            "task_type": request.form['task-type'],
        }
        
        message = 'Please fill all the fields!'
    
    # get task types from db
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM TaskType')
    task_types = cursor.fetchall()   
    
    # get todo tasks from db
    cursor.execute('SELECT * FROM Task WHERE status = %s AND user_id = %s ORDER BY deadline', (TaskStatus.TODO.value, session['userid'], ))
    task_todo = cursor.fetchall()
    
    # get done tasks from db  
    cursor.execute('SELECT * FROM Task WHERE status = %s AND user_id = %s ORDER BY done_time DESC', (TaskStatus.DONE.value, session['userid'], ))
    task_done = cursor.fetchall()
    
    # table column headers
    task_headers = {
        'complete': 'Complete',
        'title': 'Title',
        'description': 'Description',
        'status': 'Status',
        'deadline': "Deadline",
        'creation_time': "Created At",
        'done_time': 'Done At',
        'task_type': 'Category',
        'update': 'Update',
        'delete': 'Delete'
    }
    
    return render_template('task.html', task_types = task_types, task_headers = task_headers, task_todo = task_todo, form = form, task_done = task_done, update_task_id = update_task_id, update_task = update_task, message = message)

@app.route('/update_task/<int:task_id>', methods =['GET', 'POST', 'DELETE'])
def update_task(task_id, message = ''):
    message = ''
    
    if (request.method == 'POST' and 'title' in request.form and 'description' in request.form and 'due-date' in request.form and 'task-type' in request.form
        and request.form['title'] != '' and request.form['description'] != ''):
        
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due-date']
        task_type = request.form['task-type']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE Task SET title = %s, description = %s, task_type = %s, deadline = %s WHERE id = %s', (title, description, task_type, due_date, task_id,))
        mysql.connection.commit()
        
        message = 'Task successfully updated!'        
    else:
        message = 'Update is failed :('
        
    return redirect(url_for('task', message = message))

@app.route('/analysis', methods =['GET', 'POST'])
def analysis():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # analysis 1
    cursor.execute('SELECT title, TIME_TO_SEC(TIMEDIFF(done_time, deadline)) AS latency FROM Task WHERE user_id = %s AND status = %s AND done_time > deadline', (session['userid'], TaskStatus.DONE.value,))
    analysis1 = cursor.fetchall() 
    for task in analysis1:
        task['latency'] = seconds_to_time(task['latency'])
    
    analysis1_headers = {
        'title': 'Task Title',
        'latency': 'Latency'
    }
    
    # analysis 2
    cursor.execute('SELECT AVG(TIME_TO_SEC(TIMEDIFF(done_time, creation_time))) AS average_time FROM Task WHERE user_id = %s AND status = %s', (session['userid'], TaskStatus.DONE.value,))
    analysis2 = cursor.fetchall()
    if analysis2:
        analysis2[0]['average_time'] = avg_to_time(analysis2[0]['average_time'])
    
    # analysis 3
    cursor.execute('SELECT task_type, COUNT(id) AS count FROM Task WHERE user_id = %s AND status = %s GROUP BY task_type ORDER BY count DESC', (session['userid'], TaskStatus.DONE.value,))
    analysis3 = cursor.fetchall()
    
    # analysis 4
    cursor.execute('SELECT title, deadline FROM Task WHERE user_id = %s AND status = %s ORDER BY deadline', (session['userid'], TaskStatus.TODO.value,))
    analysis4 = cursor.fetchall()
    for task in analysis4:
        task['deadline'] = convert_to_datetime(task["deadline"])
    
    analysis4_headers = {
        'title': 'Task Title',
        'deadline': 'Deadline'
    }
    
    # analysis 5
    cursor.execute('SELECT title, TIME_TO_SEC(TIMEDIFF(done_time, creation_time)) AS completion_time FROM Task WHERE user_id = %s AND status = %s ORDER BY completion_time DESC LIMIT 2', (session['userid'], TaskStatus.DONE.value,))
    analysis5 = cursor.fetchall() 
    for task in analysis5:
        task['completion_time'] = seconds_to_time(task['completion_time'])
    
    analysis5_headers = {
        'title': 'Task Title',
        'completion_time': 'Completion Time'
    }
    
    return render_template('analysis.html', analysis1 = analysis1, analysis1_headers = analysis1_headers, analysis2 = analysis2, analysis3 = analysis3, analysis4 = analysis4, analysis4_headers = analysis4_headers, analysis5 = analysis5, analysis5_headers = analysis5_headers)

def redirect_login():
    try:
        if session['loggedin'] == False or session['userid'] == None:
            return redirect(url_for('login'))
    except:
        # Redirect to the login page in case of an exception
        return redirect(url_for('login'))
    

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
