from coinbase.wallet.client import Client


# Function to account details from Coinbase
def get_account_details(project_settings):
    # Retrieve the API Key
    api_key = project_settings['coinbase']['api_key']
    api_secret = project_settings['coinbase']['api_secret']
    client = Client(api_key=api_key, api_secret=api_secret)

    # Retrieve information
    accounts = client.get_accounts()
    return accounts
