from unittest.mock import patch, MagicMock
import main

def run_main_with_mocks():
    def post_side_effect(url, *args, **kwargs):
        if "oauth/token" in url:
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {"access_token": "test_token"}
            return resp
        elif "boosts/add" in url:
            resp = MagicMock()
            resp.status_code = 201
            resp.json.return_value = {"data": [{"id": "test_campaign_id"}]}
            return resp
        raise ValueError("Unknown POST URL")

    def get_side_effect(url, *args, **kwargs):
        if "boosts/performance" in url:
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {
                "data": [{
                    "impressions": 1000,
                    "clicks": 42
                }]
            }
            return resp
        raise ValueError("Unknown GET URL")

    with patch("requests.post", side_effect=post_side_effect), \
         patch("requests.get", side_effect=get_side_effect):
        main.main()

if __name__ == "__main__":
    run_main_with_mocks()
