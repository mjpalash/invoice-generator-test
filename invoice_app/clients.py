"""Client validation and SQLite persistence for Slice 1."""
import re
import sqlite3
from pathlib import Path

class ClientValidationError(ValueError):
    pass

REQUIRED = {'name': 'Client name', 'billing_address': 'Billing address', 'place_of_supply': 'Place of supply', 'state': 'State'}
GSTIN_PATTERN = re.compile(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$')

def validate_client(data):
    if not isinstance(data, dict):
        raise ClientValidationError('Client details must be an object')
    cleaned = {}
    for field, label in REQUIRED.items():
        value = data.get(field, '')
        if not isinstance(value, str) or not value.strip():
            raise ClientValidationError(f'{label} is required')
        cleaned[field] = value.strip()
    registered = data.get('gst_registered', False)
    if not isinstance(registered, bool):
        raise ClientValidationError('GST registered must be true or false')
    cleaned['gst_registered'] = registered
    gstin = data.get('gstin', '') or ''
    if registered:
        if not isinstance(gstin, str) or not GSTIN_PATTERN.fullmatch(gstin.strip().upper()):
            raise ClientValidationError('A valid 15-character GSTIN is required')
        cleaned['gstin'] = gstin.strip().upper()
    else:
        cleaned['gstin'] = None
    email = data.get('email', '') or ''
    if not isinstance(email, str) or (email.strip() and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email.strip())):
        raise ClientValidationError('Enter a valid email address')
    cleaned['email'] = email.strip()
    return cleaned

class ClientStore:
    def __init__(self, db_path):
        self.db_path = str(Path(db_path).expanduser())
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                billing_address TEXT NOT NULL,
                place_of_supply TEXT NOT NULL,
                state TEXT NOT NULL,
                gst_registered INTEGER NOT NULL DEFAULT 0,
                gstin TEXT,
                email TEXT NOT NULL DEFAULT ''
            )''')

    def _connect(self):
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        return db

    @staticmethod
    def _as_dict(row):
        item = dict(row)
        item['gst_registered'] = bool(item['gst_registered'])
        return item

    def create(self, details):
        data = validate_client(details)
        with self._connect() as db:
            cur = db.execute('''INSERT INTO clients
                (name, billing_address, place_of_supply, state, gst_registered, gstin, email)
                VALUES (:name, :billing_address, :place_of_supply, :state, :gst_registered, :gstin, :email)''', data)
            row = db.execute('SELECT * FROM clients WHERE id = ?', (cur.lastrowid,)).fetchone()
            return self._as_dict(row)

    def list_clients(self):
        with self._connect() as db:
            rows = db.execute('SELECT * FROM clients ORDER BY id DESC').fetchall()
            return [self._as_dict(row) for row in rows]
