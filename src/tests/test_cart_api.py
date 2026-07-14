import logging

import pytest
from playwright.sync_api import APIRequestContext, Page

from src.utils.api_helpers import CARTS_ENDPOINT, CURRENT_USER_ENDPOINT, DEFAULT_PRICE_FILTER_QUERY, fetch_filtered_products

logger = logging.getLogger(__name__)


@pytest.mark.regression
def test_add_item_to_existing_cart(api_request_context: APIRequestContext, page: Page):
    """Test Case: Discover a product, add it to a new backend cart, and verify via GET.

    Target: A dynamically created cart correctly reflects the added product.

    Note:
        The `page` fixture is accepted but currently unused — the original
        docstring claimed the item would be "displayed in the UI," but no
        UI interaction exists in this test body. Either implement that UI
        verification step or drop the `page` parameter; flagged here
        rather than silently either removing it or inventing a UI check.
    """
    # 1. Verify API session state integrity
    api_user_response = api_request_context.get(CURRENT_USER_ENDPOINT)
    assert api_user_response.ok, f"API session is unauthenticated: {api_user_response.status}"

    # 2. Dynamically fetch a valid live product ID
    products_list = fetch_filtered_products(api_request_context, DEFAULT_PRICE_FILTER_QUERY)
    assert len(products_list) > 0, "No products found matching the filter payload rules"
    target_product_id = products_list[0]["id"]

    # 3. Dynamically create a brand new cart session
    cart_init_data = api_request_context.post(CARTS_ENDPOINT, data={}).json()
    cart_id = cart_init_data["id"]
    cart_endpoint_url = f"{CARTS_ENDPOINT}/{cart_id}"
    logger.info("Target cart ID: %s | Product ID: %s", cart_id, target_product_id)

    # 4. Add the discovered product to the cart session
    cart_payload = {"product_id": target_product_id, "quantity": 1}
    add_response = api_request_context.post(cart_endpoint_url, data=cart_payload)
    assert add_response.ok, f"Failed to add item to cart. Status: {add_response.status}"

    # 5. Verify the updated cart state reflects the added product
    verify_response = api_request_context.get(cart_endpoint_url)
    assert verify_response.ok, f"Failed to query updated cart state: {verify_response.status}"

    cart_items = verify_response.json().get("cart_items", [])
    added_product_ids = [item["product_id"] for item in cart_items]

    assert target_product_id in added_product_ids, (
        f"Product ID {target_product_id} was not found in cart_items: {added_product_ids}"
    )
    logger.info("Verification passed: product %s found in cart %s", target_product_id, cart_id)
