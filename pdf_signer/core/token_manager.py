import os
import sys

import pkcs11
from pkcs11 import Attribute, ObjectClass


def _get_bundled_lib_paths() -> list[str]:
    """Return possible paths to the PKCS#11 library bundled with the app."""
    paths = []
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle - try multiple possible locations
        base = sys._MEIPASS
        paths.append(os.path.join(base, "pdf_signer", "drivers", "libcryptoide_pkcs11.dylib"))
        paths.append(os.path.join(base, "drivers", "libcryptoide_pkcs11.dylib"))
        paths.append(os.path.join(base, "libcryptoide_pkcs11.dylib"))
        # Also check next to the executable
        exe_dir = os.path.dirname(sys.executable)
        paths.append(os.path.join(exe_dir, "pdf_signer", "drivers", "libcryptoide_pkcs11.dylib"))
        paths.append(os.path.join(exe_dir, "drivers", "libcryptoide_pkcs11.dylib"))
        paths.append(os.path.join(exe_dir, "libcryptoide_pkcs11.dylib"))
        # macOS .app bundle: check inside Resources
        resources_dir = os.path.join(exe_dir, "..", "Resources")
        paths.append(os.path.join(resources_dir, "pdf_signer", "drivers", "libcryptoide_pkcs11.dylib"))
        paths.append(os.path.join(resources_dir, "drivers", "libcryptoide_pkcs11.dylib"))
    else:
        # Running from source
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        paths.append(os.path.join(base, "pdf_signer", "drivers", "libcryptoide_pkcs11.dylib"))
    return paths


class TokenManager:
    """Manages PKCS#11 library loading, token detection, and certificate enumeration."""

    SYSTEM_LIB_PATHS = [
        "/Applications/CryptoUserTools.app/Contents/lib/mac/libcryptoide_pkcs11.dylib",
        "/opt/CryptoIDE/lib/libcryptoide_pkcs11.dylib",
        "/usr/local/lib/libeTPkcs11.dylib",
        "/usr/local/lib/opensc-pkcs11.so",
        "/Library/OpenSC/lib/opensc-pkcs11.so",
    ]

    def __init__(self):
        self._lib = None
        self._lib_path = None
        self._session = None

    @property
    def session(self):
        return self._session

    @property
    def lib_path(self):
        return self._lib_path

    def load_library(self, path: str) -> None:
        self._lib = pkcs11.lib(path)
        self._lib_path = path

    def auto_detect_library(self) -> str | None:
        all_paths = _get_bundled_lib_paths() + self.SYSTEM_LIB_PATHS
        for path in all_paths:
            if os.path.exists(path):
                try:
                    self.load_library(path)
                    return path
                except Exception:
                    continue
        return None

    def get_tokens(self) -> list[dict]:
        if not self._lib:
            return []
        tokens = []
        for i, slot in enumerate(self._lib.get_slots()):
            try:
                token = slot.get_token()
                tokens.append({
                    "slot_index": i,
                    "label": token.label.strip() if token.label else f"Token {i}",
                    "serial": token.serial.hex() if token.serial else "",
                })
            except Exception:
                continue
        return tokens

    def open_session(self, slot_index: int, pin: str) -> None:
        token = self._lib.get_slots()[slot_index].get_token()
        self._session = token.open(user_pin=pin)

    def list_certificates(self) -> list[dict]:
        if not self._session:
            return []
        certs = []
        cert_objects = list(self._session.get_objects({Attribute.CLASS: ObjectClass.CERTIFICATE}))
        for obj in cert_objects:
            try:
                label = obj[Attribute.LABEL]
                cert_id = obj[Attribute.ID]
                subject_str = label
                try:
                    from asn1crypto import x509
                    cert_der = obj[Attribute.VALUE]
                    cert = x509.Certificate.load(cert_der)
                    subject_str = cert.subject.human_friendly
                    issuer_str = cert.issuer.human_friendly
                    not_after = str(cert["tbs_certificate"]["validity"]["not_after"].native)
                except Exception:
                    issuer_str = ""
                    not_after = ""

                certs.append({
                    "label": label,
                    "id": cert_id,
                    "subject": subject_str,
                    "issuer": issuer_str,
                    "not_after": not_after,
                })
            except Exception:
                continue
        return certs

    def close(self):
        if self._session:
            try:
                self._session.close()
            except Exception:
                pass
            self._session = None
