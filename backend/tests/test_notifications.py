"""Notification service tests for Telegram bot activation handling."""

from flask import Flask

from app.services import notifications


def test_start_command_with_phone_activates_contact(monkeypatch):
    app = Flask("test")

    captured_activation: dict = {}
    sent_messages: list[tuple[str, str, str]] = []

    def _fake_activate(phone: str, chat_id: str) -> dict:
        captured_activation["phone"] = phone
        captured_activation["chat_id"] = chat_id
        return {
            "id": "ec_1",
            "name": "Ravi",
            "phone": "+919100000001",
            "telegram_chat_id": chat_id,
            "telegram_bot_active": True,
        }

    monkeypatch.setattr(notifications, "activate_telegram_contact_by_phone", _fake_activate)
    monkeypatch.setattr(
        notifications,
        "_safe_send_message",
        lambda token, chat_id, text: sent_messages.append((token, chat_id, text)),
    )

    notifications._handle_update(
        app,
        "bot-token",
        {
            "update_id": 1,
            "message": {
                "chat": {"id": 123456},
                "text": "/start +91 91000 00001",
            },
        },
    )

    assert captured_activation["chat_id"] == "123456"
    assert captured_activation["phone"] == "+919100000001"
    assert len(sent_messages) == 1
    assert "Activation successful" in sent_messages[0][2]


def test_start_command_without_phone_prompts_for_number(monkeypatch):
    app = Flask("test")

    sent_messages: list[tuple[str, str, str]] = []

    monkeypatch.setattr(
        notifications,
        "_safe_send_message",
        lambda token, chat_id, text: sent_messages.append((token, chat_id, text)),
    )

    notifications._handle_update(
        app,
        "bot-token",
        {
            "update_id": 2,
            "message": {
                "chat": {"id": 999},
                "text": "/start",
            },
        },
    )

    assert len(sent_messages) == 1
    assert "Please send your phone number" in sent_messages[0][2]
