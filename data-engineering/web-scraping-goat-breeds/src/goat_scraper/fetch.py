"""HTTP session with retries and a descriptive User-Agent."""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

URL = "https://en.wikipedia.org/wiki/List_of_goat_breeds"
USER_AGENT = "goat-scraper/1.0 (educational project; https://github.com/0lake/projects)"


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    retry = Retry(total=3, backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504))
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def fetch_html(url: str = URL, session: requests.Session | None = None, timeout: float = 20) -> str:
    session = session or make_session()
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text
