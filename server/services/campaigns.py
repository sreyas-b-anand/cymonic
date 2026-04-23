
from config import SupabaseConfig
from supabase import Client
import logging
from uuid import UUID
logger = logging.getLogger(__name__)

class CampaignService:
    def __init__(self):
        self.supabase = SupabaseConfig()

    async def get_all_campaigns(self):
        try:
            campaigns = self.supabase.client.table("campaigns").select("*").execute()

            if not campaigns or not campaigns.data:
                logger.warning("No campaigns found in the database.")
                return {"campaigns": [] , "status" : True , "message" : "No campaigns found"}

            return {"campaigns": campaigns.data, "status": True , "message" : "Campaigns fetched successfully"}


        except Exception as e:
            logger.error("Error fetching campaigns: %s", e)
            return {"campaigns": [], "status": False, "message": "Error fetching campaigns"}

    async def get_campaign_by_id(self, campaign_id : UUID):
        try:
            campaign = self.supabase.client.table("campaigns").select("*").eq("id", campaign_id).execute()

            if not campaign or not campaign.data:
                logger.warning("Campaign with ID %d not found.", campaign_id)
                return {"campaign": None, "status": False, "message": "Campaign not found"}

            return {"campaign": campaign.data[0], "status": True}

        except Exception as e:
            logger.error("Error fetching campaign by ID: %s", e)
            return {"campaign": None, "status": False, "message": "Error fetching campaign"}

    async def delete_campaign(self, campaign_id : UUID):  
        try:
            response = self.supabase.client.table("campaigns").delete().eq("id", campaign_id).execute()

            if response.status_code == 204:
                logger.info("Campaign with ID %d deleted successfully.", campaign_id)
                return {"status": True, "message": "Campaign deleted successfully"}
            else:
                logger.warning("Failed to delete campaign with ID %d. Status code: %d", campaign_id, response.status_code)
                return {"status": False, "message": "Failed to delete campaign"}

        except Exception as e:
            logger.error("Error deleting campaign: %s", e)
            return {"status": False, "message": "Error deleting campaign"}