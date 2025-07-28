"""Configuration settings for Pathway Pharmacy POS System."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "sqlite:///./pathway.db"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    app_name: str = "Pathway Pharmacy POS"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Pharmacy Information
    pharmacy_name: str = "Pathway Pharmacy"
    pharmacy_address: str = "123 Main St, Accra, Ghana"
    pharmacy_phone: str = "+233 20 123 4567"
    pharmacy_license: str = "PH123456789"

    # Currency Settings
    currency_code: str = "GHS"
    currency_symbol: str = "₵"
    currency_name: str = "Ghana Cedis"
    
    # Expiry Alert Settings (in days)
    expiry_alert_6_months: int = 180
    expiry_alert_3_months: int = 90
    expiry_alert_1_month: int = 30
    expiry_alert_1_week: int = 7
    
    # Email Settings
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: Optional[str] = None
    
    # Backup Settings
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    backup_retention_days: int = 30
    
    # API Settings
    rate_limit_per_minute: int = 100
    
    # File Upload Settings
    max_file_size_mb: int = 10
    allowed_extensions: str = "jpg,jpeg,png,pdf,xlsx,csv"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
