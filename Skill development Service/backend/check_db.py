from app.database import engine
from sqlalchemy import inspect
insp = inspect(engine)
print("Tables in DB:", insp.get_table_names())
for table in insp.get_table_names():
    if "job" in table or "app" in table or "save" in table:
        cols = [c['name'] for c in insp.get_columns(table)]
        print(f"Table {table}: {cols}")
