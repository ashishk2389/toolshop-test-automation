import json

import pytest
from playwright.sync_api import APIRequestContext, expect


@pytest.mark.regression
def test_filter_products_via_query_method(api_request_context: APIRequestContext):
    """
    Test Case: Validate filtering storefront products using the custom QUERY method.
    Target: Products between $1 and $100, excluding rentals.
    """

    # 1. Define the QUERY data payload
    query_payload = {
        "page": "1",
        "between": "price,1,100",
        "is_rental": "false"
    }

    # 2. Execute the fetch request using the specific "QUERY" HTTP method string
    response = api_request_context.fetch(
        "https://api.practicesoftwaretesting.com/products",
        method="QUERY",
        data=query_payload  # Sends the payload as the request body
    )

    # 3. Validation: HTTP Layer status verification
    assert response.ok, f"Products API QUERY failed with status: {response.status}"
    assert response.status == 200

    # 4. Validation: Verify payload schema and array filters
    payload = response.json()
    assert "data" in payload, "Missing 'data' wrapper array in JSON response"

    products_list = payload["data"]
    assert len(products_list) > 0, "No products found matching the filter payload rules"

    # 5. Soft Assertions: Check that the filters were successfully applied by the backend
    first_product = products_list[0]

    # Confirm the item price respects the query boundaries ($1 to $100)
    product_price = first_product.get("price")
    assert 1 <= product_price <= 100, f"Product price {product_price} fell outside the $1-$100 filter bounds!"

    # Confirm it is not a rental item
    assert first_product.get("is_rental") is False, "Found a rental item despite 'is_rental=false' constraint"

from playwright.sync_api import APIRequestContext, Page

import json
from playwright.sync_api import APIRequestContext, Page

def test_add_item_to_existing_cart(api_request_context: APIRequestContext, page: Page):
    """
    Test Case: Dynamically discover a product, add it to a new backend cart,
    verify the item exists via a GET checkpoint, and display it in the UI.
    """
    # 1. Verify API session state integrity
    api_user_response = api_request_context.get("https://api.practicesoftwaretesting.com/users/me")
    assert api_user_response.ok, f"API Session is unauthenticated: {api_user_response.status}"

    # 2. Dynamically fetch a valid live product ID
    query_payload = {
        "page": "1",
        "between": "price,1,100",
        "is_rental": "false"
    }
    product_response = api_request_context.fetch(
        "https://api.practicesoftwaretesting.com/products",
        method="QUERY",
        data=query_payload
    )
    assert product_response.ok, f"Failed to fetch products: {product_response.status}"
    target_product_id = product_response.json()['data'][0]['id']

    # 3. Dynamically create a brand new cart session
    create_cart_url = "https://api.practicesoftwaretesting.com/carts"
    cart_init_data = api_request_context.post(create_cart_url, data={}).json()
    cart_id = cart_init_data["id"]
    endpoint_url = f"https://api.practicesoftwaretesting.com/carts/{cart_id}"
    print(f"\n🆔 Target Cart ID: {cart_id} | Product ID: {target_product_id}")

    # 4. Add the discovered product to the cart session
    target_quantity = 1
    cart_payload = {
        "product_id": target_product_id,
        "quantity": target_quantity
    }
    add_response = api_request_context.post(
        endpoint_url,
        data=json.dumps(cart_payload),
        headers={"Content-Type": "application/json"}
    )
    assert add_response.ok, f"Failed to add item to cart. Status: {add_response.status}"

    # -----------------------------------------------------------------
    # 🔍 VERIFICATION CHECKPOINT: Fetch and parse the updated cart schema
    # -----------------------------------------------------------------
    verify_response = api_request_context.get(endpoint_url)
    assert verify_response.ok, f"Failed to query updated cart state: {verify_response.status}"

    cart_items = verify_response.json().get("cart_items", [])

    # Extract all item product IDs currently within the backend database cart array
    added_product_ids = [item["product_id"] for item in cart_items]

    assert target_product_id in added_product_ids, (
        f"❌ Verification Failed! Product ID {target_product_id} was not found in cart_items: {added_product_ids}"
    )
    print("✅ Verification Passed! Product matches inside backend database array perfectly.")

