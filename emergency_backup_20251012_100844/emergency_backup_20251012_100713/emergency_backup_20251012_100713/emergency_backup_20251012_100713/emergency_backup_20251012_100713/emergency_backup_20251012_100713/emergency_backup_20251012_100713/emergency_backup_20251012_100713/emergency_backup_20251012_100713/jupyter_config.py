"""
Jupyter configuration for Commercial-View
Copy to ~/.jupyter/jupyter_config.py or use --config-dir
"""

c = get_config()  # noqa

# Allow all IP addresses
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.allow_origin = '*'
c.ServerApp.disable_check_xsrf = True

# Set notebook directory to project root
c.ServerApp.notebook_dir = '/Users/jenineferderas/Commercial-View'

# Enable extensions
c.ServerApp.jpserver_extensions = {
    'jupyterlab': True
}

# Custom kernel display name
c.KernelSpecManager.display_name_template = 'Commercial-View Python {0}'

# Auto-save interval (in seconds)
c.FileContentsManager.autosave_interval = 60
