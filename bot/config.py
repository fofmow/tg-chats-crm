from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Bot settings
    bot_token: str

    # Admin settings (comma-separated list of IDs)
    admin_ids: list[int]

    # Chat IDs
    ru_payin_chat_id: int
    eng_payin_chat_id: int
    payout_chat_id: int

    # Database
    database_url: str = "sqlite+aiosqlite:///data/crm.db"

    @property
    def payin_chat_ids(self) -> list[int]:
        """List of all pay-in chat IDs."""
        return [self.ru_payin_chat_id, self.eng_payin_chat_id]

    @property
    def all_chat_ids(self) -> list[int]:
        """List of all monitored chat IDs."""
        return [self.ru_payin_chat_id, self.eng_payin_chat_id, self.payout_chat_id]


settings = Settings()
