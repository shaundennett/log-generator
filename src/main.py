import logger.log_generator as logger
import os


def main():
    """configures and starts log-generator"""

    try:
        os.environ["MESSAGE_DEFINITIONS"]
    except KeyError:
        os.environ["MESSAGE_DEFINITIONS"] = "default"
    thread1 = logger.LogDriver(1, "Thread-1")
    thread1.start()


if __name__ == '__main__':
    main()
