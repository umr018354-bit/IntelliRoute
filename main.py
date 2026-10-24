"""
IntelliRoute backend entrypoint.

Run with:  python main.py
(creates DB tables + seed data automatically on first run, against
whatever DATABASE_URL points to — a Supabase/PostgreSQL connection string
as of Phase 2)
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from database import Base, engine
from utils.seed import init_and_seed
from routers import auth, orders, drivers, vehicles, routes, ml, batches, simulation, analytics

# Create tables + seed demo data on startup (idempotent — skips if already seeded)
init_and_seed()

app = FastAPI(
    title="IntelliRoute API",
    description="Intelligent Delivery & Logistics Optimization System — Phase 2 backend (ML, batching, live simulation, analytics)",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global error handling — never leak raw Python tracebacks to the frontend
# ---------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request data", "errors": exc.errors()},
    )


@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred."},
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(drivers.router)
app.include_router(vehicles.router)
app.include_router(routes.router)
app.include_router(ml.router)
app.include_router(batches.router)
app.include_router(simulation.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "IntelliRoute API", "phase": 2}


@app.get("/api/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
