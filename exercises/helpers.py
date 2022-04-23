"""Test helpers"""
import sys


def error_message():
    print("Cannot run {} from the command-line.".format(sys.argv[0]))
    print()
    print("Run python test.py <your_exercise_name> instead")
