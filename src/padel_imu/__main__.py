import argparse
import sys
from pathlib import Path

from . import run_full_analysis
from .helpers import format_metrics

PROCESSED_DIR = Path(__file__).parents[2] / "data" / "processed"


def main():
    parser = argparse.ArgumentParser(
        prog="padel-imu",
        description="Analyse a WitMotion IMU recording and print movement metrics.",
    )
    parser.add_argument("file", help="Path to the WitMotion TSV export file")
    parser.add_argument(
        "--device",
        default=None,
        metavar="NAME",
        help="Filter to a specific device name (leave blank to use all rows)",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Also write the processed DataFrame to <file>.processed.csv",
    )
    args = parser.parse_args()

    try:
        df, metrics = run_full_analysis(args.file, device_name=args.device)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nFile:   {args.file}")
    if args.device:
        print(f"Device: {args.device}")
    print(f"Rows:   {len(df)}\n")
    print(format_metrics(metrics))

    if args.csv:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        stem = Path(args.file).stem
        out_path = PROCESSED_DIR / f"{stem}.processed.csv"
        df.to_csv(out_path, index=False)
        print(f"\nProcessed data saved to: {out_path}")


if __name__ == "__main__":
    main()
