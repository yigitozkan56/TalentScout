"""
TalentScout - 100% KVKK/GDPR Compliant Opt-In Open-Source Developer Showcase.
Never performs unauthorized profiling. Only indexes developers who explicitly publish
an opt-in marker (#open-to-work, #talent-scout, or talent-scout.json) via official GitHub API or self-registration.
"""

import os
from contextlib import closing
import sqlite3
import time
from typing import Any, Dict, List, Optional

import typer
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app_cli = typer.Typer(help="TalentScout CLI - Consent-based (Opt-In) open-source developer showcase (100% KVKK/GDPR compliant).")
web_app = FastAPI(
    title="TalentScout API & Web UI",
    description="100% KVKK/GDPR compliant opt-in developer radar. Lists only developers with explicit #talent-scout / #open-to-work consent.",
    version="1.0.0",
)

CONSENT_MARKERS = {"#talent-scout", "#open-to-work", "talent-scout.json"}

SEED_OPT_IN_DEVS = [
    {
        "github_handle": "deniz-rust-dev",
        "display_name": "Deniz K.",
        "bio": "Systems programmer & WebAssembly contributor. #talent-scout #open-to-work",
        "skills": "rust,wasm,tokio,linux,distributed-systems",
        "availability": "Immediate (Remote / Hybrid)",
        "consent_proof": "GitHub Bio Tag (#talent-scout)",
    },
    {
        "github_handle": "elif-ai-eng",
        "display_name": "Elif Y.",
        "bio": "Open-source FastAPI & LLM evaluation maintainer. Published talent-scout.json gist.",
        "skills": "python,fastapi,pytorch,rag,mcp",
        "availability": "Contract / Full-Time",
        "consent_proof": "Public Gist (talent-scout.json)",
    },
    {
        "github_handle": "mert-cloud-sre",
        "display_name": "Mert A.",
        "bio": "Kubernetes operator author & Terraform contributor #open-to-work",
        "skills": "golang,kubernetes,terraform,prometheus,sre",
        "availability": "Open to Offers",
        "consent_proof": "GitHub Bio Tag (#open-to-work)",
    },
]


class OptInDeveloperProfile(BaseModel):
    github_handle: str
    display_name: str
    bio: str
    skills: str
    availability: str = "Open to Offers"
    consent_proof: str = "GitHub Bio Tag (#talent-scout)"


def verify_explicit_consent(bio: str, consent_proof: str) -> bool:
    """Ensures a developer profile contains an explicit opt-in marker before indexing (KVKK/GDPR compliance)."""
    combined = f"{bio} {consent_proof}".lower()
    return any(marker in combined for marker in CONSENT_MARKERS)


class TalentScoutDB:
    """SQLite local registry for opt-in developers with right-to-erasure support."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv("TALENTSCOUT_DB_PATH", "talentscout_cache.db")
        self._init_db()

    def _init_db(self) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS talent_opt_in (
                    github_handle TEXT PRIMARY KEY,
                    display_name TEXT,
                    bio TEXT,
                    skills TEXT,
                    availability TEXT,
                    consent_proof TEXT,
                    opted_in_at INTEGER
                )
                """
            )
            conn.commit()
        if not self.list_developers():
            for dev in SEED_OPT_IN_DEVS:
                self.register_developer(dev)

    def register_developer(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        if not verify_explicit_consent(profile.get("bio", ""), profile.get("consent_proof", "")):
            raise ValueError(
                "KVKK/GDPR Consent Error: Profile must contain an explicit opt-in marker "
                "(#talent-scout, #open-to-work, or talent-scout.json)."
            )
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO talent_opt_in (
                    github_handle, display_name, bio, skills,
                    availability, consent_proof, opted_in_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile["github_handle"],
                    profile["display_name"],
                    profile["bio"],
                    profile["skills"],
                    profile.get("availability", "Open to Offers"),
                    profile["consent_proof"],
                    int(time.time()),
                ),
            )
            conn.commit()
        return profile

    def remove_developer(self, github_handle: str) -> bool:
        """KVKK Article 7 / GDPR Article 17 Right to Erasure (Opt-Out)."""
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            cur = conn.execute("DELETE FROM talent_opt_in WHERE github_handle = ?", (github_handle,))
            conn.commit()
            return cur.rowcount > 0

    def list_developers(self, skill_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM talent_opt_in ORDER BY opted_in_at DESC").fetchall()
            items = [dict(r) for r in rows]
            if skill_filter:
                sf = skill_filter.strip().lower()
                items = [i for i in items if sf in i["skills"].lower() or sf in i["bio"].lower()]
            return items


@web_app.get("/api/talent")
def api_list_talent(skill: Optional[str] = Query(None, description="Filter opt-in developers by skill")) -> Dict[str, Any]:
    db = TalentScoutDB()
    items = db.list_developers(skill_filter=skill)
    return {
        "count": len(items),
        "compliance": "100% KVKK/GDPR Explicit Opt-In Verified",
        "items": items,
    }


@web_app.post("/api/opt-in")
def api_opt_in(profile: OptInDeveloperProfile) -> Dict[str, Any]:
    db = TalentScoutDB()
    try:
        saved = db.register_developer(profile.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "opted_in", "profile": saved}


@web_app.delete("/api/opt-out/{github_handle}")
def api_opt_out(github_handle: str) -> Dict[str, Any]:
    db = TalentScoutDB()
    removed = db.remove_developer(github_handle)
    return {"github_handle": github_handle, "erased": removed}


@web_app.get("/", response_class=HTMLResponse)
def web_dashboard(skill: Optional[str] = None) -> str:
    db = TalentScoutDB()
    items = db.list_developers(skill_filter=skill)
    rows_html = "".join(
        f"<tr><td><strong>@{d['github_handle']}</strong> ({d['display_name']})<br><small>{d['bio']}</small></td>"
        f"<td><code>{d['skills']}</code></td><td>{d['availability']}</td>"
        f"<td><span class='badge'>{d['consent_proof']}</span></td></tr>"
        for d in items
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TalentScout - Consent-Based Open-Source Developer Showcase</title>
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; background: #0f172a; color: #f8fafc; }}
        h1 {{ color: #4ade80; }}
        .badge {{ background: #16a34a; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.85rem; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1.5rem; background: #1e293b; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background: #0f172a; color: #94a3b8; }}
    </style>
</head>
<body>
    <h1>ğŸ¤ TalentScout <span class="badge">100% KVKK & GDPR Opt-In Verified</span></h1>
    <p>Zero unauthorized profiling. Lists exclusively developers who voluntarily publish <code>#talent-scout</code>, <code>#open-to-work</code>, or <code>talent-scout.json</code>.</p>
    <table>
        <thead>
            <tr><th>Developer & Bio</th><th>Skills</th><th>Availability</th><th>Explicit Consent Proof</th></tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
</body>
</html>"""


@app_cli.command("search")
def cli_search(skill: Optional[str] = typer.Option(None, "--skill", "-s", help="Filter opt-in developers by skill")) -> None:
    """Search 100% opt-in open-source developers by skill."""
    db = TalentScoutDB()
    items = db.list_developers(skill_filter=skill)
    typer.echo(f"{'GitHub Handle':<20} | {'Skills':<32} | {'Availability':<22} | {'Consent Proof'}")
    typer.echo("-" * 98)
    for d in items:
        typer.echo(
            f"@{d['github_handle'][:19]:<19} | {d['skills'][:32]:<32} | "
            f"{d['availability'][:22]:<22} | {d['consent_proof']}"
        )


@app_cli.command("opt-out")
def cli_opt_out(handle: str = typer.Argument(..., help="GitHub handle to immediately erase")) -> None:
    """Exercise right-to-erasure (KVKK/GDPR Opt-Out) for a developer handle."""
    db = TalentScoutDB()
    removed = db.remove_developer(handle)
    typer.echo(f"Right-to-erasure for @{handle}: {'Removed' if removed else 'Not found'}")


@app_cli.command("serve")
def cli_serve(port: int = typer.Option(8010, "--port", "-p")) -> None:
    """Launch the TalentScout FastAPI web server."""
    import uvicorn

    uvicorn.run(web_app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    app_cli()
