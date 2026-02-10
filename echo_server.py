import socket
from http import HTTPStatus
from urllib.parse import urlparse, parse_qs


HOST = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 4096


def parse_request(data: str):
    lines = data.split("\r\n")
    request_line = lines[0]
    headers = {}

    method, path, _ = request_line.split(" ", 2)

    for line in lines[1:]:
        if not line:
            break
        key, value = line.split(":", 1)
        headers[key.strip()] = value.strip()

    return method, path, headers


def get_status(path: str) -> HTTPStatus:
    parsed = urlparse(path)
    params = parse_qs(parsed.query)

    status_values = params.get("status")
    if not status_values:
        return HTTPStatus.OK

    try:
        code = int(status_values[0])
        return HTTPStatus(code)
    except (ValueError, KeyError):
        return HTTPStatus.OK


def build_body(method, source, status, headers):
    lines = [
        f"Request Method: {method}",
        f"Request Source: {source}",
        f"Response Status: {status.value} {status.phrase}",
    ]

    for k, v in headers.items():
        lines.append(f"{k}: {v}")

    return "\r\n".join(lines)


def handle_client(conn, addr):
    data = conn.recv(BUFFER_SIZE).decode("utf-8", errors="ignore")
    if not data:
        return

    method, path, headers = parse_request(data)
    status = get_status(path)

    body = build_body(method, addr, status, headers)
    body_bytes = body.encode("utf-8")

    response = (
        f"HTTP/1.1 {status.value} {status.phrase}\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode("utf-8") + body_bytes

    conn.sendall(response)


def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()

        print(f"Echo server started on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            with conn:
                handle_client(conn, addr)


if __name__ == "__main__":
    run_server()
