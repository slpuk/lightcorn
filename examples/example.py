import asyncio
import time
from lightcorn import Server

app = Server()


# Requested path middleware
def logger_mw(app):
    async def wrapper(scope, receive, send):
        print(f"-> {scope['method']} {scope['path']}")
        await app(scope, receive, send)

    return wrapper


# Applying middleware function
app.use(logger_mw)


# Handles / path & sends Hello World! with method GET
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


# Handles /about path & sends server version with method GET
@app.route("/about", ["GET"])
async def about(scope, recv, send):
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"text/plain"]],
        }
    )
    text = f"Lightcorn {Server.__version__}"
    await send({"type": "http.response.body", "body": text.encode()})


# Handles /post path & sends server version with method POST
@app.route("/post", ["POST"])
async def post(scope, recv, send):
    # Receives message
    message = await recv()
    body = message.get("body", b"").decode() if message.get("body") else ""

    await send(
        {
            "type": "http.response.start",
            "status": 201,
            "headers": [[b"content-type", b"text/plain"]],
        }
    )
    text = f"Received: {body}"
    await send({"type": "http.response.body", "body": text.encode()})


# Starts server
asyncio.run(app.run())
