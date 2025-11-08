from pydantic import BaseModel

# -------- User Related --------
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str  # 'customer', 'retailer'

class UserLogin(BaseModel):
    username: str
    password: str

# class TokenResponse(BaseModel):
#     access_token: str
#     token_type: str
    
# -------- Order --------
class OrderCreate(BaseModel):
    retailer_id: int
    product: str
    quantity: int

# -------- Product --------
class ProductOut(BaseModel):
    name: str
    price: float
    quantity: int
    category: str

    class Config:
        orm_mode = True

class InventoryUpdate(BaseModel):
    retailer_id: int
    product_name: str
    new_qty: int
    price: float | None = None
    category: str | None = None

from datetime import datetime

class NotificationOut(BaseModel):
    id: int
    message: str
    is_read: bool
    timestamp: datetime

    class Config:
        orm_mode = True