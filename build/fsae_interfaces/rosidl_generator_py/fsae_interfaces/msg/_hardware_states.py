# generated from rosidl_generator_py/resource/_idl.py.em
# with input from fsae_interfaces:msg/HardwareStates.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_HardwareStates(type):
    """Metaclass of message 'HardwareStates'."""

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
                'fsae_interfaces.msg.HardwareStates')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__hardware_states
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__hardware_states
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__hardware_states
            cls._TYPE_SUPPORT = module.type_support_msg__msg__hardware_states
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__hardware_states

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class HardwareStates(metaclass=Metaclass_HardwareStates):
    """Message class 'HardwareStates'."""

    __slots__ = [
        '_ebs_active',
        '_ts_active',
        '_in_gear',
        '_master_switch_on',
        '_asb_ready',
        '_brakes_engaged',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'ebs_active': 'uint8',
        'ts_active': 'uint8',
        'in_gear': 'uint8',
        'master_switch_on': 'uint8',
        'asb_ready': 'uint8',
        'brakes_engaged': 'uint8',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
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
        self.ebs_active = kwargs.get('ebs_active', int())
        self.ts_active = kwargs.get('ts_active', int())
        self.in_gear = kwargs.get('in_gear', int())
        self.master_switch_on = kwargs.get('master_switch_on', int())
        self.asb_ready = kwargs.get('asb_ready', int())
        self.brakes_engaged = kwargs.get('brakes_engaged', int())

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
        if self.ebs_active != other.ebs_active:
            return False
        if self.ts_active != other.ts_active:
            return False
        if self.in_gear != other.in_gear:
            return False
        if self.master_switch_on != other.master_switch_on:
            return False
        if self.asb_ready != other.asb_ready:
            return False
        if self.brakes_engaged != other.brakes_engaged:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def ebs_active(self):
        """Message field 'ebs_active'."""
        return self._ebs_active

    @ebs_active.setter
    def ebs_active(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'ebs_active' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'ebs_active' field must be an unsigned integer in [0, 255]"
        self._ebs_active = value

    @builtins.property
    def ts_active(self):
        """Message field 'ts_active'."""
        return self._ts_active

    @ts_active.setter
    def ts_active(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'ts_active' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'ts_active' field must be an unsigned integer in [0, 255]"
        self._ts_active = value

    @builtins.property
    def in_gear(self):
        """Message field 'in_gear'."""
        return self._in_gear

    @in_gear.setter
    def in_gear(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'in_gear' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'in_gear' field must be an unsigned integer in [0, 255]"
        self._in_gear = value

    @builtins.property
    def master_switch_on(self):
        """Message field 'master_switch_on'."""
        return self._master_switch_on

    @master_switch_on.setter
    def master_switch_on(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'master_switch_on' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'master_switch_on' field must be an unsigned integer in [0, 255]"
        self._master_switch_on = value

    @builtins.property
    def asb_ready(self):
        """Message field 'asb_ready'."""
        return self._asb_ready

    @asb_ready.setter
    def asb_ready(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'asb_ready' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'asb_ready' field must be an unsigned integer in [0, 255]"
        self._asb_ready = value

    @builtins.property
    def brakes_engaged(self):
        """Message field 'brakes_engaged'."""
        return self._brakes_engaged

    @brakes_engaged.setter
    def brakes_engaged(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'brakes_engaged' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'brakes_engaged' field must be an unsigned integer in [0, 255]"
        self._brakes_engaged = value
