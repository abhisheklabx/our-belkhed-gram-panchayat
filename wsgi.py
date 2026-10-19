import os
from app import create_app
from models.database import db
from scripts.seed_data import seed_database

app = create_app()

# Auto-initialize and seed database safely on startup in production/cloud environments
with app.app_context():
    try:
        db.create_all()
        # Seed default administrative and village records if not yet present
        seed_database()
    except Exception as e:
        app.logger.warning(f"Database auto-init notice: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
