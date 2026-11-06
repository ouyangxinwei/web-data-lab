# Database migrations

From the `backend` directory, run `alembic upgrade head` to create or update the database schema. Use `alembic downgrade -1` only in a disposable development database. Do not edit an already-applied migration; create a new revision instead.
