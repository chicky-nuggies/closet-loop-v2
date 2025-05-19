from fastapi import APIRouter
from app.api.wardrobe_routes import router as wardrobe_router
from app.api.outfit_routes import router as outfit_router
from app.api.marketplace_routes import router as marketplace_router

router = APIRouter()

router.include_router(wardrobe_router, prefix="/wardrobe", tags=["Wardrobe"])
router.include_router(outfit_router, prefix="/outfit", tags=["Outfit"])
router.include_router(marketplace_router, prefix="/marketplace", tags=["Marketplace"])
