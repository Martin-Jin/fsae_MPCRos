// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from fsae_interfaces:msg/HardwareStates.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "fsae_interfaces/msg/detail/hardware_states__struct.h"
#include "fsae_interfaces/msg/detail/hardware_states__functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool fsae_interfaces__msg__hardware_states__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[52];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("fsae_interfaces.msg._hardware_states.HardwareStates", full_classname_dest, 51) == 0);
  }
  fsae_interfaces__msg__HardwareStates * ros_message = _ros_message;
  {  // ebs_active
    PyObject * field = PyObject_GetAttrString(_pymsg, "ebs_active");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->ebs_active = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // ts_active
    PyObject * field = PyObject_GetAttrString(_pymsg, "ts_active");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->ts_active = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // in_gear
    PyObject * field = PyObject_GetAttrString(_pymsg, "in_gear");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->in_gear = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // master_switch_on
    PyObject * field = PyObject_GetAttrString(_pymsg, "master_switch_on");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->master_switch_on = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // asb_ready
    PyObject * field = PyObject_GetAttrString(_pymsg, "asb_ready");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->asb_ready = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // brakes_engaged
    PyObject * field = PyObject_GetAttrString(_pymsg, "brakes_engaged");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->brakes_engaged = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * fsae_interfaces__msg__hardware_states__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of HardwareStates */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("fsae_interfaces.msg._hardware_states");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "HardwareStates");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  fsae_interfaces__msg__HardwareStates * ros_message = (fsae_interfaces__msg__HardwareStates *)raw_ros_message;
  {  // ebs_active
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->ebs_active);
    {
      int rc = PyObject_SetAttrString(_pymessage, "ebs_active", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // ts_active
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->ts_active);
    {
      int rc = PyObject_SetAttrString(_pymessage, "ts_active", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // in_gear
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->in_gear);
    {
      int rc = PyObject_SetAttrString(_pymessage, "in_gear", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // master_switch_on
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->master_switch_on);
    {
      int rc = PyObject_SetAttrString(_pymessage, "master_switch_on", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // asb_ready
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->asb_ready);
    {
      int rc = PyObject_SetAttrString(_pymessage, "asb_ready", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // brakes_engaged
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->brakes_engaged);
    {
      int rc = PyObject_SetAttrString(_pymessage, "brakes_engaged", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
