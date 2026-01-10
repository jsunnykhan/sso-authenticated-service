from app.services.provider import ProviderService
from app.schemas.provider import ProviderCreate
from app.utils.token import Token
from app.db.session import SessionLocal
class DefaultProviderCreator:
    def __init__(self):
        self.DEFAULT_PROVIDER_NAME = "DefaultProvider"
        self.DEFAULT_REDIRECT_URL = "https://example.com/callback"
        self.token = Token()
        
    def create_default_provider(self):
        
        
        client_id = self.token.get_client_id()
        self.token.get_filepath_for_client_secret(client_id)
        self.token.create_provider_private_key(client_id)
        client_secret = self.token.get_client_secret(client_id)
        
        
        provider_data = ProviderCreate(
            name=self.DEFAULT_PROVIDER_NAME,
            client_id=client_id,
            client_secret=client_secret,
            redirect_url=self.DEFAULT_REDIRECT_URL,
        )
        
        print("Creating default provider with client_id:", client_id)
        print("Client secret stored at:", client_secret)
        return True     