from enum import StrEnum


class Permissions(StrEnum):
    create_tokens = "create_tokens"
    create_secrets = "create_secrets"
    read_secrets = "read_secrets"
