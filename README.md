# vault-init

This is AWS/python version of [vault-init](https://github.com/kelseyhightower/vault-init).

## Configuration

The following optional environment variables are supported,

- `CHECK_INTERVAL` - The time in seconds between Vault health checks. Default `10`.
- `RECOVERY_SHARES` - The number of shares to split the recovery key into. Default `5`.
- `RECOVERY_THRESHOLD` - The number of shares required to reconstruct the recovery key. This must be less than or equal to `RECOVERY_SHARES`. Default `3`.
- `SSM_PARAMTER_STORE_PREFIX` - The SSM parameter store name prefix. Default `/vault`.
- `VAULT_ADDR` - The Vault URL. Default `https://127.0.0.1:8200`.

## IAM permissions

```json
```
