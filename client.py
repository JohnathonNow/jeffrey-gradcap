#!/usr/bin/env python3
import requests
import json

def read(v):
    r = requests.get('http://gradcap.us/read?v={}'.format(v))
    p = json.loads(r.text)
    if p['status'] == 'success':
        if v < p['payload']['v']:
            print(p['payload']['colors'])
        v = p['payload']['v'];
    return v

if __name__ == '__main__':
    v = 0;
    v = read(v)
