# generated from rosidl_generator_py/resource/_idl.py.em
# with input from fsae_interfaces:msg/ConeDetection.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_ConeDetection(type):
    """Metaclass of message 'ConeDetection'."""

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
                'fsae_interfaces.msg.ConeDetection')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__cone_detection
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__cone_detection
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__cone_detection
            cls._TYPE_SUPPORT = module.type_support_msg__msg__cone_detection
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__cone_detection

            from geometry_msgs.msg import Point
            if Point.__class__._TYPE_SUPPORT is None:
                Point.__class__.__import_type_support__()

            from geometry_msgs.msg import Pose
            if Pose.__class__._TYPE_SUPPORT is None:
                Pose.__class__.__import_type_support__()

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ConeDetection(metaclass=Metaclass_ConeDetection):
    """Message class 'ConeDetection'."""

    __slots__ = [
        '_header',
        '_car_pose',
        '_yellow',
        '_blue',
        '_small_orange',
        '_big_orange',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'car_pose': 'geometry_msgs/Pose',
        'yellow': 'sequence<geometry_msgs/Point>',
        'blue': 'sequence<geometry_msgs/Point>',
        'small_orange': 'sequence<geometry_msgs/Point>',
        'big_orange': 'sequence<geometry_msgs/Point>',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Pose'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Point')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Point')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Point')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Point')),  # noqa: E501
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
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        from geometry_msgs.msg import Pose
        self.car_pose = kwargs.get('car_pose', Pose())
        self.yellow = kwargs.get('yellow', [])
        self.blue = kwargs.get('blue', [])
        self.small_orange = kwargs.get('small_orange', [])
        self.big_orange = kwargs.get('big_orange', [])

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
        if self.header != other.header:
            return False
        if self.car_pose != other.car_pose:
            return False
        if self.yellow != other.yellow:
            return False
        if self.blue != other.blue:
            return False
        if self.small_orange != other.small_orange:
            return False
        if self.big_orange != other.big_orange:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def header(self):
        """Message field 'header'."""
        return self._header

    @header.setter
    def header(self, value):
        if self._check_fields:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'header' field must be a sub message of type 'Header'"
        self._header = value

    @builtins.property
    def car_pose(self):
        """Message field 'car_pose'."""
        return self._car_pose

    @car_pose.setter
    def car_pose(self, value):
        if self._check_fields:
            from geometry_msgs.msg import Pose
            assert \
                isinstance(value, Pose), \
                "The 'car_pose' field must be a sub message of type 'Pose'"
        self._car_pose = value

    @builtins.property
    def yellow(self):
        """Message field 'yellow'."""
        return self._yellow

    @yellow.setter
    def yellow(self, value):
        if self._check_fields:
            from geometry_msgs.msg import Point
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
                 all(isinstance(v, Point) for v in value) and
                 True), \
                "The 'yellow' field must be a set or sequence and each value of type 'Point'"
        self._yellow = value

    @builtins.property
    def blue(self):
        """Message field 'blue'."""
        return self._blue

    @blue.setter
    def blue(self, value):
        if self._check_fields:
            from geometry_msgs.msg import Point
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
                 all(isinstance(v, Point) for v in value) and
                 True), \
                "The 'blue' field must be a set or sequence and each value of type 'Point'"
        self._blue = value

    @builtins.property
    def small_orange(self):
        """Message field 'small_orange'."""
        return self._small_orange

    @small_orange.setter
    def small_orange(self, value):
        if self._check_fields:
            from geometry_msgs.msg import Point
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
                 all(isinstance(v, Point) for v in value) and
                 True), \
                "The 'small_orange' field must be a set or sequence and each value of type 'Point'"
        self._small_orange = value

    @builtins.property
    def big_orange(self):
        """Message field 'big_orange'."""
        return self._big_orange

    @big_orange.setter
    def big_orange(self, value):
        if self._check_fields:
            from geometry_msgs.msg import Point
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
                 all(isinstance(v, Point) for v in value) and
                 True), \
                "The 'big_orange' field must be a set or sequence and each value of type 'Point'"
        self._big_orange = value
