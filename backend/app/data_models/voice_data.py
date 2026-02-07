from fastapi import UploadFile


class TranscribeRequest:
    audio: UploadFile
    language: str = "en"

class TranscribeResponse:
    text: str
    confidence: float
