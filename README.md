
# bps_internal_tools

A lightweight Flask platform for Brockton School internal tools.  
Currently includes the **TOC Attendance** tool (substitute teacher attendance) and is designed to host more tools as they're built and needed.

The main drive for this project is to have somewhere clean and prebuilt that I can add new project requests to. This should save time in rebuilding main app infrastructure like data handling and authentication for every project. Instead that is all provided here and new project can just add to it. In theory this should make projects like cleaning up the sign in system or building a course selction app much easier.

## ✨ Features

- **Internal Tools Hub** at `/` with per-tool namespaces
- **TOC Attendance** at `/toc-attendance`:
  - Search teachers (autocomplete)
  - Pick a course (term/role filtered)
  - Mark absences (touch-friendly UI)
  - Log results to Google Sheets (daily tab, header row, column widths)
  - Records **Submitted By** (logged-in user)
- **Auth**
  - CSV-based login (hashed passwords via Werkzeug)
  - Session-based `@login_required` protection
  - Upgrade path to **Google Workspace OAuth**

Eventually more tools will be built here. The sign in app will be transfered to this project, and once a UI is built, the Canvas<->MySchool Data migration project will also be moved here.

## 🧱 Architecture

- **Flask** app (blueprints per tool)
- **Blueprints**
  - `toc_attendance/` → routes under `/toc-attendance`
- **Data**
  - SQLite for direct Canvas CSV imports (courses, users, enrollments from Canvas SIS Export)
- **Sheets**
  - Google Sheets logging (via `gspread` + `gspread-formatting`), eventually this should be moved to our own interface.

```

bps\_internal\_tools/
├─ app.py
├─ auth.py
├─ utils.py
├─ toc\_attendance/
│  ├─ **init**.py
│  └─ routes.py
├─ templates/
│  ├─ base.html
│  ├─ tools\_index.html
│  ├─ login.html
│  ├─ index.html               # TOC attendance: teacher search
│  ├─ select\_course.html
│  └─ take\_attendance.html
├─ static/
│  ├─ styles.css
│  ├─ app.js                   # autocomplete
│  └─ ui.js                    # header menu + theme toggle
├─ scripts/
└─ README.md

````

## 🚀 Quick Start

### 1) Requirements
- Python 3.10+
- Google service account creds for Sheets (JSON)
- SQLite DB (created from Canvas Data CSVs)

### 2) Clone Repo
```bash
git clone git@github.com:brockton-school/bps_internal_tools.git
````

### 3) Environment

Create `.env` (or export env vars):

```bash
cp .env.example .env
```
Then update as needed.

Create `auth_users.csv`:

```csv
username,password_hash,display_name,role,active
alan,$pbkdf2-sha256$...hash...,Alan Ross,admin,true
```
Store this file under `./env`

Generate a password hash:

```bash
python - <<'PY'
from werkzeug.security import generate_password_hash
print(generate_password_hash("YOUR_PASSWORD"))
PY
```

### 4) Initialize DB from CSVs (example)

Get SIS file from canvas, store them in `./data` and the script below. This should be cleaned up into a settings UI eventually!

```bash
python scripts/import_to_sqlite.py
```

### 5) Run

```bash
./build.sh
```

Open: `http://localhost:5000/`

* Tools hub: `/`
* TOC Attendance: `/toc-attendance`

## 🔐 Authentication

* CSV-backed users via `auth.py`
* `@login_required` protects app routes
* Future: swap in Google Workspace OAuth; keep `current_user()` shape to avoid rewrites

## 🗒️ TOC Attendance → Google Sheets

* Daily sheet tab auto-created (`YYYY-MM-DD`)
* Frozen header row: `Date | Time | Absent Students | Course Name | Submitted By`
* Wider columns for names
* Bold course row, then one row per absent student (or “All Students Present”)

## 🖌️ UI/Branding

* **Nunito Sans** (Google Fonts)
* Brand red `#ba0c2f`
* Dark/light themes (toggle in avatar menu)
* Accessible, touch-friendly controls

## 🧪 Dev Notes

* Use `url_for()` in templates/JS for robust routing with blueprints
* To add a new tool:

  1. Create a blueprint `your_tool/`
  2. Register it in `app.py` with a `url_prefix`
  3. Add it to the tools list on `/`

## 🛠️ Troubleshooting

* **404 on tool routes**: ensure blueprint imports execute (import routes in `your_tool/__init__.py`)
* **Sheets write errors**: check `GOOGLE_APPLICATION_CREDENTIALS` and `SHEET_ID`
* **Auth won’t work**: verify `AUTH_USERS_CSV`, `SECRET_KEY`, and password hashes

## 📦 Deployment

* Set all env vars in your host / container
* Use gunicorn: `gunicorn -w 2 'app:app'`
* Mount credentials/CSV files read-only where possible

## 📝 License

See [`LICENSE`](./LICENSE) for details.

