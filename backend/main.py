import os
import uuid
from datetime import datetime, timezone

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_NAME = os.getenv("DYNAMODB_TABLE", "url-shortener")
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")

# Boto3 usa automáticamente las credenciales temporales del rol IAM de la EC2
dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

app = FastAPI(title="Acortador de enlaces")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ShortenRequest(BaseModel):
    original_url: HttpUrl


@app.post("/shorten")
def shorten(body: ShortenRequest):
    short_code = str(uuid.uuid4())
    original_url = str(body.original_url)
    table.put_item(
        Item={
            "short_code": short_code,
            "original_url": original_url,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return {
        "short_code": short_code,
        "original_url": original_url,
        "short_url": f"{PUBLIC_BASE_URL}/{short_code}",
    }


@app.get("/urls/{short_code}")
def get_url_info(short_code: str):
    item = table.get_item(Key={"short_code": short_code}).get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Enlace no encontrado")
    return item


@app.get("/{short_code}")
def redirect(short_code: str):
    item = table.get_item(Key={"short_code": short_code}).get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Enlace no encontrado")
    return RedirectResponse(url=item["original_url"], status_code=307)