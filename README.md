# Project Repository

This is the initial README file for the project.

## Backend Database Configuration

The backend uses SQLAlchemy and is ready to connect to a variety of databases.

### Default (Development): SQLite

By default, if no environment variable is set, it will use a local SQLite file for fast testing and dev:

```
sqlite:///./jobportal.db
```

### Switching to an External Database (PostgreSQL, MySQL, etc.)

To use an external database (such as when a 'job_portal_database' service is provided):

1. Set the `DATABASE_URL` environment variable to a valid SQLAlchemy connection string.
   - **PostgreSQL example:**  
     `export DATABASE_URL="postgresql://jobuser:jobpass@dbhost:5432/jobportal"`
   - **MySQL example:**  
     `export DATABASE_URL="mysql+mysqlconnector://jobuser:jobpass@dbhost:3306/jobportal"`

2. For containerized/cloud deployments, this is typically supplied from your service orchestrator or secrets manager.
3. Alembic migration configs (alembic.ini) and SQLAlchemy engine will both use this value.
4. **Note:** The backend app, migrations, and all DB code automatically use the value of `DATABASE_URL`.

### Future Integration: job_portal_database Service

- Once the external `job_portal_database` service is ready, update only the `DATABASE_URL` variable using the connection string provided by that service.
- No code change needed—configuration will automatically pick up the new database.

### Quick Development Run

For convenience while developing:

- To run with SQLite, do nothing extra.
- To run with an external DB, set `DATABASE_URL` before starting backend or running migrations.
