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


Docker and PostgreSQL Setup
Prerequisites
Docker Desktop installed and running.
Docker Compose available.
Git installed.
1. Configure environment variables

Create your local environment file from the example:

bash
cp .env.example .env


Edit .env and provide your own values for:

SECRET_KEY
JWT_SECRET
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
DATABASE_URL

The database URL must use db as its hostname because db is the PostgreSQL service name in Docker Compose.

Example format:

text
DATABASE_URL=postgresql+psycopg://tracker_user:YOUR_PASSWORD@db:5432/tracker_db


Never commit .env or share its secrets.

2. Build and start the application

From the project root, run:

bash
docker compose up -d --build


Check the services:

bash
docker compose ps


PostgreSQL should report healthy, and the web application should be running.

3. Apply database migrations

Run Flask-Migrate inside the web container:

bash
docker compose exec web flask --app wsgi db upgrade


This applies existing database migrations to PostgreSQL.

4. Verify application health

Check the health endpoint:

bash
curl -i http://localhost:5000/health


Expected response:

json
{
  "status": "healthy"
}


The HTTP status should be 200 OK.

5. Verify authentication and task creation

Register a test user or log in with an existing user:

bash
curl -i -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"YOUR_EMAIL","password":"YOUR_PASSWORD"}'


Use the returned access token for authenticated requests.

Create a task:

bash
curl -i -X POST http://localhost:5000/auth/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Docker Persistence Test","description":"Testing PostgreSQL persistence."}'


Expected response: 201 CREATED.

Retrieve the task using its returned ID:

bash
curl -i http://localhost:5000/auth/tasks/TASK_ID \
  -H "Authorization: Bearer YOUR_TOKEN"


Expected response: 200 OK.

6. Verify PostgreSQL data persistence

Stop the application:

bash
docker compose down


Restart it:

bash
docker compose up -d


Check that the services are running:

bash
docker compose ps


Log in again to obtain a fresh access token, then retrieve the previously created task.

The task should still exist with the same ID and data.

Important: Do not use docker compose down -v when performing a normal restart. The -v option removes named volumes, including the PostgreSQL data volume.

7. Verify Git ignores local secrets

Check that .env is ignored:

bash
git check-ignore -v .env


Check that .env.example is tracked:

bash
git ls-files --error-unmatch .env.example


The first command should identify the .gitignore rule, and the second should return .env.example.

Never commit actual credentials or database passwords.

8. Stopping the application

To stop the containers while preserving database data:

bash
docker compose down


To start them again:

bash
docker compose up -d


The named PostgreSQL volume preserves database data across these container restarts.
