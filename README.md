# 👑 Contact Manager Pro — Enterprise CRM & Network Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%203%20%7C%20SQLAlchemy%202.0-orange.svg)](https://www.sqlalchemy.org/)
[![UI Theme](https://img.shields.io/badge/Theme-Royal%20Enterprise%20Palette-gold.svg)]()
[![Tests](https://img.shields.io/badge/Tests-26%20Passed%20(100%25)-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Contact Manager Pro** is a production-grade desktop contact management and CRM platform built with **Python, Object-Oriented Architecture, SQLite & SQLAlchemy, ttk/ttkbootstrap, Pandas, and Matplotlib**. 

Designed with an **executive Qlik/PowerBI aesthetic**, it delivers a **summarized Home Cockpit**, embedded interactive visual charts, automated natural-language data insights, a **100% offline autonomous ContactAI Assistant** (supporting text and voice input), a **fuzzy duplicate detection & merge engine**, and a **multi-format ETL pipeline** for CSV, Excel, JSON, and vCard data.

---

## 🏛️ Application Architecture

```
                       CONTACT MANAGER PRO
                                │
    ┌───────────────────────────┼───────────────────────────┐
    ▼                           ▼                           ▼
[PRESENTATION LAYER]    [AI & BUSINESS LOGIC]       [DATA & STORAGE]
  • Executive Cockpit     • ContactAI Assistant       • SQLite 3 (WAL Mode)
  • Contacts Directory    • ContactService            • SQLAlchemy ORM
  • Groups & Tags         • SearchService (Faceted)   • Repository Pattern
  • Visual Analytics      • DuplicateService (Fuzzy)  • Atomic Backups
  • Import / Export UI    • Import/Export Pipelines   • Audit Trail Logs
  • Royal Theme System    • Analytics & Insights
```

```
Directory Structure:
contact_manager/
├── main.py                     # Primary entry point (Desktop GUI default, --cli support)
├── config/
│   └── settings.py             # Global settings, Royal color palette, paths
├── models/
│   ├── contact.py              # Domain Contact model (25+ portfolio attributes)
│   ├── group.py                # Group entity
│   └── tag.py                  # Tag entity
├── database/
│   ├── connection.py           # SQLite connection manager, WAL pragmas, sessions
│   ├── models.py               # SQLAlchemy ORM schemas & junction tables
│   ├── repository.py           # Repository layer with CRUD, soft-delete, and audit logs
│   └── migrations.py           # Schema initialization & realistic seed generator
├── services/
│   ├── contact_service.py      # Core contact business operations
│   ├── search_service.py       # Instant full-text & advanced multi-field search
│   ├── validation_service.py   # Multi-field regex validation & normalizer
│   ├── duplicate_service.py    # Deterministic & fuzzy matcher, smart merge engine
│   ├── import_service.py       # Smart CSV, Excel, JSON, vCard ingestion pipeline
│   ├── export_service.py       # Scoped multi-format exporter
│   ├── analytics_service.py    # Pandas aggregations & automated Insight Engine
│   ├── backup_service.py       # SQLite atomic snapshot backup & restore
│   └── ai_assistant_service.py # 100% offline NLP conversational assistant
├── gui/
│   ├── app.py                  # Master window shell with Royal sidebar navigation
│   ├── theme.py                # Royal palette color tokens & Icon+Wording standards
│   ├── animations.py           # Number roll counter animations & hover effects
│   ├── dashboard.py            # Summarized Home Cockpit: KPI cards, charts, insights
│   ├── contacts.py             # Contacts directory table, sorting, and pagination
│   ├── contact_form.py         # Dedicated Add/Edit modal with tabbed categories
│   ├── duplicate_view.py       # Duplicate comparison cards & merge resolution
│   ├── groups.py               # Group and tag management
│   ├── analytics.py            # Deep-dive analytics charts & integrity metrics
│   ├── ai_assistant_view.py    # Dedicated in-app chat interface with voice & text
│   ├── import_view.py          # 4-step import wizard with schema mapping preview
│   ├── export_view.py          # Multi-format export dialog
│   └── settings.py             # System settings & backup restore points
├── utils/
│   ├── validators.py           # Regex engines for email, phone, URLs, names
│   ├── formatters.py           # International phone & display standardizers
│   ├── logger.py               # Rotating file and console logger
│   └── helpers.py              # Filesystem utilities
├── tests/                      # Automated test suite (pytest)
├── assets/                     # Application icons (PNG & ICO)
├── build_exe.py                # PyInstaller packaging automation script
├── requirements.txt            # Frozen dependencies
└── README.md
```

---

## 🚀 Key Feature Highlights

### 1. 🏠 Executive Summarized Home Cockpit
* **Qlik/PowerBI-Grade KPI Tiles**: Displays Total Contacts, VIP Favorites, Active Groups, Data Quality Score %, and Duplicate Alerts with **rolling counter tally animations**.
* **Embedded Interactive Visualizations**:
  * **Donut Chart**: Contact distribution across groups with central totals.
  * **Horizontal Bar Chart**: Top geographic hubs and cities.
  * **Growth Area Chart**: Monthly contact addition trajectory.
* **Automated AI Insight Engine**: Dynamically calculates and renders high-level natural-language observations (e.g., *"72% of contacts have verified email addresses"*, *"Chennai is your top geographic hub representing 34% of total"*).
* **Recent Activity Quick Table**: Inspect newest contacts with direct quick-action links.

### 2. 🤖 ContactAI Assistant (100% Offline Capability)
* **Autonomous Local NLP Engine**: Runs **100% offline** without any cloud API keys or external internet connectivity. Operates out-of-the-box in the compiled `.exe`.
* **Conversational CRUD & Analytics**:
  * `Add contact Sundar Pichai, 9876543210, sundar@google.com, Google, Mountain View`
  * `Analyze my contacts`
  * `Check for duplicates`
  * `Find contacts in Bangalore`
  * `Who is missing email or phone?`
  * `Show my favorites`
* **Voice and Text Support**: Dual-mode input with speech transcription and structured text-only card replies.

### 3. 👤 Comprehensive 25+ Field Contact Management
* **Personal**: First Name, Last Name, Display Name, Date of Birth, Gender, Profile Photo.
* **Contact**: Primary Phone, Alternate Phone, Email, Alternate Email, Website.
* **Professional**: Company, Job Title, Department.
* **Address**: Address Line, City, State, Country, Postal / ZIP Code.
* **Organization**: Many-to-many Groups, Tags, VIP Priority Favorite toggle, Contact Type.
* **Metadata & Soft Delete**: Notes, Created Date, Updated Date, `is_deleted = TRUE` soft-deletion preserving history.

### 4. 🔀 Duplicate Detection & Intelligent Merge Engine
* **Deterministic Rules**: Matches identical normalized phone numbers and emails.
* **Fuzzy String Similarity**: Evaluates names and affiliations using `SequenceMatcher` to calculate an overall match confidence score (0–100%).
* **Intelligent Merge Engine**: Unifies duplicate pairs by prioritizing non-empty values, consolidating unique groups and tags, merging conversation notes, soft-deleting the duplicate, and writing an immutable audit log entry.

### 5. 📥 Smart ETL Ingestion & Export Pipelines
* **Multi-Format Ingestion**: Supports CSV, Excel (.xlsx), JSON, and vCard (.vcf).
* **Smart Column Mapping**: Automatically resolves synonym column headers (e.g. `mobile`, `cell`, `contact_no` ➔ `phone`; `mail`, `e_mail` ➔ `email`).
* **Multi-Format Export**: Generates CSV, formatted Excel workbooks, JSON arrays, and standard vCard 3.0 address cards. Supports exporting the entire database or scoped filtered results.

### 6. 🎨 Royal Enterprise Palette & Icon+Wording Standard
* **Color Scheme**: Deep Midnight Navy (`#0b132b`), Elevated Card Navy (`#1c2541`), Imperial Gold (`#d4af37`), Royal Sapphire (`#2563eb`), Royal Emerald (`#059669`), and Ruby Crimson (`#dc2626`).
* **Icon + Wording Standard**: Zero ambiguous icon-only buttons. Every action button explicitly pairs an intuitive icon with clear descriptive wording (e.g. `[ ➕ Add Contact ]`, `[ ✏️ Edit Details ]`, `[ 🗑️ Delete Contact ]`, `[ ⭐ Mark Favorite ]`, `[ 🔀 Merge Duplicates ]`).

### 7. 💾 Disaster Recovery & Backups
* **Atomic Snapshots**: Creates online point-in-time SQLite backups to `backups/contacts_backup_YYYY_MM_DD_HHMMSS.db`.
* **Verified Restore**: Runs SQLite integrity checks before applying restore points with automatic rollback guards.

---

## 🛠️ Technology Stack

| Component | Technologies |
| :--- | :--- |
| **Core** | Python 3.11+ |
| **GUI Framework** | Tkinter, ttk, ttkbootstrap, Pillow |
| **Database** | SQLite 3 (WAL mode), SQLAlchemy 2.0 ORM |
| **Data Engineering** | Pandas, OpenPyXL, re, difflib |
| **Visual Analytics** | Matplotlib (TkAgg canvas backend) |
| **Testing** | pytest |
| **Packaging** | PyInstaller (Standalone single-file/directory `.exe`) |

---

## ⚡ Quickstart & Installation

### 1. Prerequisites
Ensure Python 3.11+ is installed.

### 2. Setup Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Launch Application
To launch the desktop GUI:
```powershell
python main.py
```

To run in CLI mode:
```powershell
python main.py --cli
```

To re-seed realistic sample contacts:
```powershell
python main.py --seed
```

---

## 🧪 Automated Testing

Contact Manager Pro includes a comprehensive automated test suite with **100% passing test coverage**:

```powershell
pytest tests/ -v
```

### Verified Test Modules:
* `tests/test_validation.py` — Phone normalization, email RFC validation, name rules.
* `tests/test_database.py` — In-memory SQLite CRUD, relationships, soft delete, metrics.
* `tests/test_search.py` — Universal full-text search and faceted filtering.
* `tests/test_duplicates.py` — Fuzzy similarity scoring, deduplication scan, merge engine.
* `tests/test_import_export.py` — CSV, Excel, JSON, and vCard round-trip pipelines.
* `tests/test_ai_assistant.py` — Offline NLP intent parsing and command execution.

---

## 📦 Building the Standalone Executable (.exe)

You can package the entire application into a standalone Windows executable (`ContactManagerPro.exe`) with embedded icons, fonts, and assets:

```powershell
# 1. Verify dependencies
python build_exe.py --check

# 2. Build executable
python build_exe.py
```
The compiled binary will be placed in `dist/ContactManagerPro.exe`.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
