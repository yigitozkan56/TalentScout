# 🤝 TalentScout

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi&logoColor=white)
![Legal Data Flow](https://img.shields.io/badge/KVKK%20%26%20GDPR-100%25%20Opt--In%20Consent-success)

**TalentScout** is a consent-based (Opt-In) open-source developer showcase. Instead of scraping or profiling developers without permission, TalentScout exclusively lists engineers who voluntarily add `#talent-scout`, `#open-to-work`, or a public `talent-scout.json` gist to their GitHub profile.

---

## ⚖️ Legal Data Architecture & KVKK/GDPR Compliance (Legal Pivot)

- **Zero Unauthorized Profiling:** Rejects any profile that does not contain verifiable opt-in markers (`#talent-scout`, `#open-to-work`, or `talent-scout.json`).
- **Built-in Right to Erasure (KVKK Art. 7 / GDPR Art. 17):** Includes a 1-command CLI (`python app.py opt-out <handle>`) and REST endpoint (`DELETE /api/opt-out/{handle}`) for immediate removal.
- **Local SQLite Cache:** Stores verified opt-in records in `talentscout_cache.db`.

---

## 📊 Sample Output

```text
GitHub Handle        | Skills                           | Availability           | Consent Proof
--------------------------------------------------------------------------------------------------
@deniz-rust-dev      | rust,wasm,tokio,linux,distribute | Immediate (Remote / Hy | GitHub Bio Tag (#talent-scout)
@elif-ai-eng         | python,fastapi,pytorch,rag,mcp   | Contract / Full-Time   | Public Gist (talent-scout.json)
@mert-cloud-sre      | golang,kubernetes,terraform,prom | Open to Offers         | GitHub Bio Tag (#open-to-work)
```

| GitHub Handle | Skills | Availability | Explicit Consent Proof |
| :--- | :--- | :--- | :--- |
| `@deniz-rust-dev` | `rust,wasm,tokio,linux` | Immediate (Remote / Hybrid) | `GitHub Bio Tag (#talent-scout)` |
| `@elif-ai-eng` | `python,fastapi,pytorch,rag,mcp` | Contract / Full-Time | `Public Gist (talent-scout.json)` |
| `@mert-cloud-sre` | `golang,kubernetes,terraform,sre` | Open to Offers | `GitHub Bio Tag (#open-to-work)` |

---

## 🚀 Step-by-Step Installation

```bash
git clone https://github.com/yigitozkan56/TalentScout.git
cd TalentScout
cp .env.example .env
pip install -r requirements.txt
```

---

## 💻 Usage Examples

### CLI Mode
```bash
# Search verified opt-in developers by skill
python app.py search --skill python

# Exercise KVKK/GDPR Right-to-Erasure (Opt-Out)
python app.py opt-out deniz-rust-dev
```

### Web Dashboard & REST API Mode
```bash
python app.py serve --port 8010
```
Visit `http://127.0.0.1:8010` or `GET http://127.0.0.1:8010/api/talent`.

### Running Unit Tests
```bash
pytest tests/
```

---

## 🗺️ Roadmap

- [x] Strict opt-in consent gatekeeper (`#talent-scout`, `#open-to-work`, `talent-scout.json`)
- [x] Instant KVKK/GDPR right-to-erasure (`DELETE /api/opt-out/{handle}`)
- [x] SQLite cache & FastAPI showcase dashboard
- [ ] Cryptographic GPG signature verification for `talent-scout.json` gists
- [ ] RSS feed for newly opted-in open-source maintainers
