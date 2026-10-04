from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.database.database import init_db, close_db
from app.api import health_router, twin_router, websocket_router
from app.twin.state import digital_twin
from app.api.websocket import broadcast_state


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting Digital Twin Simulator...")
    
    init_db()
    
    digital_twin.set_state_callback(broadcast_state)
    await digital_twin.start()
    
    logger.info("Digital Twin Simulator started")
    
    yield
    
    await digital_twin.stop()
    await close_db()
    logger.info("Digital Twin Simulator stopped")


app = FastAPI(
    title="Digital Twin Simulator",
    description="Real-time electric motor digital twin with anomaly detection and predictive analytics",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(twin_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    return {
        "name": "Digital Twin Simulator",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "websocket": "/ws/twin",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)