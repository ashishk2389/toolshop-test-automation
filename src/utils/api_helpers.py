"""Shared helpers and endpoint constants for API-level test suites."""

import logging

from playwright.sync_api import APIRequestContext

logger = logging.getLogger(__name__)

API_BASE_URL = "https://api.practicesoftwaretesting.com"
PRODUCTS_ENDPOINT = f"{API_BASE_URL}/products"
CARTS_ENDPOINT = f"{API_BASE_URL}/carts"
CURRENT_USER_ENDPOINT = f"{API_BASE_URL}/users/me"

DEFAULT_PRICE_FILTER_QUERY = {
    "page": "1",
    "between": "price,1,100",
    "is_rental": "false",
}


def fetch_filtered_products(api_request_context: APIRequestContext, query_payload: dict) -> list:
    """Fetch products filtered via the custom QUERY HTTP method.

    Args:
        api_request_context: Authenticated Playwright API request context.
        query_payload: Filter parameters sent as the QUERY request body.

    Returns:
        list: The "data" array of matching products from the response.
    """
    logger.debug("Fetching filtered products with query: %s", query_payload)
    response = api_request_context.fetch(PRODUCTS_ENDPOINT, method="QUERY", data=query_payload)
    assert response.ok, f"Products API QUERY failed with status: {response.status}"
    assert response.status == 200

    payload = response.json()
    assert "data" in payload, "Missing 'data' wrapper array in JSON response"
    return payload["data"]
