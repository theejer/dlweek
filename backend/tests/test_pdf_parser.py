from app.services import pdf_parser


def test_select_itinerary_text_returns_full_when_under_limit():
    text = "Day 1: Patna\nDay 2: Gaya"
    selected, strategy = pdf_parser._select_itinerary_text_for_llm(text, limit=200)
    assert strategy == "full"
    assert selected == text


def test_select_itinerary_text_prefers_itinerary_lines_for_long_input():
    filler = "\n".join(f"Noise line {idx}" for idx in range(400))
    itinerary_tail = "\n".join(
        [
            "Day 1: Patna Museum",
            "Day 2: Nalanda Ruins",
            "Day 3: Bodh Gaya Temple",
            "Stay: Gaya guest house",
        ]
    )
    text = f"{filler}\n{itinerary_tail}"

    selected, strategy = pdf_parser._select_itinerary_text_for_llm(text, limit=300)

    assert strategy in {"itinerary_lines", "head_tail"}
    assert len(selected) <= 300
    assert "Day 3: Bodh Gaya Temple" in selected
