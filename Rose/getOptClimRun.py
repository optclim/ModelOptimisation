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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('study', type=Path,
                        help='name of study directory')
    parser.add_argument('-s', '--state', choices=STATES,
                        default='NEW',
                        help="look for run in particular state, default NEW")
    parser.add_argument('-c', '--change-state', action='store_true',
                        default=False, help="advance state")
    args = parser.parse_args()

    if not args.study.is_dir():
        parser.error(f'{args.study} is not a directory')

    next_state = STATES.index(args.state) + 1
    if next_state < len(STATES):
        next_state = STATES[next_state]
    else:
        next_state = None

    runs = []

    for r in args.study.iterdir():
        statefile = r / 'state'
        if statefile.exists():
            if statefile.read_text().strip() == args.state:
                runs.append(r.name)
                if args.change_state and next_state is not None:
                    statefile.write_text(next_state)
    if len(runs) > 0:
        print(' '.join(runs))


if __name__ == '__main__':
    main()
