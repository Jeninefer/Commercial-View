"""
IPython configuration for Commercial-View development
Place this in ~/.ipython/profile_default/ or use with --profile-dir
"""

c = get_config()  # noqa

# Enable autoreload by default
c.InteractiveShellApp.exec_lines = [
    '%load_ext autoreload',
    '%autoreload 2',
    'import pandas as pd',
    'import numpy as np',
    'from pathlib import Path',
    'print("🔄 Auto-reload enabled for Commercial-View development")'
]

# Set colors for better readability
c.TerminalIPythonApp.colors = 'Linux'

# Enable matplotlib inline plotting
c.InteractiveShellApp.matplotlib = 'inline'

# Custom prompts
c.PromptManager.in_template = 'CV[{count}]: '
c.PromptManager.out_template = 'CV[{count}]: '

# History configuration
c.HistoryManager.hist_file = ':memory:'  # Don't save history to disk
