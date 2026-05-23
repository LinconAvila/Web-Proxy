import socket
import threading

PROXY_HOST = "0.0.0.0"
PROXY_PORT = 8080 

def _relay(src: socket.socket, dst: socket.socket) -> None:
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        src.close()
        dst.close()


def _handle_client(client: socket.socket) -> None:
    try:
        request = client.recv(4096).decode(errors="ignore")
        first_line = request.splitlines()[0]

        if not first_line.startswith("CONNECT"):
            client.close()
            return

        _, host_port, _ = first_line.split(" ")
        host, port = host_port.rsplit(":", 1)
        port = int(port)

        remote = socket.create_connection((host, port), timeout=10)

        client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

        t1 = threading.Thread(target=_relay, args=(client, remote), daemon=True)
        t2 = threading.Thread(target=_relay, args=(remote, client), daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    except Exception as e:
        print(f"[tunnel] error: {e}")
        client.close()


def start_tunnel_server() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((PROXY_HOST, PROXY_PORT))
    server.listen(100)
    print(f"[tunnel] listening on {PROXY_HOST}:{PROXY_PORT}")

    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=_handle_client, args=(client,), daemon=True)
        thread.start()