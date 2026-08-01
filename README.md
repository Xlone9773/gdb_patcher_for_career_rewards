# gdb_patcher_for_career_rewards

A simple and lightweight Python script that allows you to edit the rewards of Asphalt 9: Legends career mode.

## Overview

This is a small single-file command-line tool (gdb_patch.py) that scans a binary career/gdb file, locates level records and their reward fields, and allows you to list or modify the following fields for each level:

- flag (unsigned 4-byte integer)
- diff (4-byte float difficulty value)
- rank fields (unsigned 2-byte integers, up to 4 values found per level)

The script makes a backup of the target file (path + `.bak`) before writing changes.

> Warning: Modifying game files may violate the game's Terms of Service and can result in account sanctions. Use this tool only for offline research or local testing and at your own risk.

## Requirements

- Python 3.x (recommended 3.7+)
- No third-party dependencies
- Asphalt 9: Legends 1.2.1 Leia version
- A9-business.gdb file of the above Leia version (available at `/assets/main/business-logic/A9-business.gdb`)

## Usage

Basic invocation:

```bash
python3 gdb_patch.py <mode> <path> [options/specs...]
```

Modes:

- list — Scan and print all detected levels and fields
- patch — Modify specific levels using one or more spec arguments
- all — Apply the same value(s) to all detected levels (use optional flags)

### list

Scan and show detected levels and fields:

```bash
python3 gdb_patch.py list path/to/career.gdb
```

Output columns: ID, diff, flag, R1..R4 (up to 4 rank fields)

### patch

Modify one or more specific levels. Each modification is provided as a spec parameter with the format:

```
<lid>:<flag>:<diff>:<rank1,rank2,rank3,rank4>
```

Notes:
- `lid` can be specified in decimal or hex (e.g. `0x1A2B`).
- `flag` is an integer (written as 4 bytes).
- `diff` is a floating-point value (written as 4-byte float).
- `rankN` are integers (written as 2-byte unsigned shorts).
- Only provided fields are written; omit parts if you don't want to change them.

Example — modify a single level (hex id) and set flag/diff/ranks:

```bash
python3 gdb_patch.py patch path/to/career.gdb 0x1A2B:1000:1.2:60,120,180,240
```

If the script finds fewer than 4 rank fields for a level, it will only write to the found fields and print a warning for any extra values.

### all

Apply the same value(s) to all detected levels. Use the optional parameters `--flag`, `--diff`, and `--rank`:

```bash
python3 gdb_patch.py all path/to/career.gdb [--flag <int>] [--diff <float>] [--rank <int>]
```

Example — batch update all levels:

```bash
python3 gdb_patch.py all A9-business.gdb --flag 99999 --diff 0.1 --rank 5000
```

This sets the `flag` to 99999, `diff` to 0.1, and all detected rank fields to 5000 for every level found in `A9-business.gdb`.

## Implementation notes (for developers)

- The core scanner is `scan(data)` in `gdb_patch.py`, which performs byte-pattern matching to locate level entries and extract offsets for the difficulty (float), flag (uint32), and rank (uint16) fields.
- The script uses `struct.unpack_from` / `struct.pack_into` to read and write binary values in-place.
- Before writing changes the script copies the original file to `path + '.bak'`.


## License

See the LICENSE file in the repository.
