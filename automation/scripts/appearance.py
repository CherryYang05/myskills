"""Curated semantic SVG icons for generated Agent Plugins.

The SVG glyphs are structured source data, not executable scripts. A shared
rendering shell enforces dimensions, corner radii, strokes and spacing.
Every generated plugin must have explicit appearance metadata; the generic
default exists solely for previews of new, not-yet-reviewed plugins.
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

CONFIG_PATH = "automation/plugin-appearance.json"
SVG_NS = "{http://www.w3.org/2000/svg}"
ALLOWED_TAGS = {"path", "rect", "circle", "line", "polyline", "polygon", "ellipse"}
ALLOWED_ATTRS = {
    "d", "x", "y", "x1", "x2", "y1", "y2", "width", "height",
    "rx", "ry", "cx", "cy", "r", "points", "stroke", "fill",
    "stroke-width", "fill-opacity", "stroke-opacity", "opacity",
}
BRAND_COLOR = re.compile(r"#[0-9A-F]{6}\Z")
PATH_DATA = re.compile(r"[MmLlHhVvCcSsQqTtAaZz0-9.,+\-\s]+\Z")
NUMERIC_DATA = re.compile(r"[0-9.,+\-\s]+\Z")
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def load_config(root):
    config = json.loads((Path(root) / CONFIG_PATH).read_text(encoding="utf-8"))
    if not isinstance(config, dict) or set(config) != {"schemaVersion", "default", "skills"}:
        raise ValueError("Appearance configuration must define schemaVersion, default, skills")
    if config["schemaVersion"] != 1 or type(config["schemaVersion"]) is not int:
        raise ValueError("Unsupported appearance schema version")
    if not isinstance(config["skills"], dict):
        raise ValueError("Appearance skills must be a mapping")
    validate_entry("default", config["default"])
    for name, entry in config["skills"].items():
        if not isinstance(name, str) or not NAME.fullmatch(name):
            raise ValueError(f"Invalid appearance plugin name: {name!r}")
        validate_entry(name, entry)
    return config


def contrast_against_white(color):
    rgb = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    luminance = sum(w * c for w, c in zip((0.2126, 0.7152, 0.0722), linear))
    return 1.05 / (luminance + 0.05)


def validate_entry(name, entry):
    if not isinstance(entry, dict) or set(entry) != {"brandColor", "concept", "glyph"}:
        raise ValueError(f"{name}: expected brandColor, concept and glyph only")
    color, concept, glyph = (entry[key] for key in ("brandColor", "concept", "glyph"))
    if not isinstance(color, str) or not BRAND_COLOR.fullmatch(color):
        raise ValueError(f"{name}: brandColor must be an uppercase #RRGGBB")
    if contrast_against_white(color) < 2.0:
        raise ValueError(f"{name}: brandColor lacks 2:1 contrast against white")
    if not isinstance(concept, str) or not concept.strip() or len(concept) > 96:
        raise ValueError(f"{name}: concept must explain the functional icon")
    if not isinstance(glyph, str) or not glyph.strip() or len(glyph.encode("utf-8")) > 4096:
        raise ValueError(f"{name}: glyph must be a compact SVG shape fragment")
    if any(part in glyph.upper() for part in ("<!DOCTYPE", "<!ENTITY", "<?XML")):
        raise ValueError(f"{name}: prohibited XML construct")
    try:
        tree = ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg">' + glyph + "</svg>")
    except ET.ParseError as error:
        raise ValueError(f"{name}: malformed SVG glyph") from error
    if not 1 <= len(tree) <= 24:
        raise ValueError(f"{name}: glyph needs between 1 and 24 shapes")
    for shape in tree.iter():
        if shape is tree:
            continue
        if shape.tag not in {SVG_NS + tag for tag in ALLOWED_TAGS}:
            raise ValueError(f"{name}: SVG element not permitted: {shape.tag}")
        if list(shape) or (shape.text or "").strip() or (shape.tail or "").strip():
            raise ValueError(f"{name}: nested SVG elements and text are forbidden")
        if set(shape.attrib) - ALLOWED_ATTRS:
            raise ValueError(f"{name}: SVG attribute not permitted")
        for key, value in shape.attrib.items():
            if key in ("fill", "stroke"):
                if value not in ("#fff", "none"):
                    raise ValueError(f"{name}: only shared white/none paint allowed")
            elif key == "d":
                if not PATH_DATA.fullmatch(value):
                    raise ValueError(f"{name}: unsafe path data")
            elif not NUMERIC_DATA.fullmatch(value):
                raise ValueError(f"{name}: invalid numeric SVG attribute {key}")


def validate_coverage(config, plugin_names):
    names = set(plugin_names)
    configured = set(config["skills"])
    missing, extra = sorted(names - configured), sorted(configured - names)
    if missing or extra:
        raise ValueError(
            f"Plugin appearance coverage mismatch: missing={missing}, extra={extra}. "
            "Design a semantic glyph and add it to automation/plugin-appearance.json "
            "before merging a new plugin."
        )
    return len(names)


def render_icon(name, config):
    """Return generated SVG bytes, brand color and whether fallback was used."""
    entry = config["skills"].get(name)
    fallback = entry is None
    if fallback:
        entry = config["default"]
    title = escape(name + " — " + entry["concept"])
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" '
        'viewBox="0 0 128 128">\n'
        f'  <title>{title}</title>\n'
        f'  <rect width="128" height="128" rx="30" fill="{entry["brandColor"]}"/>\n'
        '  <rect x="8" y="8" width="112" height="112" rx="24" '
        'fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="2"/>\n'
        '  <g fill="none" stroke="#fff" stroke-width="6" '
        'stroke-linecap="round" stroke-linejoin="round">\n'
        f'    {entry["glyph"]}\n'
        '  </g>\n'
        '</svg>\n'
    )
    if len(svg.encode("utf-8")) > 5 * 1024 * 1024:
        raise ValueError(f"{name}: generated SVG too large")
    root = ET.fromstring(svg)
    if (root.tag != SVG_NS + "svg" or root.get("viewBox") != "0 0 128 128"
            or root.get("width") != "128" or root.get("height") != "128"):
        raise ValueError(f"{name}: invalid generated SVG dimensions")
    return svg.encode("utf-8"), entry["brandColor"], fallback
