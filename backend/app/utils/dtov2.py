from datetime import datetime

from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional
#User
class UserRegisterDTO(BaseModel):
    fname: constr(min_length=2, max_length=50)
    lname: constr(min_length=2, max_length=50)
    username: constr(min_length=5, max_length=20)
    email: EmailStr
    phone: constr(regex=r'^\+?(\d{1,4})?[\s-]?\(?\d{1,3}\)?[\s-]?\d{1,3}[\s-]?\d{1,4}$')
    password: constr(min_length=8, max_length=20)

class UserList(BaseModel):
    name: Optional[str]
    username: Optional[str]
    email: str
    phone: constr(regex=r'^\+?(\d{1,4})?[\s-]?\(?\d{1,3}\)?[\s-]?\d{1,3}[\s-]?\d{1,4}$')

    class Config:
        orm_mode = True
class ManagerRegisterDTO(BaseModel):
    name: constr(min_length=2, max_length=50)
    username: constr(min_length=5, max_length=20)
    email: EmailStr
    phone: constr(regex=r'^\+?(\d{1,4})?[\s-]?\(?\d{1,3}\)?[\s-]?\d{1,3}[\s-]?\d{1,4}$')
    password: constr(min_length=8, max_length=20)

class UserDTO(BaseModel):
    email: EmailStr
    username: constr(min_length=5, max_length=20)
    password: constr(min_length=8, max_length=20)
    public_id: Optional[str] = None
#Driver
class DriverRegisterDTO(BaseModel):
    name: constr(min_length=2, max_length=50)
    username: constr(min_length=5, max_length=20)
    email: EmailStr
    phone: constr(regex=r'^\+?(\d{1,4})?[\s-]?\(?\d{1,3}\)?[\s-]?\d{1,3}[\s-]?\d{1,4}$')
    password: constr(min_length=8, max_length=20)
    blx: constr(min_length=1, max_length=100)
    bus_id: int

class DriverUpdateDTO(BaseModel):
    name: constr(min_length=2, max_length=50)
    username: constr(min_length=5, max_length=20)
    email: EmailStr
    phone: constr(regex=r'^\+?(\d{1,4})?[\s-]?\(?\d{1,3}\)?[\s-]?\d{1,3}[\s-]?\d{1,4}$')
    blx: constr(min_length=1, max_length=100)
    bus_id: int
#Auth
class AuthDTO(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=20)
class RefreshTokenDTO(BaseModel):
    refresh_token: str
#Bus
class BusDTO(BaseModel):
    bus_id: int
    plate_number: str
    name: Optional[str]
    model: Optional[str]
    status: str
    route_id: int

    class Config:
        orm_mode = True
#Man
class ManDTO(BaseModel):
    name: Optional[str]
    username: Optional[str]
    email: str
    phone: constr(regex=r'^\+?(\d{1,4})?[\s-]?\(?\d{1,3}\)?[\s-]?\d{1,3}[\s-]?\d{1,4}$')

    class Config:
        orm_mode = True
#Noti
class NotiDTO(BaseModel):
    id: int
    message: str
    read: bool
    created_at: datetime
    type: Optional[str]  # Optional type of notification
    link: Optional[str]   # Optional link for the notification
    user_id: int # Optional user ID

    class Config:
        orm_mode = True