from . import main


@main.route("/")
def index():
    return "Hello from the main blueprint!"

@main.route("/health", methods=["GET"])
def health():
    return {"status": "healthy"}, 200