import logging
from watchtower import CloudWatchLogHandler
from dotenv import load_dotenv
import os

load_dotenv()

# Local development env variable is only defined locally
is_local_development = os.getenv('LOCAL_DEVELOPMENT') is not None 

if is_local_development:
    logging.basicConfig(level=logging.INFO)
    cloudwatch_logger = logging.getLogger(__name__)
else:
    cloudwatch_logger = logging.getLogger(__name__)
    cloudwatch_logger.setLevel(logging.INFO)

    cw_handler = CloudWatchLogHandler(
        log_group='qgen-ec2-server-logs',
        stream_name='qgen-logs',
    )
    cloudwatch_logger.addHandler(cw_handler)
