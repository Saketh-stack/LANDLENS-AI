import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Information
    PROJECT_NAME: str = 'SIH26018 — Intelligent Land Record Digitization and Validation System'
    API_V1_STR: str = '/api'
    VERSION: str = '1.0.0'
    MINISTRY: str = 'Ministry of Rural Development'
    DEPARTMENT: str = 'Department of Land Resources (DoLR)'

    # Database
    DATABASE_URL: str = 'sqlite:///./land_records.db'

    # Security & JWT
    JWT_SECRET_KEY: str = 'sih26018-super-secret-key-dolr-smart-land-records-2026-prod'
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # AI & LLM Providers
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = 'gpt-5.0'
    GEMINI_API_KEY: Optional[str] = None

    # Spatial GIS & Google Maps
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    GOOGLE_GEOCODING_API_KEY: Optional[str] = None
    GOOGLE_STREET_VIEW_API_KEY: Optional[str] = None

    # OCR Providers
    OCR_PROVIDER: str = 'RAPIDOCR'
    OCR_API_KEY: Optional[str] = None

    # Storage
    STORAGE_PROVIDER: str = 'local'
    STORAGE_BUCKET: str = 'uploads'
    UPLOAD_DIR: str = 'uploads'

    # Operating Modes
    ENVIRONMENT: str = 'development'
    MOCK_MODE: bool = False
    DEMO_MODE: bool = True
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    @property
    def is_openai_enabled(self) -> bool:
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.strip() and not self.OPENAI_API_KEY.startswith("your_"))

    @property
    def is_gemini_enabled(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip() and not self.GEMINI_API_KEY.startswith("your_"))

    @property
    def is_llm_enabled(self) -> bool:
        return self.is_openai_enabled or self.is_gemini_enabled

    @property
    def is_google_maps_enabled(self) -> bool:
        return bool(self.GOOGLE_MAPS_API_KEY and self.GOOGLE_MAPS_API_KEY.strip() and not self.GOOGLE_MAPS_API_KEY.startswith("your_"))

    @property
    def is_ocr_configured(self) -> bool:
        return bool(self.OCR_PROVIDER != 'MOCK')

settings = Settings()
