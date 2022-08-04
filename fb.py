import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import time


class firebase:
    def __init__(self, cred, database):
        firebase_admin.initialize_app(credentials.Certificate(cred),{'databaseURL':database})
    def reference(self, path):
        return db.reference(path)
    def read(self, path):
        return self.reference(path).get()
    def push(self, path, content):
        return self.reference(path).push(content)
    def update(self, path, content):
        return self.reference('/').child(path[1::] if path.startswith('/') else path).update(content)
    def delete(self, path):
        return self.reference('/').child(path[1::] if path.startswith('/') else path).set({})

if __name__=='__main__':
    # Firebase
    base = firebase('sdk.json','https://events-2fa90-default-rtdb.firebaseio.com')

    # Read
    print(base.read('/users'))

    # Push
    for i in range(3):
        base.push('/users',dict(name='Rahman',email='example@to.invalid',password='123456'))
    
    # Read
    l = base.read('/users')
    print(l)

    # Update
    base.update('/users/'+list(l.keys())[-1], {'password': '654321'})
    
    # Read
    print(base.read('/users'))

    # Delete
    base.delete('/users/'+list(l.keys())[-1])

    # Read
    print(base.read('/users'))