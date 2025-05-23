from fastapi import APIRouter, Header, UploadFile, Form
from fastapi.params import File
from fastapi_decorators import depends
from fastapi import Request
from SharedBackend.middlewares import SDKMiddleware
from config import get_settings
from services import *
from services.scanner import ScannerService

# from managers import *

router = APIRouter(prefix="/scanner")
settings = get_settings()
scanner_service = ScannerService()


@router.post("/udder-check")
async def udder_check(image: UploadFile = File(...)):
    result = await scanner_service.get_udder_type(image)
    return result


@router.post("/bcs")
async def udder_check(image: UploadFile = File(...)):
    result = await scanner_service.get_bcs(image)
    return result


@router.post("/breed")
async def udder_check(image: UploadFile = File(...)):
    result = await scanner_service.get_breed(image)
    return result


@router.post("/breed-grade")
async def udder_check(image: UploadFile = File(...), breed=None):
    result = await scanner_service.get_breed_grade(image=image, breed=breed)
    return result

@router.post("/aes", response_model=dict)
async def animal_economic_status(
    breed: str = Form(...),
    breed_grade: str = Form(...),
    bcs_score: str = Form(...),          # JSON string → will convert below
    udder_pred: str = Form(...),
    skin_pred: str = Form(...),
    worm_load: str = Form(...),
    language: str = Form("en"),
):
    """
    Proxy to the Scanner micro-service that computes *Animal Economic Status*.

    The endpoint expects the **same multipart/form-data fields** you used in Postman.
    `bcs_score` arrives as a JSON string, so we decode it before forwarding.
    """
    # Validate & convert the JSON string that Postman sends
    try:
        bcs_dict = json.loads(bcs_score)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="`bcs-score` must be valid JSON")

    result = await ScannerService.get_animal_economic_status(
        breed=breed,
        breed_grade=breed_grade,
        bcs_score=bcs_dict,
        udder_pred=udder_pred,
        skin_pred=skin_pred,
        worm_load=worm_load,
        language=language,
    )
    return result