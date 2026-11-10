"""Compare two CSV snapshots using a unique key column."""

import argparse
import csv
import json
from pathlib import Path


def load(path, key):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        header = next(reader, [])
        if not header or any(not name for name in header) or len(set(header)) != len(header):
            raise ValueError(f"{path}: expected unique, nonempty column names")
        if key not in header:
            raise ValueError(f"{path}: missing key column {key!r}")
        rows = {}
        for values in reader:
            if not values:
                continue  # blank line, commonly left at the end of an export
            if len(values) != len(header):
                raise ValueError(f"{path}:{reader.line_num}: wrong number of fields")
            row = dict(zip(header, values))
            identity = row[key]
            if not identity or identity in rows:
                raise ValueError(f"{path}:{reader.line_num}: empty or duplicate key {identity!r}")
            rows[identity] = row
    return set(header), rows


def compare(before, after, key):
    old_fields, old = load(before, key)
    new_fields, new = load(after, key)
    if old_fields != new_fields:
        raise ValueError("the snapshots must contain the same columns")

    changed = {}
    for identity in sorted(old.keys() & new.keys()):
        fields = {
            field: {"before": old[identity][field], "after": new[identity][field]}
            for field in sorted(old_fields)
            if old[identity][field] != new[identity][field]
        }
        if fields:
            changed[identity] = fields
    return {
        "added": [new[identity] for identity in sorted(new.keys() - old.keys())],
        "removed": [old[identity] for identity in sorted(old.keys() - new.keys())],
        "changed": changed,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--key", required=True)
    args = parser.parse_args()
    try:
        report = compare(args.before, args.after, args.key)
    except (ValueError, OSError, csv.Error) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
