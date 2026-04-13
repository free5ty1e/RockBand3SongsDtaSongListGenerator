#!/usr/bin/env python3
"""
ANSI Console Styling Module

Provides color codes, emoji icons, progress bars, spinners, and styled output helpers for console scripts.

Usage:
    from console_styling import style, icon, log, progress_bar, spinner, COLORS, ICONS
    
    # Simple styled output
    print(style("Processing...", color='cyan', bold=True))
    
    # With icon
    print(f"{icon('check')} Done!")
    
    # Progress bar
    print(progress_bar(75, 100, length=20))
    
    # Spinner (use in a loop with update())
    spin = spinner("Loading")
    for i in range(10):
        spin.update()  # advances to next frame
"""

import sys
import time
import threading

# ANSI codes
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'
ITALIC = '\033[3m'
UNDERLINE = '\033[4m'
BOLD = '\033[1m'

# ANSI control sequences
SAVE_CURSOR = '\033[s'
RESTORE_CURSOR = '\033[u'
CLEAR_LINE = '\033[2K'
HIDE_CURSOR = '\033[?25l'
SHOW_CURSOR = '\033[?25h'

# Color codes
COLORS = {
    'red': '\033[91m',
    'green': '\033[92m', 
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'gray': '\033[90m',
    'pink': '\033[95m',
    'orange': '\033[38;5;208m',
}

# Emoji icons
ICONS = {
    'folder': '📁',
    'package': '📦',
    'music': '🎵',
    'check': '✓',
    'cross': '✗',
    'arrow': '→',
    'gear': '⚙️',
    'chart': '📊',
    'warning': '⚠️',
    'sparkles': '✨',
    'cd': '💿',
    'floppy': '💾',
    'trophy': '🏆',
    'mag': '🔍',
    'star': '⭐',
    'fire': '🔥',
    'eyes': '👀',
    'wrench': '🔧',
    'hammer': '🔨',
    'mic': '🎤',
    'guitar': '🎸',
    'drum': '🥁',
    'key': '🎹',
    'memo': '📝',
    'clip': '📋',
    'clock': '⏰',
    'hour': '🕐',
    'rocket': '🚀',
    'hourglass': '⏳',
    'dots': '⋮',
}

def icon(name, fallback='•'):
    """Get icon by name, fallback to dot if not found."""
    return ICONS.get(name, fallback)

def color(name):
    """Get color code by name."""
    return COLORS.get(name, '')

def style(msg, color_name=None, bold=False, italic=False, underline=False):
    """Apply color/style to a message."""
    codes = []
    if bold: codes.append(BOLD)
    if italic: codes.append(ITALIC)
    if underline: codes.append(UNDERLINE)
    if color_name: codes.append(COLORS.get(color_name, ''))
    return ''.join(codes) + msg + RESET

def log(msg, file=None, color_name=None, bold=False):
    """Log to console and optional file with styling."""
    styled = msg
    if color_name:
        styled = style(msg, color_name=color_name, bold=bold)
    print(styled)
    if file:
        with open(file, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')

# Convenience functions for common styled outputs
def success(msg): return style(f"✓ {msg}", color_name='green', bold=True)
def error(msg): return style(f"✗ {msg}", color_name='red', bold=True)
def warning(msg): return style(f"⚠️ {msg}", color_name='yellow')
def info(msg): return style(msg, color='cyan')
def progress(msg): return style(msg, color='blue')
def highlight(msg): return style(msg, color='magenta', bold=True)

# ── Progress Bar ─────────────────────────────────────────────────────────────
def progress_bar(current, total, length=30, color='cyan', show_percent=True):
    """Generate a progress bar string.
    
    Args:
        current: Current value (0 to total)
        total: Maximum value
        length: Character length of bar
        color: Color name
        show_percent: Show percentage
    
    Returns:
        Styled progress bar string
    """
    if total <= 0:
        pct = 0
    else:
        pct = min(100, max(0, int(current / total * 100)))
    
    filled = int(length * current / total) if total > 0 else 0
    bar_len = length
    
    # Build bar with gradient feel
    filled_char = '█'
    empty_char = '░'
    
    bar = filled_char * filled + empty_char * (bar_len - filled)
    c = COLORS.get(color, '')
    
    result = f"{c}[{bar}]{RESET}"
    if show_percent:
        result += f" {pct}%"
    result += f" ({current:,}/{total:,})"
    
    return result

# ── Spinner Class ─────────────────────────────────────────────────────────────
class Spinner:
    """Animated spinner for activity indication."""
    
    FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, message="", color='cyan'):
        self.message = message
        self.color = color
        self.frame = 0
        self.running = False
        
    def update(self, message=None):
        """Show next frame."""
        c = COLORS.get(self.color, '')
        frame = self.FRAMES[self.frame % len(self.FRAMES)]
        msg = message or self.message
        
        # Save cursor, print, restore
        sys.stdout.write(f"{SAVE_CURSOR}{CLEAR_LINE}{c}{frame} {msg}{RESET}{RESTORE_CURSOR}")
        sys.stdout.flush()
        
        self.frame += 1
        
    def stop(self, final_message=None):
        """Stop animation, optionally show final message."""
        c = COLORS.get('green', '')
        sys.stdout.write(f"{SAVE_CURSOR}{CLEAR_LINE}")
        if final_message:
            sys.stdout.write(f"{c}{final_message}{RESET}")
        sys.stdout.write(f"{RESTORE_CURSOR}")
        sys.stdout.flush()
        print()  # newline after spinner