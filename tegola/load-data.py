# %%
from sqlalchemy import create_engine, insert, text, Column, Integer, String, DateTime, select
from sqlalchemy.orm import declarative_base
from geoalchemy2 import Geometry

## Pgadmin connection settings
# - host: docker.for.mac.host.internal
# - port: 5432
# - user: postgres
# - password: postgres
# - database: bonn
# - schema: public

# %%
# postgresql+psycopg2://user:password@host:port/dbname
# host = "docker.for.mac.host.internal"
# psql -h localhost -p 5434 -U postgres -d postgres
host = "localhost"
engine = create_engine(f"postgresql+psycopg2://postgres:postgres@{host}:5432/bonn")

# %%
Base = declarative_base()


class NlMeters(Base):
    __tablename__ = "nl_meters"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    address = Column(String)
    info = Column(String)
    shape = Column(Geometry("POINT", srid=28992))


Base.metadata.create_all(engine)
# %%
with open("nl.csv") as f:
    data = f.readlines()
    data = [
        dict(zip(["id", "timestamp", "address", "info", "shape"], row.strip().split(",")))
        for row in data[1:]
    ]

# %%
with engine.begin() as conn:
    insert_query = insert(
        NlMeters
    ).values(data)
    conn.execute(insert_query)
    
# %%
with engine.begin() as conn:
    select_query = text("SELECT ST_AsMVTGeom(shape) AS shape, id FROM nl_meters")
    result = conn.execute(select_query)
    print(result.fetchall())
# %%
