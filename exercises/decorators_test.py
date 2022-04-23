"""Tests for decorator exercises"""
import cmath
import math
from numbers import Number
from decimal import Decimal

import unittest

from decorators import count_calls, positional_only, allow_snake, overload, record_calls


class CountCallsTests(unittest.TestCase):

    """Test for count_calls."""

    def test_accepts_a_function(self):
        # Function value is returned
        def one(): return 1
        decorated = count_calls(one)
        self.assertEqual(decorated(), 1)
        self.assertEqual(decorated.calls, 1)

    def test_calls_a_function(self):
        # Function is called each time
        recordings = []
        def my_func():
            recordings.append('call')
            return recordings
        decorated = count_calls(my_func)
        self.assertEqual(recordings, [])
        self.assertEqual(decorated.calls, 0)
        self.assertEqual(decorated(), ['call'])
        self.assertEqual(decorated.calls, 1)
        self.assertEqual(decorated(), ['call', 'call'])
        self.assertEqual(decorated.calls, 2)

    def test_accepts_arguments(self):
        # Function accepts positional arguments
        @count_calls
        def add(x, y):
            return x + y
        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add(1, 3), 4)

        # Function accepts keyword arguments
        recordings = []
        @count_calls
        def my_func(*args, **kwargs):
            recordings.append((args, kwargs))
            return recordings
        self.assertEqual(my_func(), [((), {})])
        self.assertEqual(my_func(1, 2, a=3), [((), {}), ((1, 2), {'a': 3})])

        # Exceptions are still counted as calls
        @count_calls
        def my_func():
            raise AssertionError("Function called too soon")
        self.assertEqual(my_func.calls, 0)
        with self.assertRaises(AssertionError):
            my_func()
        self.assertEqual(my_func.calls, 1)
        self.assertEqual(my_func.calls, 1)
        with self.assertRaises(AssertionError):
            my_func()
        self.assertEqual(my_func.calls, 2)

    def test_docstring_and_name_preserved(self):
        import pydoc
        decorated = count_calls(example)
        self.assertIn('function example', str(decorated))
        documentation = pydoc.render_doc(decorated)
        self.assertIn('function example', documentation)
        self.assertIn('Example function.', documentation)
        self.assertIn('(a, b=True)', documentation)


def example(a, b=True):
    """Example function."""
    print('hello world')


class PositionalOnlyTests(unittest.TestCase):

    """Tests for positional_only."""

    def test_restrict_all_arguments_to_positional(self):
        @positional_only
        def divide(x, y): return x / y
        self.assertEqual(divide(21, 3), 7)
        self.assertEqual(divide(5, 2), 2.5)
        with self.assertRaises(TypeError):
            divide(x=5, y=2)
        with self.assertRaises(TypeError):
            divide(5, y=2)
        with self.assertRaises(TypeError):
            divide(5, x=2)
        with self.assertRaises(TypeError):
            divide(1, 2, 3)
        with self.assertRaises(TypeError):
            divide(1)

    def test_no_keyword_arguments_allowed(self):
        @positional_only
        def my_func(a, b=2, **kwargs): return a
        self.assertEqual(my_func(3), 3)
        with self.assertRaises(TypeError):
            my_func(3, b=3)
        with self.assertRaises(TypeError):
            my_func(3, a=3)

    def test_any_number_of_positional_arguments(self):
        @positional_only
        def add(a, b, *args): return a + b + sum(args)
        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add(1, 2, 3, 4), 10)
        self.assertEqual(add(1, 2, 3), 6)
        @positional_only
        def product(*numbers):
            total = 1
            for n in numbers:
                total *= n
            return total
        self.assertEqual(product(1, 2, 3, 4), 24)
        self.assertEqual(product(1, 2), 2)
        self.assertEqual(product(10), 10)
        self.assertEqual(product(), 1)
        with self.assertRaises(TypeError):
            add(1, 2, b=3)
        with self.assertRaises(TypeError):
            product(numbers=3)

    def test_with_positional_argument_count(self):
        @positional_only(3)
        def add(a, b, c, d): return a + b + c + d
        self.assertEqual(add(1, 2, 3, 4), 10)
        self.assertEqual(add(1, 2, 3, d=4), 10)
        with self.assertRaises(TypeError):
            add(1, 2, c=3, d=4)
        with self.assertRaises(TypeError):
            add(1, b=2, c=3, d=4)
        with self.assertRaises(TypeError):
            add(a=1, b=2, c=3, d=4)
        @positional_only(2)
        def divide(x=1, y=1): return x / y
        self.assertEqual(divide(3, 2), 1.5)
        with self.assertRaises(TypeError):
            divide(x=3, y=2)
        with self.assertRaises(TypeError):
            divide(3, y=2)


class AllowSnakeTests(unittest.TestCase):

    """Tests for allow_snake."""

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
        @allow_snake
        class SnakeTest(unittest.TestCase):
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
        @allow_snake
        class SnakeTest(unittest.TestCase):
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
        @allow_snake
        class SnakeTest(unittest.TestCase):
            def test_id_and_skip_test(self):
                self.id()
                self.skip_test("For fun")
            def test_short_description(self):
                """Hello!"""
                self.assert_equal(self.short_description(), "Hello!")
        result = self.run_test(SnakeTest)
        self.assertEqual(len(result.skipped), 1)

    def test_set_up(self):
        @allow_snake
        class SnakeTest(unittest.TestCase):
            def set_up(self):
                self.set_up_run = True
            def test_setup_up_run(self):
                self.assertTrue(self.set_up_run)
        result = self.run_test(SnakeTest)

    def test_setup_up_and_tear_down(self):
        @allow_snake
        class SnakeTest(unittest.TestCase):
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


class OverloadTests(unittest.TestCase):

    """Tests for overload."""

    def test_two_arguments_with_str_and_int_combos(self):
        @overload(int, int, id='add')
        def add(x, y):
            return x + y
        @overload(str, str, id='add')
        def add(x, y):
            return x + y
        @overload(str, int, id='add')
        def add(x, y):
            return x + str(y)
        @overload(int, str, id='add')
        def add(x, y):
            return str(x) + y
        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add('3', 4), '34')
        self.assertEqual(add(5, '6'), '56')
        self.assertEqual(add('7', '8'), '78')

    def test_different_numbers_of_arguments(self):
        @overload(id='do_stuff')
        def do_stuff():
            return (0,)
        @overload(str, id='do_stuff')
        def one(x):
            return (1, x)
        @overload(str, str, id='do_stuff')
        def two(x, y):
            return (2, x, y)
        @overload(str, str, str, id='do_stuff')
        def three(x, y, z):
            return (3, x, y, z)
        self.assertEqual(do_stuff('a'), (1, 'a'))
        self.assertEqual(do_stuff(), (0,))
        self.assertEqual(do_stuff('b', 'c'), (2, 'b', 'c'))
        self.assertEqual(do_stuff('d', 'e', 'f'), (3, 'd', 'e', 'f'))
        with self.assertRaises(TypeError):
            do_stuff('g', 'h', 'i', 'j')

    def test_base_types_and_abstract_types(self):
        @overload(object, id='add2')
        def add(x):
            return x
        @overload(object, object, id='add2')
        def add(x, y):
            return x + y
        self.assertEqual(add([4]), [4])
        self.assertEqual(add('5', '6'), '56')

        @overload(complex, id='sqrt')
        def sqrt(x):
            return cmath.sqrt(x)
        @overload((int, float), id='sqrt')
        def sqrt(x):
            if x >= 0:
                return math.sqrt(x)
            else:
                return sqrt(x+0j)
        @overload(Decimal, id='sqrt')
        def sqrt(x):
            return x.sqrt()
        self.assertEqual(sqrt(6.25), 2.5)
        self.assertEqual(sqrt(25), 5.0)
        self.assertEqual(sqrt(16+30j), 5+3j)
        self.assertEqual(sqrt(-1), 1j)
        self.assertEqual(sqrt(Decimal(24)), Decimal('4.898979485566356196394568149'))

        @overload(Number, id='costs')
        def costs(x):
            return "It costs ${:.2f}".format(x)
        @overload(str, id='costs')
        def costs(x):
            return "It costs {}".format(x)
        self.assertEqual(costs(5), "It costs $5.00")
        self.assertEqual(costs('nothing'), "It costs nothing")

    def test_original_function_name_and_docstring_maintained(self):
        @overload(id='greet')
        def greet():
            """Say hello!"""
            return "Hi there"
        @overload(str, id='greet')
        def greet(string):
            """Greet a specific user."""
            return "Why hello {}!".format(string)
        self.assertEqual(greet(), "Hi there")
        self.assertEqual(greet("Trey"), "Why hello Trey!")
        self.assertEqual(greet.__doc__, "Say hello!")
        self.assertEqual(greet.__name__, "greet")


class RecordCallsTests(unittest.TestCase):

    """Tests for record_calls."""

    def test_call_count_starts_at_zero(self):
        decorated = record_calls(lambda: None)
        self.assertEqual(decorated.call_count, 0)

    def test_not_called_on_decoration_time(self):
        def my_func():
            raise AssertionError("Function called too soon")
        record_calls(my_func)

    def test_function_still_callable(self):
        recordings = []
        def my_func():
            recordings.append('call')
        decorated = record_calls(my_func)
        self.assertEqual(recordings, [])
        decorated()
        self.assertEqual(recordings, ['call'])
        decorated()
        self.assertEqual(recordings, ['call', 'call'])

    def test_return_value(self):
        def one(): return 1
        one = record_calls(one)
        self.assertEqual(one(), 1)

    def test_takes_arguments(self):
        def add(x, y): return x + y
        add = record_calls(add)
        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add(1, 3), 4)

    def test_takes_keyword_arguments(self):
        recordings = []
        @record_calls
        def my_func(*args, **kwargs):
            recordings.append((args, kwargs))
            return recordings
        self.assertEqual(my_func(), [((), {})])
        self.assertEqual(my_func(1, 2, a=3), [((), {}), ((1, 2), {'a': 3})])

    def test_call_count_increments(self):
        decorated = record_calls(lambda: None)
        self.assertEqual(decorated.call_count, 0)
        decorated()
        self.assertEqual(decorated.call_count, 1)
        decorated()
        self.assertEqual(decorated.call_count, 2)

    def test_different_functions(self):
        my_func1 = record_calls(lambda: None)
        my_func2 = record_calls(lambda: None)
        my_func1()
        self.assertEqual(my_func1.call_count, 1)
        self.assertEqual(my_func2.call_count, 0)
        my_func2()
        self.assertEqual(my_func1.call_count, 1)
        self.assertEqual(my_func2.call_count, 1)

    def test_docstring_and_name_preserved(self):
        import pydoc
        decorated = record_calls(example)
        self.assertIn('function example', str(decorated))
        documentation = pydoc.render_doc(decorated)
        self.assertIn('function example', documentation)
        self.assertIn('Example function.', documentation)
        self.assertIn('(a, b=True)', documentation)

    def test_record_arguments(self):
        @record_calls
        def my_func(*args, **kwargs): return args, kwargs
        self.assertEqual(my_func.calls, [])
        my_func()
        self.assertEqual(len(my_func.calls), 1)
        self.assertEqual(my_func.calls[0].args, ())
        self.assertEqual(my_func.calls[0].kwargs, {})
        my_func(1, 2, a=3)
        self.assertEqual(len(my_func.calls), 2)
        self.assertEqual(my_func.calls[1].args, (1, 2))
        self.assertEqual(my_func.calls[1].kwargs, {'a': 3})

    def test_record_return_values(self):
        from decorators import NO_RETURN
        @record_calls
        def my_func(*args, **kwargs): return sum(args), kwargs
        my_func()
        self.assertEqual(my_func.calls[0].return_value, (0, {}))
        my_func(1, 2, a=3)
        self.assertEqual(my_func.calls[1].return_value, (3, {'a': 3}))
        self.assertIs(my_func.calls[1].exception, None)
        with self.assertRaises(TypeError) as context:
            my_func(1, 'hi', a=3)
        self.assertIs(my_func.calls[2].return_value, NO_RETURN)
        self.assertEqual(my_func.calls[2].exception, context.exception)


def example(a, b=True):
    """Example function."""
    print('hello world')


if __name__ == "__main__":
    unittest.main(verbosity=2)
