import logging


class PRESETLIBLogger:
    def __init__(self, name="PRESETLIB", level=logging.INFO):
        # Initialize the logger
        self.logger = logging.getLogger(name)

        # If the logger is already configured, return to avoid duplicate setup
        if not self.logger.handlers:
            # Set logging level
            self.logger.setLevel(level)

            # Create a console log handler
            ch = logging.StreamHandler()
            ch.setLevel(level)

            # Set logging format
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)

            # Add console handler to the logger
            self.logger.addHandler(ch)

    def get_logger(self):
        return self.logger


# Usage example
"""
logger = PRESETLIBLogger().get_logger()
logger.info("This is an info message from PRESETLIB logger.")
logger.error("This is an error message from PRESETLIB logger.")
"""