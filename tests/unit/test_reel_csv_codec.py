import pytest

from kavunbet_optimizer.domain.reel_set import ReelSet
from kavunbet_optimizer.infrastructure.reel_csv_codec import ReelCsvCodec


@pytest.mark.parametrize(
    ("csv_content", "expected_reels"),
    [
        (
            "H1,H2,H3\nL1,L2,L3\nH4,H5,L4\n",
            [
                ["H1", "L1", "H4"],  # reel 1
                ["H2", "L2", "H5"],  # reel 2
                ["H3", "L3", "L4"],  # reel 3
            ],
        ),
    ],
)
def test_decode_transposes_csv_rows_into_reels(
    csv_content: str, expected_reels: list[list[str]]
) -> None:
    result = ReelCsvCodec.decode(csv_content)

    assert result.reels == expected_reels


@pytest.mark.parametrize(
    ("expected_csv", "reels_content"),
    [
        (
            "H1,H2,H3\nL1,L2,L3\nH4,H5,L4\n",
            [
                ["H1", "L1", "H4"],  # reel 1
                ["H2", "L2", "H5"],  # reel 2
                ["H3", "L3", "L4"],  # reel 3
            ],
        ),
    ],
)
def test_encode_transposes_reels_into_csv_rows(
    expected_csv: str,
    reels_content: list[list[str]],
) -> None:
    result = ReelCsvCodec.encode(ReelSet(reels_content))

    assert result == expected_csv


@pytest.mark.parametrize("csv_content", ["", "\n", "\r\n"])
def test_decode_rejects_empty_csv(csv_content: str) -> None:
    with pytest.raises(ValueError, match="reel CSV is empty"):
        ReelCsvCodec.decode(csv_content)


def test_decode_rejects_inconsistent_row_widths() -> None:
    csv_content = "H1,H2,H3\nL1,L2\n"

    with pytest.raises(ValueError, match="reel CSV rows have inconsistent widths"):
        ReelCsvCodec.decode(csv_content)


def test_decode_ignores_blank_lines() -> None:
    csv_content = "H1,H2\n\nL1,L2\n"

    result = ReelCsvCodec.decode(csv_content)

    assert result.reels == [
        ["H1", "L1"],
        ["H2", "L2"],
    ]


def test_encode_rejects_reels_with_different_lengths() -> None:
    reel_set = ReelSet(
        [
            ["H1", "L1"],
            ["H2"],
        ]
    )

    with pytest.raises(ValueError, match="CSV output requires equally sized reels"):
        ReelCsvCodec.encode(reel_set)


def test_csv_round_trip_preserves_reels() -> None:
    original = ReelSet(
        [
            ["H1", "L1", "H4"],
            ["H2", "L2", "H5"],
            ["H3", "L3", "L4"],
        ]
    )

    encoded = ReelCsvCodec.encode(original)
    decoded = ReelCsvCodec.decode(encoded)

    assert decoded.reels == original.reels
