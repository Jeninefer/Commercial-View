import logging

# Configure logger
logger = logging.getLogger(__name__)

def load_module():
    """Load the Feature Engineering module"""
    logger.info("Módulo 3: Ingeniería de Características cargado correctamente")
    # Additional module initialization code would go here
    pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_module()
