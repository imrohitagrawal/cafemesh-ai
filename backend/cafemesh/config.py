from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database: str = Field(default="data/cafemesh.db", alias="CAFEMESH_DATABASE")
    storage_backend: str = Field(default="sqlite", alias="CAFEMESH_STORAGE_BACKEND", pattern="^(sqlite|firestore)$")
    firestore_collection: str = Field(default="cafemesh_state", alias="CAFEMESH_FIRESTORE_COLLECTION", min_length=1, max_length=100)
    firestore_document: str = Field(default="demo", alias="CAFEMESH_FIRESTORE_DOCUMENT", min_length=1, max_length=100)
    demo_mode: bool = Field(default=True, alias="CAFEMESH_DEMO_MODE")
    request_timeout_seconds: float = Field(default=20, gt=0, le=60, alias="CAFEMESH_REQUEST_TIMEOUT_SECONDS")
    google_api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")
    google_client_id: str | None = Field(default=None, alias="GOOGLE_CLIENT_ID")
    require_google_auth: bool = Field(default=False, alias="CAFEMESH_REQUIRE_GOOGLE_AUTH")
    google_maps_api_key: str | None = Field(default=None, alias="GOOGLE_MAPS_API_KEY")
    google_maps_demo_origin: str = Field(default="Indiranagar Metro Station, Bengaluru, Karnataka, India", alias="GOOGLE_MAPS_DEMO_ORIGIN", min_length=4, max_length=180)
    google_places_bias_radius_meters: float = Field(default=5000, alias="GOOGLE_PLACES_BIAS_RADIUS_METERS", ge=100, le=50000)
    google_genai_use_vertexai: bool = Field(default=False, alias="GOOGLE_GENAI_USE_VERTEXAI")
    google_cloud_project: str | None = Field(default=None, alias="GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = Field(default="global", alias="GOOGLE_CLOUD_LOCATION")
    google_tts_model: str = Field(default="gemini-2.5-flash-tts", alias="GOOGLE_TTS_MODEL")
    model: str = Field(default="gemini-2.5-flash", alias="CAFEMESH_MODEL")
    prep_calibration_min_samples: int = Field(default=3, ge=1, le=100, alias="CAFEMESH_PREP_CALIBRATION_MIN_SAMPLES")
    prep_calibration_max_minutes: int = Field(default=180, gt=0, le=1440, alias="CAFEMESH_PREP_CALIBRATION_MAX_MINUTES")


settings = Settings()
