"""
Vault init
"""
import logging
import os
import time
import signal
import hvac
import boto3

logging.basicConfig(format="%(asctime)s [%(levelname)s] - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.info("Starting the vault-init service...")

try:
    VAULT_ADDR = os.environ["VAULT_ADDR"]
except KeyError:
    VAULT_ADDR = "https://127.0.0.1:8200"

try:
    VAULT_TLS_VERIFY = os.environ["VAULT_TLS_VERIFY"]
except KeyError:
    VAULT_TLS_VERIFY = False

try:
    AWS_DEFAULT_REGION = os.environ["AWS_DEFAULT_REGION"]
except KeyError:
    AWS_DEFAULT_REGION = "eu-west-1"

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
    client = boto3.client("ssm", region_name=AWS_DEFAULT_REGION)
    logging.info("Writing %s to SSM", name)
    client.put_parameter(
        Name=name,
        Description=description,
        Value=secret,
        Type="SecureString",
        Overwrite=True,
        AllowedPattern=r"^(?!\s*$).+",
    )
    return True


def initialize(client):
    """
    Initialize Vault if not already
    """
    if client.sys.is_initialized():
        logging.info("Vault already Initialized")
    else:
        logging.info("Initializing...")
        result = client.sys.initialize(
            recovery_shares=RECOVERY_SHARES, recovery_threshold=RECOVERY_THRESHOLD
        )
        write_to_ssm(
            result["root_token"],
            f"{SSM_PARAMETER_STORE_PREFIX}/root_token",
            "Vault Root Token",
        )
        write_to_ssm(
            result["keys"],
            f"{SSM_PARAMETER_STORE_PREFIX}/recovery_keys",
            "Vault Recovery Keys",
        )
        logging.info("Vault Initialized")


killer = GracefulKiller()
while not killer.kill_now:
    vault_client = hvac.Client(url=VAULT_ADDR, verify=VAULT_TLS_VERIFY)
    try:
        vault_client.sys.read_health_status(method="GET")
    # pylint: disable=W0703
    except Exception as err:
        logging.warning("Retrying after the exception, %s", err)
        time.sleep(CHECK_INTERVAL)
        continue
    initialize(vault_client)
    time.sleep(CHECK_INTERVAL)
