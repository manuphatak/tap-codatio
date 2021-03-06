"""REST client handling, including CodatIoStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import APIKeyAuthenticator


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class CodatIoStream(RESTStream):
    """tap-codatio stream class."""

    records_jsonpath = "$.results[*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return (
            "https://api-uat.codat.io"
            if self.config["uat"]
            else "https://api.codat.io/"
        )

    @property
    def authenticator(self) -> APIKeyAuthenticator:
        """Return a new authenticator object."""
        api_key = self.config.get("api_key")
        return APIKeyAuthenticator.create_for_stream(
            self, key="Authorization", value=f"Basic {api_key}", location="header"
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        # If not using an authenticator, you may also provide inline auth headers:
        # headers["Private-Token"] = self.config.get("auth_token")
        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        next_href = next(
            iter(extract_jsonpath("$._links.next.href", response.json())), None
        )
        if next_href is None:
            return None

        next_page = next(iter(extract_jsonpath("$.pageNumber", response.json())))
        return next_page + 1

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        params["pageSize"] = 500
        params["page"] = 1
        if next_page_token:
            params["page"] = next_page_token

        if self.replication_key:
            params["orderBy"] = self.replication_key

        return params

    def prepare_request_payload(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Optional[dict]:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).
        """
        # TODO: Delete this method if no payload is required. (Most REST APIs.)
        return None

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # TODO: Parse response body and return a set of records.
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """As needed, append or transform raw data to match expected structure."""
        # TODO: Delete this method if not needed.
        return row
