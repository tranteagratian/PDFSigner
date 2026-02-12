import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QProgressBar, QFileDialog, QMessageBox, QHeaderView,
    QLineEdit, QAbstractItemView,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

from pdf_signer.core.token_manager import TokenManager
from pdf_signer.core.signer import PdfSigner
from pdf_signer.core.worker import SigningWorker
from pdf_signer.gui.pin_dialog import PinDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Signer")
        self.setMinimumSize(850, 600)
        self.setAcceptDrops(True)

        self.token_manager = TokenManager()
        self.pdf_files: list[str] = []
        self.signing_worker: SigningWorker | None = None
        self._tokens: list[dict] = []
        self._certs: list[dict] = []
        self._pin_attempts = 0

        self._build_ui()
        self._auto_detect()

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_token_status)
        self._poll_timer.start(3000)

    # ── UI Construction ──────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # ── Token panel ──
        token_panel = QVBoxLayout()
        token_panel.setSpacing(6)

        # Library row
        lib_row = QHBoxLayout()
        lib_row.addWidget(QLabel("PKCS#11 Library:"))
        self.lib_path_edit = QLineEdit()
        self.lib_path_edit.setReadOnly(True)
        self.lib_path_edit.setPlaceholderText("Auto-detecting...")
        lib_row.addWidget(self.lib_path_edit, 1)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_library)
        lib_row.addWidget(self.browse_btn)
        token_panel.addLayout(lib_row)

        # Token + Certificate row
        tc_row = QHBoxLayout()
        tc_row.addWidget(QLabel("Token:"))
        self.token_combo = QComboBox()
        self.token_combo.setMinimumWidth(200)
        self.token_combo.currentIndexChanged.connect(self._on_token_changed)
        tc_row.addWidget(self.token_combo, 1)

        tc_row.addWidget(QLabel("  Certificate:"))
        self.cert_combo = QComboBox()
        self.cert_combo.setMinimumWidth(250)
        tc_row.addWidget(self.cert_combo, 1)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh_tokens)
        tc_row.addWidget(self.refresh_btn)
        token_panel.addLayout(tc_row)

        # Status row
        status_row = QHBoxLayout()
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(12, 12)
        self._set_status_color("gray")
        status_row.addWidget(self.status_dot)
        self.status_label = QLabel("No token detected")
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        token_panel.addLayout(status_row)

        layout.addLayout(token_panel)

        # ── Separator ──
        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #ccc;")
        layout.addWidget(sep)

        # ── File table ──
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["#", "Filename", "Path", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(3, 150)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

        # ── File buttons ──
        file_btns = QHBoxLayout()
        self.add_files_btn = QPushButton("+ Add Files")
        self.add_files_btn.clicked.connect(self._add_files)
        file_btns.addWidget(self.add_files_btn)

        self.add_folder_btn = QPushButton("+ Add Folder")
        self.add_folder_btn.clicked.connect(self._add_folder)
        file_btns.addWidget(self.add_folder_btn)

        self.clear_btn = QPushButton("Clear List")
        self.clear_btn.clicked.connect(self._clear_files)
        file_btns.addWidget(self.clear_btn)

        file_btns.addStretch()
        layout.addLayout(file_btns)

        # ── Progress ──
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        # ── Action buttons ──
        action_row = QHBoxLayout()
        self.sign_btn = QPushButton("Sign All")
        self.sign_btn.setFixedHeight(40)
        self.sign_btn.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; font-size: 15px; "
            "font-weight: bold; border-radius: 6px; padding: 0 30px; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
            "QPushButton:disabled { background-color: #94a3b8; }"
        )
        self.sign_btn.clicked.connect(self._start_signing)
        action_row.addWidget(self.sign_btn, 1)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_signing)
        action_row.addWidget(self.cancel_btn)

        layout.addLayout(action_row)

    # ── Auto-detect ──────────────────────────────────────────────

    def _auto_detect(self):
        self.lib_path_edit.setPlaceholderText("Searching for PKCS#11 library...")
        try:
            path = self.token_manager.auto_detect_library()
        except Exception as e:
            path = None
        if path:
            self.lib_path_edit.setText(path)
            self._refresh_tokens()
        else:
            self.lib_path_edit.setPlaceholderText("")
            self.lib_path_edit.setText("")
            self._set_status_color("orange")
            self.status_label.setText("No PKCS#11 library found - click Browse to select .dylib")

    def _browse_library(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select PKCS#11 Library", "/usr/local/lib",
            "Libraries (*.dylib *.so);;All Files (*)"
        )
        if path:
            try:
                self.token_manager.load_library(path)
                self.lib_path_edit.setText(path)
                self._refresh_tokens()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load library:\n{e}")

    # ── Token management ─────────────────────────────────────────

    def _refresh_tokens(self):
        if not self.token_manager.lib_path:
            return
        # Reload library to refresh slot state
        try:
            self.token_manager.load_library(self.token_manager.lib_path)
        except Exception:
            pass

        self._tokens = self.token_manager.get_tokens()
        self.token_combo.clear()
        if self._tokens:
            for t in self._tokens:
                self.token_combo.addItem(f"{t['label']} ({t['serial'][:8]}...)")
            self._set_status_color("#22c55e")
            self.status_label.setText("Token connected")
        else:
            self._set_status_color("red")
            self.status_label.setText("No token detected")
            self.cert_combo.clear()

    def _on_token_changed(self, index):
        self.cert_combo.clear()
        self._certs = []
        # Certs will be loaded after PIN entry during signing

    def _poll_token_status(self):
        if not self.token_manager.lib_path:
            return
        try:
            self.token_manager.load_library(self.token_manager.lib_path)
            tokens = self.token_manager.get_tokens()
            if tokens:
                self._set_status_color("#22c55e")
                self.status_label.setText("Token connected")
                if not self._tokens:
                    self._tokens = tokens
                    self.token_combo.clear()
                    for t in tokens:
                        self.token_combo.addItem(f"{t['label']} ({t['serial'][:8]}...)")
            else:
                self._set_status_color("red")
                self.status_label.setText("No token detected")
                self._tokens = []
        except Exception:
            self._set_status_color("orange")
            self.status_label.setText("Error reading token")

    def _set_status_color(self, color: str):
        self.status_dot.setStyleSheet(
            f"background-color: {color}; border-radius: 6px; min-width: 12px; min-height: 12px;"
        )

    # ── File management ──────────────────────────────────────────

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", str(Path.home() / "Desktop"),
            "PDF Files (*.pdf);;All Files (*)"
        )
        for f in files:
            self._add_pdf(f)

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder", str(Path.home() / "Desktop")
        )
        if folder:
            for root, _, files in os.walk(folder):
                for fname in sorted(files):
                    if fname.lower().endswith(".pdf"):
                        self._add_pdf(os.path.join(root, fname))

    def _add_pdf(self, path: str):
        if path in self.pdf_files:
            return
        self.pdf_files.append(path)
        row = self.table.rowCount()
        self.table.insertRow(row)
        p = Path(path)
        self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.table.setItem(row, 1, QTableWidgetItem(p.name))
        self.table.setItem(row, 2, QTableWidgetItem(str(p.parent)))
        status_item = QTableWidgetItem("Pending")
        status_item.setForeground(QColor("#64748b"))
        self.table.setItem(row, 3, status_item)

    def _clear_files(self):
        self.pdf_files.clear()
        self.table.setRowCount(0)

    # ── Drag and drop ────────────────────────────────────────────

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".pdf"):
                    event.acceptProposedAction()
                    return

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".pdf"):
                self._add_pdf(path)
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for fname in sorted(files):
                        if fname.lower().endswith(".pdf"):
                            self._add_pdf(os.path.join(root, fname))

    # ── Signing ──────────────────────────────────────────────────

    def _start_signing(self):
        if not self.pdf_files:
            QMessageBox.warning(self, "No Files", "Add PDF files first.")
            return

        if not self._tokens:
            QMessageBox.warning(self, "No Token", "No crypto token detected.\nConnect your token and click Refresh.")
            return

        token_idx = self.token_combo.currentIndex()
        if token_idx < 0:
            return
        token_info = self._tokens[token_idx]

        # Ask for PIN
        self._pin_attempts = 0
        pin = self._ask_pin(token_info["label"])
        if pin is None:
            return

        # Open session and list certs
        try:
            self.token_manager.open_session(token_info["slot_index"], pin)
        except Exception as e:
            QMessageBox.critical(self, "PIN Error", f"Failed to open session:\n{e}")
            return

        certs = self.token_manager.list_certificates()
        if not certs:
            QMessageBox.critical(self, "No Certificates", "No signing certificates found on this token.")
            self.token_manager.close()
            return

        # Select certificate
        self.cert_combo.clear()
        self._certs = certs
        for c in certs:
            display = c["subject"] if c["subject"] else c["label"]
            self.cert_combo.addItem(display)

        cert_idx = 0
        if len(certs) > 1:
            # Use first cert by default, user can change in combo
            pass
        cert_info = certs[cert_idx]

        # Reset statuses
        for row in range(self.table.rowCount()):
            status_item = QTableWidgetItem("Pending")
            status_item.setForeground(QColor("#64748b"))
            self.table.setItem(row, 3, status_item)

        # Start signing
        signer = PdfSigner(self.token_manager.session, cert_info)
        self.signing_worker = SigningWorker(signer, list(self.pdf_files))
        self.signing_worker.progress.connect(self._on_progress)
        self.signing_worker.file_done.connect(self._on_file_done)
        self.signing_worker.all_done.connect(self._on_all_done)

        self._set_signing_ui(True)
        self.progress_bar.setMaximum(len(self.pdf_files))
        self.progress_bar.setValue(0)
        self.signing_worker.start()

    def _ask_pin(self, token_label: str) -> str | None:
        while self._pin_attempts < 3:
            dialog = PinDialog(token_label, self)
            pin = dialog.get_pin()
            if pin is None:
                return None
            # Validate PIN by trying to open session
            try:
                self.token_manager.open_session(
                    self._tokens[self.token_combo.currentIndex()]["slot_index"], pin
                )
                self.token_manager.close()
                self._pin_attempts = 0
                return pin
            except Exception:
                self._pin_attempts += 1
                remaining = 3 - self._pin_attempts
                if remaining > 0:
                    QMessageBox.warning(
                        self, "Wrong PIN",
                        f"Invalid PIN. {remaining} attempt(s) remaining."
                    )
                else:
                    QMessageBox.critical(
                        self, "PIN Blocked",
                        "Too many wrong PIN attempts.\nToken may be locked."
                    )
                    return None
        return None

    def _cancel_signing(self):
        if self.signing_worker:
            self.signing_worker.cancel()

    def _set_signing_ui(self, signing: bool):
        self.sign_btn.setEnabled(not signing)
        self.cancel_btn.setEnabled(signing)
        self.add_files_btn.setEnabled(not signing)
        self.add_folder_btn.setEnabled(not signing)
        self.clear_btn.setEnabled(not signing)
        self.refresh_btn.setEnabled(not signing)
        self.progress_bar.setVisible(signing)
        self.progress_label.setVisible(signing)

    # ── Worker signals ───────────────────────────────────────────

    def _on_progress(self, current: int, total: int):
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"Signing {current + 1} / {total}...")
        # Mark current file as signing
        if current < self.table.rowCount():
            item = QTableWidgetItem("Signing...")
            item.setForeground(QColor("#2563eb"))
            self.table.setItem(current, 3, item)

    def _on_file_done(self, index: int, filepath: str, success: bool, message: str):
        if index < self.table.rowCount():
            if success:
                item = QTableWidgetItem("Signed")
                item.setForeground(QColor("#16a34a"))
            else:
                item = QTableWidgetItem(f"Failed")
                item.setForeground(QColor("#dc2626"))
                item.setToolTip(message)
            self.table.setItem(index, 3, item)
        self.progress_bar.setValue(index + 1)

    def _on_all_done(self, success_count: int, fail_count: int):
        self._set_signing_ui(False)
        self.token_manager.close()
        self.progress_label.setText(
            f"Done: {success_count} signed, {fail_count} failed"
        )
        self.progress_label.setVisible(True)

        if fail_count == 0:
            QMessageBox.information(
                self, "Success",
                f"All {success_count} documents signed successfully!"
            )
        else:
            QMessageBox.warning(
                self, "Completed with errors",
                f"Signed: {success_count}\nFailed: {fail_count}\n\n"
                "Hover over 'Failed' status for error details."
            )
