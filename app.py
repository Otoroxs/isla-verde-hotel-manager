import streamlit as st
import sqlite3
from datetime import date, datetime, timedelta

# ----------------- CONFIG -----------------
APP_PASSWORD = "islaverde"
ADMIN_PASSWORD = "admin000"
DB_PATH = "hotel.db"

STATUSES = [
    ("reserved", "Reserved"),
    ("checkedin", "Checked In"),
    ("noshow", "No Show"),
    ("checkedout", "Checked Out"),
]

ROOM_TYPES = [
    "Standard",
    "Superior",
    "Deluxe",
    "Deluxe Superior",
    "Deluxe Superior Balcony",
]

# ----------------- I18N (English/Spanish) -----------------
TEXT = {
    "en": {
        "app_title": "Isla Verde Hotel Manager",
        "enter_password": "Enter password to access.",
        "password": "Password",
        "log_in": "Log in",
        "incorrect_password": "Incorrect password.",
        "menu": "Menu",
        "go_to": "Go to",
        "calendar": "Calendar",
        "rooms": "Rooms",
        "room_calendar": "Room Calendar",
        "guests": "Guests",
        "settings": "Settings",
        "admin_sensitive": "Admin (sensitive view)",
        "admin_mode_on": "Admin mode: ON",
        "disable_admin": "Disable admin",
        "admin_password": "Admin password",
        "unlock_admin": "Unlock admin",
        "type_admin_pass": "Type admin pass…",
        "logout": "Logout",
        "selected_date": "Selected date:",
        "cal_header": "Calendar",
        "cal_caption": "Click a date. • means reservation exists. ⛔ means blackout/holiday.",
        "prev": "◀ Prev",
        "today": "Today",
        "next": "Next ▶",
        "selected": "Selected:",
        "go_rooms_hint": "Go to the Rooms tab to manage reservations for the selected date.",
        "rooms_header": "Rooms",
        "rooms_caption": "Shows status + guest. (No Show/Checked Out do not occupy.)",
        "no_rooms_warn": "No rooms found. Go to Settings and add rooms.",
        "res_details": "Reservation Details",
        "select_room_hint": "Select a room from the left to create/edit a reservation.",
        "guest_name": "Guest name",
        "status": "Status",
        "checkin": "Check-in",
        "checkout": "Check-out",
        "num_guests": "Number of guests in room",
        "observations": "Observations / Notes",
        "nights": "Nights",
        "save": "Save",
        "delete_res": "Delete reservation",
        "saved": "Saved.",
        "deleted": "Deleted.",
        "guest_required": "Guest name is required.",
        "invalid_range": "Invalid date range (check-out must be after check-in).",
        "blackout_conflict": "This date range overlaps a blackout/holiday (reservations not allowed).",
        "room_conflict": "Conflict: this room is already booked in that range (or blocked).",
        "more_details": "More details (passport / contact / room type / payment)",
        "guest_profile": "Guest profile (saved)",
        "passport_profile": "Passport number (profile)",
        "dob": "Date of birth (YYYY-MM-DD)",
        "email": "Email address",
        "phone": "Phone number",
        "address": "Home address",
        "room_type_pref": "Room type preference",
        "this_res": "This reservation",
        "passport_this": "Passport number (this reservation)",
        "room_type_this": "Room type (this reservation)",
        "card_details": "Card details (staff can enter; only Admin can view later)",
        "card_hidden_exists": "Card data exists but is hidden. Leave blank to keep existing.",
        "cardholder": "Cardholder name",
        "card_number": "Card number",
        "expiry": "Expiry (MM/YY)",
        "cvv": "CVV",
        "pay_note": "Payment note (optional)",
        "admin_clear_card": "Admin: clear stored card details for this reservation",
        "all_res_for_room": "All reservations for this room",
        "no_res_yet": "No reservations for this room yet.",
        "roomcal_header": "Room Calendar",
        "roomcal_caption": "Pick a room, browse months, select a date to see who was in the room that day.",
        "select_room": "Select room",
        "who_in_room": "Who was in",
        "no_cov_day": "No reservation covers this day for this room.",
        "guests_header": "Guests",
        "guests_caption": "Search guest history. Card details only visible when Admin is unlocked.",
        "search_guest": "Search guest",
        "type_to_search": "Type a name above to search.",
        "no_guests_found": "No guests found.",
        "select_guest": "Select guest",
        "history_for": "History for",
        "admin_only_card": "Admin-only card details",
        "unlock_admin_sidebar": "Unlock Admin in the sidebar to view stored card details.",
        "settings_header": "Settings",
        "rooms_tab": "Rooms",
        "blackouts_tab": "Blackouts / Holidays",
        "rooms_manage": "Rooms",
        "new_room": "New room number",
        "add_room": "Add room",
        "room_added": "Room added.",
        "room_exists": "Room already exists (or invalid).",
        "delete": "Delete",
        "blackouts_header": "Blackouts / Holidays (no reservations allowed)",
        "blackouts_caption": "Block dates. End date is exclusive (like check-out).",
        "title": "Title",
        "start_date": "Start date",
        "end_excl": "End date (exclusive)",
        "notes_optional": "Notes (optional)",
        "add_blackout": "Add blackout",
        "title_required": "Title is required.",
        "end_after": "End date must be after start date.",
        "blackout_added": "Blackout added.",
        "existing_blackouts": "Existing blackouts",
        "no_blackouts": "No blackouts created yet.",
        "deleted_blackout": "Deleted blackout.",
        "language": "Language",
        "choose_language": "Choose language",
        "english": "English",
        "spanish": "Spanish",
        "save_language": "Save language",
        "lang_saved": "Language saved. Refreshing…",
        "available": "Available",
        "occupied": "Occupied",
        "room": "Room",
        "free": "Available",
        "no_rooms": "No rooms exist. Add rooms in Settings.",
        "select_room_left": "Select a room on the left.",
    },
    "es": {
        "app_title": "Administrador del Hotel Isla Verde",
        "enter_password": "Introduce la contraseña para acceder.",
        "password": "Contraseña",
        "log_in": "Entrar",
        "incorrect_password": "Contraseña incorrecta.",
        "menu": "Menú",
        "go_to": "Ir a",
        "calendar": "Calendario",
        "rooms": "Habitaciones",
        "room_calendar": "Calendario de Habitación",
        "guests": "Huéspedes",
        "settings": "Ajustes",
        "admin_sensitive": "Admin (vista sensible)",
        "admin_mode_on": "Modo admin: ACTIVADO",
        "disable_admin": "Desactivar admin",
        "admin_password": "Contraseña admin",
        "unlock_admin": "Desbloquear admin",
        "type_admin_pass": "Escribe la contraseña admin…",
        "logout": "Cerrar sesión",
        "selected_date": "Fecha seleccionada:",
        "cal_header": "Calendario",
        "cal_caption": "Haz clic en una fecha. • = hay reserva. ⛔ = cierre/festivo.",
        "prev": "◀ Anterior",
        "today": "Hoy",
        "next": "Siguiente ▶",
        "selected": "Seleccionado:",
        "go_rooms_hint": "Ve a Habitaciones para gestionar reservas en la fecha seleccionada.",
        "rooms_header": "Habitaciones",
        "rooms_caption": "Muestra estado + huésped. (No show/Salida no ocupan.)",
        "no_rooms_warn": "No hay habitaciones. Ve a Ajustes y añade habitaciones.",
        "res_details": "Detalles de Reserva",
        "select_room_hint": "Selecciona una habitación a la izquierda para crear/editar una reserva.",
        "guest_name": "Nombre del huésped",
        "status": "Estado",
        "checkin": "Entrada",
        "checkout": "Salida",
        "num_guests": "Número de huéspedes en la habitación",
        "observations": "Observaciones / Notas",
        "nights": "Noches",
        "save": "Guardar",
        "delete_res": "Borrar reserva",
        "saved": "Guardado.",
        "deleted": "Borrado.",
        "guest_required": "El nombre del huésped es obligatorio.",
        "invalid_range": "Rango inválido (la salida debe ser después de la entrada).",
        "blackout_conflict": "Este rango coincide con un cierre/festivo (no se aceptan reservas).",
        "room_conflict": "Conflicto: la habitación ya está reservada en ese rango (o bloqueada).",
        "more_details": "Más detalles (pasaporte / contacto / tipo / pago)",
        "guest_profile": "Perfil del huésped (guardado)",
        "passport_profile": "Número de pasaporte (perfil)",
        "dob": "Fecha de nacimiento (YYYY-MM-DD)",
        "email": "Correo",
        "phone": "Teléfono",
        "address": "Dirección",
        "room_type_pref": "Tipo de habitación preferido",
        "this_res": "Esta reserva",
        "passport_this": "Número de pasaporte (esta reserva)",
        "room_type_this": "Tipo de habitación (esta reserva)",
        "card_details": "Datos de tarjeta (se puede introducir; solo Admin puede ver después)",
        "card_hidden_exists": "Hay datos de tarjeta guardados pero están ocultos. Deja en blanco para mantenerlos.",
        "cardholder": "Titular de la tarjeta",
        "card_number": "Número de tarjeta",
        "expiry": "Caducidad (MM/AA)",
        "cvv": "CVV",
        "pay_note": "Nota de pago (opcional)",
        "admin_clear_card": "Admin: borrar datos de tarjeta guardados para esta reserva",
        "all_res_for_room": "Todas las reservas de esta habitación",
        "no_res_yet": "Aún no hay reservas para esta habitación.",
        "roomcal_header": "Calendario de Habitación",
        "roomcal_caption": "Elige una habitación, cambia de mes, selecciona un día para ver quién estuvo.",
        "select_room": "Seleccionar habitación",
        "who_in_room": "Quién estuvo en",
        "no_cov_day": "Ninguna reserva cubre ese día para esta habitación.",
        "guests_header": "Huéspedes",
        "guests_caption": "Busca historial del huésped. Tarjetas solo visibles con Admin.",
        "search_guest": "Buscar huésped",
        "type_to_search": "Escribe un nombre arriba para buscar.",
        "no_guests_found": "No se encontraron huéspedes.",
        "select_guest": "Seleccionar huésped",
        "history_for": "Historial de",
        "admin_only_card": "Datos de tarjeta (solo Admin)",
        "unlock_admin_sidebar": "Desbloquea Admin en la barra lateral para ver datos de tarjeta.",
        "settings_header": "Ajustes",
        "rooms_tab": "Habitaciones",
        "blackouts_tab": "Cierres / Festivos",
        "rooms_manage": "Habitaciones",
        "new_room": "Nuevo número de habitación",
        "add_room": "Añadir habitación",
        "room_added": "Habitación añadida.",
        "room_exists": "La habitación ya existe (o es inválida).",
        "delete": "Borrar",
        "blackouts_header": "Cierres / Festivos (no se aceptan reservas)",
        "blackouts_caption": "Bloquea fechas. La fecha final es exclusiva (como salida).",
        "title": "Título",
        "start_date": "Fecha inicio",
        "end_excl": "Fecha fin (exclusiva)",
        "notes_optional": "Notas (opcional)",
        "add_blackout": "Añadir cierre",
        "title_required": "El título es obligatorio.",
        "end_after": "La fecha fin debe ser después de la inicio.",
        "blackout_added": "Cierre añadido.",
        "existing_blackouts": "Cierres existentes",
        "no_blackouts": "No hay cierres creados.",
        "deleted_blackout": "Cierre borrado.",
        "language": "Idioma",
        "choose_language": "Elegir idioma",
        "english": "Inglés",
        "spanish": "Español",
        "save_language": "Guardar idioma",
        "lang_saved": "Idioma guardado. Actualizando…",
        "available": "Disponible",
        "occupied": "Ocupada",
        "room": "Habitación",
        "free": "Disponible",
        "no_rooms": "No hay habitaciones. Añade habitaciones en Ajustes.",
        "select_room_left": "Selecciona una habitación a la izquierda.",
    },
}

def t(key: str) -> str:
    lang = st.session_state.get("lang", "en")
    return TEXT.get(lang, TEXT["en"]).get(key, key)

# ----------------- DB HELPERS -----------------
def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def now_utc() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")

def iso(d: date) -> str:
    return d.isoformat()

def parse_iso(s: str) -> date:
    return date.fromisoformat(s)

def nights(ci: date, co: date) -> int:
    return (co - ci).days

def overlaps(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    return a_start < b_end and b_start < a_end

def table_exists(conn, table: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (table,),
    ).fetchone()
    return row is not None

def column_exists(conn, table: str, col: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table});").fetchall()
    return any(r[1] == col for r in rows)

def ensure_column(conn, table: str, col_def_sql: str, col_name: str):
    if table_exists(conn, table) and not column_exists(conn, table, col_name):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_def_sql};")

def get_setting(key: str, default: str) -> str:
    conn = db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)
    conn.commit()
    row = conn.execute("SELECT value FROM settings WHERE key=?;", (key,)).fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key: str, value: str):
    conn = db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)
    conn.execute(
        "INSERT INTO settings(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value;",
        (key, value),
    )
    conn.commit()
    conn.close()

def init_db():
    conn = db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL UNIQUE
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            guest_name TEXT NOT NULL,
            status TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL,
            notes TEXT DEFAULT "",
            num_guests INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT NOT NULL UNIQUE,
            passport_number TEXT DEFAULT "",
            dob TEXT DEFAULT "",
            email TEXT DEFAULT "",
            phone TEXT DEFAULT "",
            address TEXT DEFAULT "",
            room_type_pref TEXT DEFAULT "",
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS reservation_details (
            reservation_id INTEGER PRIMARY KEY,
            passport_number TEXT DEFAULT "",
            room_type TEXT DEFAULT "",
            cardholder_name TEXT DEFAULT "",
            card_number TEXT DEFAULT "",
            card_expiry TEXT DEFAULT "",
            card_cvv TEXT DEFAULT "",
            payment_note TEXT DEFAULT "",
            FOREIGN KEY(reservation_id) REFERENCES reservations(id) ON DELETE CASCADE
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS blackouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            notes TEXT DEFAULT "",
            created_at TEXT NOT NULL
        );
    """)

    ensure_column(conn, "reservations", "num_guests INTEGER DEFAULT 1", "num_guests")
    conn.commit()

    cur = conn.execute("SELECT COUNT(*) FROM rooms;")
    if cur.fetchone()[0] == 0:
        for n in range(101, 111):
            conn.execute("INSERT OR IGNORE INTO rooms(number) VALUES (?);", (str(n),))
        conn.commit()

    conn.close()

# ----------------- DATA ACCESS -----------------
def normalize_guest_name(name: str) -> str:
    return " ".join((name or "").strip().split())

def get_rooms():
    return db().execute("SELECT id, number FROM rooms ORDER BY number;").fetchall()

def get_room_number(room_id: int) -> str:
    row = db().execute("SELECT number FROM rooms WHERE id=?;", (room_id,)).fetchone()
    return row[0] if row else "—"

def add_room(num: str):
    conn = db()
    conn.execute("INSERT INTO rooms(number) VALUES (?);", (num.strip(),))
    conn.commit()
    conn.close()

def delete_room(rid: int):
    conn = db()
    conn.execute("DELETE FROM rooms WHERE id=?;", (rid,))
    conn.commit()
    conn.close()

def get_res(res_id: int):
    return db().execute("""
        SELECT id, room_id, guest_name, status, check_in, check_out, notes, num_guests
        FROM reservations
        WHERE id = ?;
    """, (res_id,)).fetchone()

def get_res_for_room(room_id: int):
    return db().execute("""
        SELECT id, guest_name, status, check_in, check_out, notes, num_guests
        FROM reservations
        WHERE room_id = ?
        ORDER BY check_in DESC;
    """, (room_id,)).fetchall()

def delete_res(res_id: int):
    conn = db()
    conn.execute("DELETE FROM reservations WHERE id=?;", (res_id,))
    conn.commit()
    conn.close()

def save_res(res_id, room_id, name, status, ci, co, notes, num_guests: int):
    tstamp = now_utc()
    conn = db()
    if res_id:
        conn.execute("""
            UPDATE reservations
            SET room_id=?, guest_name=?, status=?, check_in=?, check_out=?, notes=?, num_guests=?, updated_at=?
            WHERE id=?;
        """, (room_id, name, status, iso(ci), iso(co), notes, int(num_guests), tstamp, res_id))
        conn.commit()
        conn.close()
        return res_id
    else:
        conn.execute("""
            INSERT INTO reservations(room_id, guest_name, status, check_in, check_out, notes, num_guests, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?);
        """, (room_id, name, status, iso(ci), iso(co), notes, int(num_guests), tstamp, tstamp))
        conn.commit()
        new_id = conn.execute("SELECT last_insert_rowid();").fetchone()[0]
        conn.close()
        return new_id

# guests
def get_guest_by_name(name: str):
    name = normalize_guest_name(name)
    return db().execute("""
        SELECT id, guest_name, passport_number, dob, email, phone, address, room_type_pref
        FROM guests WHERE guest_name = ?;
    """, (name,)).fetchone()

def upsert_guest(name: str, passport: str, dob: str, email: str, phone: str, address: str, room_type_pref: str):
    name = normalize_guest_name(name)
    tstamp = now_utc()
    conn = db()
    existing = conn.execute("SELECT id FROM guests WHERE guest_name=?;", (name,)).fetchone()
    if existing:
        conn.execute("""
            UPDATE guests
            SET passport_number=?, dob=?, email=?, phone=?, address=?, room_type_pref=?, updated_at=?
            WHERE guest_name=?;
        """, (passport or "", dob or "", email or "", phone or "", address or "", room_type_pref or "", tstamp, name))
    else:
        conn.execute("""
            INSERT INTO guests(guest_name, passport_number, dob, email, phone, address, room_type_pref, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?);
        """, (name, passport or "", dob or "", email or "", phone or "", address or "", room_type_pref or "", tstamp, tstamp))
    conn.commit()
    conn.close()

# reservation details (sensitive)
def get_res_details(res_id: int):
    return db().execute("""
        SELECT reservation_id, passport_number, room_type,
               cardholder_name, card_number, card_expiry, card_cvv, payment_note
        FROM reservation_details
        WHERE reservation_id=?;
    """, (res_id,)).fetchone()

def upsert_res_details(
    res_id: int,
    passport: str,
    room_type: str,
    cardholder: str,
    card_number: str,
    expiry: str,
    cvv: str,
    pay_note: str,
    *,
    preserve_card_if_blank: bool
):
    conn = db()
    existing = conn.execute("""
        SELECT reservation_id, cardholder_name, card_number, card_expiry, card_cvv
        FROM reservation_details WHERE reservation_id=?;
    """, (res_id,)).fetchone()

    if existing and preserve_card_if_blank:
        _, ex_ch, ex_num, ex_exp, ex_cvv = existing
        cardholder = cardholder if (cardholder or "").strip() else (ex_ch or "")
        card_number = card_number if (card_number or "").strip() else (ex_num or "")
        expiry = expiry if (expiry or "").strip() else (ex_exp or "")
        cvv = cvv if (cvv or "").strip() else (ex_cvv or "")

    if existing:
        conn.execute("""
            UPDATE reservation_details
            SET passport_number=?, room_type=?, cardholder_name=?, card_number=?, card_expiry=?, card_cvv=?, payment_note=?
            WHERE reservation_id=?;
        """, (passport or "", room_type or "", cardholder or "", card_number or "", expiry or "", cvv or "", pay_note or "", res_id))
    else:
        conn.execute("""
            INSERT INTO reservation_details(reservation_id, passport_number, room_type, cardholder_name, card_number, card_expiry, card_cvv, payment_note)
            VALUES(?,?,?,?,?,?,?,?);
        """, (res_id, passport or "", room_type or "", cardholder or "", card_number or "", expiry or "", cvv or "", pay_note or ""))
    conn.commit()
    conn.close()

# blackouts / holidays
def get_blackouts():
    return db().execute("""
        SELECT id, title, start_date, end_date, notes, created_at
        FROM blackouts
        ORDER BY start_date DESC;
    """).fetchall()

def add_blackout(title: str, start_d: date, end_d: date, notes: str):
    conn = db()
    conn.execute("""
        INSERT INTO blackouts(title, start_date, end_date, notes, created_at)
        VALUES(?,?,?,?,?);
    """, (title.strip(), iso(start_d), iso(end_d), notes or "", now_utc()))
    conn.commit()
    conn.close()

def delete_blackout(bid: int):
    conn = db()
    conn.execute("DELETE FROM blackouts WHERE id=?;", (bid,))
    conn.commit()
    conn.close()

def blackout_overlaps(ci: date, co: date) -> bool:
    rows = db().execute("SELECT start_date, end_date FROM blackouts;").fetchall()
    for s, e in rows:
        if overlaps(ci, co, parse_iso(s), parse_iso(e)):
            return True
    return False

def blackouts_in_range(start: date, end: date):
    return db().execute("""
        SELECT id, title, start_date, end_date
        FROM blackouts
        WHERE start_date < ? AND end_date > ?;
    """, (iso(end), iso(start))).fetchall()

# occupancy
def room_available(room_id: int, ci: date, co: date, exclude=None) -> bool:
    if blackout_overlaps(ci, co):
        return False
    conn = db()
    q = """
        SELECT id, check_in, check_out
        FROM reservations
        WHERE room_id = ?
          AND status NOT IN ('noshow', 'checkedout')
    """
    params = [room_id]
    if exclude:
        q += " AND id != ?"
        params.append(exclude)
    for _, s_ci, s_co in conn.execute(q, params):
        if overlaps(ci, co, parse_iso(s_ci), parse_iso(s_co)):
            conn.close()
            return False
    conn.close()
    return True

def active_on(day_: date):
    return db().execute("""
        SELECT id, room_id, guest_name, status, check_in, check_out
        FROM reservations
        WHERE check_in <= ? AND ? < check_out
          AND status NOT IN ('noshow', 'checkedout');
    """, (iso(day_), iso(day_))).fetchall()

def covering_on(day_: date):
    return db().execute("""
        SELECT id, room_id, guest_name, status, check_in, check_out
        FROM reservations
        WHERE check_in <= ? AND ? < check_out;
    """, (iso(day_), iso(day_))).fetchall()

# guest search/history
def guest_search_names(q: str, limit=30):
    q = (q or "").strip()
    if not q:
        return []
    return db().execute("""
        SELECT guest_name, COUNT(*) as stays
        FROM reservations
        WHERE LOWER(guest_name) LIKE LOWER(?)
        GROUP BY guest_name
        ORDER BY stays DESC, guest_name ASC
        LIMIT ?;
    """, (f"%{q}%", limit)).fetchall()

def guest_history(guest_name: str):
    return db().execute("""
        SELECT r.id, rm.number, r.status, r.check_in, r.check_out, r.notes, r.num_guests, r.updated_at
        FROM reservations r
        JOIN rooms rm ON rm.id = r.room_id
        WHERE r.guest_name = ?
        ORDER BY r.check_in DESC, r.updated_at DESC;
    """, (guest_name,)).fetchall()

# calendar helpers
def month_grid(year: int, month: int):
    first = date(year, month, 1)
    start = first - timedelta(days=first.weekday())
    return [start + timedelta(days=i) for i in range(42)]

def reservations_in_range(start: date, end: date):
    return db().execute("""
        SELECT room_id, status, check_in, check_out
        FROM reservations
        WHERE check_in < ? AND check_out > ?;
    """, (iso(end), iso(start))).fetchall()

def room_reservations_in_range(room_id: int, start: date, end: date):
    return db().execute("""
        SELECT id, guest_name, status, check_in, check_out
        FROM reservations
        WHERE room_id = ?
          AND check_in < ? AND check_out > ?;
    """, (room_id, iso(end), iso(start))).fetchall()

def status_badge(status: str) -> str:
    if status == "checkedin":
        return "✅ Checked In" if st.session_state.lang == "en" else "✅ Check-in"
    if status == "reserved":
        return "🟧 Reserved" if st.session_state.lang == "en" else "🟧 Reservado"
    if status == "noshow":
        return "❌ No Show" if st.session_state.lang == "en" else "❌ No se presentó"
    if status == "checkedout":
        return "⬜ Checked Out" if st.session_state.lang == "en" else "⬜ Salida"
    return "🟦 Available" if st.session_state.lang == "en" else "🟦 Disponible"

# ----------------- APP START -----------------
st.set_page_config(TEXT["en"]["app_title"], layout="wide")
init_db()

# session defaults
if "authed" not in st.session_state:
    st.session_state.authed = False
if "admin" not in st.session_state:
    st.session_state.admin = False
if "admin_pw_key" not in st.session_state:
    st.session_state.admin_pw_key = 0
if "day" not in st.session_state:
    st.session_state.day = date.today()

# load language from DB (persisted)
if "lang" not in st.session_state:
    st.session_state.lang = get_setting("lang", "en")

# login
if not st.session_state.authed:
    st.title(t("app_title"))
    st.caption(t("enter_password"))
    pw = st.text_input(t("password"), type="password")
    if st.button(t("log_in")):
        if pw == APP_PASSWORD:
            st.session_state.authed = True
            st.rerun()
        else:
            st.error(t("incorrect_password"))
    st.stop()

# sidebar navigation
st.sidebar.title(t("menu"))
view = st.sidebar.radio(t("go_to"), [t("calendar"), t("rooms"), t("room_calendar"), t("guests"), t("settings")], index=0)

VIEW_MAP = {
    t("calendar"): "Calendar",
    t("rooms"): "Rooms",
    t("room_calendar"): "Room Calendar",
    t("guests"): "Guests",
    t("settings"): "Settings",
}
view_key = VIEW_MAP[view]

# admin sidebar (fixed)
st.sidebar.divider()
st.sidebar.subheader(t("admin_sensitive"))
if st.session_state.admin:
    st.sidebar.success(t("admin_mode_on"))
    if st.sidebar.button(t("disable_admin")):
        st.session_state.admin = False
        st.rerun()
else:
    with st.sidebar.form("admin_unlock_form", clear_on_submit=True):
        admin_pw = st.text_input(
            t("admin_password"),
            type="password",
            key=f"admin_pw_{st.session_state.admin_pw_key}",
            placeholder=t("type_admin_pass"),
        )
        unlock = st.form_submit_button(t("unlock_admin"))
    if unlock:
        if admin_pw == ADMIN_PASSWORD:
            st.session_state.admin = True
        st.session_state.admin_pw_key += 1
        st.rerun()

# logout
st.sidebar.divider()
if st.sidebar.button(t("logout")):
    st.session_state.authed = False
    st.session_state.admin = False
    st.rerun()

# main header
day = st.session_state.day
st.title(t("app_title"))
st.caption(f"{t('selected_date')} {day}")

# ----------------- VIEWS -----------------
if view_key == "Calendar":
    st.subheader(t("cal_header"))
    st.caption(t("cal_caption"))

    if "month_cursor" not in st.session_state:
        st.session_state.month_cursor = day.replace(day=1)
    mc: date = st.session_state.month_cursor

    c1, c2, c3, c4 = st.columns([1, 1, 2, 1])

    if c1.button(t("prev"), key="cal_prev"):
        y, m = mc.year, mc.month - 1
        if m == 0:
            y, m = y - 1, 12
        st.session_state.month_cursor = date(y, m, 1)
        st.rerun()

    if c2.button(t("today"), key="cal_today"):
        st.session_state.day = date.today()
        st.session_state.month_cursor = date.today().replace(day=1)
        st.rerun()

    c3.markdown(f"### {mc.strftime('%B %Y')}")

    if c4.button(t("next"), key="cal_next"):
        y, m = mc.year, mc.month + 1
        if m == 13:
            y, m = y + 1, 1
        st.session_state.month_cursor = date(y, m, 1)
        st.rerun()

    grid = month_grid(mc.year, mc.month)

    r_in_range = reservations_in_range(grid[0], grid[-1] + timedelta(days=1))
    booked_days = set()
    for _, _, ci_s, co_s in r_in_range:
        ci = parse_iso(ci_s)
        co = parse_iso(co_s)
        d = ci
        while d < co:
            booked_days.add(d)
            d += timedelta(days=1)

    bo = blackouts_in_range(grid[0], grid[-1] + timedelta(days=1))
    blackout_days = set()
    for _, _, s, e in bo:
        s_d = parse_iso(s)
        e_d = parse_iso(e)
        d = s_d
        while d < e_d:
            blackout_days.add(d)
            d += timedelta(days=1)

    dows = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    header = st.columns(7)
    for i, name in enumerate(dows):
        header[i].markdown(f"**{name}**")

    for week in range(6):
        cols = st.columns(7)
        for i in range(7):
            d = grid[week * 7 + i]
            in_month = (d.month == mc.month)

            label = str(d.day)
            if d in blackout_days:
                label += " ⛔"
            if d in booked_days:
                label += " •"
            if d == day:
                label = "✅ " + label

            if cols[i].button(label, disabled=not in_month, use_container_width=True,
                              key=f"cal_{mc.year}_{mc.month}_{week}_{i}_{d.isoformat()}"):
                st.session_state.day = d
                st.rerun()

    st.info(f"{t('selected')} {day.strftime('%A, %B %d, %Y')}")
    st.caption(t("go_rooms_hint"))

elif view_key == "Rooms":
    left, right = st.columns([1.2, 1])

    rooms = get_rooms()
    active = active_on(day)
    active_map = {r[1]: r for r in active}
    covering = covering_on(day)
    cover_map = {r[1]: r for r in covering}

    with left:
        st.subheader(t("rooms_header"))
        st.caption(t("rooms_caption"))

        if not rooms:
            st.warning(t("no_rooms_warn"))
        else:
            for room_id, room_num in rooms:
                occ = active_map.get(room_id)
                cov = cover_map.get(room_id)

                if cov:
                    _, _, guest, stt, _, _ = cov
                    display_status = status_badge(stt)
                    display_guest = guest
                else:
                    display_status = status_badge("available")
                    display_guest = "—"

                free_text = t("available") if not occ else t("occupied")
                label = f"{t('room')} {room_num} — {display_status} — {display_guest} ({free_text})"

                if st.button(label, key=f"room_{room_id}", use_container_width=True):
                    st.session_state.sel_room = room_id
                    st.session_state.sel_res = (occ[0] if occ else (cov[0] if cov else None))
                    st.rerun()

    with right:
        st.subheader(t("res_details"))

        rid = st.session_state.get("sel_room", None)
        res_id = st.session_state.get("sel_res", None)

        if rid is None:
            st.info(t("select_room_hint"))
        else:
            st.markdown(f"### {t('room')} {get_room_number(rid)}")

            res = get_res(res_id) if res_id else None

            ci = parse_iso(res[4]) if res else day
            co = parse_iso(res[5]) if res else (day + timedelta(days=1))
            name = res[2] if res else ""
            status = res[3] if res else "reserved"
            note = res[6] if res else ""
            num_guests = int(res[7]) if (res and res[7] is not None) else 1

            guest_row = get_guest_by_name(name) if name.strip() else None
            g_pass = guest_row[2] if guest_row else ""
            g_dob = guest_row[3] if guest_row else ""
            g_email = guest_row[4] if guest_row else ""
            g_phone = guest_row[5] if guest_row else ""
            g_addr = guest_row[6] if guest_row else ""
            g_room_pref = guest_row[7] if guest_row else ROOM_TYPES[0]

            det = get_res_details(res_id) if res_id else None
            d_pass = det[1] if det else ""
            d_room_type = det[2] if det else ROOM_TYPES[0]

            if st.session_state.admin and det:
                d_cardholder = det[3] or ""
                d_cardnum = det[4] or ""
                d_exp = det[5] or ""
                d_cvv = det[6] or ""
                d_paynote = det[7] or ""
            else:
                d_cardholder = ""
                d_cardnum = ""
                d_exp = ""
                d_cvv = ""
                d_paynote = (det[7] if det else "")

            with st.form("res_form", clear_on_submit=False):
                guest = st.text_input(t("guest_name"), value=name)
                stat = st.selectbox(
                    t("status"),
                    [s[0] for s in STATUSES],
                    format_func=lambda x: dict(STATUSES)[x],
                    index=[s[0] for s in STATUSES].index(status)
                )

                cA, cB = st.columns(2)
                d1 = cA.date_input(t("checkin"), value=ci)
                d2 = cB.date_input(t("checkout"), value=co)

                num_g = st.number_input(t("num_guests"), min_value=1, max_value=20, value=int(num_guests), step=1)

                notes_text = st.text_area(t("observations"), value=note, height=120)
                st.caption(f"{t('nights')}: {nights(d1, d2) if nights(d1, d2) > 0 else '—'}")

                with st.expander(t("more_details"), expanded=False):
                    st.markdown(f"#### {t('guest_profile')}")
                    gp_pass = st.text_input(t("passport_profile"), value=g_pass)
                    gp_dob = st.text_input(t("dob"), value=g_dob, placeholder="1990-04-27")
                    gp_email = st.text_input(t("email"), value=g_email)
                    gp_phone = st.text_input(t("phone"), value=g_phone)
                    gp_addr = st.text_area(t("address"), value=g_addr, height=80)
                    gp_room_pref = st.selectbox(
                        t("room_type_pref"),
                        ROOM_TYPES,
                        index=ROOM_TYPES.index(g_room_pref) if g_room_pref in ROOM_TYPES else 0
                    )

                    st.markdown(f"#### {t('this_res')}")
                    rd_pass = st.text_input(t("passport_this"), value=d_pass)
                    rd_room_type = st.selectbox(
                        t("room_type_this"),
                        ROOM_TYPES,
                        index=ROOM_TYPES.index(d_room_type) if d_room_type in ROOM_TYPES else 0
                    )

                    st.markdown(f"#### {t('card_details')}")
                    if (not st.session_state.admin) and det and any((det[3], det[4], det[5], det[6])):
                        st.info(t("card_hidden_exists"))

                    rd_cardholder = st.text_input(t("cardholder"), value=d_cardholder)
                    rd_cardnum = st.text_input(t("card_number"), value=d_cardnum)
                    rd_exp = st.text_input(t("expiry"), value=d_exp)
                    rd_cvv = st.text_input(t("cvv"), value=d_cvv)
                    rd_paynote = st.text_area(t("pay_note"), value=d_paynote, height=70)

                    clear_card = False
                    if st.session_state.admin and det:
                        clear_card = st.checkbox(t("admin_clear_card"), value=False)

                save_btn = st.form_submit_button(t("save"), type="primary")
                if save_btn:
                    gname = normalize_guest_name(guest)
                    if not gname:
                        st.error(t("guest_required"))
                    elif nights(d1, d2) <= 0:
                        st.error(t("invalid_range"))
                    elif blackout_overlaps(d1, d2):
                        st.error(t("blackout_conflict"))
                    elif not room_available(rid, d1, d2, exclude=res_id):
                        st.error(t("room_conflict"))
                    else:
                        new_id = save_res(res_id, rid, gname, stat, d1, d2, notes_text, int(num_g))
                        upsert_guest(gname, gp_pass, gp_dob, gp_email, gp_phone, gp_addr, gp_room_pref)

                        if st.session_state.admin and clear_card:
                            rd_cardholder2 = ""
                            rd_cardnum2 = ""
                            rd_exp2 = ""
                            rd_cvv2 = ""
                        else:
                            rd_cardholder2 = rd_cardholder
                            rd_cardnum2 = rd_cardnum
                            rd_exp2 = rd_exp
                            rd_cvv2 = rd_cvv

                        upsert_res_details(
                            new_id, rd_pass, rd_room_type,
                            rd_cardholder2, rd_cardnum2, rd_exp2, rd_cvv2,
                            rd_paynote,
                            preserve_card_if_blank=True
                        )

                        st.session_state.sel_res = new_id
                        st.success(t("saved"))
                        st.rerun()

            if res_id:
                if st.button(t("delete_res"), type="secondary"):
                    delete_res(res_id)
                    st.session_state.sel_res = None
                    st.success(t("deleted"))
                    st.rerun()

            st.divider()
            st.markdown(f"#### {t('all_res_for_room')}")
            all_res = get_res_for_room(rid)
            if not all_res:
                st.info(t("no_res_yet"))
            else:
                for r in all_res:
                    st.write(f"- **{r[1]}**: {r[3]} → {r[4]} ({dict(STATUSES).get(r[2], r[2])}) | {t('num_guests')}: {r[6]}")

elif view_key == "Room Calendar":
    st.subheader(t("roomcal_header"))
    st.caption(t("roomcal_caption"))

    rooms = get_rooms()
    if not rooms:
        st.warning(t("no_rooms"))
        st.stop()

    room_label_map = {f"{t('room')} {num}": rid for rid, num in rooms}
    room_choice = st.selectbox(t("select_room"), list(room_label_map.keys()))
    room_id = room_label_map[room_choice]

    key_mc = f"roomcal_month_cursor_{room_id}"
    if key_mc not in st.session_state:
        st.session_state[key_mc] = day.replace(day=1)
    mc: date = st.session_state[key_mc]

    c1, c2, c3, c4 = st.columns([1, 1, 2, 1])
    if c1.button(t("prev"), key=f"rc_prev_{room_id}"):
        y, m = mc.year, mc.month - 1
        if m == 0:
            y, m = y - 1, 12
        st.session_state[key_mc] = date(y, m, 1)
        st.rerun()

    if c2.button(t("today"), key=f"rc_today_{room_id}"):
        st.session_state.day = date.today()
        st.session_state[key_mc] = date.today().replace(day=1)
        st.rerun()

    c3.markdown(f"### {mc.strftime('%B %Y')} — {room_choice}")

    if c4.button(t("next"), key=f"rc_next_{room_id}"):
        y, m = mc.year, mc.month + 1
        if m == 13:
            y, m = y + 1, 1
        st.session_state[key_mc] = date(y, m, 1)
        st.rerun()

    grid = month_grid(mc.year, mc.month)
    rr = room_reservations_in_range(room_id, grid[0], grid[-1] + timedelta(days=1))

    room_booked_days = set()
    for _, _, _, ci_s, co_s in rr:
        ci = parse_iso(ci_s)
        co = parse_iso(co_s)
        d = ci
        while d < co:
            room_booked_days.add(d)
            d += timedelta(days=1)

    bo = blackouts_in_range(grid[0], grid[-1] + timedelta(days=1))
    blackout_days = set()
    for _, _, s, e in bo:
        s_d = parse_iso(s)
        e_d = parse_iso(e)
        d = s_d
        while d < e_d:
            blackout_days.add(d)
            d += timedelta(days=1)

    dows = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    header = st.columns(7)
    for i, name in enumerate(dows):
        header[i].markdown(f"**{name}**")

    for week in range(6):
        cols = st.columns(7)
        for i in range(7):
            d = grid[week * 7 + i]
            in_month = (d.month == mc.month)

            label = str(d.day)
            if d in blackout_days:
                label += " ⛔"
            if d in room_booked_days:
                label += " •"
            if d == day:
                label = "✅ " + label

            if cols[i].button(label, disabled=not in_month, use_container_width=True,
                              key=f"roomcal_{room_id}_{mc.year}_{mc.month}_{week}_{i}_{d.isoformat()}"):
                st.session_state.day = d
                st.rerun()

    st.divider()
    st.markdown(f"#### {t('who_in_room')} {room_choice} — **{day}**")

    cov_today = db().execute("""
        SELECT guest_name, status, check_in, check_out
        FROM reservations
        WHERE room_id = ?
          AND check_in <= ? AND ? < check_out
        ORDER BY check_in;
    """, (room_id, iso(day), iso(day))).fetchall()

    if not cov_today:
        st.info(t("no_cov_day"))
    else:
        for g, stt, ci_s, co_s in cov_today:
            st.write(f"- **{g}**: {ci_s} → {co_s} ({dict(STATUSES).get(stt, stt)})")

elif view_key == "Guests":
    st.subheader(t("guests_header"))
    st.caption(t("guests_caption"))

    q = st.text_input(t("search_guest"), placeholder="Type part of the name…" if st.session_state.lang == "en" else "Escribe parte del nombre…")
    matches = guest_search_names(q)

    if not q.strip():
        st.info(t("type_to_search"))
        st.stop()

    if not matches:
        st.warning(t("no_guests_found"))
        st.stop()

    options = [f"{name}  (stays: {cnt})" if st.session_state.lang == "en" else f"{name}  (estancias: {cnt})" for name, cnt in matches]
    pick = st.selectbox(t("select_guest"), options)
    guest_name = pick.split("  (")[0]

    st.markdown(f"### {t('history_for')}: **{guest_name}**")
    hist = guest_history(guest_name)

    if not hist:
        st.info(t("no_res_yet"))
    else:
        for rid_, room_num, stt, ci, co, notes, numg, updated in hist:
            st.write(f"**{t('room')} {room_num}** — {ci} → {co} — {dict(STATUSES).get(stt, stt)} — {t('num_guests')}: {numg}")
            if notes:
                st.caption(f"{t('observations')}: {notes}")
            st.caption(f"Last updated: {updated}")
            st.divider()

    if st.session_state.admin:
        st.markdown(f"### {t('admin_only_card')}")
        rows = db().execute("""
            SELECT r.id, rm.number, r.check_in, r.check_out,
                   d.cardholder_name, d.card_number, d.card_expiry, d.card_cvv, d.payment_note
            FROM reservations r
            JOIN rooms rm ON rm.id = r.room_id
            LEFT JOIN reservation_details d ON d.reservation_id = r.id
            WHERE r.guest_name = ?
            ORDER BY r.check_in DESC;
        """, (guest_name,)).fetchall()

        for r in rows:
            res_id, room_num, ci, co, ch, num, exp, cvv, note = r
            st.write(f"**Reservation #{res_id}** — {t('room')} {room_num} — {ci} → {co}")
            st.write(f"{t('cardholder')}: {ch or '—'}")
            st.write(f"{t('card_number')}: {num or '—'}")
            st.write(f"{t('expiry')}: {exp or '—'}")
            st.write(f"{t('cvv')}: {cvv or '—'}")
            if note:
                st.caption(f"{t('pay_note')}: {note}")
            st.divider()
    else:
        st.info(t("unlock_admin_sidebar"))

elif view_key == "Settings":
    st.subheader(t("settings_header"))

    # Language switch (persisted)
    st.markdown(f"### {t('language')}")
    lang_choice = st.selectbox(
        t("choose_language"),
        ["en", "es"],
        format_func=lambda x: t("english") if x == "en" else t("spanish"),
        index=0 if st.session_state.lang == "en" else 1,
        key="lang_selectbox",
    )
    if st.button(t("save_language")):
        st.session_state.lang = lang_choice
        set_setting("lang", lang_choice)
        st.success(t("lang_saved"))
        st.rerun()

    st.divider()

    tab1, tab2 = st.tabs([t("rooms_tab"), t("blackouts_tab")])

    with tab1:
        st.markdown(f"### {t('rooms_manage')}")
        new = st.text_input(t("new_room"))
        if st.button(t("add_room")):
            if new.strip():
                try:
                    add_room(new.strip())
                    st.success(t("room_added"))
                    st.rerun()
                except:
                    st.error(t("room_exists"))

        st.divider()
        rooms = get_rooms()
        if not rooms:
            st.info(t("no_rooms"))
        for rid, num in rooms:
            c1, c2 = st.columns([3, 1])
            c1.write(f"{t('room')} {num}")
            if c2.button(t("delete"), key=f"del_room_{rid}"):
                delete_room(rid)
                st.success(t("deleted"))
                st.rerun()

    with tab2:
        st.markdown(f"### {t('blackouts_header')}")
        st.caption(t("blackouts_caption"))

        with st.form("add_blackout_form"):
            title = st.text_input(t("title"), placeholder="e.g. Christmas Closure" if st.session_state.lang == "en" else "Ej. Cierre Navidad")
            c1, c2 = st.columns(2)
            start_d = c1.date_input(t("start_date"), value=date.today())
            end_d = c2.date_input(t("end_excl"), value=date.today() + timedelta(days=1))
            notes = st.text_area(t("notes_optional"), height=80)
            submitted = st.form_submit_button(t("add_blackout"), type="primary")

            if submitted:
                if not title.strip():
                    st.error(t("title_required"))
                elif nights(start_d, end_d) <= 0:
                    st.error(t("end_after"))
                else:
                    add_blackout(title, start_d, end_d, notes)
                    st.success(t("blackout_added"))
                    st.rerun()

        st.divider()
        st.markdown(f"#### {t('existing_blackouts')}")
        bos = get_blackouts()
        if not bos:
            st.info(t("no_blackouts"))
        else:
            for bid, title, s, e, notes, created in bos:
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{title}** — {s} → {e}")
                if notes:
                    c1.caption(notes)
                c1.caption(f"Created: {created}")
                if c2.button(t("delete"), key=f"del_bo_{bid}"):
                    delete_blackout(bid)
                    st.success(t("deleted_blackout"))
                    st.rerun()
