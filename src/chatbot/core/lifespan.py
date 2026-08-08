from .logging import get_logger

def lifespan():

    logger = get_logger()

    logger.info("Server starting up!\n")
    yield
    logger.info("Server shutting down!\n")