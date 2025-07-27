"""
Formatter for JSON Schema comparison output.

This module provides functionality to format differences between JSON schemas
into human-readable output with optional colored formatting.
"""

from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
import json
from .config import Config
from .path_utils import PathUtils
from .diff_finder import DiffFinder

# Optional click import for colored output
try:
    import click
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False
    click = None

if TYPE_CHECKING:
    from .render_processor import DiffGroup, DiffLine


class Formatter:
    """Class for formatting schema comparison output."""
    
    # Class variable to control whether warning was shown
    _warning_shown = False
    
    # Class variable to control colored output at formatter level
    _use_colors = True
    
    @classmethod
    def _show_click_warning(cls) -> None:
        """Show warning about Click not being available (only once)."""
        if not cls._warning_shown:
            import warnings
            warnings.warn(
                "Colored output is enabled but Click library is not installed. "
                "Install Click for colored output or set Config.USE_COLORS = False to disable this warning.",
                UserWarning,
                stacklevel=3
            )
            cls._warning_shown = True
    
    @classmethod
    def set_use_colors(cls, use_colors: bool) -> None:
        """
        Enable or disable colored output.
        
        Args:
            use_colors (bool): Whether to use colored output.
        """
        cls._use_colors = use_colors
    
    @classmethod
    def format_output(cls, text: str, mode: str = "no_diff") -> str:
        """
        Format output text with optional Click styling.
        
        Args:
            text (str): The text to format.
            mode (str): The formatting mode ('append', 'remove', 'replace', 'no_diff').
            
        Returns:
            str: Formatted text with color and symbol (if colors enabled).
        """
        display_mode = Config.get_display_mode(mode)
        formatted_text = f'{display_mode.symbol} {text}'
        
        # Check configuration setting
        should_use_colors = Config.get_use_colors() and cls._use_colors
        
        if should_use_colors:
            if CLICK_AVAILABLE and click is not None:
                return click.style(formatted_text, fg=display_mode.color, bold=True)
            else:
                # Show warning if colors are requested but Click is not available
                cls._show_click_warning()
                return formatted_text
        else:
            return formatted_text
    
    @staticmethod
    def format_list_diff(
        path: str, old_list: Optional[List[Any]], new_list: Optional[List[Any]]
    ) -> List[str]:
        """
        Format diff for lists: complete list with +/- markers.
        
        Args:
            path (str): The path to the list.
            old_list (Optional[List[Any]]): The old list (None if added).
            new_list (Optional[List[Any]]): The new list (None if removed).
            
        Returns:
            List[str]: Formatted list difference lines.
        """
        target_mode = "no_diff"

        if old_list is None:
            target_mode = "append"
            old_list = []
        elif new_list is None:
            target_mode = "remove"
            new_list = []

        result: List[str] = [Formatter.format_output(f"{path}:", target_mode)]

        # Collect all unique elements without hashing
        unique_items: List[Any] = []
        # Now old_list and new_list are guaranteed to be lists, not None
        for item in (new_list or []) + (old_list or []):
            if not any(item == existing for existing in unique_items):
                unique_items.append(item)

        have_changes = False
        for item in unique_items:
            item_str = json.dumps(item, ensure_ascii=False)
            in_old = any(item == old for old in (old_list or []))
            in_new = any(item == new for new in (new_list or []))

            if in_old and not in_new:
                result.append(Formatter.format_output(f"  {item_str},", "remove"))
                have_changes = True
            elif not in_old and in_new:
                result.append(Formatter.format_output(f"  {item_str},", "append"))
                have_changes = True
            else:
                result.append(Formatter.format_output(f"  {item_str},", "no_diff"))

        if not have_changes:
            return []

        # Remove trailing comma from last element
        head, sep, tail = result[-1].rpartition(',')
        result[-1] = head + tail

        return result
    
    @staticmethod
    def format_differences(
        differences: List[Tuple[List[str], Any, Any]]
    ) -> str:
        """
        DEPRECATED: Use format_groups instead.
        This method is kept for backward compatibility only.
        """
        # Convert old format to new format and delegate
        from .render_processor import DiffLine, DiffGroup
        
        groups = []
        for path, old_val, new_val in differences:
            main_line = DiffLine(path, old_val, new_val, "main")
            group = DiffGroup(main_line, [])
            groups.append(group)
        
        return Formatter.format_groups(groups)
    
    @staticmethod
    def format_groups(groups: List['DiffGroup']) -> str:
        """
        Format groups of differences with proper spacing and metadata.
        
        Args:
            groups: List of DiffGroup objects containing main lines and context
            
        Returns:
            str: Formatted differences string
        """
        from .render_processor import DiffGroup, DiffLine  # Import here to avoid circular import
        
        output: List[str] = []
        
        for i, group in enumerate(groups):
            # Format main line
            main_line = group.main_line
            formatted_main = Formatter._format_single_line(main_line)
            output.append(formatted_main)
            
            # Format context lines immediately after (no empty line)
            for context_line in group.context_lines:
                formatted_context = Formatter._format_single_line(context_line)
                output.append(formatted_context)
            
            # Add empty line between groups (but not after the last group)
            if i < len(groups) - 1:
                output.append("")
        
        return "\n".join(output)
    
    @staticmethod
    def _format_single_line(line: 'DiffLine') -> str:
        """
        Format a single DiffLine into a string.
        
        Args:
            line: DiffLine object to format
            
        Returns:
            str: Formatted line string
        """
        from .render_processor import DiffLine  # Import here to avoid circular import
        
        p = PathUtils.format_path(line.path)
        old_val, new_val = line.old_value, line.new_value
        
        # Handle different types of lines
        if line.line_type == "context":
            # Context lines are always no-diff (old == new)
            return Formatter.format_output(
                f"{p}: {json.dumps(old_val, ensure_ascii=False)}", "no_diff"
            )
        else:
            # Main line - could be add, remove, or change
            if old_val is None:
                return Formatter.format_output(
                    f"{p}: {json.dumps(new_val, ensure_ascii=False)}", "append"
                )
            elif new_val is None:
                return Formatter.format_output(
                    f"{p}: {json.dumps(old_val, ensure_ascii=False)}", "remove"
                )
            else:
                return Formatter.format_output(
                    f"{p}: {json.dumps(old_val)} -> {json.dumps(new_val)}", "replace"
                )
