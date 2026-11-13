from fastapi import FastAPI
from contextlib import asynccontextmanager

# Import Router
from app.api.v1.endpoints.events import router as events_router
# Import hooks
from app.core.redis import init_redis, close_redis 


@asynccontextmanager
async def lifespan(app: FastAPI):
    # connecting to DB/Redis
    print(" Events Microservice starting up... Connecting to Redis...")
    await init_redis()
    yield
    #  closing connections
    print("Events Microservice shutting down... Closing Redis connection...")
    await close_redis()


app = FastAPI(
    title="ERP Events & Webhook Microservice",
    description="High-performance async ingestion service for webhooks and alerts.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",      # Swagger UI endpoint
    redoc_url="/redoc"     # Alternative documentation UI
)

# Health Check Endpoint. Used by load balancers to verify the microservice is alive.
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "events_microservice","version": "1.0.0"}

# Mount Router under /api/v1
app.include_router(events_router, prefix="/api/v1")