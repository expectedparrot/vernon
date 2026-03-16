"""Fetch unread emails from the EP support inbox, or mark a message as read."""
import argparse
import json
import os
import sys

from dotenv import load_dotenv
from agentmail import AgentMail

load_dotenv()

INBOX = "ep-support@agentmail.to"


def fetch_unread(client):
    """Print each unread message as a JSON line."""
    msgs = client.inboxes.messages.list(INBOX, labels=["unread"]).messages
    for msg in msgs:
        full = client.inboxes.messages.get(INBOX, msg.message_id)
        sender = msg.from_
        if sender and "<" in sender:
            # Extract just the email address from "Name <email>" format
            sender = sender.split("<")[1].rstrip(">")
        record = {
            "message_id": msg.message_id,
            "from": sender,
            "to": getattr(msg, "to", None),
            "cc": getattr(msg, "cc", None),
            "subject": msg.subject,
            "timestamp": getattr(msg, "timestamp", None),
            "text": getattr(full, "text", None),
            "extracted_text": getattr(full, "extracted_text", None),
            "labels": msg.labels,
            "thread_id": getattr(msg, "thread_id", None),
        }
        print(json.dumps(record, default=str))


def mark_read(client, message_id):
    """Remove the 'unread' label from a message."""
    msg = client.inboxes.messages.get(INBOX, message_id)
    labels = list(msg.labels) if msg.labels else []
    if "unread" in labels:
        client.inboxes.messages.update(INBOX, message_id, remove_labels=["unread"])
        print(f"Marked {message_id} as read.", file=sys.stderr)
    else:
        print(f"{message_id} already read.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="EP Support inbox tool")
    parser.add_argument("--mark-read", metavar="MESSAGE_ID",
                        help="Mark a message as read")
    args = parser.parse_args()

    client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY"))

    if args.mark_read:
        mark_read(client, args.mark_read)
    else:
        fetch_unread(client)


if __name__ == "__main__":
    main()
