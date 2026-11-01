"""Account management CLI.

Usage (inside the backend container):
    python -m app.manage create-user <username>
    python -m app.manage delete-user <username>

The password is prompted for interactively, or read from stdin with
--password-stdin (e.g. `echo "$PASS" | python -m app.manage create-user ...`).
"""

import argparse
import getpass
import sys

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.auth.models import (
    AuthSession,  # noqa: F401  (register models on Base.metadata)
)
from app.database.core import SessionFactory
from app.sensors.models import Sensor  # noqa: F401
from app.users.models import User
from app.users.schemas import UserCreate
from app.users.service import user_service


class CommandError(Exception):
    pass


def _read_password(from_stdin: bool) -> str:
    if from_stdin:
        return sys.stdin.readline().rstrip("\n")
    password = getpass.getpass("Password: ")
    if password != getpass.getpass("Repeat password: "):
        raise CommandError("Passwords do not match.")
    return password


def create_user(
    db: Session,
    username: str,
    password: str,
) -> User:
    try:
        user_in = UserCreate(username=username, password=password)
    except ValidationError as e:
        messages = (
            f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()
        )
        raise CommandError("; ".join(messages)) from e
    if user_service.get_user_by_username(db, user_in.username):
        raise CommandError(f"User '{user_in.username}' already exists.")
    return user_service.create_user(db, user_in)


def delete_user(db: Session, username: str) -> None:
    user = user_service.get_user_by_username(db, username.lower())
    if user is None:
        raise CommandError(f"User '{username}' does not exist.")
    user_service.delete_user(db, user)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.manage")
    commands = parser.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create-user", help="create a user account")
    create.add_argument("username")
    create.add_argument(
        "--password-stdin", action="store_true", help="read password from stdin"
    )

    delete = commands.add_parser("delete-user", help="delete a user account")
    delete.add_argument("username")

    args = parser.parse_args(argv)
    try:
        with SessionFactory() as db:
            if args.command == "create-user":
                password = _read_password(args.password_stdin)
                user = create_user(db, args.username, password)
                print(f"Created user '{user.username}'.")
            else:
                delete_user(db, args.username)
                print(f"Deleted user '{args.username}'.")
    except CommandError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
