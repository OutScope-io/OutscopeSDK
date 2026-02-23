import respx
import httpx
from outscope_sdk import Client


@respx.mock
def test_create_check():
    respx.post("https://api.outscope.es/v1/checks").mock(
        return_value=httpx.Response(200, json={"job_id": "check_123", "status": "queued"})
    )

    client = Client(api_key="test_api_key")
    response = client.checks.create(
                {
                    'fqdn': 'outscope.es'
                }
            )

    assert response["job_id"] == "check_123"
    assert response["status"] == "queued"

