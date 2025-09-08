import argparse
from apkshadow.actions import list as list_action
from apkshadow.actions import pull as pull_action
from apkshadow.actions import decompile as decompile_action
import apkshadow.utils as utils

def initListParser(subparsers):
    list_parser = subparsers.add_parser("list", help="List apks on device")
    list_parser.add_argument(
        "-o",
        "--output",
        help="Directory where pulled APKs will be saved",
    )

    group = list_parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f", "--filter", help="Package id or path to file containing package ids"
    )
    group.add_argument(
        "-r",
        "--regex",
        help="Regex or path to file containing regexes to match package ids",
    )


def initPullParser(subparsers):
    pull_parser = subparsers.add_parser("pull", help="Pull apks from device")
    pull_parser.add_argument(
        "-o",
        "--output",
        help="Directory where pulled APKs will be saved",
    )

    group = pull_parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f", "--filter", help="Package id or path to file containing package ids"
    )
    group.add_argument(
        "-r",
        "--regex",
        help="Regex or path to file containing regexes to match package ids",
    )

def initDecompileParser(subparsers):
    decompile_parser = subparsers.add_parser(
        "decompile", help="Decompile APKs using jadx (from device or local source)"
    )

    decompile_parser.add_argument(
        "-s",
        "--source",
        default=None,
        help="Directory containing APKs to decompile (skips pulling from device if provided)"
    )

    decompile_parser.add_argument(
        "-o",
        "--output",
        default="./",
        help="Directory where decompiled source will be saved (default: current dir)"
    )

    group = decompile_parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f", "--filter",
        help="Package id or path to file containing package ids"
    )
    group.add_argument(
        "-r", "--regex",
        help="Regex or path to file containing regexes to match package ids"
    )

    decompile_parser.add_argument(
        "-m", "--mode",
        default="apktool",
        help="Tool to use for decompilation (default: 'apktool')"
    )


def main():
    parser = argparse.ArgumentParser(description="Android APK automation tool")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose debug output"
    )
    parser.add_argument(
        "-d",
        "--device",
        help="Target ADB device",
    )

    subparsers = parser.add_subparsers(
        dest="action", required=True, help="Action to perform"
    )

    initListParser(subparsers)
    initPullParser(subparsers)
    initDecompileParser(subparsers)

    args = parser.parse_args()

    utils.setVerbose(args.verbose)
    regex_mode = bool(args.regex)
    pattern_source = args.filter or args.regex

    if args.action == "list":
        list_action.handleListAction(pattern_source, args.device, regex_mode, args.output)
    elif args.action == "pull":
        pull_action.handlePullAction(
            pattern_source, args.device, regex_mode, args.output
        )
    elif args.action == "decompile":
        decompile_action.handleDecompileAction(pattern_source, args.device, regex_mode, args.source, args.output, args.mode)
