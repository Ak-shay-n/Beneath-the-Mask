import os
from dotenv import load_dotenv
from website import create_app

# Load environment variables
load_dotenv()

app = create_app()

if __name__ == "__main__":
    # Use FLASK_DEBUG from environment, default to False for security
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(debug=debug_mode, use_reloader=debug_mode)
