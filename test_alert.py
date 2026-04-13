# test_alert.py
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

from core.alerts import check_and_send_alerts
check_and_send_alerts()