import gtfs_kit as gk
from sqlalchemy import create_engine, text
from geoalchemy2 import Geometry

# --- CẤU HÌNH CỦA BẠN ---
DB_URL = "postgresql://postgres:1234@localhost:5433/manBusDB"
GTFS_PATH = "/Users/vuthinh/PycharmProjects/managing-bus/data/hanoi-gtfs.zip"
SCHEMA = "gtfs"  # change if needed; will be created if not public
# -------------------------

print("Đang kết nối đến database...")
engine = create_engine(DB_URL)

# Tạo schema nếu chưa tồn tại
if SCHEMA != 'public':
    try:
        with engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"))
            conn.commit()  # commit() là cần thiết cho câu lệnh DDL
        print(f"Đã đảm bảo schema '{SCHEMA}' tồn tại.")
    except Exception as e:
        print(f"Lỗi khi tạo schema '{SCHEMA}': {e}")
        exit() # Thoát nếu không tạo được schema

print(f"Đang đọc file GTFS từ: {GTFS_PATH}...")
# Đọc feed vào bộ nhớ
feed = gk.read_feed(GTFS_PATH, dist_units='km')
print("Đã đọc feed thành công.")

try:
    print(f"Đang ghi bảng 'trips' vào schema '{SCHEMA}'...")
    feed.trips.to_sql(
        'trips',
        engine,
        schema=SCHEMA,
        if_exists='replace',  # dùng 'append' nếu muốn ghi bổ sung
        index=False
    )
    print("-> Ghi 'trips' thành công.")
except Exception as e:
    print(f"Lỗi khi ghi 'trips': {e}")

# 4. GHI BẢNG 'stop_times' (từ file stop_times.txt)
try:
    print(f"Đang ghi bảng 'stop_times' vào schema '{SCHEMA}'...")
    feed.stop_times.to_sql(
        'stop_times',
        engine,
        schema=SCHEMA,
        if_exists='replace',  # dùng 'append' nếu muốn ghi bổ sung
        index=False
    )
    print("-> Ghi 'stop_times' thành công.")
except Exception as e:
    print(f"Lỗi khi ghi 'stop_times': {e}")
