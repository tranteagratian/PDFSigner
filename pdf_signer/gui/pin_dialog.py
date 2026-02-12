from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox,
)
from PyQt6.QtCore import Qt


class PinDialog(QDialog):
    def __init__(self, token_label: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Introduceti PIN-ul")
        self.setModal(True)
        self.setFixedSize(380, 160)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        token_lbl = QLabel(f"Token: <b>{token_label}</b>")
        layout.addWidget(token_lbl)

        layout.addWidget(QLabel("PIN:"))
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setPlaceholderText("Introduceti PIN-ul tokenului")
        self.pin_input.returnPressed.connect(self.accept)
        layout.addWidget(self.pin_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_pin(self) -> str | None:
        if self.exec() == QDialog.DialogCode.Accepted:
            pin = self.pin_input.text().strip()
            if pin:
                return pin
        return None
