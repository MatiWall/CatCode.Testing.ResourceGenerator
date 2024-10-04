import logging
logger = logging.getLogger(__name__)
from pathlib import Path
from dataclasses import dataclass

from extensions.configuration import hosting_environment, read_configs_to_dataclass
from extensions.opentelemetry import configure_opentelemetry

BASE_DIR = Path(__file__).parent



@dataclass
class Config:
   core_api: str
   logging_level: str = 10

config = read_configs_to_dataclass(Config, BASE_DIR)

logger.info(f'Running using configs {config}')

configure_opentelemetry(
   enable_otel=hosting_environment.is_production(),
   level=config.logging_level
)


