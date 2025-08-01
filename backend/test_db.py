from database.db import engine
from sqlalchemy import text

def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM facilities"))
            count = result.fetchone()[0]
            print(f"✅ DB 연결 성공! 시설물 개수: {count}개")
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")

if __name__ == "__main__":
    test_connection()