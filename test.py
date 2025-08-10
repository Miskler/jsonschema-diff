import os
from rich.console import Console
c = Console()
print("TERM=", os.getenv("TERM"))
print("COLORTERM=", os.getenv("COLORTERM"))
print("rich color_system =", c.color_system)  # None|standard|256|truecolor|windows
