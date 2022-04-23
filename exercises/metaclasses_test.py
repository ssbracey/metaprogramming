"""Tests for metaclass exercises"""
from collections import OrderedDict, defaultdict, Counter, UserDict
import unittest

from metaclasses import (
    UnsubclassableType,
    InstanceTracker,
    Mapping,
    Hashable,
    NoMethodCollisions,
    SnakeTestCase,
)


class UnsubclassableTypeTests(unittest.TestCase):

    """Tests for UnsubclassableType."""

    def test_empty_class(self):
        class A(metaclass=UnsubclassableType):
            pass
        a = A()
        a.x = 4
        self.assertEqual(a.x, 4)
        with self.assertRaises(TypeError):
            class B(A):
                pass

    def test_multiple_inheritance(self):
        class A(metaclass=UnsubclassableType):
            pass
        class B:
            pass
        with self.assertRaises(TypeError):
            class C(A, B):
                pass
        with self.assertRaises(TypeError):
            class D(B, A):
                pass
        a = A()
        a.x = 4
        self.assertEqual(a.x, 4)

    def test_inheritance_with_metaclass(self):
        class A:
            pass
        class B(A, metaclass=UnsubclassableType):
            pass
        with self.assertRaises(TypeError):
            class C(B):
                pass
        with self.assertRaises(TypeError):
            class D(B, A):
                pass
        with self.assertRaises(TypeError):
            class E(A, B):
                pass
        a = A()
        a.x = 4
        self.assertEqual(a.x, 4)


class InstanceTrackerTests(unittest.TestCase):

    """Tests for InstanceTracker."""

    def test_bank_account(self):
        class BankAccount(metaclass=InstanceTracker):
            def __init__(self, balance=0):
                self.balance = balance
            def __repr__(self):
                return "BankAccount({})".format(self.balance)
        account1 = BankAccount(5)
        self.assertEqual(set(BankAccount), {account1})
        account2 = BankAccount(10)
        self.assertEqual(set(BankAccount), {account1, account2})

    def test_works_with_inheritance(self):
        class Animal:
            def __init__(self, name):
                self.name = name
            def __repr__(self):
                return "{}({})".format(repr(self.name))
        class Squirrel(Animal, metaclass=InstanceTracker):
            def __init__(self, name, nervousness=0.99):
                self.nervousness = nervousness
                super().__init__(name)
        squirrel1 = Squirrel(name='Mike')
        squirrel2 = Squirrel(name='Carol', nervousness=0.5)
        self.assertEqual(squirrel1.name, 'Mike')
        self.assertEqual(squirrel2.name, 'Carol')
        self.assertEqual(squirrel1.nervousness, 0.99)
        self.assertEqual(squirrel2.nervousness, 0.5)
        self.assertEqual(set(Squirrel), {squirrel1, squirrel2})

    def test_usage_on_two_classes_is_independent(self):
        class A(metaclass=InstanceTracker):
            pass
        class B(metaclass=InstanceTracker):
            def __init__(self, x):
                self.x = x
                super().__init__()
        a = A()
        self.assertEqual(set(A), {a})
        b = B(3)
        self.assertEqual(set(B), {b})
        self.assertEqual(set(A), {a})


class MappingTests(unittest.TestCase):

    """Tests for Mapping."""

    def test_for_mappings(self):
        self.assertTrue(isinstance({1: 'a', 2: 'b'}, Mapping))
        self.assertTrue(isinstance(defaultdict(list), Mapping))
        self.assertTrue(isinstance(Counter('hello'), Mapping))
        self.assertTrue(isinstance(OrderedDict([(1, 2), (3, 4)]), Mapping))

    def test_for_non_mappings(self):
        self.assertFalse(isinstance(1, Mapping))
        self.assertFalse(isinstance(4.0, Mapping))
        self.assertFalse(isinstance(True, Mapping))
        self.assertFalse(isinstance(Mapping, Mapping))
        self.assertFalse(isinstance('hello', Mapping))
        self.assertFalse(isinstance([1, 2, 3], Mapping))
        self.assertFalse(isinstance((1, 2, 3), Mapping))
        self.assertFalse(isinstance({1, 2, 3}, Mapping))
        self.assertFalse(isinstance(range(10), Mapping))

    def test_issubclass(self):
        self.assertFalse(issubclass(list, Mapping))
        self.assertFalse(issubclass(set, Mapping))
        self.assertTrue(issubclass(dict, Mapping))
        self.assertFalse(issubclass(tuple, Mapping))
        self.assertFalse(issubclass(str, Mapping))
        self.assertFalse(issubclass(int, Mapping))
        self.assertFalse(issubclass(float, Mapping))
        self.assertTrue(issubclass(Counter, Mapping))
        self.assertTrue(issubclass(OrderedDict, Mapping))
        self.assertTrue(issubclass(defaultdict, Mapping))
        self.assertTrue(issubclass(UserDict, Mapping))

    def test_custom_mapping(self):
        class MyMapping:
            def __init__(self, mapping):
                self.mapping = dict(mapping)
            def __getitem__(self, index):
                return self.mapping[index]
            def __iter__(self):
                return iter(self.mapping)
            def __len__(self):
                return len(self.mapping)
            def keys(self):
                return self.mapping.keys()
            def values(self):
                return self.mapping.values()
            def items(self):
                return self.mapping.items()
        self.assertEqual(dict(MyMapping({1: 2, 3: 4})), {1: 2, 3: 4})
        self.assertTrue(isinstance(MyMapping({1: 2, 3: 4}), Mapping))
        self.assertTrue(issubclass(MyMapping, Mapping))


class HashableTests(unittest.TestCase):

    """Tests for Hashable."""

    def test_mutable_things(self):
        self.assertFalse(isinstance([1, 2, 3], Hashable))
        self.assertFalse(isinstance({1, 2, 3}, Hashable))
        self.assertFalse(isinstance({1: 'a', 2: 'b'}, Hashable))

    def test_tuples_of_mutable_things(self):
        self.assertFalse(isinstance(('apple', [], 'Lemon'), Hashable))
        self.assertFalse(isinstance(({1, 2, 3},), Hashable))
        self.assertFalse(isinstance(([], []), Hashable))
        self.assertFalse(isinstance((('b', {}), ('a', 2)), Hashable))

    def test_tuples_of_immutable_things(self):
        self.assertTrue(isinstance(('apple', 'lime', 'Lemon'), Hashable))
        self.assertTrue(isinstance((1, 2, 3), Hashable))
        self.assertTrue(isinstance(((), ()), Hashable))
        self.assertTrue(isinstance((('b', 1), ('a', 2)), Hashable))
        self.assertTrue(isinstance((frozenset({1, 2, 3}),), Hashable))

    def test_issubclass(self):
        self.assertFalse(issubclass(list, Hashable))
        self.assertFalse(issubclass(set, Hashable))
        self.assertFalse(issubclass(dict, Hashable))
        self.assertTrue(issubclass(tuple, Hashable))
        self.assertTrue(issubclass(int, Hashable))
        self.assertTrue(issubclass(float, Hashable))
        self.assertTrue(issubclass(str, Hashable))
        self.assertTrue(issubclass(Hashable, Hashable))

    def test_custom_classes(self):
        class HashableByDefault:
            pass

        class Unhashable:
            def __eq__(self, other):
                return self is other

        class PurposelyHashable:
            def __eq__(self, other):
                return self is other
            def __hash__(self):
                return id(self)

        class SometimesHashable:
            def __init__(self, hashable=True):
                self.hashable = hashable
            def __eq__(self, other):
                return self.hashable == other.hashable
            def __hash__(self):
                if not self.hashable:
                    raise TypeError("Unhashable object")
                return id(self)

        self.assertTrue(issubclass(HashableByDefault, Hashable))
        self.assertFalse(issubclass(Unhashable, Hashable))
        self.assertTrue(issubclass(PurposelyHashable, Hashable))
        self.assertTrue(issubclass(SometimesHashable, Hashable))

        self.assertTrue(isinstance(HashableByDefault(), Hashable))
        self.assertFalse(isinstance(Unhashable(), Hashable))
        self.assertTrue(isinstance(PurposelyHashable(), Hashable))
        self.assertTrue(isinstance(SometimesHashable(True), Hashable))
        self.assertFalse(isinstance(SometimesHashable(False), Hashable))


class NoMethodCollisionsTests(unittest.TestCase):

    """Tests for NoMethodCollisions."""

    def test_all_unique_class_attributes(self):
        class Point(NoMethodCollisions):
            def __init__(self, x, y, z):
                self.x, self.y, self.z = x, y, z
            def __repr__(self):
                return "{class_name}({x}, {y}, {z})".format(
                    class_name=type(self).__name__,
                    x=self.x,
                    y=self.y,
                    z=self.z,
                )
            def __eq__(self, other):
                return (self.x, self.y, self.z) == (other.x, other.y, other.z)
        p = Point(1, 2, 3)
        q = Point(1, 2, 3)
        self.assertEqual(p, q)
        self.assertEqual(repr(p), "Point(1, 2, 3)")

    def test_overlapping_class_attributes(self):
        with self.assertRaises(Exception):
            class SillyTests(NoMethodCollisions, unittest.TestCase):
                def test_add(self):
                    self.assertEqual(2 + 2, 4)
                def test_subtract(self):
                    self.assertEqual(4 - 2, 2)
                def test_add(self):
                    self.assertEqual(1 + 1, 2)

    def test_non_functions(self):
        from math import sqrt
        class Vector(NoMethodCollisions):
            def __init__(self, x, y, z):
                self.x, self.y, self.z = x, y, z
            @staticmethod
            def root_sum_squared(numbers):
                return sqrt(sum(n**2 for n in numbers))
        self.assertEqual(Vector.root_sum_squared([3, 4]), 5)
        with self.assertRaises(Exception):
            class Vector2(NoMethodCollisions):
                @staticmethod
                def root_sum_squared(numbers):
                    return sqrt(n**2 for n in numbers)
                def __init__(self, x, y, z):
                    self.x, self.y, self.z = x, y, z
                @classmethod
                def root_sum_squared(cls, numbers):
                    return sqrt(n**2 for n in numbers)

    def test_TypeError_is_raised(self):
        with self.assertRaises(TypeError):
            class SillyTests(NoMethodCollisions):
                def test_add(self):
                    self.assertEqual(2 + 2, 4)
                def test_subtract(self):
                    self.assertEqual(4 - 2, 2)
                def test_add(self):
                    self.assertEqual(1 + 1, 2)

    def test_allow_property_redefinition(self):
        class Circle(NoMethodCollisions):
            def __init__(self, radius=1):
                self.radius = radius
            @property
            def diameter(self):
                return self.radius * 2
            @diameter.setter
            def diameter(self, diameter):
                self.radius = diameter / 2
        c1 = Circle(5)
        c2 = Circle(8)
        self.assertEqual(c1.diameter, 10)
        self.assertEqual(c2.diameter, 16)
        c2.diameter = 10
        self.assertEqual(c2.diameter, 10)
        self.assertEqual(c2.radius, 5)


class SnakeTestCaseTests(unittest.TestCase):

    """Tests for SnakeTestCase."""

    def run_test(self, test_class):
        loader = unittest.defaultTestLoader.loadTestsFromTestCase(test_class)
        suite = unittest.TestSuite(loader)
        result = suite.run(unittest.TestResult())
        self.assertGreaterEqual(result.testsRun, 1)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.failures, [])
        self.assertTrue(result.wasSuccessful())
        return result

    def test_true_false_and_equal_assertions(self):
        class SnakeTest(SnakeTestCase):
            def test_true_and_false(self):
                self.assert_true(True)
                self.assert_false(False)
            def test_equality(self):
                self.assert_equal(4, 4)
                self.assert_not_equal(4, 5)
                self.assert_equal((1, 2), (1, 2))
                self.assert_not_equal((1, 2), (1, 3))
        self.run_test(SnakeTest)

    def test_more_assertions(self):
        class SnakeTest(SnakeTestCase):
            def test_assert_raises(self):
                with self.assert_raises(AssertionError):
                    self.assert_false(True)
                with self.assert_raises(AssertionError):
                    self.assert_true(False)
            def test_in_and_is_assertions(self):
                x = y = [1, 2]
                z = [1, 2]
                self.assert_is(x, y)
                self.assert_is_not(x, z)
                self.assert_in(2, x)
                self.assert_not_in(3, x)
            def test_assert_almost_equal(self):
                x = 0.2 + 0.01
                y = 0.21
                self.assert_almost_equal(x, y)
                self.assert_not_almost_equal(x, y+0.001)
        self.run_test(SnakeTest)

    def test_id_and_short_description(self):
        class SnakeTest(SnakeTestCase):
            def test_id_and_skip_test(self):
                self.id()
                self.skip_test("For fun")
            def test_short_description(self):
                """Hello!"""
                self.assert_equal(self.short_description(), "Hello!")
        result = self.run_test(SnakeTest)
        self.assertEqual(len(result.skipped), 1)

    def test_set_up(self):
        class SnakeTest(SnakeTestCase):
            def set_up(self):
                self.set_up_run = True
            def test_setup_up_run(self):
                self.assertTrue(self.set_up_run)
        result = self.run_test(SnakeTest)

    def test_setup_up_and_tear_down(self):
        class SnakeTest(SnakeTestCase):
            @classmethod
            def set_up_class(cls):
                actions.append("class up")
            @classmethod
            def tear_down_class(cls):
                actions.append("class down")
            def set_up(self):
                actions.append("up")
            def tear_down(self):
                actions.append("down")
            def test_1(self):
                self.id()
            def test_2(self):
                """Hello!"""
                self.assert_equal(self.short_description(), "Hello!")
            def test_3(self):
                self.assert_true(not False)
        actions = []
        result = self.run_test(SnakeTest)
        self.assertEqual(
            actions,
            ["class up", *(("up", "down")*3), "class down"],
        )


if __name__ == "__main__":
    from helpers import error_message
    error_message()
