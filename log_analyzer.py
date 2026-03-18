"""
=============================================================
  Log Analyzer — Python Project
  Description: Parses a log file and generates a detailed
               summary of errors, warnings and info messages.
=============================================================
"""

import re
import sys
import os
from collections import Counter
from datetime import datetime


# ─────────────────────────────────────────────
# SECTION 1: File Reading
# ─────────────────────────────────────────────

def read_log_file(filepath: str) -> list:
    """
    Reads a log file and returns its lines as a list of strings.
    Handles missing files and empty files gracefully.
    """
    # Check if the file exists before trying to open it
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: '{filepath}'")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Edge case: file exists but has no content
    if not lines:
        print("[WARNING] The log file is empty. Nothing to analyze.")
        sys.exit(0)

    return lines


# ─────────────────────────────────────────────
# SECTION 2: Parsing Each Line with Regex
# ─────────────────────────────────────────────

# Standard log format example:
# 2024-01-15 10:23:45 ERROR   Database connection failed
# 2024-01-15 10:24:01 WARNING Disk usage above 80%
# 2024-01-15 10:24:10 INFO    Server started successfully

LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})?\s*"
    r"(?P<level>ERROR|WARNING|INFO|CRITICAL|DEBUG)\s+"
    r"(?P<message>.+)"
)


def parse_line(line: str):
    """
    Uses a regular expression to extract:
      - timestamp (optional)
      - log level (ERROR, WARNING, INFO, etc.)
      - message text
    Returns a dict if matched, or None if the line doesn't match.
    """
    match = LOG_PATTERN.search(line.strip())
    if match:
        return {
            "timestamp": match.group("timestamp"),  # May be None if not present
            "level":     match.group("level"),
            "message":   match.group("message").strip(),
            "raw":       line.strip()
        }
    return None  # Line doesn't match the expected format


# ─────────────────────────────────────────────
# SECTION 3: Core Analysis Logic
# ─────────────────────────────────────────────

def analyze_logs(lines: list) -> dict:
    """
    Iterates over all lines, parses each one, and builds
    a comprehensive analysis dictionary containing:
      - counts per log level
      - list of parsed entries
      - error frequency counter
      - list of extracted timestamps
      - count of unrecognized lines
    """
    # Counters for each log level
    level_counts = Counter()

    parsed_entries  = []   # All successfully parsed log entries
    error_messages  = []   # Just error-level messages (for frequency analysis)
    timestamps      = []   # All timestamps found
    unrecognized    = 0    # Lines that didn't match the log pattern

    for line in lines:
        entry = parse_line(line)

        if entry:
            level_counts[entry["level"]] += 1
            parsed_entries.append(entry)

            # Collect timestamp if present
            if entry["timestamp"]:
                timestamps.append(entry["timestamp"])

            # Collect ERROR and CRITICAL messages separately
            if entry["level"] in ("ERROR", "CRITICAL"):
                error_messages.append(entry["message"])
        else:
            # Count lines we couldn't parse (blank lines, comments, etc.)
            if line.strip():  # Ignore truly blank lines
                unrecognized += 1

    # Use Counter to find how often each error message repeats
    error_frequency = Counter(error_messages)

    return {
        "total_lines":      len(lines),
        "parsed_count":     len(parsed_entries),
        "unrecognized":     unrecognized,
        "level_counts":     level_counts,
        "entries":          parsed_entries,
        "error_frequency":  error_frequency,
        "timestamps":       timestamps,
    }


# ─────────────────────────────────────────────
# SECTION 4: Report Formatting & Console Output
# ─────────────────────────────────────────────

# ANSI color codes for terminal highlighting
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def level_color(level: str) -> str:
    """Returns the appropriate ANSI color for a given log level."""
    return {
        "ERROR":    RED,
        "CRITICAL": RED,
        "WARNING":  YELLOW,
        "INFO":     GREEN,
        "DEBUG":    CYAN,
    }.get(level, RESET)


def print_report(analysis: dict, filepath: str) -> None:
    """
    Prints a clean, color-coded summary to the terminal.
    """
    lc = analysis["level_counts"]
    ef = analysis["error_frequency"]
    ts = analysis["timestamps"]

    print(f"\n{BOLD}{'='*55}{RESET}")
    print(f"{BOLD}  LOG ANALYZER REPORT{RESET}")
    print(f"{BOLD}{'='*55}{RESET}")
    print(f"  File    : {filepath}")
    print(f"  Analyzed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'-'*55}")

    # ── Basic counts ──
    print(f"\n{BOLD}  LINE SUMMARY{RESET}")
    print(f"  Total Lines      : {analysis['total_lines']}")
    print(f"  Parsed Lines     : {analysis['parsed_count']}")
    print(f"  Unrecognized     : {analysis['unrecognized']}")

    # ── Level breakdown ──
    print(f"\n{BOLD}  LOG LEVEL BREAKDOWN{RESET}")
    for level in ["INFO", "WARNING", "ERROR", "CRITICAL", "DEBUG"]:
        count = lc.get(level, 0)
        if count > 0:
            color = level_color(level)
            bar = "█" * min(count, 40)
            print(f"  {color}{level:<10}{RESET} : {count:>4}  {color}{bar}{RESET}")

    # ── Timestamps ──
    if ts:
        print(f"\n{BOLD}  TIMESTAMPS{RESET}")
        print(f"  First entry : {ts[0]}")
        print(f"  Last entry  : {ts[-1]}")
        print(f"  Total found : {len(ts)}")

    # ── Error frequency (sorted by most common) ──
    if ef:
        print(f"\n{BOLD}  ERROR / CRITICAL MESSAGE FREQUENCY{RESET}")
        for msg, count in ef.most_common():
            color = RED if count > 1 else YELLOW
            tag   = "  <-- REPEATED" if count > 1 else ""
            print(f"  {color}[x{count:>2}]{RESET} {msg[:65]}{color}{tag}{RESET}")

        # ── Most frequent single error ──
        top_error, top_count = ef.most_common(1)[0]
        if top_count > 1:
            print(f"\n  {RED}{BOLD}*** CRITICAL REPEAT: '{top_error}' occurred {top_count} times! ***{RESET}")
    else:
        print(f"\n  {GREEN}No ERROR or CRITICAL messages found.{RESET}")

    print(f"\n{BOLD}{'='*55}{RESET}\n")


# ─────────────────────────────────────────────
# SECTION 5: Save Report to File (Optional)
# ─────────────────────────────────────────────

def save_report(analysis: dict, filepath: str, output_path: str = "report.txt") -> None:
    """
    Writes the same analysis results to a plain-text report file.
    """
    lc = analysis["level_counts"]
    ef = analysis["error_frequency"]
    ts = analysis["timestamps"]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 55 + "\n")
        f.write("  LOG ANALYZER REPORT\n")
        f.write("=" * 55 + "\n")
        f.write(f"  File    : {filepath}\n")
        f.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-" * 55 + "\n\n")

        f.write("LINE SUMMARY\n")
        f.write(f"  Total Lines   : {analysis['total_lines']}\n")
        f.write(f"  Parsed Lines  : {analysis['parsed_count']}\n")
        f.write(f"  Unrecognized  : {analysis['unrecognized']}\n\n")

        f.write("LOG LEVEL BREAKDOWN\n")
        for level in ["INFO", "WARNING", "ERROR", "CRITICAL", "DEBUG"]:
            count = lc.get(level, 0)
            if count > 0:
                f.write(f"  {level:<10}: {count}\n")

        if ts:
            f.write(f"\nTIMESTAMPS\n")
            f.write(f"  First : {ts[0]}\n")
            f.write(f"  Last  : {ts[-1]}\n")
            f.write(f"  Total : {len(ts)}\n")

        if ef:
            f.write("\nERROR FREQUENCY (sorted by count)\n")
            for msg, count in ef.most_common():
                tag = " *** REPEATED ***" if count > 1 else ""
                f.write(f"  [x{count:>2}] {msg}{tag}\n")

        f.write("\n" + "=" * 55 + "\n")

    print(f"  Report saved to: {output_path}\n")


# ─────────────────────────────────────────────
# SECTION 6: CLI Entry Point
# ─────────────────────────────────────────────

def main():
    """
    Main entry point. Handles CLI arguments:
      python log_analyzer.py <logfile>           -> analyze only
      python log_analyzer.py <logfile> --save    -> analyze + save report.txt
    """
    print(f"\n{BOLD}{CYAN}  Log Analyzer — Python Project{RESET}")

    # ── Argument parsing ──
    if len(sys.argv) < 2:
        filepath = input("\n  Enter path to your log file: ").strip()
    else:
        filepath = sys.argv[1]

    # Optional --save flag
    save_flag = "--save" in sys.argv

    # ── Run the pipeline ──
    print(f"\n  Reading '{filepath}' ...")
    lines    = read_log_file(filepath)

    print(f"  Analyzing {len(lines)} lines ...")
    analysis = analyze_logs(lines)

    # ── Print to console ──
    print_report(analysis, filepath)

    # ── Optionally save report ──
    if save_flag:
        save_report(analysis, filepath)
    else:
        choice = input("  Save report to report.txt? (y/n): ").strip().lower()
        if choice == "y":
            save_report(analysis, filepath)


# Standard Python entry-point guard
if __name__ == "__main__":
    main()