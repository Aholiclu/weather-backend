from sqlalchemy.orm import Session
from app.models import QueryHistory
from datetime import datetime

def save_query_history(db: Session, city: str, avg_temp: float, max_temp: float, min_temp: float):
    """保存查询记录到数据库（自动转换类型）"""
    db_record = QueryHistory(
        user_id="guest",
        city=city,
        query_date=datetime.now(),
        avg_temp=round(float(avg_temp), 2),      # 保留两位小数
        max_temp=int(round(float(max_temp))),     # 转为整数
        min_temp=int(round(float(min_temp)))      # 转为整数
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_recent_history(db: Session, limit: int = 20):
    return db.query(QueryHistory).order_by(QueryHistory.created_at.desc()).limit(limit).all()