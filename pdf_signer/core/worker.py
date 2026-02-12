from PyQt6.QtCore import QThread, pyqtSignal


class SigningWorker(QThread):
    """Performs batch PDF signing on a background thread."""

    progress = pyqtSignal(int, int)                # (current_index, total)
    file_done = pyqtSignal(int, str, bool, str)    # (index, filepath, success, message)
    all_done = pyqtSignal(int, int)                # (success_count, fail_count)

    def __init__(self, pdf_signer, file_paths: list[str]):
        super().__init__()
        self._signer = pdf_signer
        self._files = file_paths
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        total = len(self._files)
        success = 0
        fail = 0
        for i, path in enumerate(self._files):
            if self._cancelled:
                break
            self.progress.emit(i, total)
            try:
                self._signer.sign_pdf(path)
                self.file_done.emit(i, path, True, "Semnat cu succes")
                success += 1
            except Exception as e:
                self.file_done.emit(i, path, False, str(e))
                fail += 1
        self.all_done.emit(success, fail)
