from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import ollama
import os
from dotenv import load_dotenv
from datetime import  datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext



API_KEYS_CREDIT = {os.getenv("API_KEY"): 2}

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

db = {
    "Tim": {
        "username": "Tim",
        "full_name": "Tim XOXO",
        "email": "askip@gmail.com",
        "hashed_password": "$2b$12$VXiYDV6HJCEXEI1LbD.jWutF2URWr.LIs70xsVvp6jolyy17ZZ/u2",
        "disabled": False
    }
}

app = FastAPI()

def verify_api_key(x_key: str = Header(None)): 
    credit = API_KEYS_CREDIT.get(x_key, 0)
    if credit <= 0:
        raise HTTPException(status_code=401, detail="Invalid API key, or no more credits left")
    return x_key




@app.post("/generate")


# def generate(request: Prompt):
#     response = ollama.chat(model="deepseek-r1:7b", messages=[{"role": "user", "content": request.prompt}])
#     return {"response": response["message"]["content"]}

def generate(prompt: str, x_key: str = Depends(verify_api_key)):
    API_KEYS_CREDIT[x_key] -= 1
    response = ollama.chat(model="deepseek-r1:7b", messages=[{"role": "user", "content": prompt}])
    return {"response": response["message"]["content"]}



@app.get("/test")
def test():
    return {"message": "Hello World"}


# @app.post ("/create")

class Name(BaseModel):
    name: str

@app.post("/create")
def create(name: Name):
    return {"name": name}


class Token(BaseModel):
    access_token: str
    token: str

class TokenData(BaseModel):
    username: str or None = None

class User(BaseModel):
    username: str
    email: str or None = None
    full_name: str or None = None
    disabled: bool or None = None

class UserInDB(User):
    hashed_password: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_data = db[username]
        return UserInDB(**user_data)


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "1", "owner": current_user.username}]


pwd = get_password_hash("askip")
print(pwd)