# vault-init

This is AWS/python version of [vault-init](https://github.com/kelseyhightower/vault-init).

## Assumption

It assumes, you are running the Vault on EKS with AWS KMS auto-unseal option.

## Configuration

The following optional environment variables are supported,

- `AWS_DEFAULT_REGION` - The default AWS region. Default `eu-west-1`.
- `CHECK_INTERVAL` - The time in seconds between Vault health checks. Default `10`.
- `RECOVERY_SHARES` - The number of shares to split the recovery key into. Default `5`.
- `RECOVERY_THRESHOLD` - The number of shares required to reconstruct the recovery key. This must be less than or equal to `RECOVERY_SHARES`. Default `3`.
- `SSM_PARAMTER_STORE_PREFIX` - The SSM parameter store name prefix. Default `/vault`.
- `VAULT_ADDR` - The Vault URL. Default `https://127.0.0.1:8200`.
- `VAULT_TLS_VERIFY` - Either a boolean to indicate whether TLS verification should be performed when sending requests to Vault, or a string pointing at the CA bundle to use for verification. Default `False`.

## Vault Helm chart value

```yaml
server:
  extraContainers:
  - env:
    - name: VAULT_TLS_VERIFY
      value: /vault/userconfig/vault-tls/tls.ca
    image: gopisaba/vault-init:latest
    imagePullPolicy: Always
    name: vault-init
    volumeMounts:
    - mountPath: /vault/userconfig/vault-tls
      name: userconfig-vault-tls
      readOnly: true
```

## IAM permissions

The Vault Service Account IAM Role should have permission to write to SSM parameter store.

```json
{
    "Sid": "SSMWritePermissions",
    "Effect": "Allow",
    "Action": "ssm:PutParameter",
    "Resource": "arn:aws:ssm:eu-west-1:1234567890123:parameter/vault"
}
```
