import argparse
import csv
import re
import sys

from datetime import datetime
from typing import Any, Iterator


def parse_args() -> argparse.Namespace:
    """
    Parses the arguments needed for the input
    """
    parser = argparse.ArgumentParser(description="UBS Transactions")
    parser.add_argument(
        "--regexp", help="The regexp to match on", type=str, required=True
    )
    parser.add_argument(
        "--start_date",
        help="Consider dates only after this date. Must be of the form DD.MM.YYYY",
        type=str,
        default=None,
        required=False,
    )
    parser.add_argument(
        "--end_date",
        help="Consider dates only before this date. Must be of the form DD.MM.YYYY",
        type=str,
        default=None,
        required=False,
    )
    parser.add_argument(
        "--delimiter",
        help="The delimiter to use to read the CSV",
        type=str,
        default=";",
        required=False,
    )
    parser.add_argument(
        "--path",
        help="The path to the CSV",
        type=str,
        default="transactions.csv",
        required=False,
    )
    parser.add_argument(
        "--print_individual_transactions",
        help="Whether to print individual transactions",
        action="store_true",
    )
    return parser.parse_args()


def safe_iter(it: csv.DictReader) -> Iterator[Any]:
    """
    Returns a safe iterator that won't fail on common exceptions.
    """
    while True:
        try:
            item = next(it)
            if len(item) < 8 or item[0] == "Account number" or item[0] == "":
                continue
            yield item
        except StopIteration:
            break
        except UnicodeDecodeError as e:
            print(f"The unicode decode error is {e}")


def main():
    """
    This is a script to read UBS banking transactions and
    see how many match a certain regexp. It also includes
    supports for start/end dates.
    """
    args = parse_args()
    total = 0
    with open(args.path, "rt", encoding="cp1252") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=args.delimiter)
        print(type(csv_reader))
        return
        for row in safe_iter(csv_reader):
            purchase_date = datetime.strptime(row[3], "%d.%m.%Y")
            booking_text = row[4]
            original_amount = float(row[6])
            try:
                conversion_rate = float(row[8])
            except ValueError as e:
                conversion_rate = 1.0
            if not re.match(args.regexp, booking_text):
                continue

            if args.start_date:
                start_date = datetime.strptime(args.start_date, "%d.%m.%Y")
                if purchase_date < start_date:
                    continue

            if args.end_date:
                end_date = datetime.strptime(args.end_date, "%d.%m.%Y")
                if end_date < purchase_date:
                    continue

            total += original_amount * conversion_rate
            if args.print_individual_transactions:
                print(
                    f"The total transaction is: \n",
                    f"purchase_date: {purchase_date}\n",
                    f"booking_text: {booking_text}\n",
                    f"original_amount: {original_amount}\n",
                    f"conversion_rate: {conversion_rate}\n",
                )

    print(
        "The total amount spend on all transactions matching"
        f" the regexp {args.regexp} is {total:.2f}."
    )
    if args.start_date:
        print(f"This started on {start_date}.")
    if args.end_date:
        print(f"This ended on {end_date}.")


if __name__ == "__main__":
    main()
