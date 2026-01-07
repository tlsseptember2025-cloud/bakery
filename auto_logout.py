class AutoLogoutManager:
    """
    Automatically logs out user after inactivity.
    Uses Tkinter after() – safe, no threads.
    """

    def __init__(self, root, timeout_minutes, on_timeout):
        self.root = root
        self.timeout_ms = timeout_minutes * 60 * 1000
        self.on_timeout = on_timeout
        self.job = None

        self._bind_activity()
        self.reset_timer()

    def _bind_activity(self):
        events = ["<Motion>", "<Key>", "<Button>"]
        for event in events:
            self.root.bind_all(event, self.reset_timer, add="+")

    def reset_timer(self, event=None):
        if self.job:
            self.root.after_cancel(self.job)
        self.job = self.root.after(self.timeout_ms, self._timeout)

    def _timeout(self):
        self.on_timeout()

    def stop(self):
        if self.job:
            self.root.after_cancel(self.job)
            self.job = None
