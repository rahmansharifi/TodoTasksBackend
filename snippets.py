import time
from fb import firebase

base = firebase('sdk.json', 'https://events-2fa90-default-rtdb.firebaseio.com')

def signup(name, email, password):
    users = base.read('/users')
    users = {} if users == None else users
    for key, value in users.items():
        if value['email'] == email.lower():
            raise Exception('already-exists')
    data = {
        'name': name,
        'email': email.lower(),
        'admin': False,
        'password': password,
        'created': int(time.time()),
    }
    p = base.push('/users', data)
    return p.key

def login(email, password):
    users = base.read('/users')
    if base.read('/users') == None:
        raise Exception('empty-table')
    for key, value in users.items():
        if value['email'] == email.lower():
            if value['password'] == password:
                return key
            else:
                raise Exception('wrong-password')
    raise Exception('not-found')

def me(key):
    user = base.read('/users/'+key)
    if user == None:
        raise Exception('not-found')
    return user

def get_users(key):
    user = base.read('/users/'+key)
    if user == None:
        raise Exception('user-not-found')
    if not user['admin']:
        raise Exception('unauthorized')
    users = base.read('/users')
    users = {} if users == None else users
    return users

def get_events(key):
    user = base.read('/users/'+key)
    if user == None:
        raise Exception('user-not-found')
    events = base.read('/events')
    events = {} if events == None else events
    out = {}
    for key, value in events.items():
        if value['owner'] == user['email']:
            out.update({key:value})
    return out

def get_event(key, id):
    user = base.read('/users/'+key)
    if user == None:
        raise Exception('user-not-found')
    email = user['email']
    event = base.read('/events/'+id)
    if event == None:
        raise Exception('not-found')
    if user['email'] != event['owner']:
        raise Exception('unauthorized')
    return event

def add_event(key, title, body, priority):
    user = base.read('/users/'+key)
    if user == None:
        raise Exception('user-not-found')
    event = {
        'title': title,
        'body': body,
        'priority': priority,
        'owner': user['email'],
        'created': int(time.time()),
        'edited': int(time.time()),
    }
    p = base.push('/events', event)
    return p.key

def update_event(key, id, title=None, body=None, priority=None):
    user = base.read('/users/'+key)
    if user == None:
        raise Exception('user-not-found')
    event = base.read('/events/'+id)
    if user['email'] != event['owner']:
        raise Exception('unauthorized')
    changes = {}
    if title != None:
        changes.update({'title':title})
    if body != None:
        changes.update({'body':body})
    if priority != None:
        changes.update({'priority':priority})
    changes.update({'edited':int(time.time())})
    base.update('/events/'+id, changes)

def delete_event(key, id):
    user = base.read('/users/'+key)
    if user == None:
        raise Exception('user-not-found')
    event = base.read('/events/'+id)
    if user['email'] != event['owner']:
        raise Exception('unauthorized')
    base.delete('/events/'+id)

if __name__=='__main__':

    base.delete('/users')
    base.delete('/events')

    print(base.read('/users'))
    print('>>> users\n\n')

    s = signup('Rahman Sharifi', 'sharifi.rahman.4651@gmail.com', 'password00')
    print(s)
    print('>>> signup\n\n')

    print(base.read('/users'))
    print('>>> users\n\n')

    l = login('sharifi.rahman.4651@gmail.com', 'password00')
    print(l)
    print('>>> login\n\n')

    m = me(s)
    print(m)
    print('>>> me\n\n')

    g = get_events(s)
    print(g)
    print('>>> all events\n\n')

    a = add_event(s, 'New', 'This is a test.', 'red')
    print(a)
    print('>>> add event\n\n')

    e = get_events(s)
    print(e)
    print('>>> all events\n\n')

    u = update_event(s, a, title='Old')
    print('>>> update event\n\n')

    d = get_events(s)
    print(d)
    print('>>> all events\n\n')

    delete_event(s, a)
    print('>>> delete event\n\n')

    print(get_events(s))
    print('>>> all events\n\n')
