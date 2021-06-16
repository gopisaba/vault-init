"""
Vault init
"""
import logging
import os
import time
import signal
import hvac
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.info("Starting the vault-init service...")

try:
    VAULT_ADDR = os.environ["VAULT_ADDR"]
except KeyError:
    VAULT_ADDR = "https://127.0.0.1:8200"

try:
    CHECK_INTERVAL = int(os.environ["CHECK_INTERVAL"])
except KeyError:
    CHECK_INTERVAL = 10

try:
    SSM_PARAMETER_STORE_PREFIX = os.environ["SSM_PARAMTER_STORE_PREFIX"]
except KeyError:
    SSM_PARAMETER_STORE_PREFIX = "/vault"

try:
    RECOVERY_SHARES = int(os.environ["RECOVERY_SHARES"])
except KeyError:
    RECOVERY_SHARES = 5

try:
    RECOVERY_THRESHOLD = int(os.environ["RECOVERY_THRESHOLD"])
except KeyError:
    RECOVERY_THRESHOLD = 3

# pylint: disable=R0903
class GracefulKiller:
    """
    Graceful Killer
    """

    kill_now = False
    signals = {
        signal.SIGINT: "SIGINT",
        signal.SIGTERM: "SIGTERM",
    }

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum):
        """
        Log and Exit
        """
        logging.info("Received %s signal", self.signals[signum])
        logging.info("End of the program")
        self.kill_now = True


def write_to_ssm(secret, name, description):
    """
    Write Vault Secrets to SSM Parameter Store
    """
    client = boto3.client("ssm")
    client.put_parameter(
        Name=name,
        Description=description,
        Value=secret,
        Type="SecureString",
        Overwrite=True,
        AllowedPattern=r"^(?!\s*$).+",
    )
    return True


def initialize():
    """
    Initialize Vault if not already
    """
    client = hvac.Client(url=VAULT_ADDR)
    killer = GracefulKiller()
    while not killer.kill_now:
        try:
            client.sys.read_health_status(method="GET")
            break
        # pylint: disable=W0703
        except Exception as err:
            logging.warning("Retrying after the exception, %s", err)
            time.sleep(CHECK_INTERVAL)
            continue

    if client.sys.is_initialized():
        logging.info("Vault already Initialized")
    else:
        result = client.sys.initialize(
            recovery_shares=RECOVERY_SHARES, recovery_threshold=RECOVERY_THRESHOLD
        )
        write_to_ssm(
            f"{SSM_PARAMETER_STORE_PREFIX}/root_token",
            "Vault Root Token",
            result["root_token"],
        )
        write_to_ssm(
            f"{SSM_PARAMETER_STORE_PREFIX}/recovery_keys",
            "Vault Recovery Keys",
            result["keys"],
        )
        logging.info("Vault Initialized")


initialize()
