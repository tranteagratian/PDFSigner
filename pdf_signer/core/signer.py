from io import BytesIO
from pathlib import Path

from pyhanko.sign import signers
from pyhanko.sign.pkcs11 import PKCS11Signer
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter


class PdfSigner:
    """Signs PDFs using a PKCS#11 session."""

    def __init__(self, session, cert_info: dict):
        self._session = session
        self._cert_id = cert_info["id"]
        self._cert_label = cert_info["label"]

    def sign_pdf(self, pdf_path: str) -> None:
        signer = PKCS11Signer(
            self._session,
            cert_id=self._cert_id,
            key_id=self._cert_id,
        )

        path = Path(pdf_path)
        pdf_bytes = path.read_bytes()
        tmp_path = path.with_suffix(".pdf.tmp")

        try:
            w = IncrementalPdfFileWriter(BytesIO(pdf_bytes))
            meta = signers.PdfSignatureMetadata(
                field_name="Signature1",
                reason="Semnare document",
                location="Romania",
            )
            result = signers.sign_pdf(w, meta, signer=signer)
            tmp_path.write_bytes(result.getbuffer())
            tmp_path.replace(path)
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()
            raise
