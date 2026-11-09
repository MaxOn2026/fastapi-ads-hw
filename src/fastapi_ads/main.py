from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, users, advertisements

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Advertisement Service")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(advertisements.router)