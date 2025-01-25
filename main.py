import json
import os
import string
import random
from gc import collect
from typing import Annotated
from urllib import request
import motor.motor_asyncio
import aiofiles
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from httptools import HttpRequestParser

app = FastAPI()
MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_USER = os.environ.get("MONGO_USER", "root")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "example")
templates = Jinja2Templates(directory="templates")
db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_HOST,27017,username=MONGO_USER, password=MONGO_PASSWORD)
app_db = db_client["url_shortener"]
collection = app_db["urls"]
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/")
async def root(request: Request, long_url: Annotated[str, Form()]):
    short_url = "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(5)]
    )
    await collection.insert_one({"short_url": short_url, "long_url": long_url})
    return{"message": f"Shortened url is {short_url}"}


@app.get("/{short_url}")
async def convert_url(short_url: str):
    collection_data = await collection.find_one({"short_url": short_url})
    redirect_url = collection_data.get("long_url") if collection_data else None
    collection_data = await collection.update_one({"short_url": short_url}, {"$inc":{"clicks": 1} })
    print(
            f"Short URL: {short_url} || Clicks : {collection_data.modified_count}"
    )
    if redirect_url is None:
        raise HTTPException(status_code=404, detail="Url is not found")
    else:
        return RedirectResponse(redirect_url)

@app.get("/{short_url}/{user_id}stats")
async def stats(request: Request, short_url: str, user_id: int):
    collection_data = await collection.find_one({"short_url": short_url, "user_id": user_id})
    if collection_data is None:
        raise HTTPException(status_code=404, detail="Url is not found")
    return templates.TemplateResponse(request= request, name="stats.html",context= {"url_data": collection_data})

@app.post("/{short_url}/{user_id}/stats")
async def edit_stats(request: Request, short_url: str, user_id: int, long_url: Annotated[str, Form()]):

    await collection.update_one({"short_url": short_url}, {"$set":{ "long_url": long_url}} )
    collection_data = await collection.find_one({"short_url": short_url, "user_id": user_id})
    return templates.TemplateResponse(request= request, name="stats.html",context= {"url_data": collection_data})



