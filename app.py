import dash
from dash import Dash

from lib.appshell import create_appshell
from dotenv import load_dotenv
from os import path


stylesheets = [
    "https://fonts.googleapis.com/css2?family=Roboto:wght@100;200;300;400;500&display=swap"
]


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=stylesheets,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"}
    ]
)

#app.config.suppress_callback_exceptions = True
app.layout = create_appshell(dash.page_registry.values())

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
