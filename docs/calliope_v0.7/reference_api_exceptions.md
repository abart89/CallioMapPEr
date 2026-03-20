# API Reference: Exceptions

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/exceptions/

## Overview

The `calliope.exceptions` module handles exceptions and warning management for the Calliope modeling framework.

## Exception Classes

### BackendError
Inherits from Python's base `Exception` class. This exception should be raised when issues occur during backend processing operations.

### BackendWarning
Inherits from Python's base `Warning` class. Use this warning type to flag potential backend processing issues where execution can continue despite the problem.

### ModelError
Inherits from Python's base `Exception` class. Raise this exception when encountering problems with model formulation or input data that prevent further execution.

### ModelWarning
Inherits from Python's base `Warning` class. This warning signals possible model issues but allows execution to proceed.

## Functions

### warn()
```python
warn(message: str, _class: type[Warning] = ModelWarning)
```
Raises the specified type of warning with formatted output.

### print_warnings_and_raise_errors()
```python
print_warnings_and_raise_errors(
    warnings=None,
    errors=None,
    during='model processing',
    bullet=' * '
)
```

Processes collections of warnings and errors with formatted output.

**Key features:**
- Prints warnings without stopping execution
- Raises `ModelError` if errors are present
- Supports both list and nested dictionary formats
- Simple lists display as bullet points
- Dictionary structures create nested bullet hierarchies

**Parameters:**
- `warnings`: String list or dict of lists; None/empty lists print nothing
- `errors`: String list or dict of lists; None/empty lists raise nothing
- `during`: Contextual phase descriptor (default: "model processing")
- `bullet`: Bullet character style (default: " * ")
