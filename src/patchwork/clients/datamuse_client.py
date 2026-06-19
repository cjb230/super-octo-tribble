import requests

from patchwork.config import AppConfig


class DatamuseClient(object):
    def __init__(self, base_url=None, timeout=None):
        self.base_url = base_url or AppConfig.DATAMUSE_URL
        self.timeout = timeout or AppConfig.EXTERNAL_TIMEOUT

    def related_words(self, term):
        if not term:
            return []
        try:
            response = requests.get(
                self.base_url,
                params={"ml": term, "max": 3},
                timeout=self.timeout,
            )
            response.raise_for_status()
            body = response.json()
        except requests.RequestException:
            return []

        words = []
        for row in body:
            word = row.get("word")
            if word:
                words.append(word.replace(" ", "_"))
        return words
