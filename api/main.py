from fastapi import FastAPI

from api.routes.health import router as health_router
from api.routes.pipeline import router as pipeline_router
from api.routes.sales import router as sales_router
from api.routes.prediction import router as prediction_router

app = FastAPI(
    title="RetailPulse API",
    description="API for the RetailPulse data platform.",
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(pipeline_router)
app.include_router(sales_router)
app.include_router(prediction_router)