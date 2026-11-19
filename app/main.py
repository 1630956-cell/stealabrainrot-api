import os

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db

ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "change-me-dev-key")

app = FastAPI(
    title="Steal a Brainrot API",
    description=(
        "Tracking API for the Roblox game Steal a Brainrot: "
        "brainrots, rarities, mutations, traits, game updates (changelog) "
        "and live events."
    ),
    version="1.0.0",
)


def require_admin(x_api_key: str = Header(default="")):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
    return x_api_key


@app.get("/health")
def health():
    return {"status": "ok", "service": "steal-a-brainrot-api", "version": app.version}


@app.get("/", include_in_schema=False)
def root():
    return {"docs": "/docs", "endpoints": ["/brainrots", "/mutations", "/traits", "/updates", "/events", "/calculator"]}


@app.get("/brainrots", response_model=list[schemas.BrainrotOut])
def list_brainrots(
    q: str | None = Query(None, description="Search by name"),
    rarity: str | None = Query(None),
    event: str | None = Query(None),
    limited: bool | None = Query(None),
    added_in_update: str | None = Query(None),
    sort: str = Query("income", pattern="^(income|cost|name|rarity)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(models.Brainrot)
    if q:
        query = query.filter(models.Brainrot.name.ilike(f"%{q}%"))
    if rarity:
        query = query.filter(models.Brainrot.rarity.ilike(rarity))
    if event:
        query = query.filter(models.Brainrot.event.ilike(event))
    if limited is not None:
        query = query.filter(models.Brainrot.limited == limited)
    if added_in_update:
        query = query.filter(models.Brainrot.added_in_update.ilike(added_in_update))

    column = getattr(models.Brainrot, sort)
    query = query.order_by(column.desc() if order == "desc" else column.asc())
    return query.offset(offset).limit(limit).all()


@app.get("/brainrots/{slug}", response_model=schemas.BrainrotOut)
def get_brainrot(slug: str, db: Session = Depends(get_db)):
    brainrot = (
        db.query(models.Brainrot)
        .filter(or_(models.Brainrot.slug == slug, models.Brainrot.name.ilike(slug)))
        .first()
    )
    if not brainrot:
        raise HTTPException(status_code=404, detail="Brainrot not found")
    return brainrot


@app.post("/brainrots", response_model=schemas.BrainrotOut, status_code=201)
def create_brainrot(payload: schemas.BrainrotIn, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    import re

    slug = re.sub(r"[^a-z0-9]+", "-", payload.name.lower()).strip("-")
    if db.query(models.Brainrot).filter(models.Brainrot.slug == slug).first():
        raise HTTPException(status_code=409, detail="Brainrot already exists")
    if payload.rarity not in models.RARITIES:
        raise HTTPException(status_code=400, detail=f"rarity must be one of {models.RARITIES}")
    data = payload.model_dump()
    data["slug"] = slug
    brainrot = models.Brainrot(**data)
    db.add(brainrot)
    db.commit()
    db.refresh(brainrot)
    return brainrot


@app.put("/brainrots/{slug}", response_model=schemas.BrainrotOut)
def update_brainrot(
    slug: str, payload: schemas.BrainrotIn, db: Session = Depends(get_db), _: str = Depends(require_admin)
):
    brainrot = db.query(models.Brainrot).filter(models.Brainrot.slug == slug).first()
    if not brainrot:
        raise HTTPException(status_code=404, detail="Brainrot not found")
    if payload.rarity not in models.RARITIES:
        raise HTTPException(status_code=400, detail=f"rarity must be one of {models.RARITIES}")
    for key, value in payload.model_dump().items():
        setattr(brainrot, key, value)
    db.commit()
    db.refresh(brainrot)
    return brainrot


@app.delete("/brainrots/{slug}", status_code=204)
def delete_brainrot(slug: str, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    brainrot = db.query(models.Brainrot).filter(models.Brainrot.slug == slug).first()
    if not brainrot:
        raise HTTPException(status_code=404, detail="Brainrot not found")
    db.delete(brainrot)
    db.commit()


@app.get("/mutations", response_model=list[schemas.MutationOut])
def list_mutations(permanent: bool | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Mutation)
    if permanent is not None:
        query = query.filter(models.Mutation.permanent == permanent)
    return query.order_by(models.Mutation.multiplier).all()


@app.post("/mutations", response_model=schemas.MutationOut, status_code=201)
def create_mutation(payload: schemas.MutationIn, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    if db.query(models.Mutation).filter(models.Mutation.name == payload.name).first():
        raise HTTPException(status_code=409, detail="Mutation already exists")
    mutation = models.Mutation(**payload.model_dump())
    db.add(mutation)
    db.commit()
    db.refresh(mutation)
    return mutation


@app.get("/traits", response_model=list[schemas.TraitOut])
def list_traits(db: Session = Depends(get_db)):
    return db.query(models.Trait).order_by(models.Trait.bonus).all()


@app.post("/traits", response_model=schemas.TraitOut, status_code=201)
def create_trait(payload: schemas.TraitIn, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    if db.query(models.Trait).filter(models.Trait.name == payload.name).first():
        raise HTTPException(status_code=409, detail="Trait already exists")
    trait = models.Trait(**payload.model_dump())
    db.add(trait)
    db.commit()
    db.refresh(trait)
    return trait


@app.get("/updates", response_model=list[schemas.UpdateOut])
def list_updates(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return (
        db.query(models.UpdateLog)
        .order_by(models.UpdateLog.released_at.desc())
        .offset(0)
        .limit(limit)
        .all()
    )


@app.get("/updates/latest", response_model=schemas.UpdateOut)
def latest_update(db: Session = Depends(get_db)):
    update = db.query(models.UpdateLog).order_by(models.UpdateLog.released_at.desc()).first()
    if not update:
        raise HTTPException(status_code=404, detail="No updates tracked yet")
    return update


@app.get("/updates/{version}", response_model=schemas.UpdateOut)
def get_update(version: str, db: Session = Depends(get_db)):
    update = db.query(models.UpdateLog).filter(models.UpdateLog.version == version).first()
    if not update:
        raise HTTPException(status_code=404, detail="Update not found")
    return update


@app.post("/updates", response_model=schemas.UpdateOut, status_code=201)
def create_update(payload: schemas.UpdateIn, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    if db.query(models.UpdateLog).filter(models.UpdateLog.version == payload.version).first():
        raise HTTPException(status_code=409, detail="Update version already exists")
    data = payload.model_dump()
    if payload.released_at:
        from datetime import datetime

        try:
            data["released_at"] = datetime.fromisoformat(payload.released_at.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="released_at must be ISO 8601, e.g. 2026-01-17T18:00:00Z")
    else:
        data["released_at"] = None
    update = models.UpdateLog(**data)
    db.add(update)
    db.commit()
    db.refresh(update)
    return update


@app.get("/events", response_model=list[schemas.EventOut])
def list_events(active: bool | None = None, db: Session = Depends(get_db)):
    query = db.query(models.GameEvent).order_by(models.GameEvent.starts_at.desc())
    if active is not None:
        query = query.filter(models.GameEvent.active == active)
    return query.all()


@app.get("/events/active-now", response_model=list[schemas.EventOut])
def events_active_now(db: Session = Depends(get_db)):
    now = models.utcnow()
    return (
        db.query(models.GameEvent)
        .filter(
            models.GameEvent.starts_at <= now,
            models.GameEvent.ends_at >= now,
        )
        .all()
    )


@app.post("/events", response_model=schemas.EventOut, status_code=201)
def create_event(payload: schemas.EventIn, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    from datetime import datetime

    try:
        data = payload.model_dump()
        data["starts_at"] = datetime.fromisoformat(payload.starts_at.replace("Z", "+00:00"))
        data["ends_at"] = datetime.fromisoformat(payload.ends_at.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="starts_at/ends_at must be ISO 8601, e.g. 2026-01-17T18:00:00Z")
    event = models.GameEvent(**data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@app.get("/calculator")
def income_calculator(
    brainrot: str,
    mutation: str | None = None,
    traits: str | None = Query(None, description="Comma-separated trait names"),
    db: Session = Depends(get_db),
):
    unit = (
        db.query(models.Brainrot)
        .filter(or_(models.Brainrot.slug == brainrot, models.Brainrot.name.ilike(brainrot)))
        .first()
    )
    if not unit:
        raise HTTPException(status_code=404, detail="Brainrot not found")

    mutation_multiplier = 1.0
    if mutation:
        record = db.query(models.Mutation).filter(models.Mutation.name.ilike(mutation)).first()
        if not record:
            raise HTTPException(status_code=404, detail="Mutation not found")
        mutation_multiplier = record.multiplier

    trait_bonus = 0.0
    applied_traits: list[dict] = []
    if traits:
        for name in [t.strip() for t in traits.split(",") if t.strip()]:
            record = db.query(models.Trait).filter(models.Trait.name.ilike(name)).first()
            if not record:
                raise HTTPException(status_code=404, detail=f"Trait not found: {name}")
            trait_bonus += record.bonus
            applied_traits.append({"name": record.name, "bonus": record.bonus})

    total_multiplier = mutation_multiplier + trait_bonus
    return {
        "brainrot": unit.name,
        "base_income": unit.income,
        "mutation": mutation,
        "mutation_multiplier": mutation_multiplier,
        "traits": applied_traits,
        "trait_bonus": trait_bonus,
        "total_multiplier": total_multiplier,
        "income_per_second": unit.income * total_multiplier,
    }
