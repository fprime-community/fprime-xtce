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

## License

Apache 2.0 License - see [LICENSE](LICENSE) for details.
