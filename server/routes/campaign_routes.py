from fastapi import APIRouter, HTTPException , Depends 
from services import CampaignService
from utils import get_current_user
from uuid import UUID
campaign_router = APIRouter()
campaign_service = CampaignService() 

@campaign_router.get("/campaigns")
async def get_campaigns(user=Depends(get_current_user)):
    try:
        campaigns = await campaign_service.get_all_campaigns()
        return {"campaigns": campaigns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@campaign_router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: UUID, user=Depends(get_current_user)):
    try:
        campaign = await campaign_service.get_campaign_by_id(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaign
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@campaign_router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: UUID, user=Depends(get_current_user)):
    try:
        success = await campaign_service.delete_campaign(campaign_id)
        if not success:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return {"message": "Campaign deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))