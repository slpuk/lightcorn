import asyncio

__version__ = "0.3.0-alpha.2"


class Server:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.routes = {"GET": {}, "POST": {}}

    def route(self, path, method="GET"):
        def dec(f):
            self.routes[method][path] = f
            return f

        return dec

    async def parse(self, reader):
        # Reading headers
        data = b""
        while b"\r\n\r\n" not in data:
            data += await reader.read(256)

        head, body = data.split(b"\r\n\r\n", 1)
        lines = head.split(b"\r\n")

        # First line
        first = lines[0].decode().split()
        method, path = first[0], first[1]

        # Headers
        headers = {}
        for line in lines[1:]:
            if b":" in line:
                k, v = line.split(b":", 1)
                headers[k.strip().decode()] = v.strip().decode()

        # Body
        clen = int(headers.get("Content-Length", 0))
        while len(body) < clen:
            body += await reader.read(256)

        return method, path, headers, body

    async def handle(self, r, w):
        try:
            method, path, headers, body = await self.parse(r)
            handler = self.routes[method].get(path)

            if handler:
                res = await handler(headers, body)
                if isinstance(res, tuple):
                    body, status = res
                else:
                    body, status = res, "200 OK"
            else:
                body, status = b"Not Found", "404 Not Found"

            # Send
            w.write(f"HTTP/1.1 {status}\r\n".encode())
            w.write(f"Content-Length: {len(body)}\r\n".encode())
            w.write(b"Content-Type: text/plain\r\n\r\n")
            w.write(body)

        except Exception as e:
            w.write(b"HTTP/1.1 500 Error\r\n\r\nServer Error")

        await w.drain()
        w.close()

    async def run(self):
        s = await asyncio.start_server(self.handle, self.host, self.port)
        print(f"\033[32mINFO:\033[0m\t\033[1mLightcorn\033[0m {__version__}")
        print(f"\033[32mINFO:\033[0m\tRunning on http://{self.host}:{self.port}/")
        await s.serve_forever()


# Example app
if __name__ == "__main__":
    app = Server(host="127.0.0.1", port=8000)

    @app.route("/", "GET")
    async def root(h, b):
        return b"Hello World!"

    @app.route("/about", "GET")
    async def about(h, b):
        text = f"Lightcorn {__version__}"
        return text.encode()

    @app.route("/echo", "POST")
    async def echo(h, b):
        return b, "201 Created"

    asyncio.run(app.run())
