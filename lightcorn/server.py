import asyncio

class Server:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port

    async def handle(self, reader, writer):
        data = await reader.readline()
        path = data.decode().split()[1] if data else "/"
        
        body = b"Hello World!" if path == "/" else b"Not Found"
        status = "200 OK" if path == "/" else "404 Not Found"
        
        writer.write(f"HTTP/1.1 {status}\r\nContent-Length: {len(body)}\r\n\r\n".encode())
        writer.write(body)
        await writer.drain()
        writer.close()

    async def run(self):
        server = await asyncio.start_server(self.handle, self.host, self.port)
        print(f"\033[32mINFO:\033[0m\t\033[1mLightcorn\033[0m 0.1.0-pre.0")
        print(f"\033[32mINFO:\033[0m\tRunning on http://{self.host}:{self.port}/")
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(Server().run())