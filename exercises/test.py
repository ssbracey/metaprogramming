#!/usr/bin/env python3
from __future__ import print_function
import sys
import unittest

from test_data import MODULES, TESTS


def get_test(obj_name):
    if obj_name not in TESTS:
        raise SystemExit("Test for {} doesn't exist.".format(obj_name))
    return unittest.defaultTestLoader.loadTestsFromName(TESTS[obj_name])


def run_tests(tests):
    test_suite = unittest.TestSuite(tests)
    unittest.TextTestRunner().run(test_suite)


def print_object_names():
    for module, objects in MODULES.items():
        print("\n{}:\n".format(module))
        for obj in objects:
            print(obj)
        print()


def main(*arguments):
    if not arguments:
        print("Please select a thing to test")
        print_object_names()
    elif len(arguments) > 1:
        print("""
Can only call test.py with one argument: the name of the exercise being tested

Examples:

- python test.py get_hypotenuse
- python test.py hello.py
- python test.py BankAccount

This test script runs Trey's tests against your code.
The tests are written in files that end in "_test.py".

If you'd like to test your code manually, you can either:

1. Open a Python REPL, import your code, and execute it with specific arguments
2. Write your own test code at the bottom of your file (e.g. functions.py) and
run that file (e.g. "python functions.py").

Consult the website for instructions for running the exercises and ask Trey
for help when you get stuck.
        """.strip())
    elif ' ' in arguments[0] or '(' in arguments[0] or ',' in arguments[0]:
        print("Invalid characters found: {}\n".format(arguments[0]))
        print("This test script doesn't accept code, just an exercise name.\n")
        print("Example usage:")
        print("python test.py <exercise_name>\n")
    else:
        [argument] = arguments
        if argument.startswith(('modules/', 'modules\\', './modules/')):
            argument = argument.split('/', 1)[1]
        if argument == '--all':
            arguments = list(TESTS)
        else:
            arguments = [argument]
        tests = [
            get_test(arg)
            for arg in arguments
        ]
        print("Testing {}\n".format(', '.join(arguments)))
        test_classes = set(
            tuple(test.id().split('.')[:-1])
            for suite in tests
            for test in suite._tests
        )
        for module, cls in test_classes:
            print("Running {} test class in {}.py\n".format(cls, module))
        run_tests(tests)


if __name__ == "__main__":
    # Version check before all else
    major, minor, micro, releaselevel, serial = sys.version_info
    if (major, minor) < (3, 5):
        print("You are running Python {0}.{1}".format(major, minor))
        print("Must use Python version 3.5 or above")
        sys.exit(1)
    main(*sys.argv[1:])
