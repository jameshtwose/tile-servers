## Commands
- `pip install -r requirements.txt` to install dependencies

# Set your PostGIS database instance URL in the environment
- `export DATABASE_URL=postgresql://postgres:postgres@0.0.0.0:5432/bonn`
- `uvicorn main:app --reload` to start the server