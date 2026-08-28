
import asyncio, sqlite3
from pathlib import Path

class DB:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = asyncio.Lock()

    def conn(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        return c

    async def init(self):
        async with self.lock:
            c=self.conn()
            c.executescript("""
            CREATE TABLE IF NOT EXISTS business_connections(
              owner_id INTEGER PRIMARY KEY,
              connection_id TEXT NOT NULL,
              enabled INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS contacts(
              owner_id INTEGER NOT NULL,
              contact_id INTEGER NOT NULL,
              name TEXT,
              username TEXT,
              last_seen INTEGER NOT NULL,
              PRIMARY KEY(owner_id, contact_id)
            );
            CREATE TABLE IF NOT EXISTS streaks(
              owner_id INTEGER NOT NULL,
              contact_id INTEGER NOT NULL,
              started_on TEXT,
              last_counted_day TEXT,
              current_days INTEGER NOT NULL DEFAULT 0,
              active INTEGER NOT NULL DEFAULT 0,
              PRIMARY KEY(owner_id, contact_id)
            );
            CREATE TABLE IF NOT EXISTS daily_activity(
              owner_id INTEGER NOT NULL,
              contact_id INTEGER NOT NULL,
              day TEXT NOT NULL,
              owner_spoke INTEGER NOT NULL DEFAULT 0,
              contact_spoke INTEGER NOT NULL DEFAULT 0,
              counted INTEGER NOT NULL DEFAULT 0,
              PRIMARY KEY(owner_id, contact_id, day)
            );
            CREATE INDEX IF NOT EXISTS idx_contacts_owner ON contacts(owner_id,last_seen DESC);
            """)
            c.commit(); c.close()

    async def set_connection(self, owner_id, connection_id, enabled=1):
        async with self.lock:
            c=self.conn(); c.execute("""INSERT INTO business_connections(owner_id,connection_id,enabled)
            VALUES(?,?,?) ON CONFLICT(owner_id) DO UPDATE SET connection_id=excluded.connection_id, enabled=excluded.enabled""",
            (owner_id,connection_id,enabled)); c.commit(); c.close()

    async def get_connection(self, owner_id):
        async with self.lock:
            c=self.conn(); r=c.execute("SELECT * FROM business_connections WHERE owner_id=?",(owner_id,)).fetchone(); c.close()
            return r

    async def upsert_contact(self, owner_id, contact_id, name, username):
        async with self.lock:
            c=self.conn(); c.execute("""INSERT INTO contacts(owner_id,contact_id,name,username,last_seen)
            VALUES(?,?,?,?,strftime('%s','now')) ON CONFLICT(owner_id,contact_id) DO UPDATE SET
            name=excluded.name, username=excluded.username,last_seen=excluded.last_seen""",
            (owner_id,contact_id,name,username)); c.commit(); c.close()

    async def contacts(self, owner_id, limit=20):
        async with self.lock:
            c=self.conn(); rows=c.execute("SELECT * FROM contacts WHERE owner_id=? ORDER BY last_seen DESC LIMIT ?",(owner_id,limit)).fetchall(); c.close()
            return rows

    async def set_streak(self, owner_id, contact_id, **kwargs):
        async with self.lock:
            c=self.conn()
            r=c.execute("SELECT 1 FROM streaks WHERE owner_id=? AND contact_id=?",(owner_id,contact_id)).fetchone()
            if not r:
                c.execute("INSERT INTO streaks(owner_id,contact_id) VALUES(?,?)",(owner_id,contact_id))
            for k,v in kwargs.items():
                c.execute(f"UPDATE streaks SET {k}=? WHERE owner_id=? AND contact_id=?",(v,owner_id,contact_id))
            c.commit(); c.close()

    async def get_streak(self, owner_id, contact_id):
        async with self.lock:
            c=self.conn(); r=c.execute("SELECT * FROM streaks WHERE owner_id=? AND contact_id=?",(owner_id,contact_id)).fetchone(); c.close(); return r

    async def active_streaks(self):
        async with self.lock:
            c=self.conn(); rows=c.execute("SELECT * FROM streaks WHERE active=1").fetchall(); c.close(); return rows

    async def mark_activity(self, owner_id, contact_id, day, side):
        async with self.lock:
            c=self.conn()
            c.execute("INSERT OR IGNORE INTO daily_activity(owner_id,contact_id,day) VALUES(?,?,?)",(owner_id,contact_id,day))
            field="owner_spoke" if side=="owner" else "contact_spoke"
            c.execute(f"UPDATE daily_activity SET {field}=1 WHERE owner_id=? AND contact_id=? AND day=?",(owner_id,contact_id,day))
            r=c.execute("SELECT * FROM daily_activity WHERE owner_id=? AND contact_id=? AND day=?",(owner_id,contact_id,day)).fetchone()
            newly = bool(r["owner_spoke"] and r["contact_spoke"] and not r["counted"])
            if newly:
                c.execute("UPDATE daily_activity SET counted=1 WHERE owner_id=? AND contact_id=? AND day=?",(owner_id,contact_id,day))
            c.commit(); c.close()
            return newly, r

    async def day_row(self, owner_id, contact_id, day):
        async with self.lock:
            c=self.conn(); r=c.execute("SELECT * FROM daily_activity WHERE owner_id=? AND contact_id=? AND day=?",(owner_id,contact_id,day)).fetchone(); c.close(); return r
