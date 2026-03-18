from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.users.models import User
from app.modules.analytics.repository import AnalyticsRepository
from app.modules.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


async def get_analytics_service(session: AsyncSession = Depends(get_session)) -> AnalyticsService:
    """Dependency for receiving analytics service"""
    repository = AnalyticsRepository(session)
    return AnalyticsService(repository)


@router.get("/user-purchases")
async def get_user_purchase_analytics(
        current_user: User = Depends(get_current_user),
        service: AnalyticsService = Depends(get_analytics_service)
):
    """Get analytics of user's purchases for current year"""
    return await service.get_user_purchase_analytics(current_user.id)


@router.get("/user-stats")
async def get_user_stats(
        current_user: User = Depends(get_current_user),
        service: AnalyticsService = Depends(get_analytics_service)
):
    """Get user statistics: total orders and total spent"""
    return await service.get_user_stats(current_user.id)