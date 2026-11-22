#!/usr/bin/env python3
"""Skytrain Inc ticket validator, reconstructed from public BountyHunter behavior.

This is an intentionally unsafe training tool. It must not be used with
untrusted tickets outside the isolated lab container.
"""
from pathlib import Path


def validate_ticket(path):
    if not str(path).endswith(".md"):
        print("Wrong file type.")
        return False
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    if len(lines) < 4 or not lines[0].startswith("# Skytrain Inc"):
        return False
    if not lines[1].startswith("## Ticket to "):
        return False
    print("Destination:", lines[1][len("## Ticket to "):].strip())

    for index, line in enumerate(lines[2:], start=2):
        if line.startswith("__Ticket Code:__") and index + 1 < len(lines):
            expression = lines[index + 1]
            if not expression.startswith("**"):
                return False
            ticket_id = expression.replace("**", "").split("+", 1)[0]
            if int(ticket_id) % 7 != 4:
                return False
            # Genuine Python evaluation of the supplied ticket expression.
            # Deliberately vulnerable just like the retired training host.
            total = eval(expression.replace("**", ""))
            return total > 100
    return False


def main():
    path = input("Please enter the path to the ticket file.\n")
    if validate_ticket(path):
        print("Valid ticket.")
    else:
        print("Invalid ticket.")


if __name__ == "__main__":
    main()
