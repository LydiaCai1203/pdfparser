from fastapi import APIRouter

from app.handler.v1 import pdf_parser


api_v1_router = APIRouter()
api_v1_router.include_router(pdf_parser.router, prefix="")
