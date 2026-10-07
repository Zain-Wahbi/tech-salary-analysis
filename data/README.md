# Data

The raw data is not stored in this repository because of its size (about 134 MB).

## How to get it

1. Open the official Stack Overflow survey archive:
   https://github.com/StackExchange/Survey/tree/main/packages/archive/2025
2. Download `results.csv` and `schema.csv`.
3. Place both files in `data/raw/`.

The notebooks read from `data/raw/` and write cleaned files to `data/processed/`.

## License and attribution

The Stack Overflow Developer Survey data is published by Stack Overflow under the
Open Database License (ODbL) 1.0. See https://survey.stackoverflow.co/ for the official
source and license terms. This repository does not redistribute the survey data or the
cleaned datasets derived from it; it only contains code and analysis results.