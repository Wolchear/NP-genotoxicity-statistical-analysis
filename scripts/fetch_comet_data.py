import argparse
import re
from pathlib import Path

import pandas as pd

INFO_ROWS = ['Mean', 'Median', 'Standard Deviation', 'Minimum', 'Maximum']

def pasrse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '--input', '-i',
        nargs='+',
        required=True,
        help='Specify raw files'
    )
    
    parser.add_argument(
        '--prefix', '-p',
        required=True,
        help='Specify out-tables prefix'
    )
    
    return parser.parse_args()

def sample_replica_from_filename(filename: str):
    stem = Path(filename).stem.strip()

    m = re.match(r"^(.+?)[ _]?D(\d+)$", stem)

    if not m:
        raise ValueError(f"Can't parse sample/replica from filename: {stem}")

    sample = m.group(1).strip().replace(",", ".")
    replica = f"D{m.group(2)}"

    return sample, replica

def read_excel(filename: str) -> pd.DataFrame:
    raw = pd.read_excel(
        filename,
        sheet_name='Automated Measurement Data',
        header=None
    )
    
    rows = []
    sample, replica = sample_replica_from_filename(filename)
    sample = (
        sample
        .strip(". ")
        .replace(" ", "_")
    )

    replica = (
        replica
        .strip(". ")
        .replace(" ", "_")
    )
        
    for row in range(len(raw)):
        first = raw.iloc[row, 0]

        if pd.isna(first):
            continue
        
        first = str(first).strip()
        
        if first in INFO_ROWS:
            rows.append({
                "Sample": sample,
                "Replica": replica,
                "Metric": first,
                "Head DNA": raw.iloc[row, 1],
                "Tail DNA": raw.iloc[row, 2],
                "Integral Intesity": raw.iloc[row, 3],
                "Head Radius": raw.iloc[row, 4],
                "Tail Length": raw.iloc[row, 5],
                "Tail Moment": raw.iloc[row, 6],
                "Olive Moment": raw.iloc[row, 7],
                "Head Area": raw.iloc[row, 8],
            })

    return pd.DataFrame(rows)
        
def prepare_separate_df(df_merged: pd.DataFrame) -> dict[str, pd.DataFrame]:
    value_cols = [
        "Head DNA",
        "Tail DNA",
        "Integral Intesity",
        "Head Radius",
        "Tail Length",
        "Tail Moment",
        "Olive Moment",
        "Head Area"
    ]
    
    datasets = {}

    for col in value_cols:
        datasets[col] = df_merged.pivot_table(
            index=["Sample", "Replica"],
            columns="Metric",
            values=col
        ).reset_index()

    return datasets

def save_datasets(datasets: dict[str, pd.DataFrame], prefix: str) -> None:
    for col, table in datasets.items():
        filename = (
            prefix +
            col.lower().replace(" ", "_") +
            ".csv"
        )
        table.to_csv(filename, index=False)

def main() -> None:
    args = pasrse_args()

    df = pd.concat(
        [read_excel(f) for f in args.input],
        ignore_index=True
    )
    print(df)
    datasets = prepare_separate_df(df)
    
    save_datasets(datasets, args.prefix)

if __name__ == '__main__':
    main()
