"""Private metadata API: bound to loopback, intentionally over-trusting local callers."""
from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def index():
    return jsonify({
        "service": "Editorial API",
        "version": "v1",
        "links": [
            "/api/latest/metadata",
            "/api/latest/metadata/messages/authors",
        ],
    })

@app.get("/api/latest/metadata")
def metadata():
    return jsonify({
        "service": "editorial",
        "routes": [
            "/api/latest/metadata/messages/authors",
            "/api/latest/metadata/messages/maintenance",
        ],
    })

@app.get("/api/latest/metadata/messages/authors")
def messages_authors():
    # Deliberately historically weak onboarding practice, not an authentication API.
    return jsonify({
        "messages": [{
            "subject": "New author access",
            "body": "Hello. Your content operations account is dev. Temporary password: dev080217_devAPI!@. Please use the SSH host for editorial tools.",
        }]
    })

@app.get("/api/latest/metadata/messages/maintenance")
def messages_maintenance():
    return jsonify({"messages": [{"subject": "API migration", "body": "Old deployment notes were removed from the current repository snapshot."}]})
