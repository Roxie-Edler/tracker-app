import os
from tracker import create_app # type: ignore

app = create_app(os.getenv("FLASK_CONFIG", "development"))