#!/usr/bin/env python3

"""Test cases for logfile_check.py; run by pytest"""

import logfile_check


def test_is_strictly_increasing_1():
    """Checking monotonic sequence should return True."""
    assert logfile_check.is_strictly_increasing([0, 100, 200])


def test_is_strictly_increasing_2():
    """Checking non-monotonic sequence should return False."""
    assert not logfile_check.is_strictly_increasing([0, 200, 1000])


def test_is_strictly_increasing_3():
    """Checking an empty sequence should return True."""
    assert logfile_check.is_strictly_increasing(None)


def test_is_strictly_increasing_4():
    """Checking a sequence of one item should return True."""
    assert logfile_check.is_strictly_increasing([500])


def test_is_strictly_increasing_5():
    """Checking a sequence of two items that are not 100 different should return False."""
    assert not logfile_check.is_strictly_increasing([500, 2100])


def test_is_strictly_increasing_6():
    """Checking a sequence of two items in reverse order should return False."""
    assert not logfile_check.is_strictly_increasing([2500, 2100])


def test_find_missing_timestamps_1():
    """No missing timestamps should be found for [0, 100]."""
    missing_timestamps = logfile_check.find_missing_timestamps([0, 100])
    assert missing_timestamps is None or not missing_timestamps


def test_find_missing_timestamps_2():
    """No missing timestamps should be found for [0]."""
    missing_timestamps = logfile_check.find_missing_timestamps([0])
    assert missing_timestamps is None or not missing_timestamps


def test_find_missing_timestamps_3():
    """No missing timestamps should be found for None."""
    missing_timestamps = logfile_check.find_missing_timestamps(None)
    assert missing_timestamps is None or not missing_timestamps


def test_find_missing_timestamps_4():
    """Timestamps 300, 400, 700, 800, 900, 1100, 1200, 1300 should be detected as missing."""
    missing_timestamps = logfile_check.find_missing_timestamps(
        [0, 100, 200, 500, 600, 1000, 1400])
    assert missing_timestamps == [300, 400, 700, 800, 900, 1100, 1200, 1300]


def test_find_missing_timestamps_5():
    """Timestamps 0, 100, 300, 400, 700, 800, 900, 1100, 1200, 1300
    should be detected as missing.
    """
    missing_timestamps = logfile_check.find_missing_timestamps(
        [200, 500, 600, 1000, 1400])
    assert missing_timestamps == [0, 100, 300, 400, 700, 800, 900, 1100, 1200, 1300]

def test_find_missing_timestamps_6():
    """Timestamps 0, 100, 200, 300, 400, 500, 600, 700, 800, 900
    should be detected as missing.
    """
    missing_timestamps = logfile_check.find_missing_timestamps([1000])
    assert missing_timestamps == [0, 100, 200, 300, 400, 500, 600, 700, 800, 900]

def test_find_missing_timestamps_7():
    """No missing timestamps should be found for an empty list."""
    missing_timestamps = logfile_check.find_missing_timestamps([])
    assert missing_timestamps is None

def test_find_dup_timestamps_1():
    """An empty sequence (None) should have no duplicate."""
    assert logfile_check.find_duplicate_timestamps(None) is None


def test_find_dup_timestamps_2():
    """A sequence of one element should have no duplicate."""
    assert logfile_check.find_duplicate_timestamps([1200]) is None


def test_find_dup_timestamps_3():
    """A duplicate of 100 should be found."""
    assert logfile_check.find_duplicate_timestamps(
        [0, 100, 100, 200, 300]) == [100]


def test_find_dup_timestamps_4():
    """Timestamps 500, 1200 should be detected as duplicate."""
    assert logfile_check.find_duplicate_timestamps(
        [0, 100, 200, 300, 500, 500, 600, 1200, 1200]) == [500, 1200]


def test_last_ts_in_thousands_1():
    """An empty sequence should be considered 'last-timestamp-is-multiple-of-1000'."""
    assert logfile_check.is_last_ts_in_thousands(None)


def test_last_ts_in_thousands_2():
    """This check should return True."""
    assert logfile_check.is_last_ts_in_thousands([0])


def test_last_ts_in_thousands_3():
    """This check should return True."""
    assert logfile_check.is_last_ts_in_thousands([0, 12000])


def test_last_ts_in_thousands_4():
    """This check should return False."""
    assert not logfile_check.is_last_ts_in_thousands([1100, 1200])
