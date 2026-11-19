import sys
from datetime import datetime, timezone

from .database import Base, SessionLocal, engine
from .main import app  # ensure models are imported
from .models import Brainrot, Mutation, Trait, UpdateLog

MUTATIONS = [
    ("Gold", 1.25, True, ""),
    ("Diamond", 1.5, True, ""),
    ("Bloodrot", 2.0, False, "Bloodmoon event"),
    ("Celestial", 4.0, False, "Celestial events"),
    ("Candy", 4.0, False, "Candy Aurora event"),
    ("Lava", 6.0, False, "Molten event"),
    ("Galaxy", 7.0, False, "Galaxy event"),
    ("Yin Yang", 7.5, False, "Yin Yang event"),
    ("Radioactive", 8.5, False, "Radioactive event"),
    ("Cursed", 9.0, False, "Cursed event"),
    ("Rainbow", 10.0, True, ""),
    ("Divine", 10.0, False, "Divine event"),
    ("Cyber", 11.0, False, "Cyber event"),
    ("Phantom", 12.0, False, "Phantom event"),
    ("Crystal", 13.0, False, "Crystal event"),
    ("Eclipse", 14.0, False, "Eclipse event"),
]

TRAITS = [
    ("Taco Trait", 2.0),
    ("Fireworks", 5.0),
    ("Tung Sahur", 4.0),
    ("Bombardiro", 4.0),
    ("Fire", 6.0),
    ("Galactic", 3.0),
]

BRAINROTS = [
    ("Noobini Pizzanini", "Common", 25, 1),
    ("Tim Cheese", "Common", 50, 1),
    ("FluriFlura", "Common", 100, 2),
    ("Svinina Bombardino", "Common", 150, 3),
    ("Pipi Kiwi", "Common", 200, 3),
    ("Trippi Troppi", "Common", 250, 4),
    ("Bandito Bobritto", "Rare", 350, 4),
    ("Boneca Ambalabu", "Rare", 500, 5),
    ("Cappuccino Assassino", "Rare", 750, 7),
    ("Brr Brr Patapim", "Rare", 1000, 8),
    ("Trulimero Trulicina", "Rare", 1250, 9),
    ("Bananita Dolphinita", "Rare", 1750, 13),
    ("Perochello Lemonchello", "Rare", 160, 11),
    ("Brri Brri Bicus Dicus Bombicus", "Epic", 3000, 20),
    ("Bombardiro Crocodilo", "Epic", 3750, 40),
    ("Trenostruzzo Turbo 3000", "Epic", 4200, 55),
    ("Tung Tung Tung Sahur", "Epic", 7000, 65),
    ("Cacto Hipopotamo", "Legendary", 10000, 125),
    ("Chimpanzini Bananini", "Legendary", 15000, 250),
    ("Frigo Camelo", "Mythic", 30000, 500),
    ("Torrtuginni Dragonfrutini", "Mythic", 50000, 1000),
    ("La Vacca Saturno Saturnita", "Mythic", 250000, 50000),
    ("Girafa Celestre", "Mythic", 200000, 200000),
    ("Sammyni Spyderini", "Brainrot God", 300000, 300000),
    ("Cocofanto Elefanto", "Brainrot God", 500000, 19000),
    ("Los Tralaleritos", "Brainrot God", 600000, 85000),
    ("Las Tralaleritas", "Brainrot God", 1000000, 95000),
    ("Garama and Madundung", "Secret", 60000000, 10000000),
    ("La Grande Combinazione", "Secret", 50000000, 7000000),
    ("Matteo", "Secret", 50000000, 1500000),
    ("Dragon Cannelloni", "OG", 250000000000, 250000000),
    ("Strawberry Elephant", "OG", 500000000000, 750000000),
]

UPDATES = [
    {
        "version": "seed-1",
        "title": "Initial API database seeded",
        "body": "Baseline dataset loaded: mutations, traits, sample brainrots across all 8 rarities.",
        "released_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
]


def slugify(name: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Mutation).count() == 0:
            for name, multiplier, permanent, event in MUTATIONS:
                db.add(Mutation(name=name, multiplier=multiplier, permanent=permanent, event=event))

        if db.query(Trait).count() == 0:
            for name, bonus in TRAITS:
                db.add(Trait(name=name, bonus=bonus))

        if db.query(Brainrot).count() == 0:
            for name, rarity, cost, income in BRAINROTS:
                db.add(Brainrot(name=name, slug=slugify(name), rarity=rarity, cost=cost, income=income))

        if db.query(UpdateLog).count() == 0:
            for entry in UPDATES:
                db.add(UpdateLog(**entry))

        db.commit()
        print("Seeded: brainrots, mutations, traits, updates")
    finally:
        db.close()


if __name__ == "__main__":
    if "--reset" in sys.argv:
        Base.metadata.drop_all(bind=engine)
        print("Database reset")
    seed()
