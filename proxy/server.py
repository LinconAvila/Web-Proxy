import requests
from flask import Flask, Response, render_template
from urllib.parse import urlparse

from proxy.blocker import is_blocked
from proxy.filter import filter_content
from proxy.logger import log_access


def create_app():
    app = Flask(__name__, template_folder="../templates")

    @app.route("/<path:url>")
    def proxy(url):
        url = url if url.startswith("http") else f"http://{url}"

        if is_blocked(url):
            log_access(url, "blocked")
            domain = urlparse(url).netloc
            return render_template("blocked.html", dominio=domain), 403

        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException as exc:
            return f"Error reaching the site: {exc}", 502

        filtered_html, was_filtered = filter_content(response.text)

        action = "filtered" if was_filtered else "allowed"
        log_access(url, action)

        return Response(
            filtered_html,
            status=response.status_code,
            content_type=response.headers.get("Content-Type", "text/html")
        )

    return app