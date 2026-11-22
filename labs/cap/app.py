#!/usr/bin/python3.8
"""Cap-style dashboard reconstructed from public retired-machine evidence.

The original Flask app.py is not publicly released. The observed behavior is
preserved: live tcpdump capture under temporary UID 0, sequential PCAP IDs,
and unauthenticated /data/<id> and /download/<id> references (IDOR).
"""
import glob
import os
import re
import subprocess
import threading

from flask import Flask, abort, redirect, render_template, request, send_file, url_for

app = Flask(__name__)
app.secret_key = "cap-training-dashboard"
PCAP_DIR = "/pcaps"
APP_UID = 1000
capture_lock = threading.Lock()
os.makedirs(PCAP_DIR, exist_ok=True)


def capture_ids():
    values = []
    for path in glob.glob(os.path.join(PCAP_DIR, "*.pcap")):
        name = os.path.splitext(os.path.basename(path))[0]
        if name.isdigit():
            values.append(int(name))
    return values


def packet_summary(path):
    try:
        result = subprocess.run(
            ["tcpdump", "-nn", "-r", path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=8, check=False
        )
        lines = [line for line in result.stdout.splitlines() if " > " in line]
    except Exception:
        lines = []
    return {
        "total": len(lines),
        "ip": sum(1 for line in lines if line.startswith("IP ")),
        "tcp": sum(1 for line in lines if "Flags [" in line),
        "udp": sum(1 for line in lines if "UDP" in line),
    }


@app.route("/")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/ip")
def ip_config():
    try:
        output = subprocess.check_output(["ifconfig"], stderr=subprocess.STDOUT, text=True)
    except Exception as exc:
        output = str(exc)
    return render_template("command.html", title="IP Config", output=output)


@app.route("/netstat")
def network_status():
    try:
        output = subprocess.check_output(["netstat", "-an"], stderr=subprocess.STDOUT, text=True)
    except Exception as exc:
        output = str(exc)
    return render_template("command.html", title="Network Status", output=output)


@app.route("/capture")
def capture():
    # The observed app temporarily changes to UID 0 to run tcpdump, then drops
    # back to nathan (UID 1000). Python's file capability enables this transition.
    os.setuid(0)
    try:
        with capture_lock:
            pcap_id = max(capture_ids(), default=-1) + 1
            outfile = os.path.join(PCAP_DIR, str(pcap_id) + ".pcap")
        remote_ip = re.sub(r"[^0-9a-fA-F:.]", "", str(request.remote_addr or "127.0.0.1"))
        command = "timeout 5 tcpdump -w " + outfile + " -i any host " + remote_ip
        os.system(command)
    finally:
        os.setuid(APP_UID)
    return redirect(url_for("data", capture_id=pcap_id))


@app.route("/data/<int:capture_id>")
def data(capture_id):
    # Intentional IDOR: no ownership or session check for capture_id.
    path = os.path.join(PCAP_DIR, str(capture_id) + ".pcap")
    if not os.path.isfile(path):
        abort(404)
    return render_template("data.html", capture_id=capture_id, stats=packet_summary(path))


@app.route("/download/<int:capture_id>")
def download(capture_id):
    # Intentional IDOR: any visitor can download another user's PCAP.
    path = os.path.join(PCAP_DIR, str(capture_id) + ".pcap")
    if not os.path.isfile(path):
        abort(404)
    return send_file(path, as_attachment=True, download_name=str(capture_id) + ".pcap")
