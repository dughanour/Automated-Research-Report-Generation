import os
import yaml
import json
from pathlib import Path
from src.exceptions.custom_exception import CustomException
from src.logger.custom_logger import CustomLogger

log = CustomLogger().get_logger(__file__)

def _project_root_dir() -> Path:
    """
    Determine the absolute path of the project root directory.
    Example:
    /Users/username/Documents/automated-research-report-generation

    """
    return Path(__file__).resolve().parents[1]

def load_config(config_path: str | None = None) -> dict:
    """
    Load YAML configuration from a consistent project-level location.

    🔹 Priority:
        1. Explicit `config_path` argument (if provided)
        2. CONFIG_PATH environment variable
        3. Default path: <project_root>/config/configuration.yaml

    Args:
        config_path (str | None): Optional explicit config file path.

    Returns:
        dict: Parsed configuration dictionary.

    Raises:
        CustomException: If config file missing or invalid.
    """
    try:
        env_path = os.getenv("CONFIG_PATH")

        # step 1: Resolve the config path
        if config_path is None:
            config_path = env_path or str(_project_root_dir() / "config" / "configuration.yaml")
        
        path = Path(config_path)
        if not path.is_absolute():
            path = _project_root_dir() / path
        
        # step 2: Validate existence
        if not path.exists():
            log.error("Configuration file not found:", path=str(path))
            raise FileNotFoundError(f"Config file not found: {path}")
        
        # Step 3: Load YAML
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        # Step 4: Log config summary (not actual content)
        top_keys = list(config.keys()) if isinstance(config, dict) else []
        log.info("Configuration loaded successfully", path=str(path), keys=top_keys)

        return config

    except Exception as e:
        log.error("Failed to load configuration", error=str(e))
        raise CustomException("Failed to load configuration file", e)

if __name__ == "__main__":
    try:
        config = load_config()
        print(json.dumps(config, indent=2))
        log.info("Configuration loaded successfully")
    except CustomException as e:
        log.error("Failed to load configuration", error=str(e))


