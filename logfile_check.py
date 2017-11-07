#!/usr/bin/env python3

"""
logfile_check.py - check if a logfile is good.

A good logfile has simulations that each has
(a) non-duplicated, non-skipped, monotonically increasing timestamps; and
(b) the last timestamp value (in picoseconds) as a multiple of 1000.
"""


import argparse


def read_logfile(logfile):
    """Read logfile content and store in memory.

    Args:
        logfile (str): path to the F@H logfile.

    Returns:
        A dict mapping simulation_id's to their corresponding timestamps. A simulation_id
        follows the {project_number}:{run_number}:{clone_number} format. For example:

            {
                '1797:0:0': [0, 100, 200, ..., 12000],
                '1797:0:1': [0, 100, 200, ..., 12000],
                ...
            }
    """
    logfile_data = {}
    logfile_handle = open(logfile, "r")

    for line in logfile_handle:
        (project_number, run_number, clone_number, timestamp_in_ps) = line.split()
        simulation_id = f"{project_number}:{run_number}:{clone_number}"
        if simulation_id not in logfile_data.keys() or logfile_data[simulation_id] is None:
            logfile_data[simulation_id] = [int(timestamp_in_ps)]
        else:
            logfile_data[simulation_id].append(int(timestamp_in_ps))

    logfile_handle.close()
    return logfile_data


def check(logfile):
    """Check for missing, duplicate, and non-thousands-ending timestamps.

    Args:
        logfile(str): path to the F@H logfile.

    Returns:
        A dict maps from simulation_id's to their corresponding SimCheckResult instances.
        A simulation_id follows the {project_number}:{run_number}:{clone_number} format.
        For example:
            {
                '1797:0:0': <an instance of SimCheckResult>,
                '1797:0:1': <an instance of SimCheckResult>
                ...
            }
    """
    logfile_data = read_logfile(logfile)
    check_result = {}

    for simulation_id, timestamps in logfile_data.items():
        sim_check_result = SimCheckResult()

        if not is_strictly_increasing(timestamps) or min(timestamps) != 0:
            sim_check_result.missing_timestamps = find_missing_timestamps(
                timestamps)

        sim_check_result.duplicate_timestamps = find_duplicate_timestamps(
            timestamps)
        sim_check_result.is_last_ts_in_thousands = is_last_ts_in_thousands(
            timestamps)
        sim_check_result.last_timestamp = max(timestamps)

        check_result[simulation_id] = sim_check_result

    return check_result


def find_missing_timestamps(timestamps):
    """Find missing value(s) in a sequence of timestamps.

    This function also takes into consideration the scenario when timestamp 0
    is missing from the timestamps argument.

    Args:
        timestamps (list): A list of timestamps (in picoseconds).

    Returns:
        An ascendingly sorted list of missing timestamp values (if any).
    """
    if timestamps is None or len(timestamps) == 0:
        return None

    min_correct_timestamp = timestamps[0] if timestamps[0] == 0 else 0
    max_correct_timestamp = timestamps[-1]
    correct_time_values_in_ps = (
        set(range(min_correct_timestamp,
                  max_correct_timestamp,
                  100))
    )
    missing_timestamps = correct_time_values_in_ps.difference(timestamps)
    return sorted(missing_timestamps)


def find_duplicate_timestamps(timestamps):
    """Find duplicate value(s) in a sequence of timestamps.

    Args:
        timestamps (list): A list of timestamps (in picoseconds).

    Returns:
        An ascendingly sorted list of duplicated timestamp values (if any).
    """
    if timestamps is None or len(timestamps) < 2:
        return None

    duplicate_timestamps = set(timestamp for timestamp in timestamps
                               if timestamps.count(timestamp) > 1)
    return sorted(duplicate_timestamps)


def is_strictly_increasing(timestamps):
    """Check if the timestamps are strictly increasing.

    "Strictly increasing" means that the passed in values are increasing as
    given and they are 100ps apart from one to the next.

    Args:
        timestamps (list): An ascendingly sorted list of timestamps (in picoseconds).

    Returns:
        True if the timestamps fit the "strictly increasing" definition above,
        False otherwise.
    """
    if timestamps is None or len(timestamps) == 0:
        return True

    return all(x < y and x + 100 == y for x, y in zip(timestamps, timestamps[1:]))


def is_last_ts_in_thousands(timestamps):
    """Detect if the last timestamp in a sequence is a multiple of 1000.

    Args:
        timestamps (list): An list of timestamps (in picoseconds).

    Returns:
        True if the last timestamp is a multiple of 1000, False otherwise.
    """
    if timestamps is None:
        return True

    last_timestamp = max(timestamps)
    return last_timestamp % 1000 == 0


def print_to_file(check_result, outfile):
    """Print check result to file.

    Args:
        check_result (dict): a dict maps from simulation_id's to their corresponding
                             SimCheckResult instances. A simulation_id follows the
                             {project_number}:{run_number}:{clone_number} format.
        outfile (str): path to the outfile.
    """
    outfile_handle = open(outfile, 'w+')
    for simulation_id, sim_check_result in check_result.items():
        formatted_simulation_id = format_simulation_id(simulation_id)
        outfile_handle.write(formatted_simulation_id + "\n")

        if ((sim_check_result.missing_timestamps is None or
             len(sim_check_result.missing_timestamps) == 0) and
                (sim_check_result.duplicate_timestamps is None or
                 len(sim_check_result.duplicate_timestamps) == 0) and
                sim_check_result.is_last_ts_in_thousands):
            outfile_handle.write('\tNo issues found\n')
            continue

        if (sim_check_result.missing_timestamps is not None and
                len(sim_check_result.missing_timestamps) > 0):
            outfile_handle.write('\tMissing timestamps: ')
            outfile_handle.write(
                ", ".join(str(missing_ts)
                          for missing_ts in sim_check_result.missing_timestamps)
                + "\n")

        if (sim_check_result.duplicate_timestamps is not None and
                len(sim_check_result.duplicate_timestamps) > 0):
            outfile_handle.write('\tDuplicate timestamps: ')
            outfile_handle.write(
                ", ".join(str(duplicate_ts)
                          for duplicate_ts in sim_check_result.duplicate_timestamps)
                + "\n")

        if not sim_check_result.is_last_ts_in_thousands:
            outfile_handle.write(
                f"\tLast timestamp ({sim_check_result.last_timestamp}ps) is not in thousands\n"
            )

    outfile_handle.close()


def format_simulation_id(simulation_id):
    """Convert simulation_id into a more informative format.

    Args:
        simulation_id (str): simulation id in the
                             {project_number}:{run_number}:{clone_number} format.

    Returns:
        Simulation id in the PROJ{project_number}/RUN{run_number}/CLONE{clone_number} format.
    """
    if not simulation_id:
        return

    (project_number, run_number, clone_number) = simulation_id.split(':')
    return f"PROJ{project_number}/RUN{run_number}/CLONE{clone_number}"


class SimCheckResult:
    """Check result for a simulation.

    Attributes:
        missing_timestamps (list): a list of timestamps missing from the simulation.
        duplicate_timestamps (list): a list of duplicate timestamps found in the simulation.
        is_last_ts_in_thousands (bool): indicates if the last timestamp
                                        is in thousands (picoseconds)
        last_timestamp (int): the last timestamp (ps) in the simulation.
    """

    def __init__(self):
        """Instantiate an object with default values for the attributes."""
        self.missing_timestamps = None
        self.duplicate_timestamps = None
        self.is_last_ts_in_thousands = False
        self.simulation_id = ''
        self.last_timestamp = None


if __name__ == '__main__':
    ARGPARSE = argparse.ArgumentParser(
        prog='logfile_check', description=__doc__)
    ARGPARSE.add_argument('logfile', help='input logfile')
    ARGPARSE.add_argument('outfile', help='outfile')

    ARGS = ARGPARSE.parse_args()
    CHECK_RESULT = check(ARGS.logfile)
    print_to_file(CHECK_RESULT, ARGS.outfile)
