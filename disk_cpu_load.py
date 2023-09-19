#!/usr/bin/env python3

"""
Script to test CPU load imposed by a simple disk read operation

Copyright (c) 2016 Canonical Ltd.

Authors:
    Rod Smith <rod.smith@canonical.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3,
as published by the Free Software Foundation.
"""

import argparse
import os
import sys
import subprocess

def get_cpu_load():
    with open('/proc/stat', 'r') as f:
        return list(map(int, f.readline().split()[1:]))

def compute_cpu_load(start_use, end_use):
    diff_idle = end_use[3] - start_use[3]

    diff_total = sum(end_use) - sum(start_use)
    diff_used = diff_total - diff_idle

    if diff_total != 0:
        return (diff_used * 100) // diff_total
    else:
        return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-load", type=int, default=30,
                        help="The maximum acceptable CPU load, as a percentage.")
    parser.add_argument("--xfer", type=int, default=4096,
                        help="The amount of data to read from the disk, in mebibytes.")
    parser.add_argument("--verbose", action='store_true',
                        help="If present, produce more verbose output.")
    parser.add_argument("device_filename", default="/dev/sda", nargs='?',
                        help="This is the WHOLE-DISK device filename.")

    args = parser.parse_args()

    disk_device = os.path.normpath(args.device_filename)
    if not os.path.exists(disk_device):
        print(f"Unknown block device \"{disk_device}\"")
        sys.exit(1)

    print(f"Testing CPU load when reading {args.xfer} MiB from {disk_device}")
    print(f"Maximum acceptable CPU load is {args.max_load}")
    subprocess.run(['blockdev', '--flushbufs', disk_device])

    start_load = get_cpu_load()
    if args.verbose:
        print("Beginning disk read....")
    subprocess.run(['dd', f'if={disk_device}', 'of=/dev/null', 'bs=1048576', f'count={args.xfer}'])
    if args.verbose:
        print("Disk read complete!")
    end_load = get_cpu_load()

    cpu_load = compute_cpu_load(start_load, end_load)
    print(f"Detected disk read CPU load is {cpu_load}")
    if cpu_load > args.max_load:
        print("*** DISK CPU LOAD TEST HAS FAILED! ***")
        sys.exit(1)

if __name__ == "__main__":
    main()
