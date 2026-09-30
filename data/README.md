# Data

The raw data is not stored in this repository because of its size (about 134 MB).

## How to get it

1. Open the official Stack Overflow survey archive:
   https://github.com/StackExchange/Survey/tree/main/packages/archive/2025
2. Download `results.csv` and `schema.csv`.
3. Place both files in `data/raw/`.

The notebooks read from `data/raw/` and write cleaned files to `data/processed/`.