import http.cookiejar
import io
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as lab


class CredentialGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.TemporaryDirectory()
        root = Path(cls.work.name)
        cls.expected_flag = "TTP{test_only_credential_gate}"
        (root / "flag.txt").write_text(cls.expected_flag + "\n", encoding="utf-8")
        lab.DB_PATH = root / "operations.sqlite3"
        lab.FLAG_PATH = root / "flag.txt"
        lab.initialize()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), lab.Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)
        cls.work.cleanup()
        with lab.SESSIONS_LOCK:
            lab.SESSIONS.clear()

    def client(self):
        jar = http.cookiejar.CookieJar()
        return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    def get(self, opener, route):
        try:
            resp = opener.open(f"http://127.0.0.1:{self.port}{route}", timeout=3)
            return resp.status, resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8")

    def login(self, opener, username, password="nonsense"):
        data = urllib.parse.urlencode({"username": username, "password": password}).encode()
        try:
            resp = opener.open(f"http://127.0.0.1:{self.port}/login", data=data, timeout=3)
            return resp.status, resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8")

    def test_healthcheck(self):
        status, body = self.get(self.client(), "/healthz")
        self.assertEqual(status, 200)
        self.assertIn('"status": "ok"', body)

    def test_wrong_password_rejected(self):
        client = self.client()
        status, body = self.login(client, "admin", "wrong-password")
        self.assertEqual(status, 401)
        self.assertIn("not accepted", body)
        status, body = self.get(client, "/dashboard")
        self.assertIn("Operator sign in", body)
        self.assertNotIn("Recent dispatches", body)

    def test_unauthenticated_export_redirects(self):
        client = self.client()
        status, body = self.get(client, "/reports/export.csv")
        self.assertEqual(status, 200)  # followed redirect to login
        self.assertIn("Operator sign in", body)
        self.assertNotIn(self.expected_flag, body)

    def test_real_sql_injection_bypasses_auth(self):
        client = self.client()
        status, body = self.login(client, "admin'-- ")
        self.assertEqual(status, 200)
        self.assertIn("Operations overview", body)
        status, body = self.get(client, "/reports")
        self.assertEqual(status, 200)
        self.assertIn("Audit reports", body)
        status, body = self.get(client, "/reports/export.csv")
        self.assertEqual(status, 200)
        self.assertIn("verification_marker", body)
        self.assertIn(self.expected_flag, body)

    def test_sql_error_does_not_leak_query(self):
        status, body = self.login(self.client(), "admin' UNION SELECT blah")
        self.assertEqual(status, 401)
        self.assertNotIn("sqlite3", body)
        self.assertNotIn("SELECT id, username", body)

    def test_cannot_forge_admin_session_by_cookie(self):
        client = urllib.request.build_opener()
        request = urllib.request.Request(f"http://127.0.0.1:{self.port}/reports", headers={"Cookie": "sid=admin"})
        response = client.open(request, timeout=3)
        self.assertEqual(response.geturl().split("/")[-1], "login")


if __name__ == "__main__":
    unittest.main()
