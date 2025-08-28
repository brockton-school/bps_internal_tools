import requests


class CanvasAPIError(Exception):
    """Raised when the Canvas API returns an error response."""


def sis_import(csv_bytes: bytes, *, base_url: str, token: str, account_id: str = "1"):
    """Trigger a SIS import in Canvas for the provided CSV data.

    Args:
        csv_bytes: CSV file contents as bytes.
        base_url: Base URL for the Canvas instance.
        token: API token with SIS import permissions.
        account_id: Canvas account ID to target.

    Raises:
        CanvasAPIError: If Canvas responds with a non-OK status code.
    """
    files = {"attachment": ("users.csv", csv_bytes, "text/csv")}
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(
        f"{base_url}/api/v1/accounts/{account_id}/sis_imports",
        headers=headers,
        data={"import_type": "instructure_csv"},
        files=files,
        timeout=30,
    )
    if not resp.ok:
        raise CanvasAPIError(resp.text)
    return resp