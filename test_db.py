from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL:", DATABASE_URL)

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ 数据库连接成功！", result.scalar())
except Exception as e:
    print("❌ 连接失败：", e)