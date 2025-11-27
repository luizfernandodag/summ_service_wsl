from fastapi import APIRouter

router = APIRouter()

@router.post("/summarize")
def summarize(payload: dict):
    return {"summary": "Not implemented"}
