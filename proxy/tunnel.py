import socket
import threading
import requests
from urllib.parse import urlparse

from proxy.blocker import is_blocked
from proxy.filter import filter_content
from proxy.logger import log_access

PROXY_HOST = "0.0.0.0"
PROXY_PORT = 8080

_BLOCKED_HTML = """\
HTTP/1.1 403 Forbidden\r\nContent-Type: text/html; charset=utf-8\r\n\r\n
<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Acesso Bloqueado</title>
<style>
  body {{ background:#2c3e50; display:flex; justify-content:center;
          align-items:center; height:100vh; margin:0;
          font-family:'Segoe UI',sans-serif; }}
  .box {{ background:#fff; padding:40px 50px; border-radius:12px;
          border-top:8px solid #e74c3c; text-align:center; max-width:500px; }}
  h1 {{ color:#e74c3c; }} .domain {{ background:#fce4e4; color:#c0392b;
  padding:8px 15px; border-radius:6px; font-weight:bold; font-size:18px; }}
  .footer {{ margin-top:20px; font-size:12px; color:#aaa; }}
</style></head>
<body><div class="box">
  <div style="font-size:64px">🔒</div>
  <div style="font-size:12px;color:#7f8c8d;letter-spacing:2px">WEB PROXY SERVER — SI2</div>
  <h1>Acesso Restrito</h1>
  <p>Este domínio está na lista de restrições do proxy.</p>
  <div class="domain">{domain}</div>
  <div class="footer">Sistemas para Internet 2 &bull; Controle de Conteúdo</div>
</div></body></html>
"""


def _relay(src: socket.socket, dst: socket.socket) -> None:
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except (ConnectionResetError, BrokenPipeError, OSError, TimeoutError):
        pass
    finally:
        for s in (src, dst):
            try:
                s.close()
            except OSError:
                pass


def _handle_connect(client: socket.socket, host: str, port: int) -> None:
    check_url = f"https://{host}:{port}"
    domain = host

    if is_blocked(check_url):
        log_access(check_url, "bloqueado")
        response = _BLOCKED_HTML.format(domain=domain).encode("utf-8")
        try:
            client.sendall(response)
        except OSError:
            pass
        finally:
            try:
                client.close()
            except OSError:
                pass
        return

    try:
        remote = socket.create_connection((host, port), timeout=10)
    except OSError as exc:
        error = f"HTTP/1.1 502 Bad Gateway\r\n\r\nErro ao conectar: {exc}"
        try:
            client.sendall(error.encode())
        except OSError:
            pass
        try:
            client.close()
        except OSError:
            pass
        return

    client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

    log_access(check_url, "permitido")

    t1 = threading.Thread(target=_relay, args=(client, remote), daemon=True)
    t2 = threading.Thread(target=_relay, args=(remote, client), daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


def _handle_http(client: socket.socket, raw_request: bytes) -> None:
    try:
        request_str = raw_request.decode(errors="ignore")
        first_line = request_str.splitlines()[0] 
        if len(parts) < 2:
            client.close()
            return

        url = parts[1]
        if not url.startswith("http"):
            url = f"http://{url}"

        if is_blocked(url):
            domain = urlparse(url).netloc
            log_access(url, "bloqueado")
            body = _BLOCKED_HTML.format(domain=domain).encode("utf-8")
            client.sendall(body)
            client.close()
            return

        headers = {}
        for line in request_str.splitlines()[1:]:
            if ":" in line:
                key, _, value = line.partition(":")
                if key.strip().lower() not in ("proxy-connection", "connection"):
                    headers[key.strip()] = value.strip()

        try:
            resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        except requests.RequestException as exc:
            error_msg = f"HTTP/1.1 502 Bad Gateway\r\n\r\nErro: {exc}"
            client.sendall(error_msg.encode())
            client.close()
            return

        content_type = resp.headers.get("Content-Type", "text/html")

        if "text/html" in content_type:
            filtered_body, was_filtered = filter_content(resp.text)
            action = "filtrado" if was_filtered else "permitido"
            body_bytes = filtered_body.encode("utf-8", errors="replace")
        else:
            action = "permitido"
            body_bytes = resp.content

        log_access(url, action)

        status_line = f"HTTP/1.1 {resp.status_code} OK\r\n"
        response_headers = (
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(body_bytes)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        client.sendall((status_line + response_headers).encode() + body_bytes)

    except Exception as exc:
        print(f"[proxy] erro HTTP: {exc}")
    finally:
        try:
            client.close()
        except OSError:
            pass


def _handle_client(client: socket.socket) -> None:
    try:
        raw = client.recv(4096)
        if not raw:
            client.close()
            return

        first_line = raw.decode(errors="ignore").splitlines()[0]

        if first_line.startswith("CONNECT"):
            _, host_port, _ = first_line.split(" ", 2)
            host, port_str = host_port.rsplit(":", 1)
            _handle_connect(client, host, int(port_str))
        else:

            _handle_http(client, raw)

    except Exception as exc:
        print(f"[proxy] erro no handle_client: {exc}")
        try:
            client.close()
        except OSError:
            pass


def start_tunnel_server() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((PROXY_HOST, PROXY_PORT))
    server.listen(100)
    print(f"[proxy] escutando em {PROXY_HOST}:{PROXY_PORT} (HTTP + HTTPS)")

    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=_handle_client, args=(client,), daemon=True)
        thread.start()