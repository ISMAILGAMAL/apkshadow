from apkshadow.actions import decompile as decompile_action
from apkshadow.actions import analyze as analyze_action
from apkshadow.actions import install as install_action
from apkshadow.actions import list as list_action
from apkshadow.actions import pull as pull_action
from apkshadow.parser import Parser
import apkshadow.globals as GLOBALS
import apkshadow.utils as utils
import argparse


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
        default="./",
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
        help="Directory containing APKs to decompile (Pulls from adb connected device if not provided)",
    )

    decompile_parser.add_argument(
        "-o",
        "--output",
        default="./",
        help="Directory where decompiled source will be saved (default: current dir)",
    )

    group = decompile_parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f", "--filter", help="Package id or path to file containing package ids"
    )
    group.add_argument(
        "-r",
        "--regex",
        help="Regex or path to file containing regexes to match package ids",
    )

    decompile_parser.add_argument(
        "-m",
        "--mode",
        default="apktool",
        help="Tool to use for decompilation ('apktool', 'jadx') (default: 'apktool')",
    )


def initAnalyzeParser(subparsers):
    analyze_parser = subparsers.add_parser(
        "analyze",
        help='analyze AndroidManifests to find attack surface. (eg.. exported="true")',
    )

    analyze_parser.add_argument(
        "-s",
        "--source",
        default="./",
        help="Directory containing decompiled APKs with their AndroidManifests.",
    )

    analyze_parser.add_argument(
        "--raw-apks",
        action="store_true",
        help="Used if the source directory contains raw apks and not decompiled apks' manifests",
    )

    analyze_parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Directory where AnalyzeResult.xml will be saved",
    )

    group = analyze_parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f", "--filter", help="Package id or path to file containing package ids"
    )
    group.add_argument(
        "-r",
        "--regex",
        help="Regex or path to file containing regexes to match package ids",
    )


def initInstallParser(subparsers):
    install_parser = subparsers.add_parser(
        "install",
        help="Install apks to device from local disk"
    )

    group = install_parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f", "--filter", help="Package id or path to file containing package ids"
    )
    group.add_argument(
        "-r",
        "--regex",
        help="Regex or path to file containing regexes to match package ids",
    )

    install_parser.add_argument(
        "-s",
        "--source",
        default="./",
        help="Directory containing APKs to install on device",
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

    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clears the AndroidManifests caching which the application "
    )

    parser.add_argument(
        "--cache-dir",
        help="Directory where decompiled apks' parsed manifest representation is cached as json (to prevent decompiling several times)"
    )

    subparsers = parser.add_subparsers(
        dest="action", required=True, help="Action to perform"
    )

    initListParser(subparsers)
    initPullParser(subparsers)
    initDecompileParser(subparsers)
    initAnalyzeParser(subparsers)
    initInstallParser(subparsers)

    args = parser.parse_args()

    utils.setVerbose(args.verbose)
    utils.setDevice(args.device)
    utils.setCacheDir(args.cache_dir)
    regex_mode = bool(args.regex)
    pattern_source = args.filter or args.regex
    clear_cache = args.clear_cache

    if clear_cache:
        Parser.clearCache() 
        print(f"{GLOBALS.HIGHLIGHT}Cache cleared: {GLOBALS.CACHE_DIR}{GLOBALS.RESET}")

    if args.action == "list":
        list_action.handleListAction(
            pattern_source, regex_mode, args.output
        )
    elif args.action == "pull":
        pull_action.handlePullAction(
            pattern_source,
            regex_mode,
            args.output,
        )
    elif args.action == "decompile":
        decompile_action.handleDecompileAction(
            pattern_source,
            regex_mode,
            args.source,
            args.output,
            args.mode,
        )
    elif args.action == "analyze":
        analyze_action.handleAnalyzeAction(
            pattern_source, regex_mode, args.source, args.output, args.raw_apks
        )
    elif args.action == "install":
        install_action.handleInstallAction(pattern_source, regex_mode, args.source)
