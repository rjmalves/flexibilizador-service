import os


class Settings:
    # ===== Application Settings =====
    app_version: str = "2.0.0"
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    root_path = os.getenv("ROOT_PATH", "")
    debug = os.getenv("DEBUG", "false").lower() == "true"

    # ===== S3 Configuration =====
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    s3_endpoint_url: str | None = os.getenv("S3_ENDPOINT_URL") or None
    default_bucket: str = os.getenv("DEFAULT_BUCKET", "decomp-bucket")

    # ===== Processing Configuration =====
    temp_dir: str = os.getenv("TEMP_DIR", "/tmp/flexibilizador")
    zip_compression_level: int = int(os.getenv("ZIP_COMPRESSION_LEVEL", "6"))
    max_temp_dir_age_hours: int = int(os.getenv("MAX_TEMP_DIR_AGE_HOURS", "24"))

    @classmethod
    def read_environments(cls):
        cls.host = os.getenv("HOST", "0.0.0.0")
        cls.port = int(os.getenv("PORT", "8000"))
        cls.root_path = os.getenv("ROOT_PATH", "")
        cls.debug = os.getenv("DEBUG", "false").lower() == "true"
        # S3 Configuration
        cls.aws_region = os.getenv("AWS_REGION", "us-east-1")
        cls.s3_endpoint_url = os.getenv("S3_ENDPOINT_URL") or None
        cls.default_bucket = os.getenv("DEFAULT_BUCKET", "decomp-bucket")
        # Processing Configuration
        cls.temp_dir = os.getenv("TEMP_DIR", "/tmp/flexibilizador")
        cls.zip_compression_level = int(os.getenv("ZIP_COMPRESSION_LEVEL", "6"))
        cls.max_temp_dir_age_hours = int(
            os.getenv("MAX_TEMP_DIR_AGE_HOURS", "24")
        )
