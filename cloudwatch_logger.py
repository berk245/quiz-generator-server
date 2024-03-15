import logging
from watchtower import CloudWatchLogHandler
from dotenv import load_dotenv

load_dotenv()

cloudwatch_logger = logging.getLogger(__name__)
cloudwatch_logger.setLevel(logging.INFO)

cw_handler = CloudWatchLogHandler(
    log_group='qgen-ec2-server-logs',
    stream_name='qgen-logs',
)
cloudwatch_logger.addHandler(cw_handler)
