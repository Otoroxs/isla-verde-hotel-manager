import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict

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
        "el_roll": "El Roll",
        "settings": "Settings",
        "admin_sensitive": "Admin (sensitive view)",
        "admin_mode_on": "Admin mode: ON",
        "disable_admin": "Disable admin",
        "admin_password": "Admin password",
        "unlock_admin": "Unlock admin",
        "type_admin_pass": "Type admin pass…",
        "logout": "Logout",
        "selected_date": "Selected date:",
        "el_roll_header": "El Roll - Daily Occupancy",
        "el_roll_caption": "Manage daily room assignments and view occupancy.",
        "add_reservation": "Add Reservation",
        "room": "Room",
        "select_room": "Select room",
        "guest_name": "Guest name",
        "num_guests": "Number of people",
        "tariff": "Tariff (€)",
        "observations": "Observations",
        "add": "Add",
        "update": "Update",
        "delete": "Delete",
        "daily_overview": "Daily Overview",
        "search_placeholder": "Search by room or guest...",
        "all_rooms": "All Rooms",
        "filter_by_status": "Filter by status",
        "all_statuses": "All Statuses",
        "status": "Status",
        "checkin": "Check-in",
        "checkout": "Check-out",
        "nights": "Nights",
        "reserved": "Reserved",
        "checkedin": "Checked In",
        "noshow": "No Show",
        "checkedout": "Checked Out",
        "available": "Available",
        "occupied": "Occupied",
        "edit": "Edit",
        "save": "Save",
        "cancel": "Cancel",
        "no_reservations": "No reservations for selected date.",
        "saved": "Saved.",
        "deleted": "Deleted.",
        "guest_required": "Guest name is required.",
        "room_required": "Room selection is required.",
        "invalid_tariff": "Tariff must be a positive number.",
        "prev_day": "◀",
        "next_day": "▶",
        "today": "Today",
        "date": "Date",
        "total_guests": "Total Guests",
        "total_revenue": "Total Revenue",
        "occupancy_rate": "Occupancy Rate",
        "export_csv": "Export to CSV",
        "language": "Language",
        "choose_language": "Choose language",
        "english": "English",
        "spanish": "Spanish",
        "save_language": "Save language",
        "lang_saved": "Language saved. Refreshing…",
        "rooms_manage": "Manage Rooms",
        "new_room": "New room number",
        "add_room": "Add room",
        "room_added": "Room added.",
        "room_exists": "Room already exists.",
        "delete_room": "Delete room",
        "existing_rooms": "Existing Rooms",
        "no_rooms": "No rooms exist. Add rooms first.",
        "blackouts_header": "Blackout Dates",
        "blackouts_caption": "Dates when no reservations are allowed.",
        "title": "Title",
        "start_date": "Start date",
        "end_date": "End date",
        "notes": "Notes",
        "add_blackout": "Add blackout",
        "existing_blackouts": "Existing Blackouts",
        "no_blackouts": "No blackouts set.",
        "clear_filters": "Clear filters",
    },
    "es": {
        "app_title": "Administrador del Hotel Isla Verde",
        "enter_password": "Introduce la contraseña para acceder.",
        "password": "Contraseña",
        "log_in": "Entrar",
        "incorrect_password": "Contraseña incorrecta.",
        "menu": "Menú",
        "go_to": "Ir a",
        "el_roll": "El Roll",
        "settings": "Ajustes",
        "admin_sensitive": "Admin (vista sensible)",
        "admin_mode_on": "Modo admin: ACTIVADO",
        "disable_admin": "Desactivar admin",
        "admin_password": "Contraseña admin",
        "unlock_admin": "Desbloquear admin",
        "type_admin_pass": "Escribe la contraseña admin…",
        "logout": "Cerrar sesión",
        "selected_date": "Fecha seleccionada:",
        "el_roll_header": "El Roll - Ocupación Diaria",
        "el_roll_caption": "Gestiona asignaciones diarias y visualiza la ocupación.",
        "add_reservation": "Añadir Reserva",
        "room": "Habitación",
        "select_room": "Seleccionar habitación",
        "guest_name": "Nombre del huésped",
        "num_guests": "Número de personas",
        "tariff": "Tarifa (€)",
        "observations": "Observaciones",
        "add": "Añadir",
        "update": "Actualizar",
        "delete": "Borrar",
        "daily_overview": "Vista Diaria",
        "search_placeholder": "Buscar por habitación o huésped...",
        "all_rooms": "Todas las habitaciones",
        "filter_by_status": "Filtrar por estado",
        "all_statuses": "Todos los estados",
        "status": "Estado",
        "checkin": "Entrada",
        "checkout": "Salida",
        "nights": "Noches",
        "reserved": "Reservado",
        "checkedin": "Check-in",
        "noshow": "No se presentó",
        "checkedout": "Salida",
        "available": "Disponible",
        "occupied": "Ocupada",
        "edit": "Editar",
        "save": "Guardar",
        "cancel": "Cancelar",
        "no_reservations": "No hay reservas para la fecha seleccionada.",
        "saved": "Guardado.",
        "deleted": "Borrado.",
        "guest_required": "El nombre del huésped es obligatorio.",
        "room_required": "La selección de habitación es obligatoria.",
        "invalid_tariff": "La tarifa debe ser un número positivo.",
        "prev_day": "◀",
        "next_day": "▶",
        "today": "Hoy",
        "date": "Fecha",
        "total_guests": "Total Huéspedes",
        "total_revenue": "Ingreso Total",
        "occupancy_rate": "Tasa de Ocupación",
        "export_csv": "Exportar a CSV",
        "language": "Idioma",
        "choose_language": "Elegir idioma",
        "english": "Inglés",
        "spanish": "Español",
        "save_language": "Guardar idioma",
        "lang_saved": "Idioma guardado. Actualizando…",
        "rooms_manage": "Gestionar Habitaciones",
        "new_room": "Nuevo número de habitación",
        "add_room": "Añadir habitación",
        "room_added": "Habitación añadida.",
        "room_exists": "La habitación ya existe.",
        "delete_room": "Borrar habitación",
        "existing_rooms": "Habitaciones Existentes",
        "no_rooms": "No hay habitaciones. Añade habitaciones primero.",
        "blackouts_header": "Fechas de Cierre",
        "blackouts_caption": "Fechas en las que no se permiten reservas.",
        "title": "Título",
        "start_date": "Fecha inicio",
        "end_date": "Fecha fin",
        "notes": "Notas",
        "add_blackout": "Añadir cierre",
        "existing_blackouts": "Cierres Existentes",
        "no_blackouts": "No hay cierres establecidos.",
        "clear_filters": "Limpiar filtros",
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

def init_db():
    conn = db()

    # Rooms table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL UNIQUE
        );
    """)

    # Reservations table
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
            tariff REAL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
        );
    """)

    # Blackouts table
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

    # Settings table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)

    # Add some default rooms if none exist
    cur = conn.execute("SELECT COUNT(*) FROM rooms;")
    if cur.fetchone()[0] == 0:
        for n in range(101, 111):
            conn.execute("INSERT OR IGNORE INTO rooms(number) VALUES (?);", (str(n),))
        conn.commit()

    conn.close()

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

# ----------------- ROOM MANAGEMENT -----------------
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

def delete_room(room_id: int):
    conn = db()
    conn.execute("DELETE FROM rooms WHERE id=?;", (room_id,))
    conn.commit()
    conn.close()

# ----------------- RESERVATION MANAGEMENT -----------------
def get_reservations_for_date(selected_date: date, search_term: str = "", room_filter: str = "", status_filter: str = ""):
    conn = db()
    
    query = """
        SELECT r.id, rm.number, r.guest_name, r.status, r.check_in, r.check_out, 
               r.num_guests, r.tariff, r.notes
        FROM reservations r
        JOIN rooms rm ON r.room_id = rm.id
        WHERE r.check_in <= ? AND ? < r.check_out
    """
    
    params = [iso(selected_date), iso(selected_date)]
    
    if search_term:
        query += " AND (LOWER(r.guest_name) LIKE LOWER(?) OR LOWER(rm.number) LIKE LOWER(?))"
        params.extend([f"%{search_term}%", f"%{search_term}%"])
    
    if room_filter and room_filter != t("all_rooms"):
        query += " AND rm.number = ?"
        params.append(room_filter)
    
    if status_filter and status_filter != t("all_statuses"):
        query += " AND r.status = ?"
        params.append(status_filter)
    
    query += " ORDER BY rm.number"
    
    return conn.execute(query, params).fetchall()

def get_reservation(res_id: int):
    return db().execute("""
        SELECT r.id, rm.number, r.guest_name, r.status, r.check_in, r.check_out,
               r.num_guests, r.tariff, r.notes, r.room_id
        FROM reservations r
        JOIN rooms rm ON r.room_id = rm.id
        WHERE r.id = ?
    """, (res_id,)).fetchone()

def save_reservation(res_id=None, room_id=None, guest_name="", status="reserved", 
                     check_in=None, check_out=None, num_guests=1, tariff=0, notes=""):
    conn = db()
    tstamp = now_utc()
    
    if res_id:  # Update existing
        conn.execute("""
            UPDATE reservations 
            SET room_id=?, guest_name=?, status=?, check_in=?, check_out=?, 
                num_guests=?, tariff=?, notes=?, updated_at=?
            WHERE id=?
        """, (room_id, guest_name, status, iso(check_in), iso(check_out), 
              num_guests, tariff, notes, tstamp, res_id))
    else:  # Insert new
        conn.execute("""
            INSERT INTO reservations 
            (room_id, guest_name, status, check_in, check_out, num_guests, tariff, notes, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (room_id, guest_name, status, iso(check_in), iso(check_out), 
              num_guests, tariff, notes, tstamp, tstamp))
        res_id = conn.execute("SELECT last_insert_rowid();").fetchone()[0]
    
    conn.commit()
    conn.close()
    return res_id

def delete_reservation(res_id: int):
    conn = db()
    conn.execute("DELETE FROM reservations WHERE id=?;", (res_id,))
    conn.commit()
    conn.close()

def get_available_rooms(selected_date: date, room_id_to_exclude=None):
    """Get rooms that are available on a given date"""
    conn = db()
    
    # Get all rooms
    all_rooms = conn.execute("SELECT id, number FROM rooms ORDER BY number;").fetchall()
    
    # Get occupied rooms for this date
    occupied = conn.execute("""
        SELECT DISTINCT room_id 
        FROM reservations 
        WHERE check_in <= ? AND ? < check_out 
          AND status NOT IN ('noshow', 'checkedout')
    """, (iso(selected_date), iso(selected_date))).fetchall()
    
    occupied_ids = {row[0] for row in occupied}
    
    # Filter out occupied rooms
    available_rooms = []
    for room_id, room_number in all_rooms:
        if room_id_to_exclude and room_id == room_id_to_exclude:
            available_rooms.append((room_id, room_number, True))  # Include it even if occupied (for editing)
        elif room_id not in occupied_ids:
            available_rooms.append((room_id, room_number, True))
        else:
            available_rooms.append((room_id, room_number, False))
    
    conn.close()
    return available_rooms

# ----------------- BLACKOUT MANAGEMENT -----------------
def get_blackouts():
    return db().execute("""
        SELECT id, title, start_date, end_date, notes
        FROM blackouts 
        ORDER BY start_date DESC;
    """).fetchall()

def add_blackout(title: str, start_date: date, end_date: date, notes: str = ""):
    conn = db()
    conn.execute("""
        INSERT INTO blackouts (title, start_date, end_date, notes, created_at)
        VALUES (?,?,?,?,?)
    """, (title, iso(start_date), iso(end_date), notes, now_utc()))
    conn.commit()
    conn.close()

def delete_blackout(blackout_id: int):
    conn = db()
    conn.execute("DELETE FROM blackouts WHERE id=?;", (blackout_id,))
    conn.commit()
    conn.close()

def is_blackout_date(check_date: date) -> bool:
    """Check if a date falls within any blackout period"""
    conn = db()
    result = conn.execute("""
        SELECT COUNT(*) FROM blackouts 
        WHERE start_date <= ? AND ? < end_date
    """, (iso(check_date), iso(check_date))).fetchone()
    conn.close()
    return result[0] > 0

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
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()
if "editing_reservation" not in st.session_state:
    st.session_state.editing_reservation = None
if "search_term" not in st.session_state:
    st.session_state.search_term = ""
if "room_filter" not in st.session_state:
    st.session_state.room_filter = ""
if "status_filter" not in st.session_state:
    st.session_state.status_filter = ""

# load language from DB
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
view = st.sidebar.radio(t("go_to"), [t("el_roll"), t("settings")], index=0)

VIEW_MAP = {
    t("el_roll"): "El Roll",
    t("settings"): "Settings",
}
view_key = VIEW_MAP[view]

# admin sidebar
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
selected_date = st.session_state.selected_date
st.title(t("app_title"))
st.caption(f"{t('selected_date')} {selected_date}")

# ----------------- EL ROLL VIEW -----------------
if view_key == "El Roll":
    st.subheader(t("el_roll_header"))
    st.caption(t("el_roll_caption"))
    
    # Date Navigation
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    with col1:
        if st.button(t("prev_day"), use_container_width=True):
            st.session_state.selected_date -= timedelta(days=1)
            st.rerun()
    with col2:
        if st.button(t("today"), use_container_width=True):
            st.session_state.selected_date = date.today()
            st.rerun()
    with col3:
        st.markdown(f"### {selected_date.strftime('%A, %B %d, %Y')}")
    with col4:
        if st.button(t("next_day"), use_container_width=True):
            st.session_state.selected_date += timedelta(days=1)
            st.rerun()
    with col5:
        # Custom date selector
        new_date = st.date_input(
            t("date"),
            value=selected_date,
            label_visibility="collapsed",
            key="date_selector"
        )
        if new_date != selected_date:
            st.session_state.selected_date = new_date
            st.rerun()
    
    # Check for blackout
    if is_blackout_date(selected_date):
        st.warning("⚠️ This date is marked as a blackout/holiday. No new reservations allowed.")
    
    # Add/Edit Reservation Form
    st.markdown("---")
    st.markdown(f"### {t('add_reservation')}")
    
    # Get available rooms for this date
    available_rooms = get_available_rooms(selected_date, 
                                        room_id_to_exclude=st.session_state.get("editing_room_id"))
    
    # Create room options for dropdown
    room_options = []
    room_status = {}
    for room_id, room_number, is_available in available_rooms:
        if is_available:
            room_options.append((room_id, f"{room_number} ✅"))
            room_status[room_id] = "available"
        else:
            room_options.append((room_id, f"{room_number} ⚠️ (Occupied)"))
            room_status[room_id] = "occupied"
    
    # If editing, get the reservation data
    editing_data = None
    if st.session_state.editing_reservation:
        editing_data = get_reservation(st.session_state.editing_reservation)
    
    with st.form("reservation_form"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Room selection
            if room_options:
                # Find the index of the currently selected room if editing
                default_idx = 0
                if editing_data:
                    for idx, (room_id, label) in enumerate(room_options):
                        if room_id == editing_data[10]:  # room_id is at index 10
                            default_idx = idx
                            break
                
                room_id = st.selectbox(
                    t("room"),
                    options=[r[0] for r in room_options],
                    format_func=lambda x: dict(room_options)[x],
                    index=default_idx,
                    key="form_room"
                )
            else:
                st.error(t("no_rooms"))
                room_id = None
        
        with col2:
            # Guest name
            guest_name = st.text_input(
                t("guest_name"),
                value=editing_data[2] if editing_data else "",
                key="form_guest"
            )
        
        with col3:
            # Number of guests
            num_guests = st.number_input(
                t("num_guests"),
                min_value=1,
                max_value=20,
                value=editing_data[6] if editing_data else 1,
                key="form_num_guests"
            )
        
        with col4:
            # Tariff
            tariff = st.number_input(
                t("tariff"),
                min_value=0.0,
                value=float(editing_data[7]) if editing_data else 0.0,
                step=10.0,
                format="%.2f",
                key="form_tariff"
            )
        
        # Observations
        observations = st.text_area(
            t("observations"),
            value=editing_data[8] if editing_data else "",
            height=80,
            key="form_notes"
        )
        
        # Status and dates (hidden for simplicity, but can be shown for editing)
        if editing_data:
            status = st.selectbox(
                t("status"),
                [s[0] for s in STATUSES],
                format_func=lambda x: dict(STATUSES)[x],
                index=[s[0] for s in STATUSES].index(editing_data[3]) if editing_data else 0,
                key="form_status"
            )
            
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                check_in = st.date_input(
                    t("checkin"),
                    value=parse_iso(editing_data[4]) if editing_data else selected_date,
                    key="form_checkin"
                )
            with col_date2:
                check_out = st.date_input(
                    t("checkout"),
                    value=parse_iso(editing_data[5]) if editing_data else (selected_date + timedelta(days=1)),
                    key="form_checkout"
                )
        else:
            status = "checkedin"  # Default for new reservations
            check_in = selected_date
            check_out = selected_date + timedelta(days=1)
        
        # Form buttons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            submit_button = st.form_submit_button(
                t("update") if editing_data else t("add"),
                type="primary",
                use_container_width=True
            )
        with col_btn2:
            if editing_data:
                cancel_button = st.form_submit_button(
                    t("cancel"),
                    type="secondary",
                    use_container_width=True
                )
                if cancel_button:
                    st.session_state.editing_reservation = None
                    st.rerun()
        
        if submit_button:
            if not guest_name.strip():
                st.error(t("guest_required"))
            elif not room_id:
                st.error(t("room_required"))
            elif tariff < 0:
                st.error(t("invalid_tariff"))
            else:
                # Save the reservation
                res_id = save_reservation(
                    res_id=st.session_state.editing_reservation,
                    room_id=room_id,
                    guest_name=guest_name.strip(),
                    status=status,
                    check_in=check_in,
                    check_out=check_out,
                    num_guests=num_guests,
                    tariff=tariff,
                    notes=observations
                )
                
                st.success(t("saved"))
                st.session_state.editing_reservation = None
                st.rerun()
    
    # Search and Filter Section
    st.markdown("---")
    st.markdown(f"### {t('daily_overview')}")
    
    with st.expander("🔍 Search & Filters", expanded=True):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            search_input = st.text_input(
                "",
                value=st.session_state.search_term,
                placeholder=t("search_placeholder"),
                key="search_input"
            )
        
        with col2:
            rooms_list = [t("all_rooms")] + [r[1] for r in get_rooms()]
            room_filter = st.selectbox(
                t("room"),
                rooms_list,
                index=rooms_list.index(st.session_state.room_filter) if st.session_state.room_filter in rooms_list else 0,
                key="room_filter_select",
                label_visibility="collapsed"
            )
        
        with col3:
            status_list = [t("all_statuses")] + [dict(STATUSES).get(s[0], s[0]) for s in STATUSES]
            status_filter = st.selectbox(
                t("status"),
                status_list,
                index=0,
                key="status_filter_select",
                label_visibility="collapsed"
            )
        
        with col4:
            col4a, col4b = st.columns(2)
            with col4a:
                if st.button("🔍", use_container_width=True, key="apply_search"):
                    st.session_state.search_term = search_input
                    st.session_state.room_filter = room_filter if room_filter != t("all_rooms") else ""
                    st.session_state.status_filter = status_filter if status_filter != t("all_statuses") else ""
                    st.rerun()
            with col4b:
                if st.button("🗑️", use_container_width=True, key="clear_filters"):
                    st.session_state.search_term = ""
                    st.session_state.room_filter = ""
                    st.session_state.status_filter = ""
                    st.rerun()
    
    # Get reservations for selected date
    reservations = get_reservations_for_date(
        selected_date,
        st.session_state.search_term,
        st.session_state.room_filter,
        st.session_state.status_filter
    )
    
    # Display metrics
    if reservations:
        total_guests = sum(r[6] for r in reservations)
        total_revenue = sum(r[7] for r in reservations)
        total_rooms = len(set(r[1] for r in reservations))
        all_rooms_count = len(get_rooms())
        occupancy_rate = (total_rooms / all_rooms_count * 100) if all_rooms_count > 0 else 0
        
        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric(t("room"), f"{total_rooms}/{all_rooms_count}")
        with metric_cols[1]:
            st.metric(t("total_guests"), total_guests)
        with metric_cols[2]:
            st.metric(t("total_revenue"), f"€{total_revenue:,.2f}")
        with metric_cols[3]:
            st.metric(t("occupancy_rate"), f"{occupancy_rate:.1f}%")
    
    # Display reservations table
    st.markdown("---")
    
    if not reservations:
        st.info(t("no_reservations"))
    else:
        # Create a DataFrame for display
        data = []
        for res in reservations:
            res_id, room_num, guest_name, status, check_in, check_out, num_guests, tariff, notes = res
            
            # Calculate nights
            nights_stay = nights(parse_iso(check_in), parse_iso(check_out))
            
            # Status badge with color
            status_badge = ""
            if status == "checkedin":
                status_badge = "🟢"
            elif status == "reserved":
                status_badge = "🟡"
            elif status == "noshow":
                status_badge = "🔴"
            elif status == "checkedout":
                status_badge = "⚪"
            
            data.append({
                t("room"): room_num,
                t("guest_name"): guest_name,
                t("num_guests"): num_guests,
                t("tariff"): f"€{tariff:,.2f}",
                t("observations"): notes,
                t("status"): f"{status_badge} {dict(STATUSES).get(status, status)}",
                t("nights"): nights_stay,
                "check_in": check_in,
                "check_out": check_out,
                "res_id": res_id
            })
        
        df = pd.DataFrame(data)
        
        # Configure columns for display
        column_config = {
            t("room"): st.column_config.TextColumn(
                t("room"),
                width="small"
            ),
            t("guest_name"): st.column_config.TextColumn(
                t("guest_name"),
                width="medium"
            ),
            t("num_guests"): st.column_config.NumberColumn(
                t("num_guests"),
                width="small"
            ),
            t("tariff"): st.column_config.TextColumn(
                t("tariff"),
                width="small"
            ),
            t("observations"): st.column_config.TextColumn(
                t("observations"),
                width="large"
            ),
            t("status"): st.column_config.TextColumn(
                t("status"),
                width="medium"
            ),
            t("nights"): st.column_config.NumberColumn(
                t("nights"),
                width="small"
            ),
            "edit": st.column_config.LinkColumn(
                "Edit",
                display_text="✏️",
                width="small"
            ),
            "delete": st.column_config.LinkColumn(
                "Delete",
                display_text="🗑️",
                width="small"
            )
        }
        
        # Add edit and delete columns
        df["edit"] = ["/edit_" + str(row["res_id"]) for _, row in df.iterrows()]
        df["delete"] = ["/delete_" + str(row["res_id"]) for _, row in df.iterrows()]
        
        # Display the dataframe
        edited_df = st.dataframe(
            df[[t("room"), t("guest_name"), t("num_guests"), t("tariff"), 
                t("observations"), t("status"), t("nights"), "edit", "delete"]],
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
        
        # Handle edit/delete clicks
        if hasattr(edited_df, 'selection'):
            if edited_df.selection:
                selected_row = edited_df.selection[0]
                action = selected_row.get("action")
                if action and action.startswith("/edit_"):
                    res_id = int(action.split("_")[1])
                    st.session_state.editing_reservation = res_id
                    st.rerun()
                elif action and action.startswith("/delete_"):
                    res_id = int(action.split("_")[1])
                    delete_reservation(res_id)
                    st.success(t("deleted"))
                    st.rerun()
        
        # Export button
        if st.button(t("export_csv"), type="secondary"):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"el_roll_{selected_date}.csv",
                mime="text/csv"
            )

# ----------------- SETTINGS VIEW -----------------
elif view_key == "Settings":
    st.subheader(t("settings"))
    
    tab1, tab2, tab3 = st.tabs([t("language"), t("rooms_manage"), t("blackouts_header")])
    
    with tab1:
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
    
    with tab2:
        st.markdown(f"### {t('rooms_manage')}")
        
        # Add new room
        col1, col2 = st.columns([2, 1])
        with col1:
            new_room = st.text_input(t("new_room"), placeholder="e.g., 101")
        with col2:
            if st.button(t("add_room"), use_container_width=True):
                if new_room.strip():
                    try:
                        add_room(new_room.strip())
                        st.success(t("room_added"))
                        st.rerun()
                    except:
                        st.error(t("room_exists"))
                else:
                    st.error("Please enter a room number")
        
        st.markdown("---")
        st.markdown(f"#### {t('existing_rooms')}")
        
        rooms = get_rooms()
        if not rooms:
            st.info(t("no_rooms"))
        else:
            # Display rooms in a grid
            cols = st.columns(4)
            for idx, (room_id, room_num) in enumerate(rooms):
                with cols[idx % 4]:
                    with st.container():
                        st.markdown(f"**{room_num}**")
                        if st.button(t("delete_room"), key=f"del_room_{room_id}", use_container_width=True):
                            delete_room(room_id)
                            st.success(t("deleted"))
                            st.rerun()
    
    with tab3:
        st.markdown(f"### {t('blackouts_header')}")
        st.caption(t("blackouts_caption"))
        
        # Add blackout form
        with st.form("add_blackout_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input(t("title"), placeholder="e.g., Christmas Closure")
                start_date = st.date_input(t("start_date"), value=date.today())
            with col2:
                end_date = st.date_input(t("end_date"), value=date.today() + timedelta(days=1))
                notes = st.text_area(t("notes"), height=80)
            
            if st.form_submit_button(t("add_blackout"), type="primary"):
                if not title.strip():
                    st.error("Title is required")
                elif start_date >= end_date:
                    st.error("End date must be after start date")
                else:
                    add_blackout(title, start_date, end_date, notes)
                    st.success("Blackout added")
                    st.rerun()
        
        st.markdown("---")
        st.markdown(f"#### {t('existing_blackouts')}")
        
        blackouts = get_blackouts()
        if not blackouts:
            st.info(t("no_blackouts"))
        else:
            for blackout_id, title, start, end, notes in blackouts:
                with st.expander(f"{title} ({start} to {end})"):
                    st.write(f"**Dates:** {start} - {end}")
                    if notes:
                        st.write(f"**Notes:** {notes}")
                    
                    if st.button(t("delete"), key=f"del_blackout_{blackout_id}"):
                        delete_blackout(blackout_id)
                        st.success("Blackout deleted")
                        st.rerun()