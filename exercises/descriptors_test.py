"""Tests for descriptor exercises"""
import gc
import unittest


from descriptors import (
    alias,
    class_property,
    class_only_method,
    computed_property,
)


class AliasTests(unittest.TestCase):

    """Tests for alias."""

    def test_mirrors_attribute_on_class(self):
        class Thing:
            one = 4
            two = alias('one')
        thing = Thing()
        self.assertEqual(thing.one, 4)
        self.assertEqual(thing.two, 4)

    def test_mirrors_attribute_from_initializer(self):
        class Thing:
            two = alias('one')
            def __init__(self):
                self.one = 4
        thing = Thing()
        self.assertEqual(thing.one, 4)
        self.assertEqual(thing.two, 4)

    def test_attribute_mirroring_maintained(self):
        class Thing:
            one = 4
            two = alias('one')
        thing = Thing()
        self.assertEqual(thing.one, 4)
        self.assertEqual(thing.two, 4)
        thing.one = 6
        self.assertEqual(thing.one, 6)
        self.assertEqual(thing.two, 6)
        self.assertNotEqual(thing.two, 4)

    def test_attribute_identity(self):
        class Thing:
            two = alias('one')
            def __init__(self, one):
                self.one = one
        my_list = []
        thing = Thing(my_list)
        self.assertIs(thing.one, thing.two, my_list)

    # To test the Bonus part of this exercise, comment out the following line
    @unittest.skip("Writable alias")
    def test_writability(self):
        # Unwritable by default
        class Thing:
            one = 4
            two = alias('one')
        thing = Thing()
        with self.assertRaises(AttributeError):
            thing.two = 6
        self.assertEqual(thing.one, 4)
        self.assertEqual(thing.two, 4)

        # Writable when write=True specified
        class Thing2:
            blue = alias('red', write=True)
            red = []
        thing2 = Thing2()
        self.assertIs(thing2.blue, thing2.red)
        thing2.blue = [4, 5]
        self.assertEqual(thing2.blue, [4, 5])
        self.assertIs(thing2.blue, thing2.red)

        # write=False raises an AttributeError (mutation works though)
        class Thing3:
            blue = alias('red', write=False)
            red = []
        thing3 = Thing3()
        with self.assertRaises(AttributeError):
            thing3.blue = [4, 5]
        thing3.blue.append(6)
        self.assertEqual(thing3.blue, [6])
        self.assertIs(thing3.blue, thing3.red)


class ClassPropertyTests(unittest.TestCase):

    """Tests for class_property."""

    def test_accessing_attribute(self):
        class BankAccount:
            accounts = []
            def __init__(self, balance=0):
                self.balance = balance
                self.accounts.append(self)
            @class_property
            def total_balance(cls):
                return sum(a.balance for a in cls.accounts)
        account1 = BankAccount(5)
        account2 = BankAccount(15)
        self.assertEqual(BankAccount.total_balance, 20)
        self.assertEqual(account1.total_balance, 20)
        self.assertEqual(account1.total_balance, account2.total_balance)

    def test_first_argument_is_class_itself(self):
        class Thing:
            @class_property
            def stuff(cls):
                self.assertIs(cls, Thing)
                return cls
        self.assertIs(Thing.stuff, Thing)
        self.assertIs(Thing().stuff, Thing)

    def test_same_name_as_instance_attribute(self):
        class BankAccount:
            accounts = []
            def __init__(self, balance=0):
                self.balance = balance
                self.accounts.append(self)
            @class_property
            def total_balance(cls):
                return sum(a.balance for a in cls.accounts)
        account1 = BankAccount(5)
        account2 = BankAccount(15)
        account1.total_balance = 30
        self.assertEqual(BankAccount.total_balance, 20)
        self.assertEqual(account1.total_balance, 30)
        self.assertEqual(account2.total_balance, 20)
        del account1.total_balance
        self.assertEqual(account1.total_balance, 20)
        with self.assertRaises(AttributeError):
            del account1.total_balance

    def test_shadowing_attribute_name_on_instances(self):

        # Same-named attribute on instance
        class BankAccount:
            accounts = []
            def __init__(self, balance=0):
                self.balance = balance
                self.accounts.append(self)
            @class_property
            def balance(cls):
                return sum(a.balance for a in cls.accounts)
        account1 = BankAccount(5)
        account2 = BankAccount(15)
        self.assertEqual(account1.balance, 5)
        self.assertEqual(account2.balance, 15)
        self.assertEqual(BankAccount.balance, 20)

        # Setting attribute on instance
        class BankAccount:
            accounts = []
            def __init__(self, balance=0):
                self.balance = balance
                self.accounts.append(self)
            @class_property
            def total_balance(cls):
                return sum(a.balance for a in cls.accounts)
        account1 = BankAccount(5)
        account2 = BankAccount(15)
        account1.total_balance = 10
        account2.total_balance = 15
        self.assertEqual(BankAccount.total_balance, 20)
        self.assertEqual(account1.total_balance, 10)
        self.assertEqual(account2.total_balance, 15)


class ClassOnlyMethodTests(unittest.TestCase):

    """Tests for class_only_method."""

    def test_calling_method_on_class(self):
        class BankAccount:
            accounts = []
            def __init__(self, balance=0):
                self.balance = balance
                self.accounts.append(self)
            @class_only_method
            def total(cls):
                return sum(a.balance for a in cls.accounts)
        BankAccount(5)
        BankAccount(15)
        self.assertEqual(BankAccount.total(), 20)

    def test_calling_method_on_instance(self):
        class BankAccount:
            accounts = []
            def __init__(self, balance=0):
                self.balance = balance
                self.accounts.append(self)
            @class_only_method
            def total(cls):
                return sum(a.balance for a in cls.accounts)
        account1 = BankAccount(5)
        account2 = BankAccount(15)
        with self.assertRaises(AttributeError):
            account1.total()
            account2.total()

    def test_first_argument_is_class_itself(self):
        class Thing:
            @class_only_method
            def stuff(cls):
                self.assertIs(cls, Thing)
                return cls
        self.assertIs(Thing.stuff(), Thing)

    def test_passing_arguments(self):
        class Thing:
            @class_only_method
            def stuff(cls, a, b):
                self.assertIs(cls, Thing)
                return (a, b)
        self.assertEqual(Thing.stuff(3, b=4), (3, 4))

    def test_method_name(self):
        class Thing:
            @class_only_method
            def stuff(cls, a, b):
                self.assertIs(cls, Thing)
                return (a, b)
        self.assertIn('stuff', repr(Thing.stuff))

    def test_documentation(self):
        class Thing:
            @class_only_method
            def stuff(cls, a, b):
                """Do things."""
                self.assertIs(cls, Thing)
                return (a, b)
        self.assertIsNotNone(Thing.stuff.__doc__)
        self.assertIn('Do things', Thing.stuff.__doc__)

    def test_same_name_as_instance_attribute(self):
        class BankAccount:
            accounts = []
            def __init__(self, balance=0):
                self.balance = balance
                self.accounts.append(self)
            @class_only_method
            def total(cls):
                return sum(a.balance for a in cls.accounts)
        account1 = BankAccount(5)
        account2 = BankAccount(15)
        account1.total = 30
        self.assertEqual(BankAccount.total(), 20)
        self.assertEqual(account1.total, 30)
        with self.assertRaises(AttributeError):
            del account2.total


class ComputedPropertyTests(unittest.TestCase):

    """Tests for computed_property."""

    def test_accessing_attribute(self):
        from collections import namedtuple
        class Circle(namedtuple('BaseCircle', ['radius'])):
            @computed_property('radius')
            def diameter(self):
                return self.radius * 2
        c = Circle(radius=5)
        self.assertEqual(c.diameter, 10)

    def test_does_not_call_getter_function_again(self):
        class Thing:
            called = False
            @computed_property('y')
            def x(self):
                from time import sleep
                sleep(0.01)
                if self.called:
                    raise AssertionError("getter function called again")
                self.called = True
                return self.y
        thing = Thing()
        thing.y = 4
        for i in range(1000):
            self.assertEqual(thing.x, 4)
            self.assertTrue(thing.called)

    def test_attribute_cached_until_attribute_changes(self):
        class Thing:
            @computed_property('z')
            def x(self):
                return self.y * self.z
        thing = Thing()
        thing.y, thing.z = 2, 3
        self.assertEqual(thing.x, 6)
        thing.y = 5
        self.assertEqual(thing.x, 6)
        thing.z = 7
        self.assertEqual(thing.x, 35)
        thing.y = 13
        self.assertEqual(thing.x, 35)

    def test_none_attribute(self):
        class Thing:
            @computed_property('y')
            def x(self):
                return self.y, self.z
        thing = Thing()
        thing.y = None
        thing.z = None
        self.assertEqual(thing.x, (None, None))
        thing.z = 5
        self.assertEqual(thing.x, (None, None))
        thing.y = 3
        self.assertEqual(thing.x, (3, 5))
        thing.y = None
        self.assertEqual(thing.x, (None, 5))

    def test_error_when_accessing_attribute(self):
        class Circle:
            @computed_property('radius')
            def diameter(self):
                return self.radius * 2
        c = Circle()
        with self.assertRaises(AttributeError):
            c.diameter
        c.radius = 2
        self.assertEqual(c.diameter, 4)
        del c.radius
        with self.assertRaises(AttributeError):
            c.diameter
        c.radius = 3
        self.assertEqual(c.diameter, 6)

    def test_cannot_set_attribute(self):
        class Circle:
            @computed_property('radius')
            def diameter(self):
                return self.radius * 2
        c = Circle()
        with self.assertRaises(AttributeError):
            c.diameter = 2
        c.radius = 1
        self.assertEqual(c.diameter, 2)
        with self.assertRaises(AttributeError):
            c.diameter = 3
        self.assertEqual(c.diameter, 2)

    def test_two_instances_of_same_class(self):
        class Thing:
            @computed_property('z')
            def x(self):
                return self.y * self.z
        thing1 = Thing()
        thing2 = Thing()
        thing1.y, thing1.z = 2, 3
        thing2.y, thing2.z = 4, 5
        self.assertEqual(thing1.x, 6)
        self.assertEqual(thing2.x, 20)
        thing1.y = 7
        self.assertEqual(thing1.x, 6)
        self.assertEqual(thing2.x, 20)
        thing1.z = 5
        self.assertEqual(thing1.x, 35)
        self.assertEqual(thing2.x, 20)
        thing2.z = 3
        self.assertEqual(thing1.x, 35)
        self.assertEqual(thing2.x, 12)

    def test_objects_are_garbage_collected_properly(self):
        def count_instances(cls):
            return sum(
                isinstance(obj, cls)
                for obj in gc.get_objects()
            )
        class Thing:
            @computed_property('z')
            def x(self):
                return self.y * self.z
        self.assertEqual(count_instances(Thing), 0)
        thing = Thing()
        thing.y, thing.z = 2, 3
        self.assertEqual(thing.x, 6)
        self.assertEqual(count_instances(Thing), 1)
        del thing
        self.assertEqual(count_instances(Thing), 0)

    def test_accessing_attribute_on_class(self):
        class Thing:
            @computed_property('y')
            def x(self):
                return self.y
        thing = Thing()
        self.assertEqual(type(Thing.x), computed_property)
        thing.y = 4
        self.assertEqual(Thing.x.__get__(thing, Thing), 4)
        thing.y = 5
        self.assertEqual(Thing.x.__get__(thing, Thing), 5)


if __name__ == "__main__":
    from helpers import error_message
    error_message()
