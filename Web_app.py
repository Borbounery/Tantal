from fastapi import FastAPI, Depends, Cookie, HTTPException, status, Response, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from jwt import PyJWT
from typing import Optional
import os, base64, json
import shutil
import tempfile

INITIATE_SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

MAX_FILE_SIZE = 20 * 1024 * 1024
dialogi = [{"11-11-1111":"Связь установлена."}]

# Место для того, чтобы при дальнейшей реализации
# подключить базу данных

Database = {
    "11-11-1111":{
        "password":"112233445566",
        "user_id":"1",
    },
    "22-22-2222":{
        "password":"112233445566",
        "user_id":"2",
    }
}

class LoginRequest(BaseModel):
    identificator: str
    password: str

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
jwt = PyJWT()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": 111111111111111111111111})
    encoded_jwt = jwt.encode(key=INITIATE_SECRET_KEY, algorithm=ALGORITHM, payload=to_encode)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        print(token, "token")
        decoded_token = jwt.decode(jwt=token,key=INITIATE_SECRET_KEY,algorithms=[ALGORITHM])
        print(decoded_token)
        return decoded_token
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Invalid token")

def c_e(
              padding,
              data,
              additional_padding):

        return ''.join(chr((ord(symbol) + padding + (i+additional_padding)) % 1114112) for i, symbol in enumerate(data, start=1))

def c_d(
              padding,
              data,
              additional_padding):

    return ''.join(chr((ord(symbol) - padding - (i+additional_padding)) % 1114112) for i, symbol in enumerate(data, start=1))

@app.post("/sendMessage")
async def smsg(request: Request):
    print(request.cookies)
    global dialogi
    if request.cookies.get("AAA-X"):
        r_b = await request.body()
        print(c_d(3, r_b.decode("utf-8"), 5))
        jsn_r = json.loads(c_d(3, r_b.decode("utf-8"), 5))
        act = decode_access_token(request.cookies.get("AAA-X"))
        dialogi.append({act["sub"]:jsn_r['message']})
        return JSONResponse({"status":"success"})
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Invalid token")

@app.get("/getMe")
async def getme(request: Request):
    print(request.cookies)
    global dialogi
    if request.cookies.get("AAA-X"):

        act = decode_access_token(request.cookies.get("AAA-X"))
        return JSONResponse({"user_name":act["sub"]})
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Invalid token")

@app.get("/getMyDialogs")
async def dials(request: Request):
    print(request.cookies)
    if request.cookies.get("AAA-X"):
        act = decode_access_token(request.cookies.get("AAA-X"))
        return JSONResponse(dialogi)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Invalid token")
    
@app.get("/")
async def main(request: Request):
    print(request.cookies)
    if request.cookies.get("AAA-X"):
        act = decode_access_token(request.cookies.get("AAA-X"))
        if act["sub"] == "11-11-1111":
            with open("main2.html", "r", encoding='utf-8') as f:
                content = f.read()
            return HTMLResponse(content=content)
        elif act["sub"] == "22-22-2222":
            with open("main.html", "r", encoding='utf-8') as f:
                content = f.read()
            return HTMLResponse(content=content)

    else:
        with open("login.html", "r", encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join("uploaded_files/", filename)
    
    # Check if the file exists
    if os.path.isfile(file_path):
        return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')
    else:
        raise HTTPException(status_code=404, detail="Файл не найден")

@app.post("/sendFile")
async def create_upload_file(request: Request):
    jsn = json.loads(c_d(3, await request.text(), 5))
    file_name = jsn.get("fileName")
    file_base64 = jsn.get("fileBase64")
    
    if not file_name or not file_base64:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Отсутствует fileName или fileBase64")

    if ".exe" in file_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Исполняемые файлы запрещены к отправке")
    
    with tempfile.NamedTemporaryFile(dir="uploaded_files", prefix=file_name, delete=False) as temp_file:
        file_base64=file_base64.split(',')[1]
        temp_file.write(base64.b64decode(file_base64))
        temp_file.flush()
        file_size = temp_file.tell()
        
        if file_size > MAX_FILE_SIZE:
            temp_file.close()
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Объём файлов превышает 20 MB")
        with open(f"uploaded_files/{file_name}", "wb") as f:
            f.write(base64.b64decode(file_base64))
    return {"download_url": f'<a href="http://127.0.0.1:8000/download/{file_name}">{file_name}</a>'}





@app.post("/token")
async def login(request: LoginRequest, response: Response):
    if not request.identificator or not request.password:
        missing_field = "identificator" if not request.identificator else "password"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"No field {missing_field}")
    if request.identificator in list(Database.keys()):
        access_token = create_access_token(data={"sub": request.identificator, "user_id":Database[request.identificator]["user_id"]})
        response.set_cookie(key="AAA-X", value=access_token)
        return {"status": "success", "token": access_token}
    else:
        return {"status": "error", "msg": "Invalid credentials"}
