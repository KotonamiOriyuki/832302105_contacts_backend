import secrets
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Header
from pymongo import MongoClient
from models.model import UserRegister, UserLogin, UserUpdate, PasswordChange, ContactData

router = APIRouter()
client = MongoClient("mongodb://localhost:27017/")
db = client['contacts']
# We would like to use a list to store the active user
token_list = {}
users_collection = db['users']
contacts_collection = db['contacts']

# deployment on web server
backend_url = "localhost:8000"

def findMaxUID():
    if db is None:
        raise HTTPException(status_code=500, detail="Disconnected from MongoDB")
    # counter would +1 if a user is found on mongodb
    counter = db['counters'].find_one_and_update(
        {"_id": "user_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return counter.get("seq", 1)

def getToken(token: str):
    # auto login using token
    # when login, the backend would provide a token
    if not token:
        raise HTTPException(status_code=401, detail="Not login")
    uid = token_list.get(token)
    # the token will not in the list if the session is expired
    if not uid:
        raise HTTPException(status_code=401, detail="Login expired")
    user = users_collection.find_one({"uid": uid})
    # Rarely happen actually, we write this just for the code robustness
    if not user:
            raise HTTPException(status_code=404, detail="User not exist!")
    return user

def getUIDToken(token: str):
    # auto login using token
    # when login, the backend would provide a token
    if not token:
        raise HTTPException(status_code=401, detail="Not login")
    uid = token_list.get(token)
    # the token will not in the list if the session is expired
    if not uid:
        raise HTTPException(status_code=401, detail="Login expired")
    return uid


# test connection
@router.get("/api/")
async def root():
    return {"message": "Connected"}

@router.post("/api/register")
async def register(user: UserRegister):
    if db is None:
        raise HTTPException(status_code=500, detail="Disconnected from MongoDB")

    # Find existing data
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    if users_collection.find_one({"phone": user.phone}):
        raise HTTPException(status_code=400, detail="Phone already registered")

    user_uid = findMaxUID()
    user_data = {
        "uid": user_uid,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "password": user.password,
        "address": user.address or "",
    }
    # store in the mongodb
    users_collection.insert_one(user_data)

    return {'message': 'Registered'}

@router.post("/api/login")
async def login(user: UserLogin):
    if db is None:
        raise HTTPException(status_code=500, detail="Disconnected from MongoDB")

    # support to login using UID, email, phone, name
    # we would like to find someone using password instead of guessing wheter the input is uid, email, etc
    query = {"password": user.password}
    if user.account.isdigit():
        query["uid"] = int(user.account)
    else:
        # return if one of them is matched
        query["$or"] = [
            {"email": user.account},
            {"phone": user.account},
            {"name": user.account}
        ]

    # debug: tabbing error, this result in return 200 OK without anything
    db_user = users_collection.find_one(query)
    if not db_user:
        raise HTTPException(status_code=401, detail="Wrong password or username")

    # generate a base64 encrypted token
    token = secrets.token_urlsafe(32)
    token_list[token] = db_user["uid"]

    return {
            "token": token,
            "uid": db_user["uid"],
            "name": db_user["name"],
        }

@router.post("/api/logout")
async def logout(authorization: str = Header(None)):
    # check if the token is expired
    if authorization and authorization in token_list:
        del token_list[authorization]
        return {"message": "Logged out"}
    else:
        return {"message": "You've been logged out or not login!"}

@router.get("/api/user")
async def get_user(authorization: str = Header(None)):
    if db is None:
        raise HTTPException(status_code=500, detail="Disconnected from MongoDB")

    try:
        user = getToken(authorization)
        return {
                # debug "user" -> "uid" typo for display error
                "uid": user["uid"],
                "name": user["name"],
                "email": user["email"],
                "phone": user["phone"],
                "address": user.get("address") or "",
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/user")
async def update_user(data: UserUpdate, authorization: str = Header(None)):
    if db is None:
        raise HTTPException(status_code=500, detail="Disconnected from MongoDB")

    try:
        user = getToken(authorization)
        # filter the empty stuff
        update_data = {k: v for k, v in data.dict().items() if v is not None}
        # if something updated
        if update_data:
            if 'email' in update_data and update_data['email'] != user["email"]:
                if users_collection.find_one({"email": user["email"], "uid": {"$ne": user["uid"]}}):
                    raise HTTPException(status_code=400, detail="Email already registered")
            if "phone" in update_data and update_data["phone"] != user["phone"]:
                if users_collection.find_one({"phone": update_data["phone"], "uid": {"$ne": user["uid"]}}):
                    raise HTTPException(status_code=400, detail="Phone already registered")
            # debug: inappropriate bracket and tab settings result in 500 error
            users_collection.update_one({"uid": user["uid"]}, {"$set": update_data})

        return {"message": "User updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/user/password")
async def change_password(data: PasswordChange, authorization: str = Header(None)):
    if db is None:
        raise HTTPException(status_code=500, detail="Disconnected from MongoDB")

    try:
        user = getToken(authorization)
        if user["password"] != data.old_password:
            raise HTTPException(status_code=400, detail="Incorrect old password")
        users_collection.update_one({"uid": user["uid"]}, {"$set": {"password": data.new_password}})
        return {"message": "Password changed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/contacts")
async def get_contacts(authorization: str = Header(None)):
    if db is None:
        raise HTTPException(status_code=500, detail="Disconnected from MongoDB")

    try:
        user = getToken(authorization)
        contacts = list(contacts_collection.find({"owner_uid": user["uid"]}))
        # debug: transform to string
        for contact in contacts:
            contact["_id"] = str(contact["_id"])
        return contacts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/contacts")
async def create_contact(contact: ContactData, authorization: str = Header(None)):
    if db is None:
        raise HTTPException(status_code=500, detail="Disconnected from MongoDB")
    try:
        user = getToken(authorization)
        contact_data = {
            "owner_uid": user["uid"],
            "name": contact.name,
            "email": contact.email or "",
            "phone": contact.phone or "",
            "address": contact.address or "",
        }
        result = contacts_collection.insert_one(contact_data)
        return {"message": "Added", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/contacts/{contact_id}")
async def update_contact(contact_id: str, contact: ContactData, authorization: str = Header(None)):
    if db is None:
        raise HTTPException(status_code=500, detail="Disconnected from MongoDB")
    try:
        user = getToken(authorization)
        update_data = {
            "name": contact.name,
            "email": contact.email or "",
            "phone": contact.phone or "",
            "address": contact.address or "",
        }
        # debug: use ObjectId to transform string to mongodb id type, instead of string -> search error, so does code below
        result = contacts_collection.update_one(
            {"_id": ObjectId(contact_id), "owner_uid": user["uid"]},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "Updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/contacts/{contact_id}")
async def delete_contact(contact_id: str, authorization: str = Header(None)):
    if db is None:
        raise HTTPException(status_code=500, detail="Disconnected from MongoDB")
    try:
        user = getToken(authorization)
        result = contacts_collection.delete_one(
            {"_id": ObjectId(contact_id), "owner_uid": user["uid"]}
        )
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User does not exist")
        return {"message": "Deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/addfriend/{uid}")
async def add_friend(uid: int, authorization: str = Header(None)):
    if db is None:
        raise HTTPException(status_code=500, detail="Disconnected from MongoDB")

    auth_token = authorization
    current_user = getToken(auth_token)

    friend = users_collection.find_one({"uid": uid})
    if not friend:
        raise HTTPException(status_code=404, detail="User does not exist")
    if friend["uid"] == current_user["uid"]:
        raise HTTPException(status_code=400, detail="You cannot add yourself as a friend")

    # if something has recorded identical to the new one
    existing = contacts_collection.find_one({
        "owner_uid": current_user["uid"],
        "$or": [
            {"email": friend.get("email")},
            {"phone": friend.get("phone")}
        ]
    })
    if existing:
        raise HTTPException(status_code=400, detail="This contact is already in use")

    contact_data = {
        "owner_uid": current_user["uid"],
        "name": friend["name"],
        "email": friend.get("email") or "",
        "phone": friend.get("phone") or "",
        "address": friend.get("address") or "",
    }
    contacts_collection.insert_one(contact_data)


    return {"message": "Added"}
