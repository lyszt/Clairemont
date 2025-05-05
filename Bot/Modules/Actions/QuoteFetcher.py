import requests

class QuoteFetcher:
    def __init__(self, console):
        self.console = console
        self.quote = ""


    def get_quote(self) -> str:
        return self.quote

    def fetch_random_quote(self):
        api_url = 'https://api.animechan.io/v1/quotes/random'
        response = requests.get(api_url)
        if response.status_code == requests.codes.ok:
            self.console.log(f"Acquired random quote: STATUS CODE {response.status_code}")
            quote = response.json()
            self.quote = quote['data']['content']
            return self
        else:
            self.console.log("Failed at getting random quote.")
            return self
