from __future__ import annotations
import re
################################################################################

__all__ = ("IconMap", )

SYMBOL_MAP = {
    "CurveArrowL": "",
    "CurveArrowR": "",
    "FancyS": "",
    "HexDots": "",
    "CrossHollow": "",
    "HQ": "",
    "Collectible": "",
    "Clock": "",
    "Shield": "",
    "Asterisk": "",
    "Sprout": "",
    "DownArrow": "",
    "Hex": "",
    "NoEntry": "",
    "Links": "",
    "CrystalIcon": "",
    "Gil": "",
    "Circle": "",
    "Square": "",
    "Triangle": "",
    "Cross": "",
    "Die": "",
    "Plus": "",
    "XPointer": "",
    "OPointer": "",
    "Flower": "",
    "CircleA": "",
    "FancyX": "",
    "TrianglePointer": "",
    "LevelSyncA": "",
    "LevelSyncB": "",
    "DiamondDown": "",
    "DiamondX": ""
}

################################################################################
class IconMap:

    @staticmethod
    def parse_markdown(markdown: str) -> str:
        
        # Use regex to find all patterns in braces
        pattern = re.compile(r'\{(\w+)}')
    
        def replace_match(match):
            # Extract the shorthand from the match
            shorthand = match.group(1)
            # Return the corresponding Unicode symbol or the original shorthand if not found
            return SYMBOL_MAP.get(shorthand, match.group(0))
    
        # Substitute all matches with the corresponding Unicode symbol
        return pattern.sub(replace_match, markdown)
    
################################################################################
    