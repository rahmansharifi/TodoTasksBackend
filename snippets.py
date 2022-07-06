import os
import time
import json
import random
import datetime

# kos bibi jenda sadam

class exceptions:
    class Found(Exception):
        pass
    class NotFound(Exception):
        pass
    class EmailExists(Exception):
        pass
    class UsernameExists(Exception):
        pass
    class WrongPassword(Exception):
        pass

class Found(Exception):
    pass
class NotFound(Exception):
    pass
class EmailExists(Exception):
    pass
class UsernameExists(Exception):
    pass
class WrongPassword(Exception):
    pass

def save(d):
    with open('app.json','w+') as f:
        f.write(json.dumps(d))
    os.system('chmod -R 777 '+os.path.dirname(__file__))
def load():
    if not os.path.isfile('app.json'):
        d = {
            'version': 'v1',
            'require': [
                'users',
                'sessions',
                'tasks',
            ],
            'users': [],
            'sessions': [],
            'tasks': [],
        }
        save(d)
    with open('app.json','r') as f:
        return json.loads(f.read())
def reset():
    os.remove('app.json')
    load()
def generate(l=8):
    key = ''
    for i in range(l):
        key=key+random.choice('abcdefghijklmnopqrstuvwxyz1234567890')
    return key
def ensure_database():
    db = load()
    try:
        db['version']
    except Exception as e:
        db['version'] = 'v1'
    try:
        db['require']
    except Exception as e:
        db['require'] = [
            'users',
            'sessions',
            'tasks',
        ]
    try:
        db['users']
    except Exception as e:
        db['users'] = []
    try:
        db['sessions']
    except Exception as e:
        db['sessions'] = []
    try:
        db['tasks']
    except Exception as e:
        db['tasks'] = []
    save(db)
def register(fullname, username, email, password):
    ensure_database()
    db = load()
    for user in db['users']:
        if user['username'] == username:
            raise exceptions.UsernameExists('Username already exists.')
        if user['email'] == email:
            raise exceptions.EmailExists('Email already exists.')
    db['users'].append(
        {
            'fullname': fullname,
            'username': username,
            'email': email,
            'admin': False,
            'password': password,
        }
    )
    while True:
        key = generate()
        for session in db['sessions']:
            if session['auth'] == key:
                continue
        db['sessions'].append(
            {
                'username': username,
                'auth': key,
            }
        )
        break
    save(db)
    return [key, {'fullname': fullname,'username': username,'email': email}]
def login(username, password):
    ensure_database()
    db = load()
    target = None
    for user in db['users']:
        if user['username'] == username:
            target = user
            break
    if target == None:
        raise exceptions.NotFound('Username doesn\'t exists.')
    if target['password'] != password:
        raise exceptions.WrongPassword('Passwords doesn\'t match.')
    while True:
        key = generate()
        for session in db['sessions']:
            if session['auth'] == key:
                continue
        db['sessions'].append(
            {
                'username': username,
                'auth': key,
            }
        )
        break
    save(db)
    return [key, {'fullname': target['fullname'],'username': target['username'],'email': target['email']}]
def forget(username, email, password):
    ensure_database()
    db = load()
    target = None
    for user in db['users']:
        if user['username'] == username and user['email'] == email:
            target = user
            break
    if target == None:
        raise exceptions.NotFound('User doesn\'t exists or username doesn\'t match with email.')
    for user in db['users']:
        if user['username'] == username and user['email'] == email:
            user['password'] == password
            break
    while True:
        key = generate()
        for session in db['sessions']:
            if session['auth'] == key:
                continue
        db['sessions'].append(
            {
                'username': username,
                'auth': key,
            }
        )
        break
    save(db)
    return [key, {'fullname': target['fullname'],'username': target['username'],'email': target['email']}]
def me(auth):
    ensure_database()
    db = load()
    session_flag = None
    for session in db['sessions']:
        if session['auth'] == auth:
            session_flag = session
    if session_flag == None:
        raise exceptions.NotFound('Session doesn\'t exists.')
    for user in db['users']:
        if user['username'] == session_flag['username']:
            return {'fullname': user['fullname'],'username': user['username'],'email': user['email']}
class tasks:
    def all(auth):
        ensure_database()
        db = load()
        session_flag = None
        for session in db['sessions']:
            if session['auth'] == auth:
                session_flag = session
        if session_flag == None:
            raise exceptions.NotFound('Session doesn\'t exists.')
        out = []
        for task in db['tasks']:
            if task['owner']['username'] == session_flag['username']:
                out.append(task)
        return out
    def add(auth, title, body, priority, date):
        ensure_database()
        db = load()
        session_flag = None
        user_flag = None
        for session in db['sessions']:
            if session['auth'] == auth:
                session_flag = session
                break
        if session_flag == None:
            raise exceptions.NotFound('Session doesn\'t exists.')
        for user in db['users']:
            if session_flag['username'] == user['username']:
                user_flag = user
                break
        if user_flag == None:
            raise exceptions.NotFound('User doesn\'t exists.')
        while True:
            key = generate()
            for task in db['tasks']:
                if task['id'] == key:
                    continue
            break
        TaskDict = {
            'id': key,
            'owner': {
                'fullname': user_flag['fullname'],
                'username': user_flag['username'],
                'email': user_flag['email'],
            },
            'title': str(title),
            'body': str(body),
            'priority': str(priority),
            'pending': True,
            'date': float(date),
            'created': time.time(),
            'edited': time.time(),
        }
        db['tasks'].append(TaskDict)
        save(db)
        return TaskDict
    def update(auth, id, title, body, priority, pending, date):
        ensure_database()
        db = load()
        session_flag = None
        for session in db['sessions']:
            if session['auth'] == auth:
                session_flag = session
        if session_flag == None:
            raise exceptions.NotFound('Session doesn\'t exists.')
        task_flag = None
        for task in db['tasks']:
            if task['owner']['username'] == session_flag['username']:
                session_flag = session
        if session_flag == None:
            raise exceptions.NotFound('Task doesn\'t exists or it\'s not yours.')
        for task in db['tasks']:
            if task['id'] == id:
                task['title'] = str(title)
                task['body'] = str(body)
                task['priority'] = str(priority)
                task['pending'] = bool(pending)
                task['date'] = float(date)
                task['edited'] = time.time()
        save(db)
        for task in db['tasks']:
            if task['id'] == id:
                return task
    def delete(auth, id):
        ensure_database()
        db = load()
        session_flag = None
        for session in db['sessions']:
            if session['auth'] == auth:
                session_flag = session
        if session_flag == None:
            raise exceptions.NotFound('Session doesn\'t exists.')
        task_flag = None
        for task in db['tasks']:
            if task['owner']['username'] == session_flag['username']:
                session_flag = session
        if session_flag == None:
            raise exceptions.NotFound('Task doesn\'t exists or it\'s not yours.')
        for task in db['tasks']:
            if task['id'] == id:
                db['tasks'].remove(task)
        save(db)
        return True
        
if __name__=='__main__':
    reset()
    print('register')
    r = register('Rahman Sharifi','rahmansharifi','sharifi.rahman.4651@gmail.com','password')
    print(r)
    input('')
    print('login')
    l = login('rahmansharifi','password')
    print(l)
    input('')
    print('forget')
    f = forget('rahmansharifi','sharifi.rahman.4651@gmail.com','password00')
    print(f)
    input('')
    print('tasks::all')
    tl = tasks.all(f[0])
    print(tl)
    input('')
    print('tasks::add')
    ta = tasks.add(f[0], 'Test', 'This is just a test.', 'blue', time.time())
    print(ta)
    input('')
    print('tasks::update')
    tu = tasks.update(f[0], ta['id'], 'Test', 'This is just a test.', 'red', False, time.time())
    print(tu)
    input('')
    print('tasks::all')
    tl = tasks.all(f[0])
    print(tl)
    input('')
    print('tasks::delete')
    td = tasks.delete(f[0], ta['id'])
    print(td)
    input('')