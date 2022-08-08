import time
import json
import snippets
from flask import Flask, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def response(out):
    res = Response(json.dumps(out),200)
    res.headers['Content-Type'] = 'application/json'
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = '*'
    res.headers['Access-Control-Allow-Headers'] = '*'
    return res

@app.route('/')
def default():
    return response(dict(
        http=200,
        name=dict(
            first='Rahman',
            last='Sharifi',
            full='Rahman Sharifi',
            web='rahmansharifi.ir',
        )
    ))

@app.route('/signup', methods=['POST'])
def signup():
    params = request.json
    try:
        name = params['name']
        email = params['email']
        password = params['password']
    except KeyError as e:
        return response(dict(
            http=400,
            exception=f'<{str(e)[1:-1:1]}> is not provided.'
        ))
    try:
        secret = snippets.signup(name, email, password)
    except Exception as e:
        if str(e) == 'already-exists':
            return response(dict(
                http=400,
                exception='<email> already exists.'
            ))
    return response(dict(
        http=201,
        auth=secret,
    ))

@app.route('/login', methods=['POST'])
def login():
    params = request.json
    try:
        email = params['email']
        password = params['password']
    except KeyError as e:
        return response(dict(
            http=400,
            exception=f'<{str(e)[1:-1:1]}> is not provided.'
        ))
    try:
        secret = snippets.login(email, password)
    except Exception as e:
        if str(e) == 'not-found':
            return response(dict(
                http=400,
                exception='<email> not registered.'
            ))
        elif str(e) == 'empty-table':
            return response(dict(
                http=400,
                exception='<email> not registered.'
            ))
        elif str(e) == 'wrong-password':
            return response(dict(
                http=400,
                exception='<password> is wrong.'
            ))
    return response(dict(
        http=200,
        auth=secret,
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
        return response(dict(
            http=400,
            exception='<Authorization> header is missing.',
        ))
    try:
        action = snippets.me(auth)
    except Exception as e:
        if str(e) == 'not-found':
            return response(dict(
                http=400,
                exception='<session> is invalid.',
            ))
    return response(dict(
        http=200,
        user={
            'name': action['name'],
            'email': action['email'],
            'admin': action['admin'],
            'created': int(action['created']),
        },
    ))

@app.route('/users', methods=['GET'])
def all_users():
    headers = request.headers.to_wsgi_list()
    auth = None
    for header in headers:
        if header[0] == 'Authorization':
            auth = header[1].split()[1]
            break
    if auth == None:
        return response(dict(
            http=400,
            exception='<Authorization> header is missing.',
        ))
    try:
        action = snippets.get_users(auth)
    except Exception as e:
        if str(e) == 'user-not-found':
            return response(dict(
                http=404,
                exception='<session> is invalid.',
            ))
        elif str(e) == 'unauthorized':
            return response(dict(
                http=404,
                exception='Unauthorized',
            ))
    return response(dict(
        http=200,
        users=action,
    ))

@app.route('/events/', methods=['GET'])
def all_events():
    headers = request.headers.to_wsgi_list()
    auth = None
    for header in headers:
        if header[0] == 'Authorization':
            auth = header[1].split()[1]
            break
    if auth == None:
        return response(dict(
            http=400,
            exception='<Authorization> header is missing.',
        ))
    try:
        action = snippets.get_events(auth)
    except Exception as e:
        if str(e) == 'user-not-found':
            return response(dict(
                http=404,
                exception='<session> is invalid.',
            ))
    return response(dict(
        http=200,
        events=action,
    ))

@app.route('/events/', methods=['POST'])
def add_event():
    params = request.json
    try:
        body = params['body']
        priority = params['priority']
        title = params['title']
    except Exception as e:
        return response(dict(
            http=400,
            exception=f'<{str(e)[1:-1:1]}> is not provided.'
        ))
    if not priority.lower() in ['hot','normal','cold']:
        return response(dict(
            http=400,
            exception='<priority> type is invalid. [hot, normal, cold]'
        ))
    headers = request.headers.to_wsgi_list()
    auth = None
    for header in headers:
        if header[0] == 'Authorization':
            auth = header[1].split()[1]
            break
    if auth == None:
        return response(dict(
            http=400,
            exception='<Authorization> header is missing.',
        ))
    try:
        action = snippets.add_event(auth, title, body, priority)
    except Exception as e:
        if str(e) == 'user-not-found':
            return response(dict(
                http=404,
                exception='<session> is invalid.',
            ))
    return response(dict(
        http=200,
        event=action,
    ))

@app.route('/events/<event>', methods=['PATCH'])
def update_event(event):
    params = request.json
    try:
        title = params['title']
    except KeyError:
        title = None
    try:
        body = params['body']
    except KeyError:
        body = None
    try:
        priority = params['priority'].lower()
    except KeyError:
        priority = None
    if priority != None:
        if priority in ['hot','normal','cold']:
            pass
        else:
            return response(dict(
                http=400,
                exception='<priority> is invalid. [hot, normal, cold]'
            ))
    headers = request.headers.to_wsgi_list()
    auth = None
    for header in headers:
        if header[0] == 'Authorization':
            auth = header[1].split()[1]
            break
    if auth == None:
        return response(dict(
            http=400,
            exception='<Authorization> header is missing.',
        ))
    try:
        action = snippets.update_event(auth, event, title, body, priority)
    except Exception as e:
        if str(e) == 'user-not-found':
            return response(dict(
                http=404,
                exception='<session> is invalid.',
            ))
        elif str(e) == 'unauthorized':
            return response(dict(
                http=403,
                exception='<event> is not yours.',
            ))
    return response(dict(
        http=200,
        event=event,
    ))

@app.route('/events/<id>', methods=['DELETE'])
def delete_event(id):
    headers = request.headers.to_wsgi_list()
    auth = None
    for header in headers:
        if header[0] == 'Authorization':
            auth = header[1].split()[1]
            break
    if auth == None:
        return response(dict(
            http=400,
            exception='<Authorization> header is missing.',
        ))
    try:
        action = snippets.delete_event(auth, id)
    except Exception as e:
        if str(e) == 'user-not-found':
            return response(dict(
                http=400,
                exception='<session> is invalid.',
            ))
        elif str(e) == 'unauthorized':
            return response(dict(
                http=403,
                exception='<event> is not yours.',
            ))
    return response(dict(
        http=200
    ))

if __name__=='__main__':
    app.run()
