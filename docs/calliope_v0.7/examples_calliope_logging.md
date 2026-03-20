# Calliope Logging (Tutorial)

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/calliope_logging/

This page provides guidance on configuring logging in Calliope to monitor model execution and debug issues.

## Using Internal Calliope Functionality

Calliope includes built-in logging capabilities that can be leveraged to track model operations. The internal logging system allows you to access debugging information and execution details throughout the modeling process.

## Adding Your Own Console Logging Handler

You can extend Calliope's logging by implementing custom console handlers. This approach enables you to capture and display log messages directly to the console with custom formatting and filtering based on your specific requirements.

To add a console logging handler, configure the Python logging module to work alongside Calliope's logger. This allows you to:

- Direct output to standard output or error streams
- Apply custom formatting to log messages
- Filter messages by level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Control which components' messages appear in console output

## Adding Your Own File Logging Handler

For persistent record-keeping, you can configure file-based logging handlers. This approach writes log messages to files for later analysis and troubleshooting.

File logging handlers allow you to:

- Save detailed execution logs to disk
- Maintain separate files for different logging levels
- Implement log rotation to manage file sizes
- Preserve historical data about model runs

Both console and file handlers can be customized to suit your analysis workflow and debugging needs.
