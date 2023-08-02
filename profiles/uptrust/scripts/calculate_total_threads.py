#!/usr/bin/env python

import argparse
import logging

def calculate_total_threads(children, depth):
    return sum(children**i for i in range(depth))

def main():
    parser = argparse.ArgumentParser(description='Calculate total conversation threads based on children per branch and depth of branching.')
    parser.add_argument('-c', '--children', type=int, default=2, help='Number of children per thread.')
    parser.add_argument('-d', '--depth', type=int, default=5, help='Depth of branching.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.')
    args = parser.parse_args()

    logging_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logging_level)

    logging.debug('Arguments: %s', vars(args))

    total_threads = calculate_total_threads(args.children, args.depth)

    logging.info('Total threads: %s', total_threads)

if __name__ == '__main__':
    main()
