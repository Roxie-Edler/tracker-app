Tracker App Backend

A Flask-based backend application for the Tracker App. This project uses Flask, Flask-SQLAlchemy, and Flask-Migrate, with environment-specific configuration for development, testing, and production.

Setup
1. Clone the repository
bash
git clone <repository-url>
cd tracker-app

2. Create a virtual environment
bash
python3 -m venv venv

3. Activate the virtual environment

On macOS/Linux:

bash
source venv/bin/activate

4. Install dependencies
bash
pip install -r requirements.txt

5. Configure environment variables

Create your local .env file using .env.example as a template:

bash
cp .env.example .env


Edit .env and replace the placeholder values with your own settings and randomly generated secrets.

6. Run the application
bash
flask --app wsgi run --debug


The development application will be available at:

http://127.0.0.1:5000

Environment Variables

The application uses environment variables to manage configuration and keep sensitive information out of source code.

Variable	Description
FLASK_ENV	Identifies the intended environment, such as development.
FLASK_APP	Identifies the Flask application entry point (wsgi.py).
SECRET_KEY	Secret key used by Flask for signing session data.
JWT_SECRET	Secret key used to sign and verify JWT tokens.
SQLALCHEMY_DATABASE_URI	Database connection URI used by Flask-SQLAlchemy.

Never commit your actual .env

Migrations

This project uses Flask-Migrate (powered by Alembic) to manage database schema changes.

Once database models have been created, use the following commands to manage migrations.

1. Initialize migrations

Run this command once to create the migrations repository:

bash
flask db init

2. Generate a migration

After creating or changing database models, generate a migration:

bash
flask db migrate -m "describe changes"


This creates a migration script based on changes detected in your models.

3. Apply migrations

Apply pending migrations to your database:

bash
flask db upgrade


This updates the database schema to match your latest migration.

Note: Migration commands should be run with the project's virtual environment activated. The migration initialization command only needs to be run once per project.
