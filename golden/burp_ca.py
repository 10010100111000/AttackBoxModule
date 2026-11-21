"""Initialize a shared lab CA using Burp itself and verify browser trust."""
from contextlib import contextmanager
import hashlib
import http.client
import http.server
import json
import os
from pathlib import Path
import signal
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import xml.etree.ElementTree as ET

JAR = Path('/usr/share/burpsuite/burpsuite_community.jar')
USER_CONFIG = Path('/usr/share/attackbox/burp-user-config.json')
PUBLIC_CA = Path('/usr/share/attackbox/burp-ca.der')
HOME_CA = Path('.local/share/attackbox/burp-ca.der')
PAGE_TITLE = 'AttackBox Chromium OK'


def stop(process):
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()


@contextmanager
def proxy(home, initialize=False):
    # Never silently connect to an unrelated proxy already using this port.
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        probe.bind(('127.0.0.1', 8080))
    arguments = ['/usr/bin/java', '-Djava.awt.headless=true', f'-Duser.home={home}',
                 f'-Djava.util.prefs.userRoot={home}', '-jar', str(JAR),
                 '--disable-auto-update', f'--user-config-file={USER_CONFIG}']
    if initialize:
        arguments.append('--use-defaults')
    home.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, HOME=str(home), XDG_CACHE_HOME=str(home / '.cache'))
    with tempfile.TemporaryFile() as log:
        process = subprocess.Popen(arguments, stdin=subprocess.PIPE, stdout=log,
                                   stderr=subprocess.STDOUT, start_new_session=True, env=environment)
        try:
            # The owner explicitly authorizes license acceptance for CI builds.
            process.stdin.write(b'y\n' if initialize else b'')
            process.stdin.close()
            client = urllib.request.build_opener(urllib.request.ProxyHandler(
                {'http': 'http://127.0.0.1:8080'}))
            deadline = time.monotonic() + 90
            last_error = ''
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError('Burp exited before its proxy became ready')
                try:
                    with client.open('http://burp/cert', timeout=2) as response:
                        certificate = response.read(1024 * 1024)
                    # Reject proxy error pages before trusting the response.
                    subprocess.run(['openssl', 'x509', '-inform', 'DER', '-noout'],
                                   input=certificate, check=True, capture_output=True)
                    break
                except (OSError, ValueError, subprocess.CalledProcessError) as error:
                    last_error = str(error)
                    time.sleep(0.25)
            else:
                raise RuntimeError(f'Burp proxy startup timed out: {last_error}')
            yield certificate
        except Exception:
            log.seek(max(0, log.seek(0, 2) - 4096))
            print(log.read().decode(errors='replace'), file=sys.stderr)
            raise
        finally:
            stop(process)


def retain_seed_preferences(home):
    """Keep the actual CA and accepted terms; discard build-device identities."""
    directory = home / '.java/.userPrefs/burp'
    prefs = directory / 'prefs.xml'
    root = ET.parse(prefs).getroot()
    entries = {entry.get('key'): entry for entry in root.findall('entry')}
    required = {'caCert', 'eulacommunity'}
    if not required <= entries.keys() or any(not entries[key].get('value') for key in required):
        raise RuntimeError('Burp did not persist its CA and accepted license')
    for entry in list(root):
        if entry.get('key') not in required | {'free.suite.feedbackReportingEnabled'}:
            root.remove(entry)
    prefs.write_text('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
                     '<!DOCTYPE map SYSTEM "http://java.sun.com/dtd/preferences.dtd">\n'
                     + ET.tostring(root, encoding='unicode') + '\n')
    prefs.chmod(0o600)
    # Other nodes contain window geometry and other initialization state.
    for child in directory.iterdir():
        if child.is_dir():
            shutil.rmtree(child)


def initialize(home):
    with proxy(home, initialize=True) as certificate:
        destination = home / HOME_CA
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(certificate)
    retain_seed_preferences(home)
    print('Burp generated and persisted shared CA:', hashlib.sha256(certificate).hexdigest())


@contextmanager
def https_fixture():
    class Page(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            body = (f'<!doctype html><title>Loading</title>'
                    f'<script>document.title="{PAGE_TITLE}"</script>').encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                        '-keyout', str(temp / 'key.pem'), '-out', str(temp / 'cert.pem'),
                        '-days', '1', '-subj', '/CN=localhost'], check=True, capture_output=True)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(temp / 'cert.pem', temp / 'key.pem')
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Page)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield server.server_port
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


def trusted_ca_context(certificate):
    # An explicit lab trust anchor, with signature and hostname verification.
    # create_default_context() also imports the OS roots and, on Python 3.13,
    # enables additional strict-profile checks not required by browser trust.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cadata=ssl.DER_cert_to_PEM_cert(certificate))
    return context


def verify_browser(home):
    expected = PUBLIC_CA.read_bytes()
    with proxy(home) as certificate, https_fixture() as port:
        if certificate != expected:
            raise RuntimeError('Restarted Burp is not using the golden shared CA')
        # Verify a real TLS handshake and response through Burp, without -k.
        context = trusted_ca_context(expected)
        connection = http.client.HTTPSConnection('127.0.0.1', 8080, timeout=15, context=context)
        try:
            connection.set_tunnel('localhost', port)
            connection.request('GET', '/')
            response = connection.getresponse()
            if response.status != 200 or PAGE_TITLE.encode() not in response.read():
                raise RuntimeError('HTTPS response through Burp did not match the fixture')
        finally:
            connection.close()
        with open('/var/log/attackbox-check/chromium.log', 'wb') as log:
            browser = subprocess.Popen([
                'chromium', '--no-first-run', '--no-default-browser-check',
                '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=0',
                '--user-data-dir=/tmp/chromium-check', '--proxy-server=http://127.0.0.1:8080',
                '--proxy-bypass-list=<-loopback>', f'https://localhost:{port}/'],
                stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                wait_browser(browser)
            finally:
                stop(browser)
    print('Burp restart, TLS interception, Chromium CA trust and extensions passed')


def wait_browser(browser):
    policy = json.loads(Path('/etc/chromium/policies/managed/attackbox.json').read_text())
    extensions = [item.split(';')[0] for item in policy['ExtensionInstallForcelist']]
    profile = Path('/tmp/chromium-check')
    client = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    deadline = time.monotonic() + 120
    last_error = ''
    observed_pages = []
    while time.monotonic() < deadline:
        if browser.poll() is not None:
            raise RuntimeError('Chromium exited before acceptance completed')
        try:
            port = int((profile / 'DevToolsActivePort').read_text().splitlines()[0])
            with client.open(f'http://127.0.0.1:{port}/json/list', timeout=2) as response:
                pages = json.load(response)
            observed_pages = [{key: page.get(key) for key in ('type', 'title', 'url')} for page in pages]
            if not any(page.get('title') == PAGE_TITLE for page in pages):
                raise RuntimeError('Chromium did not load the intercepted HTTPS page')
            if not all(any((profile / 'Default/Extensions' / item).glob('*/manifest.json'))
                       for item in extensions):
                raise RuntimeError('Required Chromium extensions are not installed')
            return
        except (OSError, ValueError, RuntimeError) as error:
            last_error = str(error)
            time.sleep(0.25)
    raise RuntimeError(f'Chromium acceptance timed out: {last_error}; pages={json.dumps(observed_pages)}')


if __name__ == '__main__':
    if os.geteuid() == 0:
        raise SystemExit('Run as the box user')
    if sys.argv[1:] == ['initialize']:
        initialize(Path.home())
    elif sys.argv[1:] == ['verify-browser']:
        verify_browser(Path.home())
    else:
        raise SystemExit('Usage: burp_ca.py initialize|verify-browser')
