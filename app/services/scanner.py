import logging
from typing import Any, Dict
from typing import Dict, Union, Any, Optional
import json
import httpx
from fastapi import HTTPException, UploadFile, status

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class ScannerService:
    """
    Client wrapper around the Silofortune AI-Scanner micro-service.
    """
    # Auth & base-path pulled from your settings the same way as other sub-services
    HEADERS: Dict[str, str] = {
        # "X-API-KEY": settings.subservices.scanner.api_key,   # ⇦ adjust key name if different
        "Accept": "application/json",
    }
    BASE_URL: str = settings.ScannerSettings.base_url  # e.g. https://scanner.silofortune.com/api/v3

    @classmethod
    async def get_udder_type(
            cls,
            image: UploadFile,  # FastAPI UploadFile (or anything with .filename/.read())
            language: str = "en",  # matches the Postman “language” field
            timeout: float = 30.0,
    ) -> Any:
        """
        Hit `/udder-pred` with the cow side image and return the JSON payload
        containing `interpretation`, `recommendation`, and `value`.

        Raises
        ------
        HTTPException
            502 if the downstream service is unreachable,
            or propagates the status code returned by the scanner.
        """
        uri = "/udder-pred"
        url = f"{cls.BASE_URL}{uri}"

        # Build multipart/form-data exactly like the Postman call
        files = {
            "side-img": (image.filename, await image.read(), image.content_type or "image/jpeg"),
        }
        form = {"language": language}

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                resp = await client.post(url, headers=cls.HEADERS, data=form, files=files)
                resp.raise_for_status()
                return resp.json()

            except httpx.HTTPStatusError as exc:
                # Bubble the exact status code from the scanner so your API responds transparently
                logger.error("ScannerService responded %s: %s", exc.response.status_code, exc.response.text)
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=exc.response.json() if exc.response.headers.get("content-type") == "application/json"
                    else exc.response.text,
                ) from exc

            except httpx.RequestError as exc:
                # Network / DNS / timeout issues
                logger.exception("ScannerService unreachable: %s", exc)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Unable to reach Scanner micro-service",
                ) from exc

    @classmethod
    async def get_bcs(
            cls,
            image: UploadFile,  # FastAPI UploadFile (or anything with .filename/.read())
            language: str = "en",  # matches the Postman “language” field
            timeout: float = 30.0,
    ) -> Any:
        """
        Hit `/udder-pred` with the cow side image and return the JSON payload
        containing `interpretation`, `recommendation`, and `value`.

        Raises
        ------
        HTTPException
            502 if the downstream service is unreachable,
            or propagates the status code returned by the scanner.
        """
        uri = "/bcs-score"
        url = f"{cls.BASE_URL}{uri}"

        # Build multipart/form-data exactly like the Postman call
        files = {
            "side-img": (image.filename, await image.read(), image.content_type or "image/jpeg"),
        }
        form = {"language": language}

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                resp = await client.post(url, headers=cls.HEADERS, data=form, files=files)
                resp.raise_for_status()
                return resp.json()

            except httpx.HTTPStatusError as exc:
                # Bubble the exact status code from the scanner so your API responds transparently
                logger.error("ScannerService responded %s: %s", exc.response.status_code, exc.response.text)
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=exc.response.json() if exc.response.headers.get("content-type") == "application/json"
                    else exc.response.text,
                ) from exc

            except httpx.RequestError as exc:
                # Network / DNS / timeout issues
                logger.exception("ScannerService unreachable: %s", exc)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Unable to reach Scanner micro-service",
                ) from exc

    @classmethod
    async def get_breed(
            cls,
            image: UploadFile,  # FastAPI UploadFile (or anything with .filename/.read())
            language: str = "en",
            timeout: float = 30.0,
    ) -> Any:
        """
        Hit `/udder-pred` with the cow side image and return the JSON payload
        containing `interpretation`, `recommendation`, and `value`.

        Raises
        ------
        HTTPException
            502 if the downstream service is unreachable,
            or propagates the status code returned by the scanner.
        """
        uri = "/breed-pred"
        url = f"{cls.BASE_URL}{uri}"

        # Build multipart/form-data exactly like the Postman call
        files = {
            "side-img": (image.filename, await image.read(), image.content_type or "image/jpeg"),
        }
        form = {"language": language}

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                resp = await client.post(url, headers=cls.HEADERS, data=form, files=files)
                resp.raise_for_status()
                return resp.json()

            except httpx.HTTPStatusError as exc:
                # Bubble the exact status code from the scanner so your API responds transparently
                logger.error("ScannerService responded %s: %s", exc.response.status_code, exc.response.text)
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=exc.response.json() if exc.response.headers.get("content-type") == "application/json"
                    else exc.response.text,
                ) from exc

            except httpx.RequestError as exc:
                # Network / DNS / timeout issues
                logger.exception("ScannerService unreachable: %s", exc)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Unable to reach Scanner micro-service",
                ) from exc

    @classmethod
    async def get_breed_grade(
            cls,
            breed: str,
            image: UploadFile,  # FastAPI UploadFile (or anything with .filename/.read())
            language: str = "en",
            timeout: float = 30.0,
    ) -> Any:
        """
        Hit `/udder-pred` with the cow side image and return the JSON payload
        containing `interpretation`, `recommendation`, and `value`.

        Raises
        ------
        HTTPException
            502 if the downstream service is unreachable,
            or propagates the status code returned by the scanner.
        """
        uri = "/breed-grade"
        url = f"{cls.BASE_URL}{uri}"

        # Build multipart/form-data exactly like the Postman call
        files = {
            "side-img": (image.filename, await image.read(), image.content_type or "image/jpeg"),
        }
        form = {"language": language,
                "breed": breed}

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                resp = await client.post(url, headers=cls.HEADERS, data=form, files=files)
                resp.raise_for_status()
                return resp.json()

            except httpx.HTTPStatusError as exc:
                # Bubble the exact status code from the scanner so your API responds transparently
                logger.error("ScannerService responded %s: %s", exc.response.status_code, exc.response.text)
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=exc.response.json() if exc.response.headers.get("content-type") == "application/json"
                    else exc.response.text,
                ) from exc

            except httpx.RequestError as exc:
                # Network / DNS / timeout issues
                logger.exception("ScannerService unreachable: %s", exc)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Unable to reach Scanner micro-service",
                ) from exc

    @classmethod
    async def get_animal_economic_status(
            cls,
            breed: str,
            breed_grade: str,
            bcs_score: dict,
            udder_pred: str,
            skin_pred: str,
            worm_load: str,
            language: str = "en",
            timeout: float = 30.0,
    ) -> Any:
        """
        Call `/animal-economic-status` and return the JSON payload.

        Parameters
        ----------
        breed, breed_grade, bcs_score, udder_pred, skin_pred, worm_load
            Inputs required by the Scanner micro-service.
        language
            Optional locale for downstream text generation.
        timeout
            HTTP timeout (seconds).

        Raises
        ------
        HTTPException
            • 502 if the scanner is unreachable
            • or propagates the status code returned by the scanner.
        """
        url = f"{cls.BASE_URL}/animal-economic-status"

        # Build multipart/form-data payload exactly like Postman
        form_data = {
            "breed": breed,
            "breed-grade": breed_grade,
            "bcs-score": json.dumps(bcs_score),  # the service expects a JSON string
            "udder-pred": udder_pred,
            "skin-pred": skin_pred,
            "worm-load": worm_load,
            "language": language,
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                resp = await client.post(url, headers=cls.HEADERS, data=form_data)
                resp.raise_for_status()
                return resp.json()

            except httpx.HTTPStatusError as exc:
                logger.error(
                    "ScannerService responded %s: %s",
                    exc.response.status_code,
                    exc.response.text,
                )
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=exc.response.json()
                    if exc.response.headers.get("content-type") == "application/json"
                    else exc.response.text,
                ) from exc

            except httpx.RequestError as exc:
                logger.exception("ScannerService unreachable: %s", exc)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Unable to reach Scanner micro-service",
                ) from exc
