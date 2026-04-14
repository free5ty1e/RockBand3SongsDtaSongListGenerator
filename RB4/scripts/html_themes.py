#!/usr/bin/env python3
"""
HTML Themes for Rock Band 4 Song List
Each theme is a tuple of (name, CSS styles)
"""

# Theme: Dark Blue (default)
DARK_BLUE = {
    "name": "Dark Blue",
    "body_bg": "#1a1a2e",
    "panel_bg": "#16213e", 
    "text": "#eee",
    "accent": "#00d4ff",
    "header_bg": "#0f3460",
    "hover": "#2a2a4e",
    "input_bg": "#0f0f23",
}

# Theme: Matrix Green
MATRIX = {
    "name": "Matrix",
    "body_bg": "#0a0a0a",
    "panel_bg": "#0d1117",
    "text": "#00ff41",
    "accent": "#00ff00",
    "header_bg": "#003300",
    "hover": "#1a3a1a",
    "input_bg": "#0a0a0a",
}

# Theme: Cyberpunk
CYBERPUNK = {
    "name": "Cyberpunk",
    "body_bg": "#0d0d0d",
    "panel_bg": "#1a1a2e",
    "text": "#ff00ff",
    "accent": "#00ffff",
    "header_bg": "#2d004d",
    "hover": "#3d1a4d",
    "input_bg": "#1a1a2e",
}

# Theme: Sunset Orange
SUNSET = {
    "name": "Sunset",
    "body_bg": "#1a1410",
    "panel_bg": "#2a1f1a",
    "text": "#ffcc99",
    "accent": "#ff6633",
    "header_bg": "#4a2a1a",
    "hover": "#3a2a1a",
    "input_bg": "#1a1410",
}

# Theme: Forest
FOREST = {
    "name": "Forest",
    "body_bg": "#0a1a0a",
    "panel_bg": "#0d2a0d",
    "text": "#aaffaa",
    "accent": "#00ff00",
    "header_bg": "#003300",
    "hover": "#1a3a1a",
    "input_bg": "#0a1a0a",
}

# Theme: Rose
ROSE = {
    "name": "Rose",
    "body_bg": "#1a0a10",
    "panel_bg": "#2a0a1a",
    "text": "#ffaacc",
    "accent": "#ff3366",
    "header_bg": "#4a002a",
    "hover": "#3a1a2a",
    "input_bg": "#1a0a10",
}

# Theme: Monochrome
MONO = {
    "name": "Monochrome",
    "body_bg": "#111111",
    "panel_bg": "#222222",
    "text": "#dddddd",
    "accent": "#ffffff",
    "header_bg": "#333333",
    "hover": "#444444",
    "input_bg": "#111111",
}


THEMES = {
    "dark_blue": DARK_BLUE,
    "matrix": MATRIX,
    "cyberpunk": CYBERPUNK,
    "sunset": SUNSET,
    "forest": FOREST,
    "rose": ROSE,
    "mono": MONO,
}


def generate_theme_js():
    """Generate JavaScript for theme switching."""
    themes_js = "const THEMES = {\n"
    for key, theme in THEMES.items():
        themes_js += f'''    "{key}": {{
        name: "{theme['name']}",
        body_bg: "{theme['body_bg']}",
        panel_bg: "{theme['panel_bg']}",
        text: "{theme['text']}",
        accent: "{theme['accent']}",
        header_bg: "{theme['header_bg']}",
        hover: "{theme['hover']}",
        input_bg: "{theme['input_bg']}",
    }},\n'''
    themes_js += "};"
    return themes_js
