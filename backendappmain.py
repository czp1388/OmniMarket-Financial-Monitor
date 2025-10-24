# 使用 Python 创建文件，避免编码问题
python -c "
content = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import market

app = FastAPI(
    title=\"寰宇多市场金融监控系统\",
    version=\"0.1.0\",
    description=\"多市场金融数据监控与分析系统\"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[\"*\"],
    allow_credentials=True,
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

app.include_router(market.router, prefix=\"/api/v1\", tags=[\"market\"])

@app.get(\"/\")
async def root():
    return {\"message\": \"欢迎使用寰宇多市场金融监控系统 API\"}

@app.get(\"/health\")
async def health_check():
    return {\"status\": \"ok\"}
'''

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
"