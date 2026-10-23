# fprime-to-xtce

Convert F-Prime command and telemetry dictionaries into XTCE format. This function creates the YAMCS dialect of XTCE.

## Installation

```bash
pip install -e .
```

## Run

To run this conversion script, use the following:

```bash
fprime-to-xtce </path/to/fprime/dictionary> -o </path/to/xtce/dictionary>
```

## Events

F Prime events are a construct above XTCE containers. These are represented and handled in the the consuming tools (e.g. YAMCS).

## Command Completion

YAMCS reports when each command is dispatched and whether it completed or failed, using verifiers that watch the command dispatcher's events `OpCodeDispatched`, `OpCodeCompleted`, `OpCodeError` and `InvalidCommand`. A failed command shows its response code, such as `EXECUTION_ERROR`, or `INVALID_OPCODE` when the dispatcher doesn't know the opcode. These events identify a command only by its opcode, so if two commands with the same opcode are waiting at once, the events of either can mark the other dispatched, completed or failed.

## License

Apache 2.0 License - see [LICENSE](LICENSE) for details.
