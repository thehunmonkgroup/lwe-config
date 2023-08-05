#!/usr/bin/env python

import argparse
import logging

def calculate_max_posts(branch_points, depth):
    return sum(branch_points**i for i in range(depth))

def main():
    parser = argparse.ArgumentParser(description='Calculate max conversation posts based on number of branch points and depth of branching.')
    parser.add_argument('-b', '--branch-points', type=int, default=2, help='Number of branch points per thread.')
    parser.add_argument('-d', '--depth', type=int, default=5, help='Depth of branching.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.')
    args = parser.parse_args()

    logging_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logging_level)

    logging.debug('Arguments: %s', vars(args))

    max_posts = calculate_max_posts(args.branch_points, args.depth)

    logging.info('Maximum posts: %s', max_posts)

if __name__ == '__main__':
    main()
