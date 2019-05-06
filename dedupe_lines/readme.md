# Dedupe lines

Deduplicate lines in a text file.

Lines' order is preserved. Unique lines are printed in stdout.
A possible use case: deduplicate ~/.bash_history if you do not use `HISTCONTROL=erasedups`

Usage:
```bash
$ dedupe_lines.py myfile.txt
```
