import pytest
from playwright.sync_api import APIRequestContext

from src.utils.api_helpers import DEFAULT_PRICE_FILTER_QUERY, fetch_filtered_products


@pytest.mark.regression
def test_filter_products_via_query_method(api_request_context: APIRequestContext):
    """Test Case: Filter storefront products using the custom QUERY method.

    Target: Products between $1 and $100, excluding rentals.
    """
    products_list = fetch_filtered_products(api_request_context, DEFAULT_PRICE_FILTER_QUERY)
    assert len(products_list) > 0, "No products found matching the filter payload rules"

    # Assertions: confirm the backend actually applied the requested filters
    first_product = products_list[0]

    product_price = first_product.get("price")
    assert 1 <= product_price <= 100, f"Product price {product_price} fell outside the $1-$100 filter bounds!"

    assert first_product.get("is_rental") is False, "Found a rental item despite 'is_rental=false' constraint"
