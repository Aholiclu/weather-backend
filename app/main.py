from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import requests
import pandas as pd
from datetime import datetime, timedelta
import uvicorn

from app.database import get_db, engine
from app import models, crud

# 创建数据库表（首次运行自动建表）
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="全栈天气数据 API (PostgreSQL版)")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- 城市经纬度映射 ----------
CITY_COORDS = {
    "guiyang": {"lat": 26.65, "lon": 106.63},
    "beijing": {"lat": 39.90, "lon": 116.40},
    "shanghai": {"lat": 31.23, "lon": 121.47},
    "guangzhou": {"lat": 23.13, "lon": 113.26},
    "shenzhen": {"lat": 22.54, "lon": 114.06},
    "chengdu": {"lat": 30.57, "lon": 104.07},
    "wuhan": {"lat": 30.59, "lon": 114.30},
    "xian": {"lat": 34.34, "lon": 108.94},
}

def clean_temperature_data(raw_records: list) -> list:
    if not raw_records: return []
    df = pd.DataFrame(raw_records)
    df = df[(df['value'] > -20) & (df['value'] < 50)]
    df['value'] = df['value'].interpolate(method='linear', limit_direction='both')
    return df.to_dict(orient='records')

def fetch_real_weather_data(city: str, days: int) -> list:
    coords = CITY_COORDS.get(city)
    if not coords:
        raise ValueError(f"不支持的城市: {city}")
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={coords['lat']}&longitude={coords['lon']}"
        f"&daily=temperature_2m_max&timezone=Asia/Shanghai"
        f"&start_date={(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')}"
        f"&end_date={datetime.now().strftime('%Y-%m-%d')}"
    )
    res = requests.get(url)
    data = res.json()
    return [{"date": d, "value": round(t, 1)} for d, t in zip(data['daily']['time'], data['daily']['temperature_2m_max'])]

@app.get("/")
def root():
    return {"message": "Weather API with PostgreSQL is running!"}

@app.get("/api/weather")
def get_weather(
    city: str = Query(...),
    days: int = Query(30),
    db: Session = Depends(get_db)
):
    try:
        raw_data = fetch_real_weather_data(city, days)
    except Exception as e:
        return {"code": 500, "message": str(e)}
    
    cleaned_data = clean_temperature_data(raw_data)
    values = [d['value'] for d in cleaned_data]
    # 在 get_weather 函数中
    stats = {
    "avg": round(sum(values) / len(values), 2),
    "max": max(values),
    "min": min(values),
    "count": len(values)
    }
    # 保存到数据库（传递浮点数，crud 内部会转换）
    crud.save_query_history(db, city, stats["avg"], stats["max"], stats["min"])

    return {"code": 200, "city": city, "data": cleaned_data, "stats": stats}

# 🔥 新增：获取历史记录接口
@app.get("/api/history")
def get_history(limit: int = Query(20), db: Session = Depends(get_db)):
    history = crud.get_recent_history(db, limit)
    return {"code": 200, "data": history}