import os
import fastapi
from fastapi.staticfiles import StaticFiles
import click
import uvicorn


class Server:
    @staticmethod
    def start(host: str = '', port=8000):
        click.echo(click.style("Starting web server", fg="cyan"))
        app = fastapi.FastAPI()

        @app.get('/api/status')
        def get_status():
            return {'status': 'healthy'}

        local_folder = os.path.dirname(os.path.abspath(__file__))
        static_foler = os.path.join(local_folder, 'static')
        print(static_foler)
        app.mount("/", StaticFiles(directory=static_foler,
                  html=True), name="static")

        uvicorn.run(app, host=host, port=port)
