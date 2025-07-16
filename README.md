# Revcontent API Test Assignment

According to the requirements, I implemented the solution using a **script format** with API calls mocked via `unittest.mock`.  
Additionally, I wrote unit tests using `unittest` and mocks to cover all key API methods.

For the API, I was only able to access the documentation at [https://api.revcontent.io/docs/stats/](https://api.revcontent.io/docs/stats/). According to the API docs, the parameter `traffic_type` is not required when creating a campaign, and the `status` field is not present in the campaign stats response. Therefore, I strictly followed the API documentation and did not use any parameters or response fields that were not described there.

Logging is also implemented in the project for better traceability.

Since the assignment resembles work with an internal API, I decided to output the campaign statistics both to the console and to a `.json` file. I believe that in a real scenario, this format would be convenient for sending data to the frontend or for further processing.

> **Note:**  
> I intentionally left the `.env` file in the project and included it in the repository so that you can see the complete structure of the test project.  
> In real-world development, this file usually contains private data and should not be committed to the repository.

---

## How to Run

- To run the main script with mocks:
  ```bash
  python run_with_mocks.py

- To run unit tests:
  ```bash
  python -m unittest test_revcontent_api.py