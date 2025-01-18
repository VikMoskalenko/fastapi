import json
import string
from http.client import HTTPException
from random import random
from typing import Annotated
from urllib import request

import aiofiles
from fastapi import FastAPI, Request,Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from httptools import HttpRequestParser

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/")
async def root(request: Request, long_url: Annotated[str, Form()]):
    short_url = "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(5)]
    )
    async with aiofiles.open("urls.json", "r") as f:
        existing_data = json.loads(await f.read())
    async with aiofiles.open("urls.json", "w") as f:
        existing_data[short_url] = long_url
        await f.write(json.dumps({ short_url: long_url,}))
    return{"message": f"Shortened url is {short_url}"}

@app.get("/{short_url}")
async def convert_url(short_url: str):
    async with aiofiles.open("urls.json", "r") as f:
        redirect_url = json.loads(await f.read()).get(short_url)
    if redirect_url is None:
        raise HTTPException(status_code=404, detail="Url is not found")
    else:
        return RedirectResponse(redirect_url)






@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
