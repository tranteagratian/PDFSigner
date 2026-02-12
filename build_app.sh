#!/bin/bash
# Build PDF Signer as macOS .app bundle
set -e

echo "Installing build dependencies..."
pip3 install --user --break-system-packages pyinstaller

echo "Building PDF Signer.app..."
cd "$(dirname "$0")"

python3 -m PyInstaller \
    --name "PDF Signer" \
    --windowed \
    --osx-bundle-identifier com.pdfsigner.app \
    --hidden-import pkcs11 \
    --hidden-import pyhanko \
    --hidden-import pyhanko.sign.pkcs11 \
    --hidden-import asn1crypto \
    --hidden-import pyhanko.sign.signers \
    --hidden-import pyhanko.pdf_utils.incremental_writer \
    --add-data "pdf_signer:pdf_signer" \
    --add-binary "pdf_signer/drivers/libcryptoide_pkcs11.dylib:pdf_signer/drivers" \
    pdf_signer/main.py

echo ""
echo "Build complete!"
echo "App location: dist/PDF Signer.app"
