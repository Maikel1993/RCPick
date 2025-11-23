from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.api.routes_buyer import router as buyer_router
from app.api.routes_match import router as match_router
from app.api.routes_listings import router as listings_router
from app.api.routes_leads import router as leads_router  # 👈 NUEVO
from app.api.routes_dealers import router as dealers_router  # 👈 NUEVO
from app.api import routes_leads, routes_match  # 👈 añade routes_match

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Autofinder Backend",
    version="0.1.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend Autofinder funcionando"}

app.include_router(buyer_router)
app.include_router(match_router)
app.include_router(listings_router)
app.include_router(leads_router)   # 👈 NUEVO
app.include_router(dealers_router)  # 👈 NUEVO
app.include_router(routes_match.router)