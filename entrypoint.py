"""
Vault init
"""
import logging
import os
import time
import hvac
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.info("Starting the vault-init service...")

VAULT_ADDR = os.environ["VAULT_ADDR"]
if not VAULT_ADDR:
    VAULT_ADDR = "https://127.0.0.1:8200"


CHECK_INTERVAL = int(os.environ["CHECK_INTERVAL"])
if not CHECK_INTERVAL:
    CHECK_INTERVAL = 10


SSM_PARAMETER_STORE_PREFIX = os.environ["SSM_PARAMTER_STORE_PREFIX"]
if not SSM_PARAMETER_STORE_PREFIX:
    SSM_PARAMETER_STORE_PREFIX = "/vault"


RECOVERY_SHARES = int(os.environ["RECOVERY_SHARES"])
if not RECOVERY_SHARES:
    RECOVERY_SHARES = 5


RECOVERY_THRESHOLD = int(os.environ["RECOVERY_THRESHOLD"])
if not RECOVERY_THRESHOLD:
    RECOVERY_THRESHOLD = 3


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
    while True:
        try:
            client = hvac.Client(url=VAULT_ADDR)
            break
        except Exception as err:
            logging.warning("Retrying after the exception %s", err)
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
            f"{SSM_PARAMETER_STORE_PREFIX}/recovery_keys", "Vault Recovery Keys", result["keys"]
        )
        logging.info("Vault Initialized")
