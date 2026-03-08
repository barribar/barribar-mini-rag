## Run Alembic Migrations
### Configuration
```bash
cp alembicIni.example alembic.ini
```

- Update the 'alembic.ini' with your database credentials ('sqlalchemy.url')

```bash
alembic revision --autogenerate -m "Add ..." 
```

### Upgrade the database

```bash
alembic upgrade head
```

