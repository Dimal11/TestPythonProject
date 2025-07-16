from dotenv import load_dotenv
from logging_config import setup_loguru
from revcontent_api import RevcontentAPI
from loguru import logger
import json
from datetime import datetime

load_dotenv()
setup_loguru()

def save_stats_to_json(stats: dict, campaign_id: str):
    """
        Saves campaign statistics to a JSON file with a timestamp in the filename.

        Args:
            stats (dict): The statistics data to be saved.
            campaign_id (str): The ID of the campaign (used in the filename).

        Returns:
            None
    """
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"stats_RESULT_{campaign_id}_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    logger.success(f"Campaign statistics saved to {filename}")

def main():
    CLIENT_ID = "mock_client_id"
    CLIENT_SECRET = "mock_client_secret"

    api = RevcontentAPI(CLIENT_ID, CLIENT_SECRET)

    try:
        api.auth()
    except Exception as e:
        logger.exception(f"Authentication error: {e}")
        return

    try:
        campaign_id = api.create_campaign(
            name="Test Campaign - YourName",
            budget=50.0,
            bid=0.10,
            countries=["US"]
        )
        logger.success(f"Campaign created. ID: {campaign_id}")
    except Exception as e:
        logger.exception(f"Create campaign error: {e}")
        return

    try:
        stats = api.get_campaign_stats_by_id(campaign_id)
        if stats is not None:
            stats_data = stats[0] if isinstance(stats, list) and stats else stats

            print("\n--- Campaign Statistics ---")
            print(f"Campaign ID: {campaign_id}")
            print(f"Impressions: {stats_data.get('impressions', 0)}")
            print(f"Clicks: {stats_data.get('clicks', 0)}")

            save_stats_to_json(stats_data, campaign_id)
        else:
            logger.warning("No stats returned for campaign.")
    except Exception as e:
        logger.exception(f"Stats error: {e}")

if __name__ == "__main__":
    main()
