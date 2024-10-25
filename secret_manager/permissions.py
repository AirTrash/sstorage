from enum import StrEnum


class Permissions(StrEnum):
    create_tokens = "create_tokens"
    create_secrets = "create_secrets"
    read_secrets = "read_secrets"
    delete_secrets = "delete_secrets"
    delete_tokens = "delete_tokens"


all_perms = (
    Permissions.create_tokens,
    Permissions.create_secrets,
    Permissions.read_secrets,
    Permissions.delete_tokens,
    Permissions.delete_secrets
)
