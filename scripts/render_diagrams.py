#!/usr/bin/env python3
"""
Diagram Renderer for Azure Network Diagrams
Converts Graphviz DOT files to PNG and SVG images
"""

import subprocess
import sys
from pathlib import Path
import os


def check_graphviz():
    """Check if Graphviz is installed"""
    try:
        result = subprocess.run(
            ["dot", "-V"],
            capture_output=True,
            text=True
        )
        print(f"✓ Graphviz found: {result.stderr.strip()}")
        return True
    except FileNotFoundError:
        print("✗ Graphviz not found!")
        print("\nPlease install Graphviz:")
        print("  macOS:   brew install graphviz")
        print("  Linux:   sudo apt-get install graphviz")
        print("  Windows: Download from https://graphviz.org/download/")
        return False


def render_dot_file(dot_file, output_format="png"):
    """
    Render a DOT file to PNG or SVG

    Args:
        dot_file: Path to .dot file
        output_format: Output format (png, svg, pdf)
    """
    dot_path = Path(dot_file)
    if not dot_path.exists():
        print(f"✗ File not found: {dot_file}")
        return False

    output_file = dot_path.with_suffix(f".{output_format}")

    try:
        result = subprocess.run(
            ["dot", f"-T{output_format}", str(dot_path), "-o", str(output_file)],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print(f"✓ Generated: {output_file}")
            return True
        else:
            print(f"✗ Error rendering {dot_file}: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"✗ Timeout rendering {dot_file}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def render_all_diagrams(diagrams_dir="docs/diagrams", formats=["png", "svg"]):
    """
    Render all DOT files in the diagrams directory

    Args:
        diagrams_dir: Directory containing .dot files
        formats: List of output formats (png, svg, pdf)
    """
    diagrams_path = Path(diagrams_dir)

    if not diagrams_path.exists():
        print(f"✗ Diagrams directory not found: {diagrams_dir}")
        print("  Run the audit first to generate diagrams.")
        return False

    # Find all .dot files
    dot_files = list(diagrams_path.glob("*.dot"))

    if not dot_files:
        print(f"✗ No .dot files found in {diagrams_dir}")
        print("  Run the audit first to generate diagrams.")
        return False

    print(f"\n🎨 Rendering {len(dot_files)} diagram(s) to {', '.join(formats)}")
    print("=" * 60)

    success_count = 0
    for dot_file in dot_files:
        print(f"\n📄 Processing: {dot_file.name}")
        for fmt in formats:
            if render_dot_file(dot_file, fmt):
                success_count += 1

    print("\n" + "=" * 60)
    print(f"✓ Successfully rendered {success_count} diagram file(s)")

    return True


def main():
    """Main entry point"""
    print("=" * 60)
    print("Azure Network Diagram Renderer")
    print("=" * 60)
    print()

    # Check for Graphviz
    if not check_graphviz():
        sys.exit(1)

    # Parse arguments
    diagrams_dir = "docs/diagrams"
    formats = ["png", "svg"]

    if len(sys.argv) > 1:
        diagrams_dir = sys.argv[1]

    if len(sys.argv) > 2:
        formats = sys.argv[2].split(",")

    # Render diagrams
    success = render_all_diagrams(diagrams_dir, formats)

    if success:
        print(f"\n📁 Diagrams available in: {Path(diagrams_dir).absolute()}")
        print("\nYou can now:")
        print(f"  - View PNG images: open {diagrams_dir}/*.png")
        print(f"  - View SVG images: open {diagrams_dir}/*.svg")
        print(f"  - Use in documentation, presentations, etc.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
