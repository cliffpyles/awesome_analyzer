#!/usr/bin/env python3

import argparse
import json
import pandas as pd
from pathlib import Path


def load_json_data(file_path):
    """
    Load JSON data from the specified file.

    Args:
    file_path (str or Path): Path to the JSON file containing the ingested data.

    Returns:
    pd.DataFrame: DataFrame containing the ingested data.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert the data to a DataFrame
    df = pd.DataFrame.from_dict(data, orient="index")
    df.reset_index(inplace=True)
    df.rename(columns={"index": "url"}, inplace=True)

    return df


def filter_data(
    df,
    min_stars=None,
    max_stars=None,
    min_forks=None,
    max_forks=None,
    min_watchers=None,
    max_watchers=None,
):
    """
    Filter the DataFrame based on the specified min/max values for stars, forks, and watchers.

    Args:
    df (pd.DataFrame): The DataFrame to filter.
    min_stars (int): Minimum number of stars.
    max_stars (int): Maximum number of stars.
    min_forks (int): Minimum number of forks.
    max_forks (int): Maximum number of forks.
    min_watchers (int): Minimum number of watchers.
    max_watchers (int): Maximum number of watchers.

    Returns:
    pd.DataFrame: Filtered DataFrame.
    """
    if min_stars is not None:
        df = df[df["stars"] >= min_stars]
    if max_stars is not None:
        df = df[df["stars"] <= max_stars]

    if min_forks is not None:
        df = df[df["forks"] >= min_forks]
    if max_forks is not None:
        df = df[df["forks"] <= max_forks]

    if min_watchers is not None:
        df = df[df["watchers"] >= min_watchers]
    if max_watchers is not None:
        df = df[df["watchers"] <= max_watchers]

    return df


def sort_data(df, sort_by="stars", ascending=False):
    """
    Sort the DataFrame by the specified column in ascending or descending order.

    Args:
    df (pd.DataFrame): The DataFrame to sort.
    sort_by (str): The column to sort by ('stars', 'forks', or 'watchers').
    ascending (bool): Whether to sort in ascending order.

    Returns:
    pd.DataFrame: Sorted DataFrame.
    """
    return df.sort_values(by=sort_by, ascending=ascending)


def main():
    parser = argparse.ArgumentParser(
        description="Display and filter GitHub repository data."
    )
    parser.add_argument(
        "input", type=str, help="Path to the JSON file containing the ingested data."
    )
    parser.add_argument(
        "--sort-by",
        type=str,
        choices=["stars", "forks", "watchers"],
        default="stars",
        help="Field to sort by. Default is 'stars'.",
    )
    parser.add_argument(
        "--ascending",
        action="store_true",
        help="Sort in ascending order. Default is descending.",
    )
    parser.add_argument(
        "--min-stars", type=int, help="Minimum number of stars to filter by."
    )
    parser.add_argument(
        "--max-stars", type=int, help="Maximum number of stars to filter by."
    )
    parser.add_argument(
        "--min-forks", type=int, help="Minimum number of forks to filter by."
    )
    parser.add_argument(
        "--max-forks", type=int, help="Maximum number of forks to filter by."
    )
    parser.add_argument(
        "--min-watchers", type=int, help="Minimum number of watchers to filter by."
    )
    parser.add_argument(
        "--max-watchers", type=int, help="Maximum number of watchers to filter by."
    )

    args = parser.parse_args()

    # Load the data
    df = load_json_data(args.input)

    # Apply filtering
    df = filter_data(
        df,
        min_stars=args.min_stars,
        max_stars=args.max_stars,
        min_forks=args.min_forks,
        max_forks=args.max_forks,
        min_watchers=args.min_watchers,
        max_watchers=args.max_watchers,
    )

    # Apply sorting (default sort is by 'stars' in descending order)
    df = sort_data(df, sort_by=args.sort_by, ascending=args.ascending)

    # Display the data
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
