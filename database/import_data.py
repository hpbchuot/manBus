"""
Import GTFS data into PostgreSQL database
Reads CSV files from data/ directory and imports them into the database
"""

import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from shapely.geometry import Point, LineString
from geoalchemy2.shape import from_shape
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'TransitDB')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def create_db_connection():
    """Create database connection"""
    try:
        engine = create_engine(DATABASE_URL)
        logger.info("Database connection established successfully")
        return engine
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def import_stops(engine):
    """Import stops data from CSV to database"""
    logger.info("Importing stops...")

    # Read stops CSV
    stops_df = pd.read_csv(os.path.join(DATA_DIR, 'stops.csv'))

    with engine.connect() as conn:
        for _, row in stops_df.iterrows():
            # Create point geometry
            point = Point(float(row['stop_lon']), float(row['stop_lat']))
            point_wkt = from_shape(point, srid=4326)

            # Insert into database
            query = text("""
                INSERT INTO stops (id, name, location)
                VALUES (nextval('stops_id_seq'), :name, ST_GeomFromEWKT(:location))
                ON CONFLICT DO NOTHING
            """)

            conn.execute(query, {
                'name': row['stop_name'],
                'location': f'SRID=4326;POINT({row["stop_lon"]} {row["stop_lat"]})'
            })

        conn.commit()

    logger.info(f"Imported {len(stops_df)} stops")


def import_routes(engine):
    """Import routes data from CSV to database"""
    logger.info("Importing routes...")

    # Read routes CSV
    routes_df = pd.read_csv(os.path.join(DATA_DIR, 'routes.csv'))

    # Read stop_times to get route geometry
    stop_times_df = pd.read_csv(os.path.join(DATA_DIR, 'stop_times.csv'))
    trips_df = pd.read_csv(os.path.join(DATA_DIR, 'trips.csv'))
    stops_df = pd.read_csv(os.path.join(DATA_DIR, 'stops.csv'))

    with engine.connect() as conn:
        for _, route in routes_df.iterrows():
            route_id = route['route_id']
            route_name = route['route_short_name']

            # Get trips for this route
            route_trips = trips_df[trips_df['route_id'] == route_id]
            if route_trips.empty:
                logger.warning(f"No trips found for route {route_id}")
                continue

            # Get first trip to build route geometry
            first_trip = route_trips.iloc[0]
            trip_id = first_trip['trip_id']

            # Get stops for this trip, ordered by stop_sequence
            trip_stops = stop_times_df[stop_times_df['trip_id'] == trip_id].sort_values('stop_sequence')

            if trip_stops.empty:
                logger.warning(f"No stops found for trip {trip_id}")
                continue

            # Build LineString from stops
            coordinates = []
            stop_ids = []

            for _, stop_time in trip_stops.iterrows():
                stop_id = stop_time['stop_id']
                stop_info = stops_df[stops_df['stop_id'] == stop_id]

                if not stop_info.empty:
                    lat = float(stop_info.iloc[0]['stop_lat'])
                    lon = float(stop_info.iloc[0]['stop_lon'])
                    coordinates.append((lon, lat))
                    stop_ids.append(stop_id)

            if len(coordinates) < 2:
                logger.warning(f"Not enough coordinates for route {route_id}")
                continue

            # Create LineString geometry
            linestring_wkt = f"SRID=4326;LINESTRING({', '.join([f'{lon} {lat}' for lon, lat in coordinates])})"

            # Insert route into database
            query = text("""
                INSERT INTO routes (name, route_geom, current_segment, updated_at)
                VALUES (:name, ST_GeomFromEWKT(:route_geom), 0, NOW())
                RETURNING id
            """)

            result = conn.execute(query, {
                'name': route_name,
                'route_geom': linestring_wkt
            })

            db_route_id = result.fetchone()[0]

            # Insert route stops into junction table
            for sequence, stop_id in enumerate(stop_ids):
                # Find stop in database by name
                stop_query = text("""
                    SELECT id FROM stops
                    WHERE name = (SELECT stop_name FROM
                        (VALUES (:stop_id)) AS t(id)
                        JOIN (SELECT * FROM
                            (VALUES %s) AS stops(stop_id, stop_name)
                        ) s ON t.id = s.stop_id
                    )
                    LIMIT 1
                """)

                # Simplified: just insert with sequence number
                junction_query = text("""
                    INSERT INTO routestops (route_id, stop_id, stop_sequence, created_at)
                    SELECT :route_id, id, :sequence, NOW()
                    FROM stops
                    WHERE name LIKE :stop_name
                    LIMIT 1
                    ON CONFLICT DO NOTHING
                """)

                stop_info = stops_df[stops_df['stop_id'] == stop_id]
                if not stop_info.empty:
                    stop_name = stop_info.iloc[0]['stop_name']
                    conn.execute(junction_query, {
                        'route_id': db_route_id,
                        'sequence': sequence,
                        'stop_name': f'%{stop_name}%'
                    })

        conn.commit()

    logger.info(f"Imported {len(routes_df)} routes")


def import_sample_buses(engine):
    """Import sample buses for each route"""
    logger.info("Importing sample buses...")

    with engine.connect() as conn:
        # Get all routes
        routes = conn.execute(text("SELECT id, name FROM routes")).fetchall()

        for route_id, route_name in routes:
            # Create 2-3 buses per route
            for i in range(1, 3):
                plate_number = f"29A-{route_name.replace(' ', '')}-{i:03d}"

                query = text("""
                    INSERT INTO buses (plate_number, name, model, status, route_id)
                    VALUES (:plate, :name, :model, 'Active', :route_id)
                    ON CONFLICT (plate_number) DO NOTHING
                """)

                conn.execute(query, {
                    'plate': plate_number,
                    'name': f"Bus {route_name} #{i}",
                    'model': 'Hyundai Universe',
                    'route_id': route_id
                })

        conn.commit()

    logger.info("Sample buses imported")


def main():
    """Main import function"""
    try:
        logger.info("Starting data import...")

        # Create database connection
        engine = create_db_connection()

        # Import data in order
        import_stops(engine)
        import_routes(engine)
        import_sample_buses(engine)

        logger.info("Data import completed successfully!")

    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise


if __name__ == "__main__":
    main()
