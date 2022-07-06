import json
import snippets
from snippets import Found, NotFound, EmailExists, UsernameExists, WrongPassword
from flask import Flask, request, Response

app = Flask(__name__)

def response(http, out):
    res = Response(json.dumps(out), status=http)
    res.headers['Content-Type'] = 'application/json'
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = '*'
    res.headers['Access-Control-Allow-Headers'] = '*'
    return res

@app.route('/')
def default():
    return response(200, dict(
        http=200,
        name=dict(
            first='Rahman',
            last='Sharifi',
            full='Rahman Sharifi'
        ),
        web='rahmansharifi.ir',
        email='sharifi.rahman.4651@gmail.com',
    ))

@app.route('/erase')
def erase():
    os.remove('app.json')
    return response(200, dict(
        http=200
    ))

@app.route('/register', methods=['POST'])
def register():
    params = request.form.to_dict()
    try:
        fullname = params['fullname']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (fullname, username, email, password)',
            exception='fullname is not provided.'
        ))
    try:
        username = params['username']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (fullname, username, email, password)',
            exception='username is not provided.'
        ))
    try:
        email = params['email']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (fullname, username, email, password)',
            exception='email is not provided.'
        ))
    try:
        password = params['password']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (fullname, username, email, password)',
            exception='password is not provided.'
        ))
    try:
        action = snippets.register(fullname, username, email, password)
    except UsernameExists:
        return response(400, dict(
            http=400,
            message='A user already signed up with this username.',
            exception='Username already exists.'
        ))
    except EmailExists:
        return response(400, dict(
            http=400,
            message='A user already signed up with this email.',
            exception='Email already exists.'
        ))
    except Exception as e:
        return response(400, dict(
            http=400,
            message='An unknown exception occured.',
            exception=str(e)
        ))
    return response(201, dict(
        http=201,
        auth=action[0],
        user=action[1],
    ))

@app.route('/login', methods=['POST'])
def login():
    params = request.form.to_dict()
    try:
        username = params['username']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (fullname, username, email, password)',
            exception='username is not provided.'
        ))
    try:
        password = params['password']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (fullname, username, email, password)',
            exception='password is not provided.'
        ))
    try:
        action = snippets.login(username, password)
    except NotFound:
        return response(404, dict(
            http=404,
            message='Couldn\'t find any user with this username.',
            exception=str(e),
        ))
    except WrongPassword:
        return response(400, dict(
            http=400,
            message='Password doesn\'t match with the account you specified.',
            exception=str(e)
        ))
    except Exception as e:
        return response(400, dict(
            http=400,
            message='An unknown exception occured.',
            exception=str(e)
        ))
    return response(202, dict(
        http=202,
        auth=action[0],
        user=action[1],
    ))

@app.route('/forget', methods=['POST'])
def forget():
    params = request.form.to_dict()
    try:
        username = params['username']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (fullname, username, email, password)',
            exception='username is not provided.'
        ))
    try:
        email = params['email']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (fullname, username, email, password)',
            exception='email is not provided.'
        ))
    try:
        password = params['password']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (fullname, username, email, password)',
            exception='password is not provided.'
        ))
    try:
        action = snippets.forget(username, email, password)
    except NotFound:
        return response(404, dict(
            http=404,
            message=str(e),
            exception=str(e)
        ))
    except Exception as e:
        return response(400, dict(
            http=400,
            message='An unknown exception occured.',
            exception=str(e)
        ))
    return response(200, dict(
        http=200,
        auth=action[0],
        user=action[1],
    ))

@app.route('/me',methods=['GET'])
def me():
    headers = request.headers.to_wsgi_list()
    auth = None
    for header in headers:
        if header[0] == 'Authorization':
            auth = header[1].split()[1]
            break
    if auth == None:
        return response(400, dict(
            http=400,
            message='Please provide authorization header.',
            exception='Authorization header is not set',
        ))
    try:
        action = snippets.me(auth)
    except NotFound as e:
        return response(404, dict(
            http=404,
            message=str(e),
            exception=str(e),
        ))
    except Exception as e:
        return response(400, dict(
            http=400,
            message='An unknown exception occured.',
            exception=str(e),
        ))
    return response(200, dict(
        http=200,
        user=action,
    ))

@app.route('/tasks/all', methods=['GET'])
def all_tasks():
    headers = request.headers.to_wsgi_list()
    auth = None
    for header in headers:
        if header[0] == 'Authorization':
            auth = header[1].split()[1]
            break
    if auth == None:
        return response(400, dict(
            http=400,
            message='Please provide authorization header.',
            exception='Authorization header is not set',
        ))
    try:
        action = snippets.tasks.all(auth)
    except NotFound as e:
        return response(404, dict(
            http=404,
            message=str(e),
            exception=str(e),
        ))
    except Exception as e:
        return response(400, dict(
            http=400,
            message='An unknown exception occured.',
            exception=str(e),
        ))
    return response(200, dict(
        http=200,
        tasks=action,
    ))

@app.route('/tasks/add', methods=['POST'])
def add_task():
    params = request.form.to_dict()
    try:
        title = params['title']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (title, body, priority, date)',
            exception='title is not provided.'
        ))
    try:
        body = params['body']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (title, body, priority, date)',
            exception='body is not provided.'
        ))
    try:
        priority = params['priority']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (title, body, priority, date)',
            exception='priority is not provided.'
        ))
    try:
        date = params['date']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (title, body, priority, date)',
            exception='date is not provided.'
        ))
    headers = request.headers.to_wsgi_list()
    auth = None
    for header in headers:
        if header[0] == 'Authorization':
            auth = header[1].split()[1]
            break
    if auth == None:
        return response(400, dict(
            http=400,
            message='Please provide authorization header.',
            exception='Authorization header is not set',
        ))
    try:
        action = snippets.tasks.add(auth, title, body, priority, date)
    except NotFound as e:
        return response(404, dict(
            http=404,
            message=str(e),
            exception=str(e),
        ))
    except Exception as e:
        return response(400, dict(
            http=400,
            message='An unknown exception occured.',
            exception=str(e),
        ))
    return response(200, dict(
        http=200,
        task=action,
    ))

@app.route('/tasks/<id>', methods=['PATCH'])
def update_task(id):
    params = request.form.to_dict()
    try:
        title = params['title']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (title, body, priority, pending, date)',
            exception='title is not provided.'
        ))
    try:
        body = params['body']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (title, body, priority, pending, date)',
            exception='body is not provided.'
        ))
    try:
        priority = params['priority']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (title, body, priority, pending, date)',
            exception='priority is not provided.'
        ))
    try:
        pending = params['pending']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (title, body, priority, pending, date)',
            exception='pending is not provided.'
        ))
    try:
        date = params['date']
    except KeyError:
        return response(400, dict(
            http=400,
            message='Please provide all necessary data. (title, body, priority, pending, date)',
            exception='date is not provided.'
        ))
    headers = request.headers.to_wsgi_list()
    auth = None
    for header in headers:
        if header[0] == 'Authorization':
            auth = header[1].split()[1]
            break
    if auth == None:
        return response(400, dict(
            http=400,
            message='Please provide authorization header.',
            exception='Authorization header is not set',
        ))
    try:
        action = snippets.tasks.update(auth, id, title, body, priority, pending, date)
    except NotFound as e:
        return response(404, dict(
            http=404,
            message=str(e),
            exception=str(e),
        ))
    except Exception as e:
        return response(400, dict(
            http=400,
            message='An unknown exception occured.',
            exception=str(e),
        ))
    return response(200, dict(
        http=200,
        task=action,
    ))

@app.route('/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    params = request.form.to_dict()
    headers = request.headers.to_wsgi_list()
    auth = None
    for header in headers:
        if header[0] == 'Authorization':
            auth = header[1].split()[1]
            break
    if auth == None:
        return response(400, dict(
            http=400,
            message='Please provide authorization header.',
            exception='Authorization header is not set',
        ))
    try:
        action = snippets.tasks.delete(auth, id)
    except NotFound as e:
        return response(404, dict(
            http=404,
            message=str(e),
            exception=str(e),
        ))
    except Exception as e:
        return response(400, dict(
            http=400,
            message='An unknown exception occured.',
            exception=str(e),
        ))
    return response(200, dict(
        http=200
    ))

if __name__=='__main__':
    app.run()