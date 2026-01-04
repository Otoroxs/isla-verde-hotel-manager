# Isla Verde Hotel Manager (single-file Streamlit app)
# v4.0.0
# CHANGES INCLUDED:
# - ✅ User-friendly Room History search (quick access to a room’s reservation history)
# - ✅ Tax field added (next to Tariff) in Register Guests + El Roll edit form
# - ✅ Total auto-calculated (Tariff + Tax) * Nights, based on selected room
# - ✅ Room prices (Tariff/Tax/Currency defaults) are ADMIN-only to view/change
#   * Receptionists cannot view/edit room default prices
#   * Receptionists cannot edit Tariff/Tax per reservation (it auto-fills from room defaults)
#   * Admin can edit Tariff/Tax per reservation if needed
# - ✅ Debug fixes (removed accidental `np =` assignment; improved error handling)
# - ✅ DB migrations for new columns (rooms: default_tariff/default_tax/currency, reservations: tax)

import os
import glob
import sqlite3
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Tuple
from contextlib import contextmanager

import pandas as pd
import streamlit as st

# ============================================================
# CONFIG
# ============================================================
DB_PATH = "hotel.db"

# USER ACCOUNTS
USERS = {
    "receptionist a": {"password": "ISLA1", "role": "receptionist"},
    "receptionist b": {"password": "ISLA2", "role": "receptionist"},
    "admin": {"password": "admin000", "role": "admin"},
}

STATUSES: List[Tuple[str, str]] = [
    ("reserved", "Reserved"),
    ("checkedin", "Checked In"),
    ("noshow", "No Show"),
    ("checkedout", "Checked Out"),
]
STATUS_LABEL = {k: v for k, v in STATUSES}
VALID_STATUSES = {k for k, _ in STATUSES}

# Currency: USD / CRC only
CURRENCIES = [("USD", "$"), ("CRC", "₡")]
CURRENCY_SYMBOL = {code: sym for code, sym in CURRENCIES}
DEFAULT_CURRENCY = "USD"

# Daily DB backups
BACKUP_DIR = "backups"
BACKUP_RETENTION_DAYS = 30

APP_VERSION = "v4.0.0"

# ============================================================
# I18N
# ============================================================
TEXT = {
    "en": {
        "app_title": "Isla Verde Hotel Manager",
        "enter_login": "Enter your username and password to access.",
        "username": "Username",
        "password": "Password",
        "log_in": "Log in",
        "incorrect_login": "Incorrect username or password.",
        "logged_in_as": "Logged in as",
        "role": "Role",
        "menu": "Menu",
        "go_to": "Go to",
        "el_roll": "El Roll",
        "register_guests": "Register Guests",
        "search_guests": "Search Guests",
        "room_history": "Room History",
        "settings": "Settings",
        "logout": "Logout",
        "today": "Today",
        "prev": "◀",
        "next": "▶",
        "reservation_name": "Reservation Name",
        "guest_name": "Guest / Reservation Name",
        "pax": "PAX",
        "tariff": "Tariff",
        "tax": "Tax",
        "total": "Total",
        "currency": "Currency",
        "dollars": "Dollars ($)",
        "colones": "Colones (₡)",
        "observations": "Observations",
        "status": "Status",
        "available": "Available",
        "room": "Room",
        "save": "Save",
        "update": "Update",
        "delete": "Delete",
        "saved": "Saved successfully!",
        "deleted": "Deleted successfully!",
        "search_placeholder": "Search reservations…",
        "room_search_placeholder": "Type a room number…",
        "no_results": "No results found",
        "select_date": "Select a date",
        "checkin_date": "Check-in Date",
        "checkout_date": "Check-out Date",
        "num_nights": "Number of Nights",
        "cancel": "Cancel",
        "confirm_delete": "Confirm Delete",
        "delete_warning": "Are you sure you want to delete this reservation?",
        "room_occupied": "Room is already occupied on these dates",
        "date_range_error": "Check-out must be after check-in",
        "name_required": "Reservation name is required",
        "language": "Language",
        "english": "English",
        "spanish": "Spanish",
        "choose_language": "Choose language",
        "save_language": "Save language",
        "lang_saved": "Language saved. Refreshing…",
        "room_management": "Room Management",
        "add_room": "Add Room",
        "new_room": "New room number",
        "room_added": "Room added successfully",
        "room_exists": "Room already exists",
        "room_deleted": "Room deleted successfully",
        "export_csv": "Export to CSV",
        "download_csv": "Download CSV",
        "total_guests": "Total Guests",
        "total_rooms": "Total Rooms",
        "occupancy_rate": "Occupancy Rate",
        "available_rooms": "Available Rooms",
        "available_rooms_list": "Available room numbers",
        "select_to_edit": "Select",
        "select_row_hint": "Tick a row in Select to edit below.",
        "clear_selection": "Clear selection",
        "edit_from_elroll": "Edit reservation",
        "db_mgmt": "Database Management",
        "clear_all_res": "Clear All Reservations",
        "clear_all_confirm": "Are you sure? This cannot be undone.",
        "reset_rooms": "Reset Rooms to Default",
        "reset_rooms_confirm": "Reset all rooms to defaults?",
        "rooms_reset": "Rooms reset to defaults!",
        "suggestions": "Suggestions",
        "clear_search": "Clear search",
        "results": "Results",
        "no_res_for_name": "No reservations found for this name.",
        "register_success": "Register successful",
        "backup_now": "Backup now",
        "backup_created": "Backup created",
        "download_latest_backup": "Download latest backup",
        "no_backups": "No backups found yet.",
        "last_backup": "Last backup",
        "latest_backup": "Latest backup",
        "totals_by_currency": "Totals by currency",
        "nights": "Nights",
        "stays": "Total Stays",
        "confirm_action": "Confirm action",
        "unexpected_error": "Unexpected error",
        "audit_log": "Audit Log",
        "audit_hint": "Shows who made what changes (latest first).",
        "audit_export": "Export audit log CSV",
        "audit_download": "Download audit CSV",
        "enter_username": "Enter username",
        "room_history_hint": "Search a room number to see all its stays (latest first).",
        "room_prices_admin_only": "Room default prices are admin-only.",
        "auto_filled_from_room": "Auto-filled from room defaults",
    },
    "es": {
        "app_title": "Administrador del Hotel Isla Verde",
        "enter_login": "Introduce tu usuario y contraseña para acceder.",
        "username": "Usuario",
        "password": "Contraseña",
        "log_in": "Entrar",
        "incorrect_login": "Usuario o contraseña incorrectos.",
        "logged_in_as": "Sesión iniciada como",
        "role": "Rol",
        "menu": "Menú",
        "go_to": "Ir a",
        "el_roll": "El Roll",
        "register_guests": "Registrar Huéspedes",
        "search_guests": "Buscar Huéspedes",
        "room_history": "Historial de Habitación",
        "settings": "Ajustes",
        "logout": "Cerrar sesión",
        "today": "Hoy",
        "prev": "◀",
        "next": "▶",
        "reservation_name": "Nombre de la Reserva",
        "guest_name": "Nombre del Huésped / Reserva",
        "pax": "PAX",
        "tariff": "Tarifa",
        "tax": "Impuesto",
        "total": "Total",
        "currency": "Moneda",
        "dollars": "Dólares ($)",
        "colones": "Colones (₡)",
        "observations": "Observaciones",
        "status": "Estado",
        "available": "Disponible",
        "room": "Habitación",
        "save": "Guardar",
        "update": "Actualizar",
        "delete": "Borrar",
        "saved": "¡Guardado exitosamente!",
        "deleted": "¡Borrado exitosamente!",
        "search_placeholder": "Buscar reservas…",
        "room_search_placeholder": "Escribe un número de habitación…",
        "no_results": "No se encontraron resultados",
        "select_date": "Selecciona una fecha",
        "checkin_date": "Fecha de Entrada",
        "checkout_date": "Fecha de Salida",
        "num_nights": "Número de Noches",
        "cancel": "Cancelar",
        "confirm_delete": "Confirmar Borrado",
        "delete_warning": "¿Estás seguro de que quieres borrar esta reserva?",
        "room_occupied": "La habitación ya está ocupada en estas fechas",
        "date_range_error": "La salida debe ser después de la entrada",
        "name_required": "El nombre de la reserva es obligatorio",
        "language": "Idioma",
        "english": "Inglés",
        "spanish": "Español",
        "choose_language": "Elegir idioma",
        "save_language": "Guardar idioma",
        "lang_saved": "Idioma guardado. Actualizando…",
        "room_management": "Gestión de Habitaciones",
        "add_room": "Añadir Habitación",
        "new_room": "Nuevo número de habitación",
        "room_added": "Habitación añadida exitosamente",
        "room_exists": "La habitación ya existe",
        "room_deleted": "Habitación borrada exitosamente",
        "export_csv": "Exportar a CSV",
        "download_csv": "Descargar CSV",
        "total_guests": "Huéspedes Totales",
        "total_rooms": "Habitaciones Totales",
        "occupancy_rate": "Tasa de Ocupación",
        "available_rooms": "Habitaciones Disponibles",
        "available_rooms_list": "Números de habitaciones disponibles",
        "select_to_edit": "Seleccionar",
        "select_row_hint": "Marca una fila en Seleccionar para editar abajo.",
        "clear_selection": "Borrar selección",
        "edit_from_elroll": "Editar reserva",
        "db_mgmt": "Gestión de Base de Datos",
        "clear_all_res": "Borrar Todas las Reservas",
        "clear_all_confirm": "¿Seguro? Esto no se puede deshacer.",
        "reset_rooms": "Restablecer habitaciones",
        "reset_rooms_confirm": "¿Restablecer todas las habitaciones a valores por defecto?",
        "rooms_reset": "¡Habitaciones restauradas!",
        "suggestions": "Sugerencias",
        "clear_search": "Limpiar búsqueda",
        "results": "Resultados",
        "no_res_for_name": "No hay reservas para este nombre.",
        "register_success": "Registro exitoso",
        "backup_now": "Hacer backup ahora",
        "backup_created": "Backup creado",
        "download_latest_backup": "Descargar último backup",
        "no_backups": "Aún no hay backups.",
        "last_backup": "Último backup",
        "latest_backup": "Último backup",
        "totals_by_currency": "Totales por moneda",
        "nights": "Noches",
        "stays": "Estancias Totales",
        "confirm_action": "Confirmar acción",
        "unexpected_error": "Error inesperado",
        "audit_log": "Registro de Auditoría",
        "audit_hint": "Muestra quién hizo qué cambios (lo más reciente primero).",
        "audit_export": "Exportar auditoría a CSV",
        "audit_download": "Descargar auditoría CSV",
        "enter_username": "Ingrese usuario",
        "room_history_hint": "Busca un número de habitación para ver todas sus estancias (lo más reciente primero).",
        "room_prices_admin_only": "Los precios por defecto de habitaciones son solo para admin.",
        "auto_filled_from_room": "Autollenado desde la habitación",
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("lang", "en")
    return TEXT.get(lang, TEXT["en"]).get(key, key)


# ============================================================
# HELPERS
# ============================================================
def now_utc() -> str:
    # Add "Z" to indicate UTC explicitly
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def iso(d: date) -> str:
    return d.isoformat()


def parse_iso(s: str) -> date:
    try:
        return date.fromisoformat(str(s)[:10])
    except Exception:
        return date.today()


def nights(ci: date, co: date) -> int:
    try:
        return max(0, (co - ci).days)
    except Exception:
        return 0


def normalize_guest_name(name: str) -> str:
    return " ".join((name or "").strip().split())


def _normalize_currency(currency: str) -> str:
    c = (currency or DEFAULT_CURRENCY).upper()
    return c if c in CURRENCY_SYMBOL else DEFAULT_CURRENCY


def fmt_money(amount: float, currency: str) -> str:
    currency = _normalize_currency(currency)
    sym = CURRENCY_SYMBOL.get(currency, "")
    try:
        return f"{sym}{float(amount):.2f}"
    except Exception:
        return f"{sym}{amount}"


def status_display(db_status: str) -> str:
    if db_status == "available":
        return t("available")
    return STATUS_LABEL.get(db_status, db_status)


def current_user() -> str:
    return st.session_state.get("user", "unknown") or "unknown"


def current_role() -> str:
    return st.session_state.get("role", "unknown") or "unknown"


def is_admin() -> bool:
    return st.session_state.get("role") == "admin"


def calc_total(tariff: float, tax: float, nn: int) -> float:
    try:
        return max(0.0, (float(tariff) + float(tax)) * int(nn))
    except Exception:
        return 0.0


# ============================================================
# DB (safer for Streamlit reruns + less locking)
# ============================================================
def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    return conn


@contextmanager
def db():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (table,),
    ).fetchone()
    return row is not None


def column_exists(conn: sqlite3.Connection, table: str, col: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table});").fetchall()
    return any(r["name"] == col for r in rows)


def ensure_column(conn: sqlite3.Connection, table: str, col_def_sql: str, col_name: str):
    if table_exists(conn, table) and not column_exists(conn, table, col_name):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_def_sql};")


def init_db():
    with db() as conn:
        # Rooms now include default price info (admin-only UI)
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT NOT NULL UNIQUE,
                default_tariff REAL DEFAULT 0,
                default_tax REAL DEFAULT 0,
                currency TEXT DEFAULT "{DEFAULT_CURRENCY}"
            );
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                guest_name TEXT NOT NULL,
                status TEXT NOT NULL,
                check_in TEXT NOT NULL,
                check_out TEXT NOT NULL,
                notes TEXT DEFAULT "",
                num_guests INTEGER DEFAULT 1,
                tariff REAL DEFAULT 0,
                tax REAL DEFAULT 0,
                currency TEXT DEFAULT "{DEFAULT_CURRENCY}",
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
            );
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                user TEXT NOT NULL,
                role TEXT NOT NULL,
                action TEXT NOT NULL,
                entity TEXT NOT NULL,
                entity_id INTEGER,
                details TEXT
            );
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )

        # migrations (for old DBs)
        ensure_column(conn, "reservations", "tariff REAL DEFAULT 0", "tariff")
        ensure_column(conn, "reservations", "tax REAL DEFAULT 0", "tax")
        ensure_column(conn, "reservations", f'currency TEXT DEFAULT "{DEFAULT_CURRENCY}"', "currency")

        ensure_column(conn, "rooms", "default_tariff REAL DEFAULT 0", "default_tariff")
        ensure_column(conn, "rooms", "default_tax REAL DEFAULT 0", "default_tax")
        ensure_column(conn, "rooms", f'currency TEXT DEFAULT "{DEFAULT_CURRENCY}"', "currency")


def get_setting(key: str, default: str) -> str:
    with db() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key=?;", (key,)).fetchone()
        return str(row["value"]) if row else default


def set_setting(key: str, value: str):
    with db() as conn:
        conn.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value;",
            (key, value),
        )


def default_room_numbers() -> List[str]:
    nums: List[int] = []
    nums += list(range(101, 108))
    nums += list(range(201, 212))
    nums += list(range(214, 220))
    nums += list(range(221, 229))
    nums += list(range(301, 309))
    return [str(n) for n in nums]


def seed_rooms_if_empty():
    with db() as conn:
        c = int(conn.execute("SELECT COUNT(*) AS c FROM rooms;").fetchone()["c"])
        if c == 0:
            for num in default_room_numbers():
                conn.execute(
                    "INSERT OR IGNORE INTO rooms(number, default_tariff, default_tax, currency) VALUES (?,?,?,?);",
                    (num, 0.0, 0.0, DEFAULT_CURRENCY),
                )


def log_audit(action: str, entity: str, entity_id: Optional[int] = None, details: str = ""):
    with db() as conn:
        conn.execute(
            """
            INSERT INTO audit_log(ts, user, role, action, entity, entity_id, details)
            VALUES(?,?,?,?,?,?,?);
            """,
            (now_utc(), current_user(), current_role(), action, entity, entity_id, details),
        )


# ============================================================
# BACKUPS (safe temp -> atomic rename)
# ============================================================
def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def cleanup_old_backups(keep_days: int = BACKUP_RETENTION_DAYS):
    ensure_backup_dir()
    cutoff = date.today() - timedelta(days=keep_days)
    for path in glob.glob(os.path.join(BACKUP_DIR, "hotel_*.db")):
        filename = os.path.basename(path)
        try:
            stamp = filename.replace("hotel_", "").replace(".db", "")
            d = date.fromisoformat(stamp)
        except Exception:
            continue
        if d < cutoff:
            try:
                os.remove(path)
            except Exception:
                pass


def create_backup(force: bool = False) -> Optional[str]:
    ensure_backup_dir()
    today = date.today().isoformat()
    final_path = os.path.join(BACKUP_DIR, f"hotel_{today}.db")
    tmp_path = final_path + ".tmp"

    if os.path.exists(final_path) and not force:
        return final_path

    try:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    except Exception:
        pass

    with db() as conn:
        bconn = sqlite3.connect(tmp_path)
        try:
            conn.backup(bconn)
            bconn.commit()
        finally:
            bconn.close()

    os.replace(tmp_path, final_path)
    cleanup_old_backups()
    return final_path


def get_latest_backup_path() -> Optional[str]:
    ensure_backup_dir()
    backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "hotel_*.db")))
    return backups[-1] if backups else None


def get_latest_backup_name() -> str:
    p = get_latest_backup_path()
    return os.path.basename(p) if p else t("no_backups")


@st.cache_resource
def init_once():
    init_db()
    seed_rooms_if_empty()
    return True


@st.cache_data(show_spinner=False)
def daily_backup_once(day_iso: str) -> str:
    p = create_backup(force=False)
    return p or ""


# ============================================================
# DATA FUNCTIONS
# ============================================================
def get_rooms() -> List[sqlite3.Row]:
    with db() as conn:
        return conn.execute(
            "SELECT id, number, default_tariff, default_tax, currency FROM rooms ORDER BY number;"
        ).fetchall()


def get_room_by_number(room_number: str) -> Optional[sqlite3.Row]:
    rn = str(room_number).strip()
    if not rn:
        return None
    with db() as conn:
        return conn.execute(
            "SELECT id, number, default_tariff, default_tax, currency FROM rooms WHERE number=?;",
            (rn,),
        ).fetchone()


def update_room_defaults(room_id: int, default_tariff: float, default_tax: float, currency: str):
    currency = _normalize_currency(currency)
    with db() as conn:
        conn.execute(
            "UPDATE rooms SET default_tariff=?, default_tax=?, currency=? WHERE id=?;",
            (float(default_tariff), float(default_tax), currency, int(room_id)),
        )
    log_audit("UPDATE", "room", int(room_id), f"Updated room defaults: tariff={default_tariff}, tax={default_tax}, currency={currency}")


def add_room(num: str):
    num = str(num).strip()
    if not num:
        raise ValueError("Empty room number")
    with db() as conn:
        conn.execute(
            "INSERT INTO rooms(number, default_tariff, default_tax, currency) VALUES (?,?,?,?);",
            (num, 0.0, 0.0, DEFAULT_CURRENCY),
        )
        rid = int(conn.execute("SELECT id FROM rooms WHERE number=?;", (num,)).fetchone()["id"])
    log_audit("CREATE", "room", rid, f"Added room {num}")


def delete_room(room_id: int):
    with db() as conn:
        row = conn.execute("SELECT number FROM rooms WHERE id=?;", (int(room_id),)).fetchone()
        room_number = row["number"] if row else ""
        conn.execute("DELETE FROM rooms WHERE id=?;", (int(room_id),))
    log_audit("DELETE", "room", int(room_id), f"Deleted room {room_number}")


def get_reservations_for_date(selected_date: date) -> List[sqlite3.Row]:
    with db() as conn:
        return conn.execute(
            """
            SELECT r.id, rm.number AS room_number, r.guest_name, r.num_guests, r.tariff, r.tax, r.currency,
                   r.notes, r.status, r.check_in, r.check_out
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.id
            WHERE r.check_in <= ? AND ? < r.check_out
            ORDER BY rm.number;
            """,
            (iso(selected_date), iso(selected_date)),
        ).fetchall()


def get_all_rooms_with_status(selected_date: date) -> List[Dict]:
    rooms = get_rooms()
    reservations = get_reservations_for_date(selected_date)

    reservation_map: Dict[str, dict] = {}
    for res in reservations:
        room_number = str(res["room_number"])
        reservation_map[room_number] = {
            "id": int(res["id"]),
            "guest_name": res["guest_name"] or "",
            "num_guests": int(res["num_guests"] or 0),
            "tariff": float(res["tariff"] or 0.0),
            "tax": float(res["tax"] or 0.0),
            "currency": _normalize_currency(res["currency"] or DEFAULT_CURRENCY),
            "notes": res["notes"] or "",
            "status": res["status"],
            "check_in": parse_iso(res["check_in"]),
            "check_out": parse_iso(res["check_out"]),
        }

    room_status: List[Dict] = []
    for room in rooms:
        room_number = str(room["number"])
        if room_number in reservation_map:
            res = reservation_map[room_number]
            room_status.append(
                {
                    "room_number": room_number,
                    "guest_name": res["guest_name"],
                    "num_guests": res["num_guests"],
                    "tariff": res["tariff"],
                    "tax": res["tax"],
                    "currency": res["currency"],
                    "notes": res["notes"],
                    "status": res["status"],
                    "reservation_id": res["id"],
                    "occupied": True,
                    "check_in": res["check_in"],
                    "check_out": res["check_out"],
                }
            )
        else:
            room_status.append(
                {
                    "room_number": room_number,
                    "guest_name": "",
                    "num_guests": 0,
                    "tariff": 0.0,
                    "tax": 0.0,
                    "currency": DEFAULT_CURRENCY,
                    "notes": "",
                    "status": "available",
                    "reservation_id": None,
                    "occupied": False,
                    "check_in": None,
                    "check_out": None,
                }
            )
    return room_status


def get_reservation(res_id: int) -> Optional[sqlite3.Row]:
    with db() as conn:
        return conn.execute(
            """
            SELECT r.id, rm.number AS room_number, r.guest_name, r.status, r.check_in, r.check_out,
                   r.notes, r.num_guests, r.tariff, r.tax, r.currency
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.id
            WHERE r.id = ?;
            """,
            (int(res_id),),
        ).fetchone()


def save_reservation(
    room_number: str,
    guest_name: str,
    check_in: date,
    check_out: date,
    num_guests: int,
    tariff: float,
    tax: float,
    currency: str,
    notes: str,
    status: str,
    reservation_id: Optional[int] = None,
) -> bool:
    room_number = str(room_number).strip()
    guest_name = normalize_guest_name(guest_name)
    currency = _normalize_currency(currency)
    status = status if status in VALID_STATUSES else "reserved"

    if not room_number or not guest_name:
        return False
    if check_out <= check_in:
        return False

    with db() as conn:
        room_row = conn.execute("SELECT id FROM rooms WHERE number=?;", (room_number,)).fetchone()
        if not room_row:
            return False
        room_id = int(room_row["id"])

        params = {"room_id": room_id, "new_ci": iso(check_in), "new_co": iso(check_out)}
        if reservation_id is not None:
            params["rid"] = int(reservation_id)
            conflict = conn.execute(
                """
                SELECT id FROM reservations
                WHERE room_id = :room_id
                  AND status NOT IN ('noshow', 'checkedout')
                  AND id != :rid
                  AND check_in < :new_co
                  AND :new_ci < check_out
                LIMIT 1;
                """,
                params,
            ).fetchone()
        else:
            conflict = conn.execute(
                """
                SELECT id FROM reservations
                WHERE room_id = :room_id
                  AND status NOT IN ('noshow', 'checkedout')
                  AND check_in < :new_co
                  AND :new_ci < check_out
                LIMIT 1;
                """,
                params,
            ).fetchone()

        if conflict:
            return False

        tstamp = now_utc()
        if reservation_id is not None:
            conn.execute(
                """
                UPDATE reservations
                SET guest_name=?, status=?, check_in=?, check_out=?, notes=?,
                    num_guests=?, tariff=?, tax=?, currency=?, updated_at=?
                WHERE id=?;
                """,
                (
                    guest_name,
                    status,
                    iso(check_in),
                    iso(check_out),
                    notes or "",
                    int(num_guests),
                    float(tariff),
                    float(tax),
                    currency,
                    tstamp,
                    int(reservation_id),
                ),
            )
            action = "UPDATE"
            rid = int(reservation_id)
        else:
            conn.execute(
                """
                INSERT INTO reservations(room_id, guest_name, status, check_in, check_out,
                                         notes, num_guests, tariff, tax, currency, created_at, updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?);
                """,
                (
                    room_id,
                    guest_name,
                    status,
                    iso(check_in),
                    iso(check_out),
                    notes or "",
                    int(num_guests),
                    float(tariff),
                    float(tax),
                    currency,
                    tstamp,
                    tstamp,
                ),
            )
            rid = int(conn.execute("SELECT last_insert_rowid() AS id;").fetchone()["id"])
            action = "CREATE"

    nn = nights(check_in, check_out)
    total_amt = calc_total(float(tariff), float(tax), nn)
    log_audit(
        action,
        "reservation",
        rid,
        f"room={room_number}; name={guest_name}; status={status}; ci={iso(check_in)}; co={iso(check_out)}; "
        f"pax={int(num_guests)}; tariff={float(tariff)}; tax={float(tax)}; nights={nn}; total={total_amt} {currency}",
    )
    return True


def delete_reservation(res_id: int):
    row = get_reservation(int(res_id))
    details = ""
    if row:
        details = (
            f"room={row['room_number']}; name={row['guest_name']}; ci={row['check_in']}; "
            f"co={row['check_out']}; status={row['status']}"
        )
    with db() as conn:
        conn.execute("DELETE FROM reservations WHERE id=?;", (int(res_id),))
    log_audit("DELETE", "reservation", int(res_id), details)


def search_guests(query: str, limit: int = 10) -> List[str]:
    if not query or len(query.strip()) < 2:
        return []
    q = query.strip()
    with db() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT guest_name
            FROM reservations
            WHERE LOWER(guest_name) LIKE LOWER(?)
            ORDER BY guest_name
            LIMIT ?;
            """,
            (f"%{q}%", int(limit)),
        ).fetchall()
        return [str(r["guest_name"]) for r in rows]


def get_guest_reservations(guest_name: str) -> List[sqlite3.Row]:
    with db() as conn:
        return conn.execute(
            """
            SELECT r.id, rm.number AS room_number, r.status, r.check_in, r.check_out,
                   r.notes, r.num_guests, r.tariff, r.tax, r.currency, r.updated_at
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.id
            WHERE r.guest_name = ?
            ORDER BY r.check_in DESC;
            """,
            (guest_name,),
        ).fetchall()


def get_room_reservations(room_number: str, limit: int = 500) -> List[sqlite3.Row]:
    rn = str(room_number).strip()
    if not rn:
        return []
    with db() as conn:
        return conn.execute(
            """
            SELECT r.id, rm.number AS room_number, r.guest_name, r.status, r.check_in, r.check_out,
                   r.notes, r.num_guests, r.tariff, r.tax, r.currency, r.updated_at
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.id
            WHERE rm.number = ?
            ORDER BY r.check_in DESC
            LIMIT ?;
            """,
            (rn, int(limit)),
        ).fetchall()


def get_dashboard_stats(selected_date: date) -> Dict[str, float]:
    with db() as conn:
        total_rooms = int(conn.execute("SELECT COUNT(*) AS c FROM rooms;").fetchone()["c"])
        occupied_rooms = int(
            conn.execute(
                """
                SELECT COUNT(DISTINCT r.room_id) AS c
                FROM reservations r
                WHERE r.check_in <= ? AND ? < r.check_out
                  AND r.status NOT IN ('noshow', 'checkedout');
                """,
                (iso(selected_date), iso(selected_date)),
            ).fetchone()["c"]
        )
        total_guests = int(
            conn.execute(
                """
                SELECT COALESCE(SUM(r.num_guests), 0) AS c
                FROM reservations r
                WHERE r.check_in <= ? AND ? < r.check_out
                  AND r.status NOT IN ('noshow', 'checkedout');
                """,
                (iso(selected_date), iso(selected_date)),
            ).fetchone()["c"]
        )
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0.0
    return {
        "total_rooms": float(total_rooms),
        "occupied_rooms": float(occupied_rooms),
        "total_guests": float(total_guests),
        "occupancy_rate": float(occupancy_rate),
    }


def get_audit_log(limit: int = 300) -> pd.DataFrame:
    with db() as conn:
        rows = conn.execute(
            """
            SELECT ts, user, role, action, entity, entity_id, details
            FROM audit_log
            ORDER BY id DESC
            LIMIT ?;
            """,
            (int(limit),),
        ).fetchall()
    if not rows:
        return pd.DataFrame(columns=["ts", "user", "role", "action", "entity", "entity_id", "details"])
    return pd.DataFrame([dict(r) for r in rows])


# ============================================================
# STREAMLIT APP START
# ============================================================
st.set_page_config(TEXT["en"]["app_title"], layout="wide")

init_once()
_ = daily_backup_once(date.today().isoformat())

# Session defaults
st.session_state.setdefault("authed", False)
st.session_state.setdefault("user", None)
st.session_state.setdefault("role", None)
st.session_state.setdefault("selected_date", date.today())

st.session_state.setdefault("register_popup", False)
st.session_state.setdefault("elroll_selected_res_id", None)
st.session_state.setdefault("elroll_editor_key_n", 0)
st.session_state.setdefault("search_last_input", "")
st.session_state.setdefault("search_active_name", None)
st.session_state.setdefault("room_history_selected", None)
st.session_state.setdefault("delete_candidate", None)

st.session_state.setdefault("confirm_clear_all", False)
st.session_state.setdefault("confirm_reset_rooms", False)

if "lang" not in st.session_state:
    st.session_state.lang = get_setting("lang", "en")


def show_register_popup_if_needed():
    if st.session_state.get("register_popup", False):
        st.toast(t("register_success"), icon="✅")
        st.session_state.register_popup = False


# ----------------- LOGIN -----------------
if not st.session_state.authed:
    st.title(t("app_title"))
    st.caption(t("enter_login"))

    username = st.text_input(
        t("username"),
        value="",
        placeholder=t("enter_username"),
    )
    pw = st.text_input(t("password"), type="password")

    if st.button(t("log_in")):
        u = (username or "").strip().lower()
        record = USERS.get(u)
        if record and pw == record["password"]:
            st.session_state.authed = True
            st.session_state.user = u
            st.session_state.role = record["role"]
            log_audit("LOGIN", "session", None, f"user={u}; role={record['role']}")
            st.rerun()
        else:
            st.error(t("incorrect_login"))
    st.stop()

# ----------------- SIDEBAR -----------------
st.sidebar.title(t("menu"))
st.sidebar.caption(f"**{t('logged_in_as')}**: {current_user()}")
st.sidebar.caption(f"**{t('role')}**: {current_role()}")

view_options = [t("el_roll"), t("register_guests"), t("search_guests"), t("room_history"), t("settings")]
view = st.sidebar.radio(t("go_to"), view_options, index=0)

VIEW_MAP = {
    t("el_roll"): "el_roll",
    t("register_guests"): "register_guests",
    t("search_guests"): "search_guests",
    t("room_history"): "room_history",
    t("settings"): "settings",
}
view_key = VIEW_MAP[view]

st.sidebar.divider()
if st.sidebar.button(t("logout")):
    log_audit("LOGOUT", "session", None, f"user={current_user()}")
    st.session_state.authed = False
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()

# ----------------- MAIN HEADER -----------------
st.title(t("app_title"))
show_register_popup_if_needed()

# ============================================================
# VIEWS
# ============================================================
try:
    if view_key == "el_roll":
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        with col1:
            if st.button(t("prev")):
                st.session_state.selected_date -= timedelta(days=1)
                st.session_state.elroll_selected_res_id = None
                st.session_state.elroll_editor_key_n += 1
                st.rerun()
        with col2:
            if st.button(t("today")):
                st.session_state.selected_date = date.today()
                st.session_state.elroll_selected_res_id = None
                st.session_state.elroll_editor_key_n += 1
                st.rerun()
        with col3:
            st.markdown(f"### {st.session_state.selected_date.strftime('%A, %B %d, %Y')}")
        with col4:
            if st.button(t("next")):
                st.session_state.selected_date += timedelta(days=1)
                st.session_state.elroll_selected_res_id = None
                st.session_state.elroll_editor_key_n += 1
                st.rerun()
        with col5:
            new_date = st.date_input(
                t("select_date"),
                value=st.session_state.selected_date,
                label_visibility="collapsed",
            )
            if new_date != st.session_state.selected_date:
                st.session_state.selected_date = new_date
                st.session_state.elroll_selected_res_id = None
                st.session_state.elroll_editor_key_n += 1
                st.rerun()

        rooms_status = get_all_rooms_with_status(st.session_state.selected_date)
        available_rooms = [r["room_number"] for r in rooms_status if r["status"] == "available"]
        available_count = len(available_rooms)

        stats = get_dashboard_stats(st.session_state.selected_date)
        a, b, c, d = st.columns(4)
        with a:
            st.metric(t("total_rooms"), int(stats["total_rooms"]))
        with b:
            st.metric(t("total_guests"), int(stats["total_guests"]))
        with c:
            st.metric(t("occupancy_rate"), f"{stats['occupancy_rate']:.1f}%")
        with d:
            with st.popover(f"{t('available_rooms')}: {available_count}"):
                st.markdown(f"**{t('available_rooms_list')}**")
                if available_rooms:
                    cols = st.columns(6)
                    for i, rn in enumerate(available_rooms):
                        cols[i % 6].write(f"• {rn}")
                else:
                    st.info(t("no_results"))

        st.divider()

        rows = []
        for r in rooms_status:
            tariff_text = ""
            tax_text = ""
            total_text = ""
            if r["occupied"]:
                curr = r.get("currency", DEFAULT_CURRENCY)
                nn = nights(r["check_in"], r["check_out"]) if r.get("check_in") and r.get("check_out") else 0
                if float(r["tariff"] or 0) > 0:
                    tariff_text = fmt_money(float(r["tariff"]), curr)
                if float(r["tax"] or 0) > 0:
                    tax_text = fmt_money(float(r["tax"]), curr)
                total_text = fmt_money(calc_total(float(r["tariff"] or 0), float(r["tax"] or 0), nn), curr) if nn > 0 else "—"

            rows.append(
                {
                    t("room"): r["room_number"],
                    t("reservation_name"): r["guest_name"],
                    t("pax"): r["num_guests"] if r["num_guests"] else "",
                    t("tariff"): tariff_text,
                    t("tax"): tax_text,
                    t("total"): total_text,
                    t("observations"): r["notes"],
                    t("status"): status_display(r["status"]),
                    "_reservation_id": r["reservation_id"],
                    t("select_to_edit"): False,
                }
            )

        if not rows:
            st.info(t("no_results"))
        else:
            df = pd.DataFrame(rows)
            st.caption(t("select_row_hint"))

            editor_key = f"elroll_editor_{st.session_state.elroll_editor_key_n}"
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                hide_index=True,
                disabled=[
                    t("room"),
                    t("reservation_name"),
                    t("pax"),
                    t("tariff"),
                    t("tax"),
                    t("total"),
                    t("observations"),
                    t("status"),
                    "_reservation_id",
                ],
                column_config={
                    t("room"): st.column_config.TextColumn(width="small"),
                    t("reservation_name"): st.column_config.TextColumn(width="medium"),
                    t("pax"): st.column_config.TextColumn(width="small"),
                    t("tariff"): st.column_config.TextColumn(width="small"),
                    t("tax"): st.column_config.TextColumn(width="small"),
                    t("total"): st.column_config.TextColumn(width="small"),
                    t("observations"): st.column_config.TextColumn(width="large"),
                    t("status"): st.column_config.TextColumn(width="medium"),
                    t("select_to_edit"): st.column_config.CheckboxColumn(width="small"),
                    "_reservation_id": st.column_config.NumberColumn(width="small"),
                },
                key=editor_key,
            )

            selected_ids = edited_df.loc[
                (edited_df[t("select_to_edit")] == True) & (edited_df["_reservation_id"].notna()),
                "_reservation_id",
            ].tolist()
            st.session_state.elroll_selected_res_id = int(selected_ids[0]) if selected_ids else None

            r1, r2 = st.columns([1, 2])
            with r1:
                if st.button(t("clear_selection"), use_container_width=True):
                    st.session_state.elroll_selected_res_id = None
                    st.session_state.elroll_editor_key_n += 1
                    st.rerun()
            with r2:
                if st.button(t("export_csv"), use_container_width=True):
                    export_df = df.drop(columns=[t("select_to_edit"), "_reservation_id"], errors="ignore")
                    csv = export_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label=t("download_csv"),
                        data=csv,
                        file_name=f"el_roll_{st.session_state.selected_date}.csv",
                        mime="text/csv",
                    )

            # Inline edit panel
            if st.session_state.elroll_selected_res_id is not None:
                reservation_data = get_reservation(int(st.session_state.elroll_selected_res_id))
                if reservation_data:
                    res_id = int(reservation_data["id"])
                    room_number = str(reservation_data["room_number"])
                    guest_name = reservation_data["guest_name"] or ""
                    status = reservation_data["status"] or "reserved"
                    check_in_s = reservation_data["check_in"]
                    check_out_s = reservation_data["check_out"]
                    notes = reservation_data["notes"] or ""
                    num_guests = int(reservation_data["num_guests"] or 1)
                    tariff = float(reservation_data["tariff"] or 0.0)
                    tax_amt = float(reservation_data["tax"] or 0.0)
                    currency = _normalize_currency(reservation_data["currency"] or DEFAULT_CURRENCY)

                    st.divider()
                    st.subheader(t("edit_from_elroll"))

                    with st.form("elroll_inline_edit_form"):
                        rooms = get_rooms()
                        room_options = [str(r["number"]) for r in rooms]
                        room_idx = room_options.index(room_number) if room_number in room_options else 0

                        room_number_new = st.selectbox(t("room"), room_options, index=room_idx)
                        guest_name_new = st.text_input(t("reservation_name"), value=guest_name)

                        d1, d2 = st.columns(2)
                        with d1:
                            check_in_new = st.date_input(t("checkin_date"), value=parse_iso(check_in_s))
                        with d2:
                            check_out_new = st.date_input(t("checkout_date"), value=parse_iso(check_out_s))

                        nn = nights(check_in_new, check_out_new)
                        st.caption(f"{t('num_nights')}: {nn}")

                        # Pull defaults from selected room
                        room_row = get_room_by_number(room_number_new)
                        room_default_tariff = float(room_row["default_tariff"] or 0.0) if room_row else 0.0
                        room_default_tax = float(room_row["default_tax"] or 0.0) if room_row else 0.0
                        room_default_currency = _normalize_currency(room_row["currency"] or DEFAULT_CURRENCY) if room_row else DEFAULT_CURRENCY

                        e1, e2, e3, e4 = st.columns([1, 1, 1, 1])
                        with e1:
                            pax_new = st.number_input(t("pax"), min_value=1, max_value=20, value=int(num_guests))

                        # PRICE FIELDS:
                        # - admin: editable (can override per reservation)
                        # - receptionist: locked to room defaults (cannot access/change prices)
                        with e2:
                            if is_admin():
                                tariff_new = st.number_input(
                                    t("tariff"),
                                    min_value=0.0,
                                    value=float(tariff),
                                    step=10.0,
                                    format="%.2f",
                                )
                            else:
                                tariff_new = float(room_default_tariff)
                                st.number_input(
                                    t("tariff"),
                                    min_value=0.0,
                                    value=float(room_default_tariff),
                                    step=10.0,
                                    format="%.2f",
                                    disabled=True,
                                    help=t("auto_filled_from_room"),
                                )

                        with e3:
                            if is_admin():
                                tax_new = st.number_input(
                                    t("tax"),
                                    min_value=0.0,
                                    value=float(tax_amt),
                                    step=1.0,
                                    format="%.2f",
                                )
                            else:
                                tax_new = float(room_default_tax)
                                st.number_input(
                                    t("tax"),
                                    min_value=0.0,
                                    value=float(room_default_tax),
                                    step=1.0,
                                    format="%.2f",
                                    disabled=True,
                                    help=t("auto_filled_from_room"),
                                )

                        with e4:
                            currency_labels = {"USD": t("dollars"), "CRC": t("colones")}
                            currency_options = ["USD", "CRC"]
                            if is_admin():
                                cidx = currency_options.index(currency) if currency in currency_options else 0
                                currency_new = st.selectbox(
                                    t("currency"),
                                    currency_options,
                                    index=cidx,
                                    format_func=lambda x: currency_labels.get(x, x),
                                )
                            else:
                                currency_new = room_default_currency
                                st.selectbox(
                                    t("currency"),
                                    currency_options,
                                    index=currency_options.index(currency_new) if currency_new in currency_options else 0,
                                    format_func=lambda x: currency_labels.get(x, x),
                                    disabled=True,
                                    help=t("auto_filled_from_room"),
                                )

                        total_amt = calc_total(float(tariff_new), float(tax_new), nn)
                        st.metric(t("total"), fmt_money(total_amt, currency_new))

                        status_options = [s[0] for s in STATUSES]
                        status_idx = status_options.index(status) if status in status_options else 0
                        status_new = st.selectbox(
                            t("status"),
                            status_options,
                            index=status_idx,
                            format_func=lambda x: STATUS_LABEL.get(x, x),
                        )

                        notes_new = st.text_area(t("observations"), value=notes or "", height=100)

                        x1, x2, x3 = st.columns([1, 1, 2])
                        with x1:
                            save_btn = st.form_submit_button(t("update"), type="primary")
                        with x2:
                            cancel_btn = st.form_submit_button(t("cancel"))
                        with x3:
                            delete_btn = st.form_submit_button(f"🗑️ {t('delete')}")

                        if cancel_btn:
                            st.session_state.elroll_selected_res_id = None
                            st.session_state.elroll_editor_key_n += 1
                            st.rerun()

                        if save_btn:
                            if not guest_name_new.strip():
                                st.error(t("name_required"))
                            elif check_out_new <= check_in_new:
                                st.error(t("date_range_error"))
                            else:
                                # Receptionist always uses room defaults
                                if not is_admin():
                                    tariff_new = float(room_default_tariff)
                                    tax_new = float(room_default_tax)
                                    currency_new = room_default_currency

                                ok = save_reservation(
                                    room_number=room_number_new,
                                    guest_name=guest_name_new,
                                    check_in=check_in_new,
                                    check_out=check_out_new,
                                    num_guests=int(pax_new),
                                    tariff=float(tariff_new),
                                    tax=float(tax_new),
                                    currency=currency_new,
                                    notes=notes_new,
                                    status=status_new,
                                    reservation_id=int(res_id),
                                )
                                if ok:
                                    st.success(t("saved"))
                                    st.session_state.elroll_selected_res_id = None
                                    st.session_state.elroll_editor_key_n += 1
                                    st.rerun()
                                else:
                                    st.error(t("room_occupied"))

                        if delete_btn:
                            st.session_state.delete_candidate = int(res_id)
                            st.rerun()

                    if st.session_state.delete_candidate == int(res_id):
                        st.warning(t("delete_warning"))
                        y1, y2 = st.columns(2)
                        with y1:
                            if st.button(t("confirm_delete"), type="primary"):
                                delete_reservation(int(res_id))
                                st.session_state.delete_candidate = None
                                st.session_state.elroll_selected_res_id = None
                                st.session_state.elroll_editor_key_n += 1
                                st.success(t("deleted"))
                                st.rerun()
                        with y2:
                            if st.button(t("cancel")):
                                st.session_state.delete_candidate = None
                                st.rerun()

    elif view_key == "register_guests":
        st.subheader(t("register_guests"))

        with st.form("reservation_form"):
            rooms = get_rooms()
            room_options = [str(r["number"]) for r in rooms]
            room_number = st.selectbox(t("room"), room_options, index=0)

            reservation_name = st.text_input(t("reservation_name"), value="")

            col1, col2 = st.columns(2)
            with col1:
                check_in = st.date_input(t("checkin_date"), value=st.session_state.selected_date)
            with col2:
                check_out = st.date_input(t("checkout_date"), value=st.session_state.selected_date + timedelta(days=1))

            nn = nights(check_in, check_out)
            st.caption(f"{t('num_nights')}: {nn}")

            col3, col4, col5, col6 = st.columns([1, 1, 1, 1])
            with col3:
                num_guests = st.number_input(t("pax"), min_value=1, max_value=20, value=1)

            # Pull room defaults
            room_row = get_room_by_number(room_number)
            room_default_tariff = float(room_row["default_tariff"] or 0.0) if room_row else 0.0
            room_default_tax = float(room_row["default_tax"] or 0.0) if room_row else 0.0
            room_default_currency = _normalize_currency(room_row["currency"] or DEFAULT_CURRENCY) if room_row else DEFAULT_CURRENCY

            with col4:
                if is_admin():
                    tariff = st.number_input(t("tariff"), min_value=0.0, value=float(room_default_tariff), step=10.0, format="%.2f")
                else:
                    tariff = float(room_default_tariff)
                    st.number_input(
                        t("tariff"),
                        min_value=0.0,
                        value=float(room_default_tariff),
                        step=10.0,
                        format="%.2f",
                        disabled=True,
                        help=t("room_prices_admin_only"),
                    )

            with col5:
                if is_admin():
                    tax_amt = st.number_input(t("tax"), min_value=0.0, value=float(room_default_tax), step=1.0, format="%.2f")
                else:
                    tax_amt = float(room_default_tax)
                    st.number_input(
                        t("tax"),
                        min_value=0.0,
                        value=float(room_default_tax),
                        step=1.0,
                        format="%.2f",
                        disabled=True,
                        help=t("room_prices_admin_only"),
                    )

            with col6:
                currency_labels = {"USD": t("dollars"), "CRC": t("colones")}
                currency_options = ["USD", "CRC"]
                if is_admin():
                    currency = st.selectbox(
                        t("currency"),
                        currency_options,
                        index=currency_options.index(room_default_currency) if room_default_currency in currency_options else 0,
                        format_func=lambda x: currency_labels.get(x, x),
                    )
                else:
                    currency = room_default_currency
                    st.selectbox(
                        t("currency"),
                        currency_options,
                        index=currency_options.index(currency) if currency in currency_options else 0,
                        format_func=lambda x: currency_labels.get(x, x),
                        disabled=True,
                        help=t("room_prices_admin_only"),
                    )

            total_amt = calc_total(float(tariff), float(tax_amt), nn)
            st.metric(t("total"), fmt_money(total_amt, currency))

            status_options = [s[0] for s in STATUSES]
            status = st.selectbox(t("status"), status_options, index=0, format_func=lambda x: STATUS_LABEL.get(x, x))

            notes = st.text_area(t("observations"), value="", height=100)

            submit = st.form_submit_button(t("save"), type="primary")
            if submit:
                if not reservation_name.strip():
                    st.error(t("name_required"))
                elif check_out <= check_in:
                    st.error(t("date_range_error"))
                else:
                    # Receptionist always uses room defaults (cannot change prices)
                    if not is_admin():
                        tariff = float(room_default_tariff)
                        tax_amt = float(room_default_tax)
                        currency = room_default_currency

                    ok = save_reservation(
                        room_number=room_number,
                        guest_name=reservation_name,
                        check_in=check_in,
                        check_out=check_out,
                        num_guests=int(num_guests),
                        tariff=float(tariff),
                        tax=float(tax_amt),
                        currency=currency,
                        notes=notes,
                        status=status,
                    )
                    if ok:
                        st.session_state.register_popup = True
                        st.rerun()
                    else:
                        st.error(t("room_occupied"))

        # ADMIN: room management + room default prices
        if is_admin():
            st.divider()
            st.subheader(t("room_management"))

            c1, c2 = st.columns([2, 1])
            with c1:
                new_room = st.text_input(t("new_room"), placeholder="e.g., 401")
            with c2:
                if st.button(t("add_room")):
                    if new_room.strip():
                        try:
                            add_room(new_room.strip())
                            st.success(t("room_added"))
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error(t("room_exists"))
                        except Exception as e:
                            st.error(f"{t('unexpected_error')}: {e}")

            rooms = get_rooms()
            if rooms:
                st.markdown("#### Room Default Prices (Admin)")
                room_rows = []
                for r in rooms:
                    room_rows.append(
                        {
                            "id": int(r["id"]),
                            "room": str(r["number"]),
                            "default_tariff": float(r["default_tariff"] or 0.0),
                            "default_tax": float(r["default_tax"] or 0.0),
                            "currency": _normalize_currency(r["currency"] or DEFAULT_CURRENCY),
                        }
                    )
                rdf = pd.DataFrame(room_rows)

                edited = st.data_editor(
                    rdf,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "id": st.column_config.NumberColumn(disabled=True, width="small"),
                        "room": st.column_config.TextColumn(disabled=True, width="small"),
                        "default_tariff": st.column_config.NumberColumn(width="small"),
                        "default_tax": st.column_config.NumberColumn(width="small"),
                        "currency": st.column_config.SelectboxColumn(options=["USD", "CRC"], width="small"),
                    },
                    disabled=["id", "room"],
                    key="room_defaults_editor",
                )

                if st.button("💾 Save room default prices", type="primary"):
                    # Apply updates row-by-row
                    for _, row in edited.iterrows():
                        update_room_defaults(
                            room_id=int(row["id"]),
                            default_tariff=float(row["default_tariff"] or 0.0),
                            default_tax=float(row["default_tax"] or 0.0),
                            currency=str(row["currency"] or DEFAULT_CURRENCY),
                        )
                    st.success("Saved.")
                    st.rerun()

                st.divider()
                st.write("**Delete rooms:**")
                for r in rooms:
                    room_id = int(r["id"])
                    room_number = str(r["number"])
                    a, b = st.columns([3, 1])
                    with a:
                        st.write(f"• {room_number}")
                    with b:
                        if st.button("🗑️", key=f"del_room_{room_id}"):
                            delete_room(room_id)
                            st.success(t("room_deleted"))
                            st.rerun()

        else:
            st.info(t("room_prices_admin_only"))

    elif view_key == "search_guests":
        st.subheader(t("search_guests"))

        top1, top2 = st.columns([4, 1])
        with top1:
            search_input = st.text_input(
                t("guest_name"),
                value=st.session_state.search_last_input,
                placeholder=t("search_placeholder"),
            )
        with top2:
            if st.button("🧹 " + t("clear_search"), use_container_width=True):
                st.session_state.search_last_input = ""
                st.session_state.search_active_name = None
                st.rerun()

        st.session_state.search_last_input = search_input

        if search_input and len(search_input.strip()) >= 2:
            suggestions = search_guests(search_input.strip(), limit=10)
            if suggestions:
                st.write(f"**{t('suggestions')}**")
                for s in suggestions:
                    if st.button("🔎 " + s, key=f"sugg_{s}", use_container_width=True):
                        st.session_state.search_active_name = s
                        st.rerun()
            else:
                st.info(t("no_results"))

        active_name = st.session_state.search_active_name
        if active_name and len(active_name.strip()) >= 2:
            guest_name = active_name.strip()
            reservations = get_guest_reservations(guest_name)

            st.divider()
            st.subheader(f"{t('results')}: {guest_name}")

            if reservations:
                table_data = []
                totals_by_currency: Dict[str, float] = {"USD": 0.0, "CRC": 0.0}
                total_nights = 0

                for res in reservations:
                    room_number = str(res["room_number"])
                    status = res["status"]
                    check_in_str = res["check_in"]
                    check_out_str = res["check_out"]
                    notes = res["notes"] or ""
                    num_guests = int(res["num_guests"] or 0)
                    tariff = float(res["tariff"] or 0.0)
                    tax_amt = float(res["tax"] or 0.0)
                    currency = _normalize_currency(res["currency"] or DEFAULT_CURRENCY)
                    updated_at = res["updated_at"] or ""

                    check_in = parse_iso(check_in_str)
                    check_out = parse_iso(check_out_str)
                    nn = nights(check_in, check_out)
                    total_nights += nn
                    stay_total = calc_total(tariff, tax_amt, nn)
                    totals_by_currency[currency] = totals_by_currency.get(currency, 0.0) + stay_total

                    table_data.append(
                        {
                            "Room": room_number,
                            "Check-in": check_in,
                            "Check-out": check_out,
                            "Nights": nn,
                            "PAX": num_guests,
                            "Tariff": fmt_money(tariff, currency),
                            "Tax": fmt_money(tax_amt, currency),
                            "Total": fmt_money(stay_total, currency),
                            "Status": STATUS_LABEL.get(status, status),
                            "Notes": notes,
                            "Updated": updated_at,
                        }
                    )

                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric(t("stays"), len(reservations))
                with m2:
                    st.metric(t("nights"), total_nights)
                with m3:
                    parts = []
                    for code in ["USD", "CRC"]:
                        amt = totals_by_currency.get(code, 0.0)
                        if abs(amt) > 0.0001:
                            parts.append(fmt_money(amt, code))
                    st.metric(t("totals_by_currency"), " / ".join(parts) if parts else "—")

                if st.button(t("export_csv")):
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label=t("download_csv"),
                        data=csv,
                        file_name=f"guest_history_{guest_name}.csv",
                        mime="text/csv",
                    )
            else:
                st.info(t("no_res_for_name"))

    elif view_key == "room_history":
        st.subheader(t("room_history"))
        st.caption(t("room_history_hint"))

        rooms = get_rooms()
        room_numbers = [str(r["number"]) for r in rooms]

        # Simple: pick a room (fastest UX)
        sel = st.selectbox(t("room"), [""] + room_numbers, index=0)
        if sel:
            st.session_state.room_history_selected = sel

        selected_room = st.session_state.get("room_history_selected") or ""
        if selected_room:
            res = get_room_reservations(selected_room, limit=500)
            st.divider()
            st.subheader(f"{t('results')}: {t('room')} {selected_room}")

            if not res:
                st.info(t("no_results"))
            else:
                table_data = []
                totals_by_currency: Dict[str, float] = {"USD": 0.0, "CRC": 0.0}
                total_nights = 0

                for r in res:
                    tariff = float(r["tariff"] or 0.0)
                    tax_amt = float(r["tax"] or 0.0)
                    currency = _normalize_currency(r["currency"] or DEFAULT_CURRENCY)
                    ci = parse_iso(r["check_in"])
                    co = parse_iso(r["check_out"])
                    nn = nights(ci, co)
                    total_nights += nn
                    total_amt = calc_total(tariff, tax_amt, nn)
                    totals_by_currency[currency] = totals_by_currency.get(currency, 0.0) + total_amt

                    table_data.append(
                        {
                            "Reservation ID": int(r["id"]),
                            "Guest": str(r["guest_name"] or ""),
                            "Check-in": ci,
                            "Check-out": co,
                            "Nights": nn,
                            "PAX": int(r["num_guests"] or 0),
                            "Status": STATUS_LABEL.get(str(r["status"]), str(r["status"])),
                            "Tariff": fmt_money(tariff, currency),
                            "Tax": fmt_money(tax_amt, currency),
                            "Total": fmt_money(total_amt, currency),
                            "Notes": str(r["notes"] or ""),
                            "Updated": str(r["updated_at"] or ""),
                        }
                    )

                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric(t("stays"), len(res))
                with m2:
                    st.metric(t("nights"), total_nights)
                with m3:
                    parts = []
                    for code in ["USD", "CRC"]:
                        amt = totals_by_currency.get(code, 0.0)
                        if abs(amt) > 0.0001:
                            parts.append(fmt_money(amt, code))
                    st.metric(t("totals_by_currency"), " / ".join(parts) if parts else "—")

                if st.button(t("export_csv")):
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label=t("download_csv"),
                        data=csv,
                        file_name=f"room_history_{selected_room}.csv",
                        mime="text/csv",
                    )

    elif view_key == "settings":
        st.subheader(t("settings"))

        st.markdown(f"### {t('language')}")
        lang_choice = st.selectbox(
            t("choose_language"),
            ["en", "es"],
            format_func=lambda x: t("english") if x == "en" else t("spanish"),
            index=0 if st.session_state.lang == "en" else 1,
            key="lang_selectbox",
        )

        if st.button(t("save_language"), key="save_lang"):
            st.session_state.lang = lang_choice
            set_setting("lang", lang_choice)
            st.success(t("lang_saved"))
            st.rerun()

        st.divider()
        st.info(f"{t('latest_backup')}: {get_latest_backup_name()}")

        if is_admin():
            st.markdown("### Backups")
            latest = get_latest_backup_path()
            if latest:
                st.caption(f"{t('last_backup')}: {os.path.basename(latest)}")
            else:
                st.info(t("no_backups"))

            colb1, colb2 = st.columns(2)
            with colb1:
                if st.button(t("backup_now"), type="primary"):
                    path = create_backup(force=True)
                    if path:
                        log_audit("BACKUP", "database", None, f"Created backup {os.path.basename(path)}")
                        st.success(t("backup_created"))
                        st.rerun()

            with colb2:
                latest = get_latest_backup_path()
                if latest and os.path.exists(latest):
                    with open(latest, "rb") as f:
                        st.download_button(
                            label=t("download_latest_backup"),
                            data=f.read(),
                            file_name=os.path.basename(latest),
                            mime="application/octet-stream",
                            use_container_width=True,
                        )
                else:
                    st.button(t("download_latest_backup"), disabled=True, use_container_width=True)

            st.divider()
            st.markdown(f"### {t('db_mgmt')}")

            if st.button(t("clear_all_res"), type="secondary"):
                st.session_state.confirm_clear_all = True

            if st.session_state.confirm_clear_all:
                st.warning(t("clear_all_confirm"))
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(t("confirm_action"), type="primary"):
                        with db() as conn:
                            conn.execute("DELETE FROM reservations;")
                        log_audit("DELETE_ALL", "reservations", None, "Cleared all reservations")
                        st.session_state.confirm_clear_all = False
                        st.success("OK")
                        st.rerun()
                with c2:
                    if st.button(t("cancel")):
                        st.session_state.confirm_clear_all = False
                        st.rerun()

            st.divider()

            if st.button(t("reset_rooms"), type="secondary"):
                st.session_state.confirm_reset_rooms = True

            if st.session_state.confirm_reset_rooms:
                st.warning(t("reset_rooms_confirm"))
                r1, r2 = st.columns(2)
                with r1:
                    if st.button(t("confirm_action"), type="primary", key="confirm_reset_rooms_btn"):
                        with db() as conn:
                            conn.execute("DELETE FROM rooms;")
                            for num in default_room_numbers():
                                conn.execute(
                                    "INSERT OR IGNORE INTO rooms(number, default_tariff, default_tax, currency) VALUES (?,?,?,?);",
                                    (num, 0.0, 0.0, DEFAULT_CURRENCY),
                                )
                        log_audit("RESET", "rooms", None, "Reset rooms to defaults")
                        st.session_state.confirm_reset_rooms = False
                        st.success(t("rooms_reset"))
                        st.rerun()
                with r2:
                    if st.button(t("cancel"), key="cancel_reset_rooms_btn"):
                        st.session_state.confirm_reset_rooms = False
                        st.rerun()

            st.divider()
            st.markdown(f"### {t('audit_log')}")
            st.caption(t("audit_hint"))

            audit_df = get_audit_log(limit=300)
            st.dataframe(audit_df, use_container_width=True, hide_index=True)

            if st.button(t("audit_export")):
                csv = audit_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=t("audit_download"),
                    data=csv,
                    file_name=f"audit_log_{date.today().isoformat()}.csv",
                    mime="text/csv",
                )

        st.divider()
        st.markdown("### About")
        st.write(f"Isla Verde Hotel Manager {APP_VERSION}")
        st.write("El Roll System")
        st.caption("© 2024 Hotel Isla Verde")

except Exception:
    # Don’t leak full exception details to non-admin users
    if is_admin():
        st.exception(Exception("Unhandled error"))  # keeps stack in admin view
    else:
        st.error(t("unexpected_error"))
    st.stop()
