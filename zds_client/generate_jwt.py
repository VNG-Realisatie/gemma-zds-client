#!/usr/bin/env python
import argparse

from zds_client import ClientAuth


def _setup_parser():
    parser = argparse.ArgumentParser(
        description="Generate a JWT for a set of credentials"
    )
    parser.add_argument("--client-id", help="Client ID to authenticate with")
    parser.add_argument("--secret", help="Secret belonging to the Client ID")
    return parser


def main():
    parser = _setup_parser()
    args = parser.parse_args()

    client_id = args.client_id
    if client_id is None:
        client_id = input("Client ID: ")
    secret = args.secret
    if secret is None:
        secret = input("Secret: ")

    auth = ClientAuth(client_id, secret)
    creds = auth.credentials()

    print("Use the following header(s) for authorization:")
    for key, value in creds.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
