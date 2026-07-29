from fastapi import APIRouter

from app.routers import (
    auth,
    alerts,
    incidents,
    threats,
    assets as assets_router,
    detection,
    ai,
    reports,
    playbooks,
    integrations,
    admin,
    health,
    webhooks,
    analytics,
    dashboard,
    logs,
    correlation,
    ioc,
    mitre,
    threat_intel,
    notifications,
)

api_v1_router = APIRouter()

api_v1_router.include_router(health.router, tags=["health"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_v1_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_v1_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_v1_router.include_router(threats.router, prefix="/threats", tags=["threats"])
api_v1_router.include_router(assets_router.router, prefix="/assets", tags=["assets"])
api_v1_router.include_router(detection.router, prefix="/detection", tags=["detection"])
api_v1_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_v1_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_v1_router.include_router(playbooks.router, prefix="/playbooks", tags=["playbooks"])
api_v1_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_v1_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_v1_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_v1_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_v1_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_v1_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_v1_router.include_router(correlation.router, prefix="/correlation", tags=["correlation"])
api_v1_router.include_router(ioc.router, prefix="/ioc", tags=["ioc"])
api_v1_router.include_router(mitre.router, prefix="/mitre", tags=["mitre"])
api_v1_router.include_router(threat_intel.router, prefix="/threat-intelligence", tags=["threat-intelligence"])
api_v1_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
