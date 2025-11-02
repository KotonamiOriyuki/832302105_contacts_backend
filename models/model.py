from pydantic import BaseModel
from typing import Optional
# Data structure
# template for register
class UserRegister(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    # debug: use Optional[str] instead of address: str = None
    # if use strong str, it will throw 422 unsupported error if we
    # do not enter this thing
    address: Optional[str] = None

# template for login
class UserLogin(BaseModel):
    account: str
    password: str

# template for changing profile
# update: so does the debug revealed
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

# template for password change
class PasswordChange(BaseModel):
    old_password: str
    new_password: str

# template for a contact information
class ContactData(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None