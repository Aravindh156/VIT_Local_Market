from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas


router = APIRouter(prefix="/admin", tags=["Admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Invalid role for admin registration")
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Store password as plain text (NOT recommended for production)
    new_user = models.User(username=user.username, email=user.email, password=user.password, role="admin", status="active")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "admin registered successfully", "user_id": new_user.id}

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()

    # Simple password check (plain text)
    if not db_user or user.password != db_user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if db_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    return {"message": "Login successful", "user_id": db_user.id}

@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.get("/retailers")
def get_all_retailers(db: Session = Depends(get_db)):
    return db.query(models.Retailer).all()

@router.get("/orders")
def get_all_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()

@router.get("/pending-retailers")
def get_pending_retailers(db: Session = Depends(get_db)):
    pending = db.query(models.User).filter(models.User.role == "retailer", models.User.status == "pending").all()
    return [{"id": r.id, "username": r.username, "email": r.email} for r in pending]

@router.post("/approve-retailer/{retailer_id}")
def approve_retailer(retailer_id: int, db: Session = Depends(get_db)):
    retailer = db.query(models.User).filter(models.User.id == retailer_id, models.User.role == "retailer").first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found")
    retailer.status = "active"
    db.commit()

    from app.email_utils import send_email
    send_email(
        to_email="aravindh.k2022@vitstudent.ac.in",
        subject="Retailer Approved",
        body=f"Hi {retailer.username}, your account has been approved! You can now log in and manage your inventory."
    )
    return {"message": f"Retailer {retailer.username} approved"}

@router.post("/reject-retailer/{retailer_id}")
def reject_retailer(retailer_id: int, db: Session = Depends(get_db)):
    retailer = db.query(models.User).filter(models.User.id == retailer_id, models.User.role == "retailer").first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found")
    retailer.status = "rejected"
    db.commit()

    from app.email_utils import send_email
    send_email(
        to_email=retailer.email,
        subject="Retailer Registration Rejected",
        body=f"Hi {retailer.username}, unfortunately your registration was not approved."
    )
    return {"message": f"Retailer {retailer.username} rejected"}