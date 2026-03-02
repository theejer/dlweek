from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass

import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("telegram-bot")


def normalize_phone(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""

    keep_plus = raw.startswith("+")
    digits = "".join(ch for ch in raw if ch.isdigit())
    if not digits:
        return ""

    return f"+{digits}" if keep_plus else digits


def extract_phone_from_start_command(text: str) -> str:
    command_text = (text or "").strip()
    if not command_text.startswith("/start"):
        return ""

    remainder = command_text[len("/start") :].strip()
    if not remainder:
        return ""

    return normalize_phone(re.sub(r"[^0-9+]", "", remainder))


def extract_phone_from_message(message: dict) -> str:
    contact = message.get("contact") or {}
    contact_phone = normalize_phone(contact.get("phone_number"))
    if contact_phone:
        return contact_phone

    text = (message.get("text") or "").strip()
    if not text or text.startswith("/"):
        return ""

    cleaned = re.sub(r"[^0-9+]", "", text)
    return normalize_phone(cleaned)


@dataclass
class BotConfig:
    telegram_bot_token: str
    sqlalchemy_database_uri: str
    poll_interval_seconds: int = 2


class EmergencyContactRepository:
    def __init__(self, sqlalchemy_database_uri: str) -> None:
        self.engine = create_engine(sqlalchemy_database_uri, pool_pre_ping=True)

    def activate_by_phone(self, phone: str, chat_id: str) -> dict:
        normalized_phone = normalize_phone(phone)
        if not normalized_phone:
            return {}

        with self.engine.begin() as connection:
            contacts = connection.execute(
                text(
                    """
                    SELECT id, user_id, name, phone
                    FROM emergency_contacts
                    ORDER BY created_at DESC
                    """
                )
            ).mappings().all()

            matched = next(
                (row for row in contacts if normalize_phone(row.get("phone")) == normalized_phone),
                None,
            )
            if not matched:
                return {}

            connection.execute(
                text(
                    """
                    UPDATE emergency_contacts
                    SET telegram_chat_id = :chat_id,
                        telegram_bot_active = TRUE
                    WHERE id = :contact_id
                    """
                ),
                {"chat_id": str(chat_id), "contact_id": matched["id"]},
            )

        return {
            "id": matched.get("id"),
            "user_id": matched.get("user_id"),
            "name": matched.get("name"),
            "phone": matched.get("phone"),
            "telegram_chat_id": str(chat_id),
            "telegram_bot_active": True,
        }


class TelegramBotService:
    def __init__(self, config: BotConfig, repository: EmergencyContactRepository) -> None:
        self.config = config
        self.repository = repository
        self.offset = 0

    def _api_request(self, method: str, payload: dict, timeout: int = 30) -> dict:
        response = requests.post(
            f"https://api.telegram.org/bot{self.config.telegram_bot_token}/{method}",
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()

    def _send_message(self, chat_id: str, message: str) -> None:
        try:
            self._api_request("sendMessage", {"chat_id": chat_id, "text": message}, timeout=15)
        except Exception as exc:
            logger.warning("Telegram sendMessage failed: %s", exc)

    def _attempt_activation(self, chat_id: str, phone: str) -> None:
        activated = self.repository.activate_by_phone(phone, chat_id)
        if activated:
            self._send_message(
                chat_id,
                f"Activation successful for {activated.get('name')}. Telegram emergency alerts are now enabled.",
            )
            return

        self._send_message(
            chat_id,
            "No matching emergency contact found for this phone number. Please ask the traveler to verify your number in SafePassage.",
        )

    def _process_update(self, update: dict) -> None:
        message = update.get("message") or {}
        if not message:
            return

        chat = message.get("chat") or {}
        chat_id = str(chat.get("id") or "").strip()
        if not chat_id:
            return

        text_value = (message.get("text") or "").strip()
        if text_value.startswith("/start"):
            start_phone = extract_phone_from_start_command(text_value)
            if start_phone:
                self._attempt_activation(chat_id, start_phone)
                return

            self._send_message(
                chat_id,
                "SafePassage bot connected. Send /start <your_phone> or send your phone number in a separate message to activate alerts.",
            )
            return

        phone = extract_phone_from_message(message)
        if phone:
            self._attempt_activation(chat_id, phone)

    def run_forever(self) -> None:
        logger.info("Telegram bot poller started.")
        while True:
            try:
                updates_response = self._api_request(
                    "getUpdates",
                    {"timeout": 20, "offset": self.offset},
                    timeout=30,
                )
                if not updates_response.get("ok"):
                    time.sleep(self.config.poll_interval_seconds)
                    continue

                for update in updates_response.get("result", []):
                    update_id = int(update.get("update_id", 0))
                    if update_id:
                        self.offset = max(self.offset, update_id + 1)
                    self._process_update(update)

            except Exception as exc:
                logger.warning("Telegram poller error: %s", exc)
                time.sleep(self.config.poll_interval_seconds)


def load_config() -> BotConfig:
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    db_uri = os.getenv("SQLALCHEMY_DATABASE_URI", "").strip()
    poll_interval = int(os.getenv("TELEGRAM_POLL_INTERVAL_SECONDS", "2"))

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required.")
    if not db_uri:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is required.")

    return BotConfig(
        telegram_bot_token=token,
        sqlalchemy_database_uri=db_uri,
        poll_interval_seconds=max(1, poll_interval),
    )


def main() -> None:
    config = load_config()
    repository = EmergencyContactRepository(config.sqlalchemy_database_uri)
    TelegramBotService(config, repository).run_forever()


if __name__ == "__main__":
    main()
