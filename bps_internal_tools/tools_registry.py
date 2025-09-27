# tools_registry.py
from flask import url_for

TOOLS = [
    {
        "slug": "toc_attendance",
        "name": "TOC Attendance",
        "description": "Take attendance for a covered class.",
        "endpoint": ("toc.index", {}),  # (endpoint_name, kwargs)
    },
    {
        "slug": "sis_sync",
        "name": "SIS Sync",
        "description": "Synchronize MySchool CSV data with Canvas.",
        "endpoint": ("sis_sync.index", {}),
    },
    {
        "slug": "kiosks_signin",
        "name": "Sign-In Kiosk",
        "description": "Front-desk kiosk for tracking arrivals and departures.",
        "endpoint": ("kiosks_signin.index", {}),
    },
    # Add more tools here as you grow…
]

def all_tools():
    return TOOLS

def tool_slugs():
    return [t["slug"] for t in TOOLS]

def find_tool(slug):
    return next((t for t in TOOLS if t["slug"] == slug), None)

def tool_link(t):
    ep, kwargs = t.get("endpoint", (None, {}))
    return url_for(ep, **kwargs) if ep else "#"
