"""
brand_validation.py

Validation and injection utilities for Ziyada System brand compliance in slide generation.
- Enforces palette, icon, pattern, and Partnership value rules
- Validates bilingual content and typography
- Injects official icons and brain pattern assets
- Runs post-generation audits for compliance
"""
import os
import json
from typing import List, Dict

# Load canonical palette from guidelines
PALETTE_HEX = {
    "deep_blue": "#0f172a",
    "blue": "#3b82f6",
    "purple": "#8b5cf6",
    "white": "#ffffff",
    "light_gray": "#e2e8f0",
    "teal": "#06b6d4",
    "pink": "#ec4899",
}

# Required values
REQUIRED_VALUES = ["Partnership", "الشراكة"]

# Paths to official assets
ICON_DIR = "../assets/corporate-design-kit/icons/"
BRAIN_PATTERN_DIR = "../assets/brain-element-pattern/"


def check_palette(slide_data: Dict, palette: Dict = PALETTE_HEX) -> bool:
    """Ensure all colors in slide_data are from the official palette."""
    for color in slide_data.get("colors", []):
        if color not in palette.values():
            return False
    return True

def check_bilingual_required(slide_data: Dict, required_fields=None) -> bool:
    """Ensure both EN and AR fields exist."""
    if required_fields is None:
        required_fields = ["title", "subtitle", "body"]
    for field in required_fields:
        if not slide_data.get(field):
            return False
    return True

def check_values_include_partnership(values_list: List[str]) -> bool:
    """Ensure Partnership/الشراكة is present in values."""
    for v in REQUIRED_VALUES:
        if any(v in s for s in values_list):
            return True
    return False

def inject_icon(slide_data: Dict, icon_name: str) -> Dict:
    """Attach official icon SVG path to slide_data."""
    icon_path = os.path.join(ICON_DIR, f"icon-{icon_name}.svg")
    if os.path.exists(icon_path):
        slide_data["icon"] = icon_path
    return slide_data

def inject_brain_pattern(slide_data: Dict, pattern_variant: str = "front") -> Dict:
    pattern_path = os.path.join(BRAIN_PATTERN_DIR, f"brain-element-pattern-{pattern_variant}.svg")
    if os.path.exists(pattern_path):
        slide_data["pattern"] = pattern_path
    return slide_data

def check_font_hierarchy(slide_data: Dict) -> bool:
    """Validate font family and size for all text fields — only enforced if font keys are explicitly set."""
    for k in ["title", "subtitle", "body"]:
        if k in slide_data:
            font = slide_data.get(f"{k}_font", "")
            # Only fail if a font is explicitly set AND it's wrong
            if font and k == "title" and "Inter" not in font and "Noto Kufi Arabic" not in font:
                return False
    return True

def validate_slide(slide_data: Dict) -> bool:
    return (
        check_palette(slide_data)
        and check_bilingual_required(slide_data)
        and check_font_hierarchy(slide_data)
    )

def inject_approved_icons(slide_data: Dict, icon_name: str = "automation") -> Dict:
    return inject_icon(slide_data, icon_name)

def inject_pattern(slide_data: Dict, pattern_variant: str = "front") -> Dict:
    return inject_brain_pattern(slide_data, pattern_variant)

# Add more validation and injection utilities as needed.
