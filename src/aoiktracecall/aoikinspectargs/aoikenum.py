# coding: utf-8
"""
This module contains an enumeration class decorator.
"""
from __future__ import absolute_import


# Version
__version__ = '0.1.0'


# Public attribute names
__all__ = (
    'enum',
)


def metaclass(meta):
    """
    Parameterized class decorator applying metaclass to decorated class.

    The parameterized class decorator takes a metaclass and creates a class \
        decorator. The created class decorator takes a class and calls the
        metaclass to create a new class based on given class.

    :param meta: Metaclass.

    :return: Class decorator.
    """
    # Create class decorator
    def class_decorator(cls):
        """
        Class decorator.

        :param cls: Original class.

        :return: New class created by the metaclass.
        """
        # Get original class' attributes dict copy
        attrs_dict = cls.__dict__.copy()

        # Remove attribute `__dict__` from the attributes dict copy
        attrs_dict.pop('__dict__', None)

        # Remove attribute `__weakref__` from the attributes dict copy
        attrs_dict.pop('__weakref__', None)

        # Call metaclass to create new class based on given class
        return meta(cls.__name__, cls.__bases__, attrs_dict)

    # Return class decorator
    return class_decorator


class EnumMeta(type):
    """
    Metaclass that takes a class with enumeration-value attributes and \
        returns a new enumeration class with enumeration-instance attributes.

    The metaclass stores enumeration value-to-name dict in the new \
        enumeration class' `_map_value_to_name` attribute.

    The metaclass sets the new enumeration class' `__init__` function to take \
        an enumeration value. Only enumeration values defined in the original \
        class are allowed. The enumeration value's corresponding enumeration \
        name is found from the `_map_value_to_name` dict. The enumeration \
        name is stored in the enumeration instance's `name` attribute.

    The metaclass sets the new enumeration class' `__repr__` function to \
        return the enumeration name.
    """

    def __init__(cls, name, bases, attrs):
        """
        Metaclass' instance constructor.

        :param cls: Class object to be handled by the metaclass.

        :param name: Class name.

        :param bases: Class object's base classes list.

        :param attrs: Class object's attributes dict.
        """
        # Call super constructor
        super(EnumMeta, cls).__init__(name, bases, attrs)

        # Create dict that maps enumeration value to enumeration name
        cls._map_value_to_name = {}

        # Get given class' original `__init__` function
        orig_init = cls.__dict__.get('__init__', None)

        # Create given class' new `__init__` function
        def new_init(self, value):
            """
            Enumeration instance constructor.

            :param value: Enumeration value.

            :return: None.
            """
            # Enumeration name
            self.name = None

            # If have original constructor
            if orig_init is not None:
                # Call original constructor
                orig_init(self, value)

            # If not have original constructor
            else:
                # Call given class' super constructor.
                #
                # This assumes the super constructor takes no arguments,
                # e.g. super classes are `int`, `float`, or `str`.
                #
                # If the super constructor takes arguments, the original class
                # should define a constructor to handle the case.
                #
                super(cls, self).__init__()

            # If enumeration name is not initialized by original constructor
            if self.name is None:
                # Find enumeration name
                name = cls._map_value_to_name.get(value, None)

                # If enumeration name is not found.
                # It means the enumeration value is not valid.
                if name is None:
                    # Valid values' text part list
                    text_part_s = []

                    # For each valid enumeration value and name,
                    # sorted according to enumeration value.
                    for enum_value, enum_name in sorted(
                        cls._map_value_to_name.items(),
                        key=lambda x: x[0]
                    ):
                        # Get text part
                        text_part = '{}.{} == {}'.format(
                            cls.__name__,
                            enum_name,
                            repr(enum_value),
                        )

                        # Add text part to list
                        text_part_s.append(text_part)

                    # Get valid values' text
                    valid_values_text = '\n'.join(text_part_s)

                    # Get error message
                    error_msg = 'Invalid value: {}\nValid values:\n{}'.format(
                        repr(value), valid_values_text
                    )

                    # Raise error
                    raise ValueError(error_msg)

                # If enumeration name is found.
                # It means the enumeration value is valid.
                else:
                    # Set enumeration name
                    self.name = name

        # Set function name
        new_init.__name__ = '__init__'

        # Set given class' new `__init__` function
        cls.__init__ = new_init

        # Create given class' new `__repr__` function
        def new_repr(self):
            """
            Get enumeration name.

            :return: Enumeration name.
            """
            # Return enumeration name
            return self.name

        # Set function name
        new_repr.__name__ = '__repr__'

        # Set given class' new `__repr__` function
        cls.__repr__ = new_repr

        # For given class' each attribute
        for key, value in attrs.items():
            # If the attribute name not starts with underscore.
            # It is considered as enumeration-value attribute.
            if not key.startswith('_'):
                # Add to enumeration value-to-name dict
                cls._map_value_to_name[value] = key

                # Create enumeration instance
                instance = cls(value)

                # Replace enumeration value with enumeration instance
                setattr(cls, key, instance)


# Class decorator that takes a class with enumeration-value attributes and
# returns a new enumeration class with enumeration-instance attributes.
enum = metaclass(EnumMeta)
