import threading
from proxy.server import create_app
from proxy.tunnel import start_tunnel_server

app = create_app()

if __name__ == "__main__":
    t = threading.Thread(target=start_tunnel_server, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)
