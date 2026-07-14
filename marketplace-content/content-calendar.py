"""Automated content calendar for Marketplace releases."""
from datetime import datetime, timedelta
import json

SEASONAL_EVENTS = {
    "Halloween": {"month": 10, "lead_time_days": 42, "theme": "spooky"},
    "Christmas": {"month": 12, "lead_time_days": 42, "theme": "festive"},
    "Summer": {"month": 6, "lead_time_days": 30, "theme": "beach"},
    "BackToSchool": {"month": 8, "lead_time_days": 21, "theme": "academic"},
    "Valentines": {"month": 2, "lead_time_days": 21, "theme": "romantic"},
}

CONTENT_TYPES = [
    {"type": "skin_pack", "frequency_days": 14, "skins": 10},
    {"type": "texture_pack", "frequency_days": 60, "textures": 40},
    {"type": "world", "frequency_days": 45, "features": "quests+dungeons"},
    {"type": "mashup", "frequency_days": 90, "bundles": 3},
]

def generate_calendar(start=datetime.now(), months=6):
    print(f"=== CONTENT CALENDAR ({start.strftime('%b %Y')} - {(start + timedelta(days=30*months)).strftime('%b %Y')}) ===\n")
    
    schedule = []
    current = start
    
    while current < start + timedelta(days=30 * months):
        # Add seasonal prep
        for event_name, event in SEASONAL_EVENTS.items():
            target = datetime(current.year, event["month"], 1)
            prep_date = target - timedelta(days=event["lead_time_days"])
            if current.month == prep_date.month and abs(current.day - prep_date.day) < 7:
                print(f"  [SEASONAL] Prep {event_name} pack (theme: {event['theme']})")
                schedule.append({"event": event_name, "date": current.strftime("%Y-%m-%d"), "action": "prep"})
        
        # Regular cadence
        for ct in CONTENT_TYPES:
            if current.day % ct["frequency_days"] < 7:
                print(f"  {current.strftime('%b %d')}: Create {ct['type']}")
                schedule.append({"date": current.strftime("%Y-%m-%d"), "type": ct["type"]})
        
        current += timedelta(days=1)
    
    return schedule

def seasonal_checklist():
    print("\n=== SEASONAL CHECKLIST ===\n")
    for name, event in SEASONAL_EVENTS.items():
        prep = datetime(datetime.now().year, event["month"], 1) - timedelta(days=event["lead_time_days"])
        print(f"  {name} ({event['theme']}):")
        print(f"    Submit by: {prep.strftime('%b %d')}")
        print(f"    Go live:   {datetime(datetime.now().year, event['month'], 1).strftime('%b %d')}")
        print(f"    Lead time: {event['lead_time_days']} days (review + buffer)")

if __name__ == "__main__":
    generate_calendar()
    seasonal_checklist()
