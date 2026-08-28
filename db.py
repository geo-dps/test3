
from datetime import date, timedelta
from zoneinfo import ZoneInfo

def today(tz): return date.today() if tz=="UTC" else __import__("datetime").datetime.now(ZoneInfo(tz)).date()

def plural(n):
    return "день" if n%10==1 and n%100!=11 else ("дня" if n%10 in (2,3,4) and n%100 not in (12,13,14) else "дней")

async def record_message(db, owner_id, contact_id, day, side):
    newly, row = await db.mark_activity(owner_id,contact_id,day,side)
    if not newly: return None
    prev=(date.fromisoformat(day)-timedelta(days=1)).isoformat()
    prev_row=await db.day_row(owner_id,contact_id,prev)
    s=await db.get_streak(owner_id,contact_id)
    if prev_row and prev_row["counted"] and s and s["active"]:
        days=(s["current_days"] or 0)+1
        started=s["started_on"] or day
    else:
        days=1; started=day
    await db.set_streak(owner_id,contact_id,started_on=started,last_counted_day=day,current_days=days,active=1)
    return days
