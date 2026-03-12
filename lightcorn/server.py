import asyncio
import traceback
from dataclasses import dataclass

@dataclass
class Config:
    host: str = "127.0.0.1"
    port: int = 8000
    max_size: int = 1024 * 1024
    timeout: float = 10.0

class Server:
    __version__ = "0.4.0-alpha.3"

    def __init__(self, config=None):
        self.config = config or Config()
        self.routes = {"GET": {}, "POST": {}, "PUT": {}, "DELETE": {}}
        self.server = None

    def route(self, path, methods=None):
        methods = methods or ["GET"]
        def dec(f):
            for m in methods:
                self.routes[m][path] = f
            return f
        return dec

    async def _parse(self, reader):
        data = b""
        while b"\r\n\r\n" not in data:
            if len(data) > self.config.max_size:
                raise ValueError("Headers too big")
            chunk = await reader.read(512)
            if not chunk:
                raise ConnectionError("No data")
            data += chunk
        
        head, body = data.split(b"\r\n\r\n", 1)
        lines = head.split(b"\r\n")
        
        # Start line
        sline = lines[0].decode().split()
        if len(sline) < 3:
            raise ValueError("Bad request line")
        method, path = sline[0], sline[1]
        
        # Headers
        headers = {}
        for line in lines[1:]:
            if b":" in line:
                k, v = line.split(b":", 1)
                headers[k.strip().lower().decode()] = v.strip().decode()
        
        # Body
        clen = int(headers.get("content-length", 0))
        if clen > self.config.max_size:
            raise ValueError("Body too big")
        
        while len(body) < clen:
            chunk = await reader.read(min(1024, clen - len(body)))
            if not chunk:
                break
            body += chunk
        
        return method, path, headers, body

    async def _send(self, writer, status, body, headers=None):
        status_text = {200: "OK", 404: "Not Found", 500: "Error"}.get(status, "OK")
        writer.write(f"HTTP/1.1 {status} {status_text}\r\n".encode())
        writer.write(f"Content-Length: {len(body)}\r\n".encode())
        for k, v in (headers or {}).items():
            writer.write(f"{k}: {v}\r\n".encode())
        writer.write(b"\r\n")
        writer.write(body)
        await writer.drain()

    async def handle(self, r, w):
        client = w.get_extra_info('peername')
        print(f"Client: {client}")
        
        try:
            method, path, headers, body = await asyncio.wait_for(
                self._parse(r), timeout=self.config.timeout
            )
            
            handler = self.routes.get(method, {}).get(path)
            if handler:
                try:
                    res = await handler(headers, body)
                    if isinstance(res, tuple):
                        body, status, headers = res + ({},) if len(res) == 2 else res
                    else:
                        body, status, headers = res, 200, {}
                except Exception as e:
                    body, status, headers = f"Handler error: {e}".encode(), 500, {}
            else:
                body, status, headers = b"Not Found", 404, {}
            
            await self._send(w, status, body, headers)
            
        except asyncio.TimeoutError:
            await self._send(w, 408, b"Timeout")
        except ValueError as e:
            await self._send(w, 400, str(e).encode())
        except Exception as e:
            traceback.print_exc()
            await self._send(w, 500, b"Server Error")
        finally:
            w.close()
            await w.wait_closed()

    async def run(self):
        self.server = await asyncio.start_server(
            self.handle, self.config.host, self.config.port
        )
        print(f"\033[32mINFO:\033[0m\t\033[1mLightcorn\033[0m {Server.__version__}")
        print(f"\033[32mINFO:\033[0m\tRunning on http://{Config.host}:{Config.port}/")
        await self.server.serve_forever()

if __name__ == '__main__':
    app = Server(Config(port=8000))

    @app.route("/", ["GET"])
    async def root(h, b):
        return b"Hello World!"

    @app.route("/about", ["GET"])
    async def about(h, b):
        text = f"Lightcorn {Server.__version__}"
        return text.encode()

    @app.route("/data", ["POST"])
    async def data(h, b):
        return b"Received: " + b, 201, {"X-Custom": "Header"}

    asyncio.run(app.run())
    