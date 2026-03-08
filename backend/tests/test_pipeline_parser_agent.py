from app.services import pipeline_backend


def test_parser_agent_retries_on_invalid_json(monkeypatch):
    calls = {"count": 0}

    def _fake_openai_chat_json(
        prompt,
        *,
        system,
        model,
        temperature=0.1,
        max_tokens_override=None,
        enforce_json_object=False,
    ):
        calls["count"] += 1
        if calls["count"] == 1:
            return None, "Invalid JSON response: Unterminated string", '{"trip": {"days": ['
        return {
            "trip": {
                "trip_id": "run-1",
                "title": "TW",
                "destination_country": "TW",
                "days": [
                    {
                        "day_id": "day-1",
                        "label": "Day 1",
                        "locations": [
                            {
                                "location_id": "loc-1",
                                "type": "visit",
                                "name": "Taipei 101",
                                "address": {"city": "Taipei", "country": "TW"},
                                "risk_queries": {"place_keywords": ["tower", "taipei", "landmark"], "country_code": "TW"},
                            }
                        ],
                    }
                ],
            }
        }, None, '{"trip":{"trip_id":"run-1"}}'

    monkeypatch.setattr(pipeline_backend, "_openai_chat_json", _fake_openai_chat_json)

    result = pipeline_backend.parser_agent("Day 1: Taipei 101", model="gpt-4.1-mini", request_id="req_1")

    assert calls["count"] == 2
    assert result.get("trip", {}).get("trip_id") == "run-1"
    assert len(result.get("trip", {}).get("days", [])) == 1
