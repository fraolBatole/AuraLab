from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from . import DEFAULT_DB_PATH
from .db import AdminDatabase


class AdminCLI:
    def __init__(self, db_path: Path | str) -> None:
        self._db = AdminDatabase(db_path)

    def list_users(self, *, limit: int | None = None) -> None:
        for idx, record in enumerate(self._db.iter_users(), start=1):
            if limit is not None and idx > limit:
                break
            username = f"@{record.username}" if record.username else "(no username)"
            print(
                f"[{idx}] user_id={record.user_id} {username}\n"
                f"     name={record.first_name or 'N/A'} chat_id={record.chat_id}"
            )
            print(
                f"     credits: image={record.image_credits} video={record.video_credits}"
            )
            plan = record.current_plan or "None"
            print(f"     plan={plan} expires={record.plan_expiry_date or 'N/A'}")
            print(f"     created_at={record.created_at}")
            print()

    def reset(self, user_ids: Iterable[int], image: int | None, video: int | None) -> None:
        affected = self._db.reset_credits(user_ids, image=image, video=video)
        print(f"Updated credits for {affected} user(s)")

    def delete(self, user_ids: Iterable[int]) -> None:
        affected = self._db.delete_users(user_ids)
        print(f"Deleted {affected} user(s)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AuraLabs admin CLI")
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="Path to bot_database.db",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List users")
    list_parser.add_argument("--limit", type=int, default=None)

    reset_parser = subparsers.add_parser("reset-credits", help="Reset user credits")
    reset_parser.add_argument("user_ids", nargs="+", type=int)
    reset_parser.add_argument("--image", type=int, default=None)
    reset_parser.add_argument("--video", type=int, default=None)

    delete_parser = subparsers.add_parser("delete", help="Delete users")
    delete_parser.add_argument("user_ids", nargs="+", type=int)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    cli = AdminCLI(args.database)

    if args.command == "list":
        cli.list_users(limit=args.limit)
    elif args.command == "reset-credits":
        if args.image is None and args.video is None:
            parser.error("reset-credits requires --image and/or --video")
        cli.reset(args.user_ids, args.image, args.video)
    elif args.command == "delete":
        cli.delete(args.user_ids)
    else:  # pragma: no cover
        parser.error(f"Unknown command {args.command}")


if __name__ == "__main__":
    main()
