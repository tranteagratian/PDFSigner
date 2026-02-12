# PDF Signer by GTR

---

## RO - Romana

Aplicatie desktop macOS pentru semnarea digitala a documentelor PDF folosind tokeni crypto PKCS#11 (smart card-uri, tokeni USB).

### Functionalitati

- **Drag & Drop** - Trage fisierele PDF direct din Finder
- **Semnare Batch** - Semneaza mai multe PDF-uri dintr-o data
- **Orice Token PKCS#11** - Functioneaza cu CertDigital, SafeNet eToken, OpenSC si altele
- **Auto-detectare** - Gaseste automat tokenul conectat si libraria PKCS#11
- **Driver Inclus** - Include libraria CertDigital/CryptoIDE (functioneaza fara instalare suplimentara)
- **Selectare Certificat** - Alege cu ce certificat sa semnezi
- **Protectie PIN** - Introducere PIN securizata cu blocare dupa 3 incercari gresite
- **Status Live** - Monitorizare conexiune token in timp real

### Cerinte

- macOS (Apple Silicon sau Intel)
- Un token crypto compatibil PKCS#11 (smart card USB)

### Instalare

#### Varianta 1 - Download direct (recomandat)

1. Descarca **PDFSigner.dmg** din [Releases](https://github.com/tranteagratian/PDFSigner/releases/latest)
2. Deschide DMG-ul
3. Trage aplicatia in Applications (optional)
4. Conecteaza tokenul USB crypto
5. Deschide PDF Signer

#### Varianta 2 - Din sursa

```bash
git clone https://github.com/tranteagratian/PDFSigner.git
cd PDFSigner
pip3 install --user --break-system-packages -r requirements.txt
python3 -m pdf_signer.main
```

### Utilizare

1. Conecteaza tokenul crypto USB
2. Lanseaza aplicatia - detecteaza automat tokenul
3. Adauga fisiere PDF (drag & drop sau click pe "Add Files")
4. Click pe **Sign All**
5. Introdu PIN-ul cand ti se cere
6. Gata! Toate fisierele sunt semnate

### Tokeni Suportati

- **CertDigital** (CryptoIDE / Longmai mToken) - driver inclus in aplicatie
- **SafeNet eToken** - necesita middleware eToken instalat
- **OpenSC** - necesita OpenSC instalat
- **Orice token PKCS#11** - selecteaza libraria `.dylib` prin Browse

---

## EN - English

A macOS desktop application for digitally signing PDF documents using PKCS#11 crypto tokens (smart cards, USB tokens).

### Features

- **Drag & Drop** - Drag PDF files directly from Finder
- **Batch Signing** - Sign multiple PDFs at once
- **Any PKCS#11 Token** - Works with CertDigital, SafeNet eToken, OpenSC, and others
- **Auto-detect** - Automatically finds connected tokens and PKCS#11 libraries
- **Built-in Driver** - Includes CertDigital/CryptoIDE PKCS#11 library (works out of the box)
- **Certificate Selection** - Choose which certificate to sign with
- **PIN Protection** - Secure PIN entry with 3-attempt lockout protection
- **Live Status** - Real-time token connection monitoring

### Requirements

- macOS (Apple Silicon or Intel)
- A PKCS#11 compatible crypto token (USB smart card)

### Installation

#### Option 1 - Direct download (recommended)

1. Download **PDFSigner.dmg** from [Releases](https://github.com/tranteagratian/PDFSigner/releases/latest)
2. Open the DMG
3. Drag the app to Applications (optional)
4. Connect your crypto USB token
5. Open PDF Signer

#### Option 2 - From source

```bash
git clone https://github.com/tranteagratian/PDFSigner.git
cd PDFSigner
pip3 install --user --break-system-packages -r requirements.txt
python3 -m pdf_signer.main
```

### Usage

1. Connect your crypto USB token
2. Launch the app - it auto-detects the token
3. Add PDF files (drag & drop or click "Add Files")
4. Click **Sign All**
5. Enter your PIN when prompted
6. Done! All files are signed in place

### Supported Tokens

- **CertDigital** (CryptoIDE / Longmai mToken) - built-in driver included
- **SafeNet eToken** - requires eToken middleware installed
- **OpenSC** - requires OpenSC installed
- **Any PKCS#11 compatible token** - select your `.dylib` via Browse

---

## License

MIT
