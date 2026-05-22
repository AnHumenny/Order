from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.core.rate_limiter import limiter, RateLimits
from app.modules.analytics.repository import AnalyticsRepository
from app.modules.analytics.service import AnalyticsService
from app.modules.private_modules.auth.models import User

router = APIRouter(prefix="/analytics")


async def get_analytics_service(session: AsyncSession = Depends(get_session)) -> AnalyticsService:
    """Dependency for receiving analytics service"""
    repository = AnalyticsRepository(session)
    return AnalyticsService(repository)


@router.get("/user-purchases")
@limiter.limit(RateLimits.ANALYTICS)
async def get_user_purchase_analytics(
        request: Request,
        current_user: User = Depends(get_current_user),
        service: AnalyticsService = Depends(get_analytics_service)
):
    """Get analytics of user's purchases for current year"""
    return await service.get_user_purchase_analytics(current_user.id)


@router.get("/user-stats")
@limiter.limit(RateLimits.ANALYTICS)
async def get_user_stats(
        request: Request,
        current_user: User = Depends(get_current_user),
        service: AnalyticsService = Depends(get_analytics_service)
):
    """Get user statistics: total orders and total spent"""
    return await service.get_user_stats(current_user.id)
