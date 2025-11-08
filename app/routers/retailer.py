from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas


router = APIRouter(prefix="/retailer", tags=["Retailer"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register_retailer(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.role != "retailer":
        raise HTTPException(status_code=403, detail="Invalid role for retailer registration")

    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password,
        role="retailer",
        status="pending"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Registration received. Awaiting admin approval."}


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if db_user.role != "retailer":
        raise HTTPException(status_code=403, detail="Not a retailer account")
    if db_user.status != "active":
        raise HTTPException(status_code=403, detail="Account pending admin approval")
    
    return {"message": "Login successful"}


@router.get("/inventory/{retailer_id}")
def get_inventory(retailer_id: int, db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.retailer_id == retailer_id).all()

@router.get("/orders/{retailer_id}")
def get_orders(retailer_id: int, db: Session = Depends(get_db)):
    return db.query(models.Order).filter(models.Order.retailer_id == retailer_id).all()

@router.post("/delivery-status")
def set_delivery_status(retailer_id: int, deliverable: bool, db: Session = Depends(get_db)):
    retailer = db.query(models.Retailer).filter(models.Retailer.id == retailer_id).first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found")
    retailer.deliverable = deliverable
    db.commit()
    return {"message": f"Delivery status set to {deliverable}"}

@router.post("/inventory/update")
def update_inventory(update: schemas.InventoryUpdate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(
        models.Product.retailer_id == update.retailer_id,
        models.Product.name == update.product_name
    ).first()

    if not product:
        product = models.Product(
            retailer_id=update.retailer_id,
            name=update.product_name,
            quantity=update.new_qty,
            price=update.price if update.price is not None else 0.0,
            category=update.category if update.category is not None else "Uncategorized"
        )
        db.add(product)

    product.quantity = update.new_qty

    # ✅ Update optional fields if provided
    if update.price is not None:
        product.price = update.price
    if update.category is not None:
        product.category = update.category

    db.commit()
    return {
        "message": f"{product.name} updated to {update.new_qty} units",
        "price": product.price,
        "category": product.category
    }

@router.get("/notifications/{retailer_id}", response_model=list[schemas.NotificationOut])
def get_notifications(retailer_id: int, db: Session = Depends(get_db)):
    return db.query(models.Notification).filter(
        models.Notification.retailer_id == retailer_id
    ).order_by(models.Notification.timestamp.desc()).all()

@router.post("/notifications/read/{notification_id}")
def mark_notification_as_read(notification_id: int, db: Session = Depends(get_db)):
    notif = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}