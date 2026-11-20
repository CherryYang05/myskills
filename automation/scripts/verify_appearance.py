#!/usr/bin/env python3
"""Verify the semantic icon registry covers every plugin and renders valid SVG."""
from appearance import load_config, render_icon, validate_coverage
from sync import ROOT
from plugin_groups import plugin_inventory


def main():
    names = [plugin["name"] for plugin in plugin_inventory()]
    config = load_config(ROOT)
    count = validate_coverage(config, names)
    for name in names:
        svg, color, fallback = render_icon(name, config)
        if fallback:
            raise ValueError(f"{name}: generic fallback is not allowed in a merged release")
        if len(svg) > 5 * 1024 * 1024 or not svg.startswith(b'<svg '):
            raise ValueError(f"{name}: invalid generated logo")
        print(f"{name}: icon OK, {color}, {len(svg)} bytes")
    print(f"Validated custom semantic SVG icons for all {count} plugins.")


if __name__ == "__main__":
    main()
