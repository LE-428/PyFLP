from __future__ import annotations

from typing import Callable

import colour
import pytest

from pyflp.arrangement import Arrangement, Arrangements, Track


def test_arrangements(arrangements: Arrangements):
    assert len(arrangements) == 2
    assert arrangements.current == arrangements[0]
    assert arrangements.height == 456
    assert arrangements.loop_pos is None
    assert arrangements.max_tracks == 500
    assert arrangements.time_signature.num == 4
    assert arrangements.time_signature.beat == 4


@pytest.fixture(scope="session")
def arrangement(arrangements: Arrangements):
    def wrapper(index: int):
        return arrangements[index]

    return wrapper


@pytest.fixture(scope="session")
def tracks(arrangement: Callable[[int], Arrangement]):
    return tuple(arrangement(0).tracks)[:15]


def test_track_color(tracks: tuple[Track, ...]):
    for track in tracks:
        assert (
            track.color == colour.Color("red")
            if track.name == "Red"
            else track.color == colour.Color("#485156")
        )


def test_track_content_locked(tracks: tuple[Track, ...]):
    for track in tracks:
        assert (
            track.content_locked
            if track.name == "Locked to content"
            else not track.content_locked
        )


def test_track_enabled(tracks: tuple[Track, ...]):
    for track in tracks:
        assert not track.enabled if track.name == "Disabled" else track.enabled


def test_track_grouped(tracks: tuple[Track, ...]):
    for track in tracks:
        assert track.grouped if track.name == "Grouped" else not track.grouped


# TODO #35
# def test_track_height(tracks: tuple[Track, ...]):
#     for track in tracks:
#         if track.name == "Min Size":
#             assert track.height == 0.0
#         elif track.name == "Max Size":
#             assert track.height == 18.4
#         else:
#             assert track.height == 1.0


def test_track_icon(tracks: tuple[Track, ...]):
    for track in tracks:
        assert track.icon == 70 if track.name == "Iconified" else not track.icon


def test_track_items(tracks: tuple[Track, ...]):
    for track in tracks:
        num_items = 0
        if track.name == "Audio track":
            num_items = 16
        if track.name == "MIDI":
            num_items = 4
        elif track.name in ("Cut pattern", "Automation"):
            num_items = 1

        assert len(track.items) == num_items


def test_track_locked(tracks: tuple[Track, ...]):
    for track in tracks:
        assert track.locked if track.name == "Locked" else not track.locked


def test_track_name(tracks: tuple[Track, ...]):
    assert [track.name for track in tracks] == [
        "Enabled",
        "Disabled",
        "Locked",
        "Red",
        "Iconified",
        "Grouped",
        "Audio track",
        "Instrument track",
        "MIDI",
        "Cut pattern",
        "Automation",
        "Locked to content",
        "Locked to size",
        "Min Size",
        "Max Size",
    ]


def test_first_arrangement(arrangement: Callable[[int], Arrangement]):
    arr = arrangement(0)
    assert arr.name == "Just tracks"
    assert not tuple(arr.timemarkers)


def test_second_arrangement(arrangement: Callable[[int], Arrangement]):
    arr = arrangement(1)
    assert arr.name == "Just timemarkers"
    assert len(tuple(arr.timemarkers)) == 11
