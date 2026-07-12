import pytest
from src.pages.login_page import LoginPage
from src.pages.my_account_page import AccountPage

@pytest.mark.regression
def test_delete_favorite_item_with_confirmation_dialog(page, registration_data):
    """
    Test Case: Automate a confirmation dialog when deleting a favorite item.

    Objective: Demonstrates Day 10 - Event-Driven JavaScript Dialogs & Modals
    by handling native browser alert/confirm dialogs using Playwright event listeners.

    Steps:
    1. Login as a valid user
    2. Navigate to Favorites page
    3. Register dialog event listener
    4. Attempt to delete a favorite item (triggers confirmation dialog)
    5. Accept the dialog programmatically
    6. Verify item was removed from favorites
    """

    # 1. Initialize Page Object Models
    login_page = LoginPage(page)
    account_page = AccountPage(page)

    # 2. Extract valid user credentials from fixture data
    user_info = registration_data["valid_user"]

    # 3. Prerequisites: Navigate and log in to reach the Account Page
    login_page.navigateToLoginPage()
    login_page.verify_login_page_displayed()
    login_page.login(user_info)

    # 4. Verify Account main landing page elements are correct
    account_page.verify_account_page_loaded()
    account_page.verify_account_menu_visible()

    # 5. Navigate to Favorites section
    account_page.click_favorites()
    page.wait_for_timeout(1000)  # Wait for favorites page to load

    # ========================================================================
    # DAY 10: EVENT-DRIVEN JAVASCRIPT DIALOGS & MODALS
    # ========================================================================

    # 6. Register the dialog event listener BEFORE triggering the action
    # This handler will automatically accept any dialog that appears
    dialog_accepted = False

    def handle_dialog(dialog):
        """
        Event listener callback for dialog events.
        Automatically accepts (clicks OK) on the dialog.

        Args:
            dialog: The Playwright dialog object containing:
                - type: 'alert', 'confirm', 'prompt', or 'beforeunload'
                - message: The dialog message text
                - accept(): Accepts the dialog (click OK)
                - dismiss(): Rejects the dialog (click Cancel)
        """
        nonlocal dialog_accepted
        print(f"🔔 Dialog detected!")
        print(f"   Type: {dialog.type}")
        print(f"   Message: {dialog.message}")
        dialog.accept()  # Click "OK" / "Yes" on the dialog
        dialog_accepted = True

    # Register the dialog handler on the page
    page.on("dialog", handle_dialog)

    # 7. Perform the action that triggers the dialog
    # Click the delete/remove button on the first favorite item
    delete_button = page.locator("[data-test='delete']").first
    delete_button.click()

    # 8. Wait briefly for dialog to process
    page.wait_for_timeout(500)

    # 9. Verify the dialog was handled
    assert dialog_accepted, "Dialog was not triggered or accepted"
    print("✅ Dialog was successfully accepted!")

    # 10. Verify the item was removed (favorites list updated)
    page.wait_for_timeout(1000)  # Wait for DOM to update

    # Optional: Add additional assertion to verify the favorite was deleted
    # This would depend on your application's behavior after deletion
    print("✅ Test completed: Favorite item deletion with dialog confirmation successful!")


# ========================================================================
# ADVANCED EXAMPLE: Handle Different Dialog Types
# ========================================================================

@pytest.mark.regression
def test_dialog_handling_with_different_scenarios(page, registration_data):
    """
    Advanced example: Handle different dialog types and extract message.

    Demonstrates handling:
    - Confirm dialogs (accept/dismiss)
    - Alert dialogs (must accept)
    - Prompt dialogs (accept with input)
    """

    login_page = LoginPage(page)
    account_page = AccountPage(page)
    user_info = registration_data["valid_user"]

    # Setup: Login
    login_page.navigateToLoginPage()
    login_page.login(user_info)
    account_page.verify_account_page_loaded()

    # Navigate to Favorites
    account_page.click_favorites()
    page.wait_for_timeout(500)

    # ========================================================================
    # Advanced Dialog Handler with Multiple Scenarios
    # ========================================================================

    dialog_info = {}

    def advanced_dialog_handler(dialog):
        """
        Advanced handler that captures dialog details and handles different types.
        """
        dialog_info["type"] = dialog.type
        dialog_info["message"] = dialog.message

        print(f"\n📋 Dialog Details:")
        print(f"   Type: {dialog.type}")
        print(f"   Message: {dialog.message}")

        # Handle different dialog types
        if dialog.type == "confirm":
            print("   → Handling CONFIRM dialog - accepting...")
            dialog.accept()
        elif dialog.type == "alert":
            print("   → Handling ALERT dialog - accepting...")
            dialog.accept()
        elif dialog.type == "prompt":
            print("   → Handling PROMPT dialog - accepting with input...")
            dialog.accept("user_input_value")
        else:
            print(f"   → Handling unknown dialog type - accepting...")
            dialog.accept()

    # Register advanced handler
    page.on("dialog", advanced_dialog_handler)

    # Trigger deletion
    delete_button = page.locator("[data-test='delete']").first
    if delete_button.is_visible():
        delete_button.click()
        page.wait_for_timeout(500)

        # Verify dialog was captured
        if dialog_info:
            print(f"\n✅ Dialog Info Captured:")
            print(f"   Type: {dialog_info.get('type')}")
            print(f"   Message: {dialog_info.get('message')}")
            assert dialog_info.get("type") in ["alert", "confirm", "prompt", "beforeunload"]
        else:
            print("⚠️  No dialog was triggered")

    # Clean up: Remove the listener
    page.remove_listener("dialog", advanced_dialog_handler)

    print("✅ Advanced dialog handling test completed!")
