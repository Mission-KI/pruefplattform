import os


class CwdContextManager:
    """A context manager for more safer use of subprocess(.., cwd=..)
    Ensures the original cwd is recovered
    """

    def __init__(self, logger=None):
        self.logger = logger
        self.cwd = None

    def __enter__(self):
        self.cwd = os.path.realpath(os.getcwd())

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            cur_cwd = os.path.realpath(os.getcwd())
            if cur_cwd != self.cwd:
                os.chdir(self.cwd)
                if self.logger is not None:
                    self.logger.debug(f"Switched cwd back to {self.cwd}")
        except Exception:
            os.chdir(self.cwd)
            if self.logger is not None:
                self.logger.debug(f"Switched cwd back to {self.cwd}")
