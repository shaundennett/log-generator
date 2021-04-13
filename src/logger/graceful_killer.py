import signal


class GracefulKiller:
    """this class implements a way of detecting whether a termination signal
    has been sent by the host so that a graceful shutdown can occur.

    Attributes
    ----------
    kill_now : bool
        a bool representing whether a termination signal has been sent by the
        host

    Methods
    -------
    exit_gracefully(signum, frame)
        sets kill_now to true when a termination signal is detected
    """

    kill_now = False

    def __init__(self):
        """creates triggers to gracefully shutdown log-generator when a
        termination signal is detected.
        """

        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        """sets kill_now to true when a termination signal is detected."""

        self.kill_now = True
