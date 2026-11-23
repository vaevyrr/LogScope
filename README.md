# LogScope

A small command-line log explorer for plain-text application and server logs.

## Features

- Filter by level, source, or text
- Group repeated messages
- Show a readable timeline
- Export filtered records to JSON or CSV
- Read-only input handling

## Usage

Python 3.10+.

```bash
python logscope.py app.log
python logscope.py app.log --level ERROR
python logscope.py app.log --contains timeout --group
python logscope.py app.log --json results.json
python logscope.py app.log --csv results.csv
```

## Tests

```bash
python -m unittest discover -s tests -v
```

MIT licensed.
