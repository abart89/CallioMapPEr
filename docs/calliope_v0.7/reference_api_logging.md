# API Reference: Logging

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/reference/api/logging/

## Overview

The `calliope.util.logging` module provides functionality for creating the Calliope logger object and applying logging tools and features throughout the system.

## LogWriter Class

`LogWriter(logger, level, strip=False)`

A custom logger class designed to redirect solver outputs and prevent message duplication.

### Attributes
- **logger**: The logger instance to write to
- **level**: The logging level for messages
- **strip**: Boolean flag to strip whitespace from messages

### Methods

#### `write(message)`
Saves a message to the logger. Messages are filtered to exclude newline characters, and whitespace is optionally stripped based on configuration.

#### `flush()`
A placeholder method reserved for future flush functionality.

## Functions

### `log_time()`

Simultaneously logs the time of a Calliope event to both a dictionary and the logger.

**Parameters:**
- `logger`: Logger instance for recording the time
- `timings`: Dictionary storing model timing data
- `identifier`: Key for the event in the timings dictionary
- `comment`: Optional description (defaults to identifier)
- `level`: Logging level, defaulting to "info"
- `time_since_solve_start`: When enabled, appends elapsed time since solver initiation

**Returns:** POSIX timestamp of the logged event

### `set_log_verbosity()`

Configures logging verbosity and sets up the root logger for console output with timestamp formatting.

**Parameters:**
- `verbosity`: Logging level as string or integer
- `include_solver_output`: Enables DEBUG logging for backend solver output (default: True)
- `capture_warnings`: Routes Python warnings through the logger (default: True)

### `setup_root_logger()`

Initializes the Calliope root logger with proper formatting, handler configuration, and verbosity settings.

**Parameters:**
- `verbosity`: Logging level specification
- `capture_warnings`: Integrates Python warnings into logging system (default: True)

**Returns:** Configured logging.Logger instance
