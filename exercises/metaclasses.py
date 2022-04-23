"""Metaclass exercises"""


class UnsubclassableType:
    """Metaclass to make classes that cannot be subclassed."""


class InstanceTracker:
    """Metaclass to make iterating over a class iterate through instances."""


class Mapping:
    """Class that acts as a superclass of all mappings."""


class Hashable:
    """Class that acts as a superclass of hashable objects."""


class NoMethodCollisions:
    """Class which disallows class attributes to be redefined."""


class SnakeTestCase:
    """Like unittest.TestCase, but with support for snake_case methods."""
