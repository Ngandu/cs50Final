from os import stat
import sqlite3
from flask import Flask, render_template, request, redirect, session
from datetime import date

# cursor = conn.execute("select * from todos")

# print(cursor)
app = Flask(__name__)

# Global variables


def bignman():
    #print('Big man')
    groupsList = []
    conn = sqlite3.connect('db/todos.db')
    conn.row_factory = sqlite3.Row
    groups = conn.execute("SELECT * FROM groups").fetchall()
    # print(groups)
    for g in groups:
        temp = {
            'group_id': g["group_id"],
            "owner_id": g["owner_id"],
            "group_name": g["group_name"],
            "group_descrip": g["group_descrip"],
            "isActive": g["isActive"]
        }
        # print(temp)
        groupsList.append(temp)

    # print(groupsList)

    session["g"] = groupsList

    conn.commit()
    conn.close()


@app.route('/')
def index():

    bignman()

    conn = sqlite3.connect('db/todos.db')

    tasks = conn.execute(
        "SELECT * FROM todos WHERE user_id = "+str(session['loggedin'][0])+" ORDER BY duedate DESC lIMIT 3")

    dashData = conn.execute(
        "SELECT status, duedate FROM todos WHERE user_id = "+str(session['loggedin'][0])+"")

    today = date.today()
    print('Today: ', today)

    new = 0
    process = 0
    complete = 0
    overdue = 0

    for task in dashData:
        print(task)

        try:
            if task[1] < today:
                overdue += 1
            print('Not overdue')
        except:
            print("An exception occurred")

        if task[0] == 'New':
            new += 1
        elif task[0] == 'Process':
            process += 1
        elif task[0] == 'Complete':
            complete += 1
        else:
            overdue += 1

    #session['tasks'] = tasks

    return render_template("index.html", tasks=tasks, new=new, process=process, complete=complete, overdue=overdue)


@app.route('/view/<todoid>')
def todoview(todoid):

    conn = sqlite3.connect('db/todos.db')

    tasks = conn.execute(
        "SELECT * FROM todos WHERE user_id = "+str(session['loggedin'][0])+" ORDER BY duedate")

    task = conn.execute(
        "SELECT * FROM todos WHERE todo_id = "+str(todoid)+"")

    print('Todo: ', task)

    return render_template("todos.html", tasks=tasks, task=task)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('db/todos.db')

        userDetails = conn.execute("SELECT * FROM users WHERE username = '" +
                                   username+"' AND password = '"+password+"'")

        #session['loggedin'] = userDetails
        for row in userDetails:
            print(row)
            print(len(row))
            if len(row) == 5:
                session['loggedin'] = row
                userid = row[0]
                print('User found, session set')
                conn.commit()
                conn.close()
                return redirect('/login')
            else:
                print('no such user')
                conn.commit()
                conn.close()
                return redirect('/login')

    else:
        if 'loggedin' in session:
            return redirect('/')
        else:
            return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('loggedin')
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']

        conn = sqlite3.connect('db/todos.db')

        conn.execute("INSERT INTO users (username,password,firstname,lastname) VALUES ('" +
                     username+"', '"+password+"', '"+firstname+"','"+lastname+"')")
        # conn.commit()
        # conn.close()
        return redirect('/login')
    else:
        return render_template('register.html')


@app.route('/todos')
def todos():
    conn = sqlite3.connect('db/todos.db')
    tasks = conn.execute(
        "SELECT * FROM todos WHERE user_id = "+str(session['loggedin'][0])+" ORDER BY duedate DESC")

    return render_template('todos.html', tasks=tasks)


@app.route('/groups', methods=['GET', 'POST'])
def groups():
    if request.method == 'POST':

        group_name = request.form['group_name']
        group_descrip = request.form['group_descrip']
        user_id = session['loggedin'][0]

        conn = sqlite3.connect('db/todos.db')

        conn.execute("INSERT INTO groups (owner_id,group_name,group_descrip,isActive) VALUES ('" +
                     str(user_id)+"', '"+group_name+"', '"+group_descrip+"',1)")
        conn.commit()
        conn.close()
        bignman()

        return redirect('/groups')
    else:
        conn = sqlite3.connect('db/todos.db')
        groups = conn.execute(
            "SELECT * FROM groups WHERE owner_id = "+str(session['loggedin'][0])+"")
        # print(session)
        # for group in groups:
        #     print(group)
        groupList = session["g"]
        #groupList = []
        return render_template('groups.html', groups=groups, groupList=groupList)


@app.route('/group/<groupid>')
def groupview(groupid):

    conn = sqlite3.connect('db/todos.db')

    groups = conn.execute(
        "SELECT * FROM groups WHERE owner_id = "+str(session['loggedin'][0])+"")

    group = conn.execute(
        "SELECT * FROM groups WHERE group_id = "+str(groupid)+"")

    tasks = conn.execute(
        "SELECT * FROM todos WHERE group_id = "+str(groupid)+"")

    print('Todo: ', group)

    return render_template('groups.html', groups=groups, group=group, tasks=tasks, groupList=session["g"])


@app.route('/func', methods=['POST'])
def func():
    if request.method == 'POST':
        print(request.form)
        print(session['loggedin'][0])

        today = date.today()
        todo_title = request.form['todo_title']
        todo_description = request.form['todo_description']
        group_id = request.form['group']
        duedate = request.form['duedate']
        user_id = session['loggedin'][0]

        conn = sqlite3.connect('db/todos.db')

        conn.execute("INSERT INTO todos (todo_title,todo_description,group_id,user_id, created_date,status, duedate) VALUES ('" +
                     todo_title+"', '"+todo_description+"', "+str(group_id)+","+str(user_id)+", "+str(today)+", 'New', '"+str(duedate)+"')")
        conn.commit()
        conn.close()

        return redirect('/')
    else:
        return redirect('/')

# Update Task


@app.route('/funcu', methods=['POST'])
def funct():
    if request.method == 'POST':

        # todo_title = request.form['todo_title']
        # todo_description = request.form['todo_description']
        # group_id = request.form['group']
        # duedate = request.form['duedate']
        status = request.form['status']
        todo_id = request.form['todo_id']

        print(status)

        # return todo_id

        conn = sqlite3.connect('db/todos.db')

        conn.execute('UPDATE todos SET status = "' +
                     status+'" WHERE todo_id='+todo_id+'')
        conn.commit()
        conn.close()

        return redirect('/todos')
    else:
        return redirect('/')

# Delete Task


@app.route('/funcd/<r>', methods=['GET'])
def funcu(r):
    if request.method == 'GET':
        conn = sqlite3.connect('db/todos.db')
        conn.execute("DELETE FROM todos WHERE todo_id = "+str(r)+"")
        return redirect('/todos')
    else:
        return redirect('/')


if __name__ == '__main__':
    app.secret_key = '12345asdfg678jk90'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(debug=True)
