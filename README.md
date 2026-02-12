# PDF Signer

A macOS desktop application for digitally signing PDF documents using PKCS#11 crypto tokens (smart cards, USB tokens).

## Features

- **Drag & Drop** - Drag PDF files directly from Finder
- **Batch Signing** - Sign multiple PDFs at once
- **Any PKCS#11 Token** - Works with CertDigital, SafeNet eToken, OpenSC, and others
- **Auto-detect** - Automatically finds connected tokens and PKCS#11 libraries
- **Built-in Driver** - Includes CertDigital/CryptoIDE PKCS#11 library (works out of the box)
- **Certificate Selection** - Choose which certificate to sign with
- **PIN Protection** - Secure PIN entry with 3-attempt lockout protection
- **Live Status** - Real-time token connection monitoring

## Screenshot

```
+------------------------------------------------------------------+
| PDF Signer                                                        |
+------------------------------------------------------------------+
| Library: [/opt/CryptoIDE/lib/...dylib]  [Browse]                 |
| Token: [CertDigital CRYPTO ▼]  Certificate: [CN=... ▼] [Refresh]|
| Status: ● Connected                                              |
+------------------------------------------------------------------+
| #  | Filename           | Path              | Status              |
|----|--------------------|--------------------|---------------------|
| 1  | contract.pdf       | ~/Desktop/...     | Signed              |
| 2  | invoice.pdf        | ~/Documents/...   | Signed              |
+------------------------------------------------------------------+
| [+ Add Files]  [+ Add Folder]  [Clear List]                     |
| [===================>        ] 5 / 12 files                      |
| [      Sign All      ]                         [     Cancel     ]|
+------------------------------------------------------------------+
```

## Requirements

- macOS (Apple Silicon or Intel)
- Python 3.10+
- A PKCS#11 compatible crypto token (USB smart card)

## Installation

### From source

```bash
git clone https://github.com/tranteagratian/PDFSigner.git
cd PDFSigner
pip3 install --user --break-system-packages -r requirements.txt
python3 -m pdf_signer.main
```

### Build as macOS .app

```bash
./build_app.sh
# The app will be at: dist/PDF Signer.app
```

## Usage

1. Connect your crypto USB token
2. Launch the app - it auto-detects the token
3. Add PDF files (drag & drop or click "Add Files")
4. Click **Sign All**
5. Enter your PIN when prompted
6. Done! All files are signed in place

## Supported Tokens

- **CertDigital** (CryptoIDE / Longmai mToken) - built-in driver included
- **SafeNet eToken** - requires eToken middleware installed
- **OpenSC** - requires OpenSC installed
- **Any PKCS#11 compatible token** - select your `.dylib` via Browse

## License

MIT
