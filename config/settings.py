"""
Configuration settings for the Oral Health Policy Pulse system.
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Keys
    openai_api_key: str = Field(..., description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    huggingface_token: Optional[str] = Field(None, description="HuggingFace API token for dataset uploads")
    
    # HuggingFace Configuration
    hf_organization: Optional[str] = Field(None, description="HuggingFace organization name (e.g., 'CommunityOne')")
    hf_dataset_prefix: str = Field("oral-health-policy-pulse", description="Prefix for dataset names")
    
    # Databricks Configuration
    databricks_host: str = Field(..., description="Databricks workspace URL")
    databricks_token: str = Field(..., description="Databricks access token")
    databricks_warehouse_id: str = Field(..., description="SQL warehouse ID")
    
    # Delta Lake Configuration
    delta_lake_path: str = Field("dbfs:/oral-health-policy-pulse", description="Delta Lake base path")
    catalog_name: str = Field("oral_health", description="Unity Catalog name")
    schema_name: str = Field("policy_analysis", description="Schema name")
    
    # MLflow Configuration (for Databricks Agent Bricks)
    mlflow_tracking_uri: str = Field("databricks", description="MLflow tracking URI")
    mlflow_experiment_name: str = Field("/Users/shared/oral-health-agents", description="MLflow experiment")
    mlflow_model_name_prefix: str = Field("oral_health", description="Model name prefix in Unity Catalog")
    
    # Agent LLM Configuration
    classifier_model: str = Field("gpt-4-turbo-preview", description="LLM model for classification")
    sentiment_model_llm: str = Field("gpt-3.5-turbo", description="LLM model for sentiment analysis")
    advocacy_model: str = Field("gpt-4-turbo-preview", description="LLM model for advocacy generation")
    
    # Agent Configuration
    max_concurrent_agents: int = Field(5, description="Maximum concurrent agent operations")
    scraper_timeout: int = Field(30, description="Scraper timeout in seconds")
    classifier_batch_size: int = Field(50, description="Batch size for classification")
    sentiment_model: str = Field(
        "distilbert-base-uncased-finetuned-sst-2-english",
        description="HuggingFace sentiment model"
    )
    
    # Data Sources
    municode_api_key: Optional[str] = Field(None, description="Municode API key")
    legistar_api_key: Optional[str] = Field(None, description="Legistar API key")
    
    # Logging
    log_level: str = Field("INFO", description="Logging level")
    log_file: str = Field("logs/oral-health-policy-pulse.log", description="Log file path")
    
    # API Configuration
    api_host: str = Field("0.0.0.0", description="API host")
    api_port: int = Field(8000, description="API port")
    api_workers: int = Field(4, description="Number of API workers")
    
    # Vector Database
    qdrant_host: str = Field("localhost", description="Qdrant host")
    qdrant_port: int = Field(6333, description="Qdrant port")
    qdrant_collection: str = Field("policy_minutes", description="Qdrant collection name")
    
    # Email Configuration
    smtp_host: str = Field("smtp.gmail.com", description="SMTP host")
    smtp_port: int = Field(587, description="SMTP port")
    smtp_user: Optional[str] = Field(None, description="SMTP username")
    smtp_password: Optional[str] = Field(None, description="SMTP password")
    
    # Policy Topics of Interest
    policy_topics: List[str] = Field(
        default=[
            "water fluoridation",
            "fluoride",
            "school dental screening",
            "dental care funding",
            "medicaid dental",
            "children's dental health",
            "oral health",
            "dental clinic",
            "community dental"
        ],
        description="Topics to monitor"
    )
    
    # Geographic Configuration
    target_states: Optional[List[str]] = Field(
        None,
        description="Specific states to monitor (None = all states)"
    )
    
    min_population_threshold: int = Field(
        10000,
        description="Minimum city population to include"
    )


# Global settings instance
settings = Settings()
