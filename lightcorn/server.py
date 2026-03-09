import asyncio

__version__ = "0.1.0-alpha.0"

class Server:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.routes = {}

    def get(self, path):
        def dec(f):
            self.routes[path] = f
            return f

        return dec

    async def parse(self, reader):
        data = await reader.read(1024)
        lines = data.split(b"\r\n")
        if not lines:
            return "/", "GET"
        parts = lines[0].decode().split()
        return parts[1] if len(parts) > 1 else "/", parts[0]

    async def handle(self, r, w):
        path, method = await self.parse(r)
        handler = self.routes.get(path)

        if handler and method == "GET":
            body = await handler()
            status = "200 OK"
        else:
            body = b"Not Found"
            status = "404 Not Found"

        w.write(f"HTTP/1.1 {status}\r\nContent-Length: {len(body)}\r\n\r\n".encode())
        w.write(body)
        await w.drain()
        w.close()

    async def run(self):
        s = await asyncio.start_server(self.handle, self.host, self.port)
        print(f"\033[32mINFO:\033[0m\t\033[1mLightcorn\033[0m {__version__}")
        print(f"\033[32mINFO:\033[0m\tRunning on http://{self.host}:{self.port}/")
        await s.serve_forever()


if __name__ == "__main__":
    app = Server(host="127.0.0.1", port=8000)

    @app.get("/")
    async def root():
        return b"Hello World!"

    @app.get("/about")
    async def about():
        text = f"Lightcorn {__version__}"
        return text.encode()

    asyncio.run(app.run())