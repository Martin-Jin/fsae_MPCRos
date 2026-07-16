# generated from rosidl_generator_py/resource/_idl.py.em
# with input from fsae_interfaces:msg/CAN.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

# Member 'data'
import numpy  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_CAN(type):
    """Metaclass of message 'CAN'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('fsae_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'fsae_interfaces.msg.CAN')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__can
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__can
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__can
            cls._TYPE_SUPPORT = module.type_support_msg__msg__can
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__can

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'IS_RTR__DEFAULT': False,
            'DATA__DEFAULT': numpy.array((0, 0, 0, 0, 0, 0, 0, 0, ), dtype=numpy.uint8),
        }

    @property
    def IS_RTR__DEFAULT(cls):
        """Return default value for message field 'is_rtr'."""
        return False

    @property
    def DATA__DEFAULT(cls):
        """Return default value for message field 'data'."""
        return numpy.array((0, 0, 0, 0, 0, 0, 0, 0, ), dtype=numpy.uint8)


class CAN(metaclass=Metaclass_CAN):
    """Message class 'CAN'."""

    __slots__ = [
        '_id',
        '_is_rtr',
        '_data',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'id': 'uint16',
        'is_rtr': 'boolean',
        'data': 'uint8[8]',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint16'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('uint8'), 8),  # noqa: E501
    )

    def __init__(self, **kwargs):
        if 'check_fields' in kwargs:
            self._check_fields = kwargs['check_fields']
        else:
            self._check_fields = ros_python_check_fields == '1'
        if self._check_fields:
            assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
                'Invalid arguments passed to constructor: %s' % \
                ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.id = kwargs.get('id', int())
        self.is_rtr = kwargs.get(
            'is_rtr', CAN.IS_RTR__DEFAULT)
        self.data = kwargs.get(
            'data', CAN.DATA__DEFAULT)

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.get_fields_and_field_types().keys(), self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    if self._check_fields:
                        assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.id != other.id:
            return False
        if self.is_rtr != other.is_rtr:
            return False
        if any(self.data != other.data):
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property  # noqa: A003
    def id(self):  # noqa: A003
        """Message field 'id'."""
        return self._id

    @id.setter  # noqa: A003
    def id(self, value):  # noqa: A003
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'id' field must be of type 'int'"
            assert value >= 0 and value < 65536, \
                "The 'id' field must be an unsigned integer in [0, 65535]"
        self._id = value

    @builtins.property
    def is_rtr(self):
        """Message field 'is_rtr'."""
        return self._is_rtr

    @is_rtr.setter
    def is_rtr(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'is_rtr' field must be of type 'bool'"
        self._is_rtr = value

    @builtins.property
    def data(self):
        """Message field 'data'."""
        return self._data

    @data.setter
    def data(self, value):
        if self._check_fields:
            if isinstance(value, numpy.ndarray):
                assert value.dtype == numpy.uint8, \
                    "The 'data' numpy.ndarray() must have the dtype of 'numpy.uint8'"
                assert value.size == 8, \
                    "The 'data' numpy.ndarray() must have a size of 8"
                self._data = value
                return
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 len(value) == 8 and
                 all(isinstance(v, int) for v in value) and
                 all(val >= 0 and val < 256 for val in value)), \
                "The 'data' field must be a set or sequence with length 8 and each value of type 'int' and each unsigned integer in [0, 255]"
        self._data = numpy.array(value, dtype=numpy.uint8)
