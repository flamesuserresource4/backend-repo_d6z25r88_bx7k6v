import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Member, RSVP, Event, Article, Mixtape, Partner, Coupon, Special

app = FastAPI(title="I Love Hip Hop JA API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "I Love Hip Hop JA", "status": "ok"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            try:
                response["collections"] = db.list_collection_names()
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# --- Public endpoints for core content ---

@app.get("/api/events", response_model=List[Event])
def list_events(tag: Optional[str] = None, featured: Optional[bool] = None):
    flt = {}
    if tag:
        flt["tags"] = {"$in": [tag]}
    if featured is not None:
        flt["is_featured"] = featured
    docs = get_documents("event", flt)
    # Convert Mongo documents to Pydantic
    return [Event(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]


@app.get("/api/articles", response_model=List[Article])
def list_articles(tag: Optional[str] = None):
    flt = {"tags": {"$in": [tag]}} if tag else {}
    docs = get_documents("article", flt)
    return [Article(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]


@app.get("/api/mixtapes", response_model=List[Mixtape])
def list_mixtapes(dj: Optional[str] = None):
    flt = {"dj": dj} if dj else {}
    docs = get_documents("mixtape", flt)
    return [Mixtape(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]


@app.get("/api/partners", response_model=List[Partner])
def list_partners(featured: Optional[bool] = None):
    flt = {"featured": featured} if featured is not None else {}
    docs = get_documents("partner", flt)
    return [Partner(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]


@app.get("/api/specials", response_model=List[Special])
def get_specials(limit: int = Query(3, ge=1, le=12)):
    docs = get_documents("special", {}, limit=limit)
    return [Special(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]


@app.get("/api/coupons", response_model=List[Coupon])
def get_coupons(active_only: bool = True):
    now = datetime.now(timezone.utc)
    flt = {}
    if active_only:
        flt = {"starts_at": {"$lte": now}, "ends_at": {"$gte": now}}
    docs = get_documents("coupon", flt)
    return [Coupon(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]


# --- Conversion endpoints ---

class MembershipSignup(BaseModel):
    email: str
    phone: Optional[str] = None
    ig_handle: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@app.post("/api/membership/signup")
def membership_signup(payload: MembershipSignup):
    member = Member(
        email=payload.email,
        phone=payload.phone,
        ig_handle=payload.ig_handle,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    try:
        inserted_id = create_document("member", member)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class RSVPRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    package: str
    group_size: int = 2
    bottle_choice: Optional[str] = None
    notes: Optional[str] = None


@app.post("/api/rsvp")
def create_rsvp(payload: RSVPRequest):
    if payload.package not in ["Special Table", "VIP Table", "Mogul Table", "Special", "VIP", "Mogul"]:
        raise HTTPException(status_code=400, detail="Invalid package")
    rsvp = RSVP(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        package=payload.package,
        group_size=payload.group_size,
        bottle_choice=payload.bottle_choice,
        notes=payload.notes,
    )
    try:
        inserted_id = create_document("rsvp", rsvp)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Schema discovery for admin tooling ---
@app.get("/schema")
def get_schema_definitions():
    return {
        "collections": [
            "member",
            "rsvp",
            "event",
            "article",
            "mixtape",
            "partner",
            "coupon",
            "special",
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
