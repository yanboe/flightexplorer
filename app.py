import dash
from dash import Dash

from layout.appshell import create_appshell
from dotenv import load_dotenv

load_dotenv()

app = Dash(
    __name__,
    use_pages=True,
    update_title=None,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"}
    ]
)

app.config.suppress_callback_exceptions = True
app.layout = create_appshell(dash.page_registry.values())

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
