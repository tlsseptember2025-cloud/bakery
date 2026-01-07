class BackupScheduler:
    def __init__(self, root, interval_minutes, backup_func):
        self.root = root
        self.interval_ms = interval_minutes * 60 * 1000
        self.backup_func = backup_func
        self.job = None

        self.start()

    def start(self):
        self.stop()
        self.job = self.root.after(self.interval_ms, self.run)

    def run(self):
        self.backup_func()
        self.start()  # schedule next run

    def stop(self):
        if self.job:
            self.root.after_cancel(self.job)
            self.job = None
