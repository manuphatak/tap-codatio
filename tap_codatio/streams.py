"""Stream type classes for tap-codatio."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_codatio.client import CodatIoStream


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class CompaniesStream(CodatIoStream):

    name = "companies"
    path = "/companies"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "companies.json"

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        self.logger.info("Company Record %s\nCompany Context %s", record, context)
        return {
            "company_id": record["id"],
            "linked": record["dataConnections"][0]["status"] == "Linked",
        }


class ConnectionsStream(CodatIoStream):
    name = "connections"
    path = "/companies/{company_id}/connections"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "connections.json"
    parent_stream_type = CompaniesStream
    ignore_parent_replication_keys = True


class AccountsStream(CodatIoStream):
    name = "accounts"
    path = "/companies/{company_id}/data/accounts"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "accounts.json"
    parent_stream_type = CompaniesStream
    ignore_parent_replication_keys = True

    def get_records(self, context: Optional[dict]) -> Iterable[Dict[str, Any]]:
        return (
            super().get_records(context)
            if (context and context["linked"])
            else iter(())
        )
