from fastapi import APIRouter, HTTPException
from services.image_generation import ImageGenerationService

router = APIRouter()

@router.post("/api/init")
async def init_game(prompt: str):
    try:
        image_generation_service = ImageGenerationService(prompt)
        images = await image_generation_service.generate_images()
        return { "images": images }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))