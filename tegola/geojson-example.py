# %%
from sqlalchemy import (
    create_engine,
    text,
    Column,
    Integer,
    String,
    select
)
from sqlalchemy.orm import declarative_base
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from geojson_pydantic import Feature, FeatureCollection, LineString

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
engine = create_engine(
    f"postgresql+psycopg2://postgres:postgres@{host}:5432/bonn"
)

# %%
Base = declarative_base()
# %%
class AllRoads(Base):
    __tablename__ = "all_roads"
    ogc_fid = Column(Integer, primary_key=True)
    wkb_geometry = Column(Geometry("LINESTRING"))
    osm_id = Column(Integer)
    name = Column(String)
    highway = Column(String)
    waterway = Column(String)
    aerialway = Column(String)
    barrier = Column(String)
    man_made = Column(String)
    other_tags = Column(String)
# %%
with engine.begin() as conn:
    select_query = select(AllRoads)
    result = conn.execute(select_query)
data = [dict(zip(
    result.keys(),
    row
)) for row in result.fetchall()]
# %%
feature_collection = FeatureCollection(
    type="FeatureCollection",
    features=[
        Feature(
            type="Feature",
            geometry=LineString(
                type="LineString",
                coordinates=[[x, y] for x, y in zip(*to_shape(row["wkb_geometry"]).xy)]
            ),
            properties={
                "osm_id": row["osm_id"],
                "name": row["name"],
                "highway": row["highway"],
                "waterway": row["waterway"],
                "aerialway": row["aerialway"],
                "barrier": row["barrier"],
            },
        )
        for row in data
    ],
)
# %%
feature_collection.features[0].model_dump()
# %%
