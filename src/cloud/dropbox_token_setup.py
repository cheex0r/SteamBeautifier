import datetime
import dropbox
import requests
from dropbox.exceptions import AuthError

from interfaces.user_interaction import UserInteraction


class DropboxTokenSetup:
    # Step 1: Start the authorization flow
    # Step 2: User follows link to obtain access code
    # Step 3: Retrieve oauth information with access code
    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret


    # Step 1: Start the authorization flow
    def start_authorization_flow(self):
        auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(self.app_key,
                                                        self.app_secret,
                                                        token_access_type='offline')
        authorize_url = auth_flow.start()
        return auth_flow, authorize_url


    # Step 3: Finish the authorization flow getting authorization and refresh tokens
    def get_authorization_token_with_access_code(self, auth_flow, access_code):
        return auth_flow.finish(access_code)


    # Full Authorization Flow
    def get_authorization_token_from_user(self, user_interaction: UserInteraction, retries=3):
        if retries == 0:
            user_interaction.show_message("Failed to authenticate after 3 attempts.")
            return None
        auth_flow, authorize_url = self.start_authorization_flow()

        message = (
            f"1. Go to: {authorize_url}\n"
            "2. Click 'Allow' (you might have to log in first or press continue).\n"
            "3. Copy the authorization code."
        )
        user_interaction.show_message(message)
        access_code = user_interaction.get_user_input("Enter the authorization code here: ")
        
        try:
            return self.get_authorization_token_with_access_code(auth_flow, access_code)
        except AuthError as e:
            user_interaction.show_message(f"Error during authentication: {e}")
        except requests.exceptions.HTTPError as e:
            user_interaction.show_message(f"HTTP error occurred: {e.response.status_code} {e.response.reason}")
            user_interaction.show_message(f"Response content: {e.response.text}")
        except Exception as e:
            user_interaction.show_message(f"An unexpected error occurred: {e}")
        return self.get_authorization_token_from_user(user_interaction, retries-1)


    def get_token_expiry_now(self, expires_in=14400):
        return self.get_token_expiry(datetime.now(), expires_in)
