#!/usr/bin/env python3

from pathlib import Path
import argparse

# simple program that searches subdirectories in the input directory
# for the precence of a file called 'state'. If the state file is present
# and contains the specified state (by default NEW) it will report the name
# of the subdirectory to standard out as a space separated list. You can use
# the option -c to change state to the next state. See the STATES list below.


STATES = [
    'NEW',
    'QUEUED',
    'RUNNING',
    'COMPLETED']


def update_state(run, state="NEW", change_state=False):
    next_state = STATES.index(state) + 1
    if next_state < len(STATES):
        next_state = STATES[next_state]
    else:
        next_state = None

    statefile = run / 'state'
    if statefile.exists():
        if statefile.read_text().strip() == state:
            if change_state and next_state is not None:
                statefile.write_text(next_state)
            return run.name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('study', type=Path,
                        help='name of study directory')
    parser.add_argument('-s', '--state', choices=STATES,
                        default='NEW',
                        help="look for run in particular state, default NEW")
    parser.add_argument('-c', '--change-state', action='store_true',
                        default=False, help="advance state")
    parser.add_argument('-r', '--run',
                        help="modify the state of a particular run")
    args = parser.parse_args()

    if not args.study.is_dir():
        parser.error(f'{args.study} is not a directory')

    next_state = STATES.index(args.state) + 1
    if next_state < len(STATES):
        next_state = STATES[next_state]
    else:
        next_state = None

    runs = []

    if args.run is not None:
        r = update_state(args.study/args.run,
                         state=args.state, change_state=args.change_state)
        if r is not None:
            print(r)
    else:
        for r in args.study.iterdir():
            r = update_state(r, state=args.state,
                             change_state=args.change_state)
            if r is not None:
                runs.append(r)
        if len(runs) > 0:
            print(' '.join(runs))


if __name__ == '__main__':
    main()
