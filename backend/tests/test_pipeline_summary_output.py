from app.services import pipeline_backend


def test_pipeline_summary_and_recommendations_present(monkeypatch):
    def _fake_parser_agent(_itinerary_text, *, model, request_id, parser_context=None):
        return {
            "trip": {
                "trip_id": "run-1",
                "days": [
                    {
                        "day_id": "day-1",
                        "label": "Day 1",
                        "locations": [{"type": "visit", "name": "Taipei 101", "address": {}, "risk_queries": {}}],
                        "accommodation": {},
                    }
                ],
            }
        }

    def _fake_has_openai_config():
        return True, None

    def _fake_fetch_news(_analyzer_input):
        return {"enabled": False, "articles": [], "error": None, "reason": "disabled_by_config"}

    def _fake_build_news_contexts(_news_payload):
        return {}

    def _fake_analyst_agent(*, domain, parsed_itinerary, model, news_context=None, request_id=None):
        return {
            "agent": f"{domain}_analyst",
            "domain": domain,
            "items": [
                {
                    "day_id": "day-1",
                    "day_label": "Day 1",
                    "activity": "Visit Taipei 101",
                    "location": "Taipei 101",
                    "risk": "Crowd surge",
                    "severity": "Medium",
                    "mitigation": "Avoid peak queue windows and keep exits in sight.",
                    "details": "Crowd density spikes at sunset.",
                }
            ],
        }

    monkeypatch.setattr(pipeline_backend, "parser_agent", _fake_parser_agent)
    monkeypatch.setattr(pipeline_backend, "has_openai_config", _fake_has_openai_config)
    monkeypatch.setattr(pipeline_backend, "_fetch_news_articles", _fake_fetch_news)
    monkeypatch.setattr(pipeline_backend, "_build_domain_news_contexts", _fake_build_news_contexts)
    monkeypatch.setattr(pipeline_backend, "analyst_agent", _fake_analyst_agent)

    output = pipeline_backend.run_itinerary_pipeline("Day 1: Taipei 101")

    assert output["status"] == "ok"
    assert isinstance(output.get("summary"), str) and output["summary"]
    assert isinstance(output.get("recommendations"), list)
    assert output["final_report"].get("summary")
    assert isinstance(output["final_report"].get("recommendations"), list)
