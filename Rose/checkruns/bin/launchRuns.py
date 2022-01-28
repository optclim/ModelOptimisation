#!/usr/bin/env python3

import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', nargs='*', help="runs to launch")
    args = parser.parse_args()

    for r in args.run:
        print(r)


if __name__ == '__main__':
    main()
