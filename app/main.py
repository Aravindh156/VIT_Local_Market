from fastapi import FastAPI
from app.database import engine, SessionLocal

from app import models
from app.routers import customer, retailer, admin
import json
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 👇 Add this middleware!
origins = [
    "http://127.0.0.1:5500",  # Frontend served via Live Server
    "http://localhost:5500",  # Alternative localhost setup
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # In production, specify allowed frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables
models.Base.metadata.create_all(bind=engine)

# Load data from JSON into DB (only if products table is empty)
def load_inventory():
    db = SessionLocal()
    if db.query(models.Product).first():
        db.close()
        return  # Skip if already populated

    file_path = os.path.join("app", "datasets", "retailer_datasets.json")
    with open(file_path, "r") as file:
        data = json.load(file)

    retailer_map = {}  # Map for assigning retailer IDs

    for retailer_name, products in data.items():
        location, name = retailer_name.split("_", 1)

        # Create a dummy user for the retailer
        user = models.User(username=retailer_name.lower(), password="test123", role="retailer")
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create retailer entry
        retailer = models.Retailer(user_id=user.id, location=location, name=name, deliverable=True)
        db.add(retailer)
        db.commit()
        db.refresh(retailer)

        retailer_map[retailer_name] = retailer.id

        # Add all products
        for product in products:
            prod = models.Product(
                retailer_id=retailer.id,
                name=product["name"],
                price=product["price"],
                quantity=product["quantity"],
                category=product["category"]
            )
            db.add(prod)

    db.commit()
    db.close()

# Load JSON data once at startup
load_inventory()

@app.get("/")
def read_root():
    return {"msg": "Local Market Hub backend is running!"}

from app.routers import customer
app.include_router(customer.router)

from app.routers import retailer
app.include_router(retailer.router)

from app.routers import admin
app.include_router(admin.router)