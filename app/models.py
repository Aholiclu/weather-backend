from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(50), nullable=False, default="guest")
    city = Column(String(50), nullable=False)
    query_date = Column(DateTime, nullable=False)
    avg_temp = Column(Float)      # 浮点数
    max_temp = Column(Integer)    # 整数
    min_temp = Column(Integer)    # 整数
    created_at = Column(DateTime, server_default=func.now())