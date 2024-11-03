# %%
from sqlalchemy import (
    create_engine,
    text,
    Column,
    Integer,
    String,
    DateTime,
    insert,
)
from sqlalchemy.orm import declarative_base
from geoalchemy2 import Geometry
import pandas as pd
import geopandas as gpd

# %%
# postgresql+psycopg2://user:password@host:port/dbname
# host = "docker.for.mac.host.internal"
# psql -h localhost -p 5434 -U postgres -d postgres
host = "localhost"
engine = create_engine(
    f"postgresql+psycopg2://postgres:postgres@{host}:5432/bonn"
)
print("create extension")
# create postgis extension
with engine.begin() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

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


class NlHsCables(Base):
    __tablename__ = "nl_hs_cables"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    shape = Column(Geometry("LINESTRING", srid=28992))


class NlMsCables(Base):
    __tablename__ = "nl_ms_cables"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True)
    shape = Column(Geometry("LINESTRING", srid=28992))


class NlLsCables(Base):
    __tablename__ = "nl_ls_cables"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True)
    shape = Column(Geometry("LINESTRING", srid=28992))


Base.metadata.create_all(engine)


# %%
points_df = pd.read_csv("nl.csv")
print("Points dataframe")
print(points_df.head())
# %%
with engine.begin() as conn:
    query = insert(NlMeters).values(points_df.to_dict(orient="records"))
    conn.execute(query)
print("Points inserted")
# %%
layer_model_dict = {
    "hoogspanningskabels": NlHsCables,
    "middenspanningskabels": NlMsCables,
    "laagspanningskabels": NlLsCables,
}
for layer, model in layer_model_dict.items():
    lines_gdf = (
        gpd.read_file("liander_elektriciteitsnetten.gpkg", layer=layer)
        .assign(
            **{
                "shape": lambda x: x["geometry"].apply(
                    lambda y: f"SRID=28992;{y.wkb_hex}"
                )
            }
        )
        .drop(columns=["id", "geometry"])
    )
    print(f"{layer} dataframe")
    print(lines_gdf.head())
    with engine.begin() as conn:
        query = insert(model).values(lines_gdf.to_dict(orient="records"))
        conn.execute(query)
    print(f"{layer} inserted")
# %%