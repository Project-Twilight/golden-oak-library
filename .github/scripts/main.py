"""
This script validates the format of the files in a user-set directory,
based on `encoding.json`.
"""

import argparse
from collections import OrderedDict
import json
from pathlib import Path

from chardet.universaldetector import UniversalDetector


Pattern = str
Encoding = str


def detect_encoding(filepath: Path, detector: UniversalDetector) -> Encoding:
    """
    This function detects the encoding of a given file.

    :param filepath:
        The path to the file
    :param detector:
        Chardet universal detector
    :return:
        The name of the file's encoding in chardet format
    """

    detector.reset()

    with open(filepath, mode="rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done:
                break

    return (
        detector.result["encoding"].upper() if detector.result["encoding"] else "UTF-8"
    )


def main(arguments: argparse.Namespace) -> int:
    """
    **Main!**
    :param arguments:
        Parsed argument namespace
    :return:
        Exit code. 0 means success, anything else means failure.
    """

    modpath: Path = Path(arguments.path)
    if not modpath.is_dir():
        raise NotADirectoryError(f"'{arguments.path}' is not a valid directory")

    errors: list[str] = list()
    detector: UniversalDetector = UniversalDetector()
    checked_filepaths: set[Path] = set()

    with open(".github/scripts/encoding.json", mode="r", encoding="utf_8") as f:
        # noinspection PyTypeChecker
        encoding_pairs: OrderedDict[Pattern, Encoding] = json.load(
            f, object_pairs_hook=OrderedDict
        )

    for filepath_pattern, expected_encoding in encoding_pairs.items():
        for filepath in modpath.glob(filepath_pattern):
            if filepath not in checked_filepaths:
                detected_encoding: Encoding = detect_encoding(filepath, detector)
                if detected_encoding != expected_encoding:
                    errors.append(
                        f"[Error] '{filepath}' should be encoded in '{expected_encoding}'"
                    )
            checked_filepaths.add(filepath)

    detector.close()

    if errors:
        for error in errors:
            print(error)
        return 1
    return 0


if __name__ == "__main__":
    arg_parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="python .github/scripts/main.py",
        description="Victoria 3 file encoding validator",
    )
    arg_parser.add_argument(
        "-p", "--path", default=".", type=str, help="directory to validate files within"
    )
    args: argparse.Namespace = arg_parser.parse_args()
    exit_code: int = main(args)
    exit(exit_code)
