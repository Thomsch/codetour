import argparse
from codetour import CodeTour

def main():
    parser = argparse.ArgumentParser(description='CodeTour CLI')
    parser.add_argument('commit', type=str, help='Commit hash to start the tour from')
    parser.add_argument('repository', type=str, help='Path to the repository')

    args = parser.parse_args()

    CodeTour.tour(args.commit, args.repository)

if __name__ == '__main__':
    main()