"""
Logging utilities for Azure Discovery Tool
Provides comprehensive command logging, timing, and debug output
"""

import logging
import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path


class AzureLogger:
    """Centralized logger for Azure CLI commands and operations"""

    def __init__(self, log_dir="logs", verbose=False):
        self.verbose = verbose
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)

        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = self.log_dir / f"azure_audit_{timestamp}.log"
        self.command_count = 0
        self.total_time = 0

        # Set up file logger
        self.file_logger = logging.getLogger('azure_audit_file')
        self.file_logger.setLevel(logging.DEBUG)

        # File handler - logs everything
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.file_logger.addHandler(fh)

        # Console logger (only if verbose)
        if self.verbose:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(logging.Formatter('    [DEBUG] %(message)s'))
            self.file_logger.addHandler(ch)

        # Log startup
        self.file_logger.info("=" * 80)
        self.file_logger.info("Azure Infrastructure Audit - Logging Started")
        self.file_logger.info(f"Verbose mode: {verbose}")
        self.file_logger.info("=" * 80)

    def log_command(self, command, level="INFO"):
        """Log a command that will be executed"""
        self.command_count += 1
        msg = f"[Command #{self.command_count}] {command}"
        if level == "INFO":
            self.file_logger.info(msg)
        elif level == "DEBUG":
            self.file_logger.debug(msg)
        if self.verbose:
            print(f"    🔧 Executing: {command}")

    def log_result(self, result, duration=None):
        """Log command result"""
        if duration:
            self.total_time += duration
            msg = f"[Result] Success in {duration:.2f}s"
        else:
            msg = "[Result] Success"
        self.file_logger.info(msg)
        if self.verbose and duration:
            print(f"    ✓ Completed in {duration:.2f}s")

    def log_error(self, error, command=None):
        """Log an error"""
        if command:
            self.file_logger.error(f"[Error] Command failed: {command}")
        self.file_logger.error(f"[Error] {error}")
        if self.verbose:
            print(f"    ✗ Error: {error}")

    def log_json_response(self, data, preview_size=5):
        """Log JSON response data"""
        if isinstance(data, list):
            self.file_logger.debug(f"[Response] Received {len(data)} items")
            if self.verbose and len(data) > 0:
                print(f"    📦 Received {len(data)} items")
        elif isinstance(data, dict):
            self.file_logger.debug(f"[Response] Received dictionary with {len(data)} keys")
        else:
            self.file_logger.debug(f"[Response] Received data: {type(data)}")

    def log_info(self, message):
        """Log informational message"""
        self.file_logger.info(message)
        if self.verbose:
            print(f"    ℹ {message}")

    def log_section(self, section_name):
        """Log a new section"""
        self.file_logger.info("-" * 80)
        self.file_logger.info(f"SECTION: {section_name}")
        self.file_logger.info("-" * 80)

    def get_stats(self):
        """Get logging statistics"""
        return {
            "commands_executed": self.command_count,
            "total_time": self.total_time,
            "log_file": str(self.log_file)
        }

    def print_summary(self):
        """Print logging summary"""
        self.file_logger.info("=" * 80)
        self.file_logger.info("AUDIT COMPLETE - Logging Summary")
        self.file_logger.info(f"Total commands executed: {self.command_count}")
        self.file_logger.info(f"Total execution time: {self.total_time:.2f}s")
        self.file_logger.info(f"Log file: {self.log_file}")
        self.file_logger.info("=" * 80)


# Global logger instance
_logger = None


def init_logger(log_dir="logs", verbose=False):
    """Initialize the global logger"""
    global _logger
    _logger = AzureLogger(log_dir=log_dir, verbose=verbose)
    return _logger


def get_logger():
    """Get the global logger instance"""
    global _logger
    if _logger is None:
        _logger = AzureLogger()
    return _logger


def run_az_command(command, timeout=120):
    """
    Execute Azure CLI command with comprehensive logging

    Args:
        command: Azure CLI command to execute
        timeout: Command timeout in seconds

    Returns:
        JSON parsed output from command
    """
    logger = get_logger()
    logger.log_command(command)

    start_time = time.time()

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        duration = time.time() - start_time

        if result.returncode != 0:
            logger.log_error(f"Command failed with return code {result.returncode}", command)
            logger.file_logger.error(f"[STDERR] {result.stderr}")
            if logger.verbose:
                print(f"    ✗ STDERR: {result.stderr[:200]}")
            return []

        # Parse JSON response
        try:
            data = json.loads(result.stdout) if result.stdout else []
            logger.log_result(result=data, duration=duration)
            logger.log_json_response(data)

            # Log full JSON to file if verbose
            if logger.verbose:
                logger.file_logger.debug(f"[Full Response] {json.dumps(data, indent=2)[:500]}...")

            return data

        except json.JSONDecodeError as e:
            logger.log_error(f"Failed to parse JSON: {e}", command)
            logger.file_logger.debug(f"[Raw Output] {result.stdout[:500]}")
            return []

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        logger.log_error(f"Command timed out after {timeout}s", command)
        return []

    except Exception as e:
        duration = time.time() - start_time
        logger.log_error(f"Command execution failed: {e}", command)
        import traceback
        logger.file_logger.error(f"[Traceback] {traceback.format_exc()}")
        return []
