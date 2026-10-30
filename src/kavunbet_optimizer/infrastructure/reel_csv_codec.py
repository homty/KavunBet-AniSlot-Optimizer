"""
H1,H2,H3
L1,L2,L3
H4,H5,L4

is our csv, and our data in CosmosDB is actually
[
    ["H1", "L1", "H4"],  # reel 1
    ["H2", "L2", "H5"],  # reel 2
    ["H3", "L3", "L4"],  # reel 3
]

Our goal to make decoding for operation and incoding for storing our reels
"""

import csv

"""
It makes a string behave like an opened text file:
CSV stored in Cosmos as string and StringIO converts is into csv.reader
"""
from io import StringIO

from kavunbet_optimizer.domain.reel_set import ReelSet


class ReelCsvCodec:
    @staticmethod
    # csv_conten is our data from DB
    def decode(csv_content: str) -> ReelSet:
        csv_buffer = StringIO(
            csv_content, newline=""
        )  # csv module expects to control newline handling itself. This also works with CSV content using Windows \r\n or Unix \n.
        rows = [row for row in csv.reader(csv_buffer) if row]

        if not rows:
            raise ValueError("reel CSV is empty")

        width = len(rows[0])
        if any(len(row) != width for row in rows):
            raise ValueError("reel CSV rows have inconsistent widths")

        reels = [[row[column_index] for row in rows] for column_index in range(width)]

        return ReelSet(reels)

    @staticmethod
    def encode(reel_set: ReelSet) -> str:
        lengths = {len(reel) for reel in reel_set.reels}

        if len(lengths) != 1:
            raise ValueError("CSV output requires equally sized reels")
        csv_buffer = StringIO(newline="")
        writer = csv.writer(csv_buffer, lineterminator="\n")
        writer.writerows(zip(*reel_set.reels, strict=True))

        return csv_buffer.getvalue()
