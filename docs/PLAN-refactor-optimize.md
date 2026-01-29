# PLAN-refactor-optimize

> **Status**: PENDING APPROVAL
> **Goal**: Refactor `squid-manager` to Enterprise-grade Clean Code, Security, and modern UI while keeping deployment **simple**.
> **Context**: Flask + SQLite application.

---

## 1. Overview

Refactor the codebase to:
1.  **Clean Architecture**: Service Pattern (Routes → Services → Models).
2.  **Security Hardening**: All secrets in `.env`, Security Headers, CSRF.
3.  **Modern UI**: Tailwind CSS (CDN) for a clean, responsive interface.

**Constraints**:  
- ❌ NO Node.js / npm build steps.  
- ❌ NO new database engine (keep SQLite).

---

## 2. Success Criteria

| Metric | Target |
|--------|--------|
| **Architecture** | Routes contain NO logic; all logic in `services/`. |
| **Security** | Zero secrets in source code; all from `.env`. |
| **UI** | Tailwind CSS applied; responsive on mobile. |
| **Integrity** | All features (Auth, Dashboard, Clients, Logs) work. |

---

## 3. Architecture Changes

### 3.1 Backend (Clean Code)

**Current → Proposed:**
```diff
app/
- routes/           # Mixed logic + routing
+ blueprints/       # View Layer (thin controllers)
+   auth/
+   dashboard/
+   clients/
  services/         # Business Logic (existing, expand)
+ utils/            # Helpers, validators
  models/           # Database Models (keep)
```

### 3.2 Configuration (.env)

> 🔴 **NEW SECTION: Enterprise-grade Configuration**

**Pattern**: `python-dotenv` loads `.env` → `config.py` reads via `os.getenv()`.

**Files:**
| File | Purpose |
|------|---------|
| `.env.example` | Template for required variables (commit to Git). |
| `.env` | Actual secrets (NEVER commit, add to `.gitignore`). |
| `config.py` | Loads ENV and provides defaults. |

**Required Variables in `.env`:**
```ini
# === Core Security ===
SECRET_KEY=<random-64-char-string>
DEBUG=False

# === Database ===
DATABASE_URL=sqlite:///app/squid_manager.db

# === Squid Paths ===
SQUID_CONF_DIR=/etc/squid/conf.d/
SQUID_DOMAINS_DIR=/etc/squid/domains/
BACKUP_DIR=/etc/squid/backups/

# === Scheduler ===
JOB_HOUR=0
JOB_MINUTE=30

# === Network ===
DNS_SERVER=10.30.110.1

# === Application ===
WEBSITE_NAME=Squid Manager VTT
MAX_CLIENTS=100
SESSION_LIFETIME_MINUTES=30
```

### 3.3 Frontend (UI)

- **Library**: Tailwind CSS v3.4 (CDN Script).
- **Templates**:
    - `templates/base.html`: Layout, Navbar, Footer.
    - `templates/components/`: Modals, Cards, Alerts.

---

## 4. Implementation Phases

### Phase 0: Configuration Foundation _(Priority P0)_
- [ ] Add `python-dotenv` to `requirements.txt`.
- [ ] Create `.env.example` with all required variables.
- [ ] Add `.env` to `.gitignore`.
- [ ] Refactor `config.py` to use `load_dotenv()` and `os.getenv()` for ALL config.
- [ ] Remove any hardcoded secrets from codebase.

### Phase 1: Security Hardening _(Priority P0)_
- [ ] Add Security Headers middleware (`Flask-Talisman` or custom).
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Strict-Transport-Security` (for HTTPS)
- [ ] Verify CSRF (`Flask-WTF`) is active on all forms.
- [ ] Audit session cookie settings in `config.py`.

### Phase 2: Clean Architecture Refactor _(Priority P1)_
#### 2.1 Auth Module
- [ ] Move `routes/auth.py` → `blueprints/auth/__init__.py`.
- [ ] Extract logic to `services/auth_service.py`.

#### 2.2 Dashboard Module
- [ ] Move `routes/dashboard.py` → `blueprints/dashboard/`.
- [ ] Extract stats logic to `services/system_service.py`.

#### 2.3 Clients Module
- [ ] Move `routes/manage_clients.py`, `routes/log.py` → `blueprints/clients/`.
- [ ] Extract logic to `services/client_service.py`.

### Phase 3: UI Modernization _(Priority P2)_
- [ ] Create `templates/base.html` with Tailwind CDN.
- [ ] Design Navbar component.
- [ ] Migrate `login.html` to Tailwind.
- [ ] Migrate `dashboard.html` to Tailwind (Stats Cards, Grid layout).
- [ ] Migrate `manage_clients.html` (Table, Forms).
- [ ] Migrate `log.html` (Log viewer).

---

## 5. Dependencies

```python
# requirements.txt (additions)
python-dotenv>=1.0.0
Flask-Talisman>=1.0.0  # Optional: for easy security headers
```

---

## 6. Verification (Phase X)

### 6.1 Automated Tests (Existing)
```bash
# Run existing test suite (ensure routes still work after refactor)
cd d:/VibeCode/Squid_Manager/squid-manager
pytest tests/ -v
```
**Expected**: All tests in `test_routes.py`, `test_models.py`, `test_services.py` pass.

### 6.2 Security Checks
| Check | Command / Method |
|-------|------------------|
| **No Hardcoded Secrets** | `Select-String -Path "app\*.py","config.py" -Pattern "SECRET_KEY=|password=" -Recurse` (PowerShell) → returns 0 matches. |
| **Security Headers** | Browser DevTools → Network → Response Headers → verify `X-Frame-Options`, `X-Content-Type-Options`. |
| **CSRF Tokens** | View page source of login/add client forms → verify `<input type="hidden" name="csrf_token"`. |

### 6.3 Manual UI Test
1. Start server: `python run.py`
2. Open browser: `http://localhost:5000`
3. **Test Flow**: Login → View Dashboard → Add Client → View Logs → Logout
4. **Responsive**: Chrome DevTools → Toggle Device Toolbar → verify layout on mobile.

---

## 7. File Tree (Final)

```text
squid-manager/
├── .env.example          # [NEW] Config template
├── .gitignore            # [UPDATE] Add .env
├── config.py             # [UPDATE] Load from .env
├── requirements.txt      # [UPDATE] Add python-dotenv
├── run.py
├── app/
│   ├── __init__.py       # [UPDATE] Security middleware
│   ├── blueprints/       # [NEW] Thin controllers
│   │   ├── auth/
│   │   ├── dashboard/
│   │   └── clients/
│   ├── services/         # [EXISTING] Business logic
│   ├── models/
│   ├── templates/
│   │   ├── base.html     # [UPDATE] Tailwind layout
│   │   ├── components/   # [NEW] Reusable UI
│   │   └── ...
│   └── static/
└── docs/
    └── PLAN-refactor-optimize.md
```

---

> **Next Steps**: Review and approve this plan, then run `/create` to begin Phase 0.
