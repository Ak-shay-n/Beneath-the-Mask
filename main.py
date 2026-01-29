from website import create_app

app = create_app()
if __name__ == "__main__":
    # Enable debug and auto-reloader so changes to code and templates
    # are picked up automatically during development.
    app.run(debug=True, use_reloader=True)
