import sys
from PyQt6.QtWidgets import QApplication
from pdf_signer.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Signer")
    app.setOrganizationName("PDFSigner")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
