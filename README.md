
# bps_internal_tools

A lightweight Flask platform for Brockton School internal tools.  
Currently includes the **TOC Attendance** tool (substitute teacher attendance) and is designed to host more tools as they're built and needed.

The main drive for this project is to have somewhere clean and prebuilt that I can add new project requests to. This should save time in rebuilding main app infrastructure like data handling and authentication for every project. Instead that is all provided here and new project can just add to it. In theory this should make projects like cleaning up the sign in system or building a course selction app much easier.

## 🆕 Recent Updates

- Migrated persistence layer to **MariaDB** with import scripts for Canvas SIS CSVs
- Added **Google Workspace OAuth** login alongside local CSV credentials
- Introduced role-based access control with per-tool permissions
- Expanded TOC Attendance with block selection, grade-level attendance, teacher logging, and inactive student filtering
- Updated UI colours and branding with BPS logo files

## ✨ Features

- **Internal Tools Hub** at `/` with per-tool namespaces
- **TOC Attendance** at `/toc-attendance`:
  - Search teachers (autocomplete)
  - Pick a course (term/role filtered) and optional block
  - Take attendance by course or by grade
  - Filter out inactive students
  - Log regular teacher names for context
  - Mark absences (touch-friendly UI)
  - Log results to Google Sheets (daily tab, header row, column widths)
  - Records **Submitted By** (logged-in user)
- **Auth**
  - Local CSV credentials and Google Workspace OAuth for `brocktonschool.com`
  - Session-based `@login_required` protection
  - Role-based access control per tool

Eventually more tools will be built here. The sign in app will be transfered to this project, and once a UI is built, the Canvas<->MySchool Data migration project will also be moved here.

## 🧱 Architecture

- **Flask** app (blueprints per tool)
- **Blueprints**
  - `toc_attendance/` → routes under `/toc-attendance`
- **Data**
  - MariaDB/MySQL backend with scripts to import Canvas SIS CSVs
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
- MariaDB/MySQL database

### 2) Clone Repo
```bash
git clone git@github.com:brockton-school/bps_internal_tools.git
````

### 3) Environment

Create `.env` (or export env vars):

```bash
cp .env.example .env
```
Then update as needed (set `DATABASE_URL`, Google OAuth credentials, etc.). Key Google Sheets variables:

* `GOOGLE_SHEET_ID` → TOC Attendance Google Sheet ID
* `SIGNIN_GOOGLE_SHEET_ID` → Sign-in kiosk Google Sheet ID (falls back to `GOOGLE_SHEET_ID` if unset)

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

### 4) Import Canvas CSVs

Place Canvas SIS export files under `./env/sis_export` and run:

```bash
python scripts/update-db-from-canvas.py
```

### 5) Run

```bash
./build.sh
```

Open: `http://localhost:5000/`

* Tools hub: `/`
* TOC Attendance: `/toc-attendance`

## 🔐 Authentication

* Local CSV users or Google Workspace OAuth restricted to `brocktonschool.com`
* `@login_required` and role checks protect app routes
* `current_user()` helper keeps a consistent shape across auth methods

## 🗒️ TOC Attendance → Google Sheets

* Daily sheet tab auto-created (`YYYY-MM-DD`)
* Frozen header row: `Date | Time | Absent Students | Course Name | Submitted By`
* Wider columns for names
* Bold course row, then one row per absent student (or “All Students Present”)

## 🖌️ UI/Branding

* **Nunito Sans** (Google Fonts)
* BPS colour palette and logo assets
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
* **Sheets write errors**: check `GOOGLE_CREDENTIALS_PATH`, `GOOGLE_SHEET_ID`, and `SIGNIN_GOOGLE_SHEET_ID`
* **Auth won’t work**: verify `AUTH_USERS_CSV`, `SECRET_KEY`, and password hashes

## 📦 Deployment

* Set all env vars in your host / container
* Use gunicorn: `gunicorn -w 2 'app:app'`
* Mount credentials/CSV files read-only where possible

## 📝 License

See [`LICENSE`](./LICENSE) for details.

