import asyncio
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable
from .logger import Logger, Colors

log = Logger()


@dataclass
class Config:
    host: str = "127.0.0.1"
    port: int = 8000
    max_size: int = 10 * 1024 * 1024
    timeout: float = 30.0
    buffer: int = 8192


class Server:
    __version__ = "0.5.0-alpha.4"

    def __init__(self, config=None, debug=False):
        self.config = config or Config()
        self.middlewares = []
        self.routes = {}

    def use(self, middleware):
        self.middlewares.append(middleware)
        return self

    def route(self, path, methods=None):
        methods = methods or ["GET"]

        def dec(f):
            for m in methods:
                self.routes[(path, m)] = f
            return f

        return dec

    async def _parse(self, reader):
        # Headers
        data = b""
        while b"\r\n\r\n" not in data:
            if len(data) > self.config.max_size:
                raise ValueError("Headers too large")
            chunk = await reader.read(self.config.buffer)
            if not chunk:
                raise ConnectionError("Client disconnected")
            data += chunk

        head, body = data.split(b"\r\n\r\n", 1)
        lines = head.split(b"\r\n")

        # Request line
        rline = lines[0].decode().split()
        if len(rline) != 3:
            raise ValueError("Invalid request line")
        method, path, version = rline

        # Parse path and query
        path_parts = path.split("?", 1)
        path = path_parts[0]
        qs = path_parts[1].encode() if len(path_parts) > 1 else b""

        # Headers
        headers = []
        clen = 0
        for line in lines[1:]:
            if b":" in line:
                k, v = line.split(b":", 1)
                k = k.strip()
                v = v.strip()
                headers.append((k, v))
                if k.lower() == b"content-length":
                    clen = int(v)
                    if clen > self.config.max_size:
                        raise ValueError("Body too large")

        # Body
        while len(body) < clen:
            chunk = await reader.read(min(self.config.buffer, clen - len(body)))
            if not chunk:
                break
            body += chunk

        scope = {
            "type": "http",
            "method": method.upper(),
            "path": path,
            "query_string": qs,
            "headers": headers,
            "version": version.split("/")[-1],
        }
        return scope, body

    async def handle(self, r, w):
        client = w.get_extra_info("peername")
        start = time.time()

        try:
            scope, body = await asyncio.wait_for(
                self._parse(r), timeout=self.config.timeout
            )

            # Message queues
            recv_q = asyncio.Queue()
            send_q = asyncio.Queue()
            await recv_q.put({"type": "http.request", "body": body})

            # Find handler
            handler = self.routes.get((scope["path"], scope["method"]))
            if not handler:
                handler = self.routes.get((scope["path"], "GET"))

            async def receive():
                return await recv_q.get()

            async def send(msg):
                await send_q.put(msg)

            # Run with middlewares
            app = handler if handler else self._not_found
            for mw in reversed(self.middlewares):
                app = mw(app)

            # Execute
            task = asyncio.create_task(app(scope, receive, send))

            # Send response
            try:
                start_msg = await send_q.get()
                if start_msg["type"] == "http.response.start":
                    status = start_msg["status"]
                    headers = start_msg.get("headers", [])

                    w.write(f"HTTP/1.1 {status} OK\r\n".encode())
                    for k, v in headers:
                        w.write(k + b": " + v + b"\r\n")
                    w.write(b"\r\n")

                    body_msg = await send_q.get()
                    if body_msg["type"] == "http.response.body":
                        w.write(body_msg.get("body", b""))

                    await w.drain()
            finally:
                task.cancel()
                try:
                    await task
                except:
                    pass

            connection_log = f"{client} {scope['method']} -> {scope['path']} {time.time()-start:.3f}s"
            log.debug(connection_log)

        except asyncio.TimeoutError:
            w.write(b"HTTP/1.1 408 Timeout\r\n\r\nTimeout")
            await w.drain()
        except Exception as e:
            log.error(f"Unhandled error: {e}")
            w.write(b"HTTP/1.1 500 Error\r\n\r\nError")
            await w.drain()
        finally:
            w.close()
            await w.wait_closed()

    async def _not_found(self, scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 404,
                "headers": [[b"content-type", b"text/plain"]],
            }
        )
        await send({"type": "http.response.body", "body": b"Not Found"})

    async def run(self):
        s = await asyncio.start_server(self.handle, self.config.host, self.config.port)
        log.info(f"\033[1mLightcorn\033[0m {Server.__version__}")
        log.info(f"Running on http://{self.config.host}:{self.config.port}/")
        await s.serve_forever()


if __name__ == "__main__":
    app = Server()

    @app.route("/", ["GET"])
    async def root(scope, recv, send):
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"text/plain"]],
            }
        )
        await send({"type": "http.response.body", "body": b"Hello World!"})

    asyncio.run(app.run())
