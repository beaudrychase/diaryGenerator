import sys

from diary_generator.example_diary import create_example_diary


def main():
    create_example_diary(sys.argv[1])


if __name__ == "__main__":
    main()
