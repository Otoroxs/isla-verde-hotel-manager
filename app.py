import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Optional, List
from contextlib import contextmanager

# ----------------- CONFIG -----------------
DB_PATH = "hotel.db"

APP_PASSWORD = st.secrets.get("APP_PASSWORD", "islaverde")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin000")

STATUSES = [
    ("reserved", "Reserved"),
    ("checkedin", "Checked In"),
    ("noshow", "No Show"),
    ("checkedout", "Checked Out"),
]
STATUS_LABEL = {k: v for k, v in STATUSES}


# ----------------- I18N -----------------
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
        "register_guests": "Register Guests",
        "search_guests": "Search Guests",
        "settings": "Settings",
        "logout": "Logout",
        "admin_sensitive": "Admin (sensitive view)",
        "admin_mode_on": "Admin mode: ON",
        "disable_admin": "Disable admin",
        "admin_password": "Admin password",
        "unlock_admin": "Unlock admin",
        "type_admin_pass": "Type admin pass…",
        "today": "Today",
        "prev": "◀",
        "next": "▶",
        "guest_name": "Reservation Name",
        "pax": "PAX",
        "tariff": "Tariff",
        "observations": "Observations",
        "status": "Status",
        "available": "Available",
        "room": "Room",
        "save": "Save",
        "update": "Update",
        "delete": "Delete",
        "edit": "Edit",
        "saved": "Saved successfully!",
        "deleted": "Deleted successfully!",
        "search_placeholder": "Search guests…",
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
        "guest_required": "Reservation name is required",
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
        "history_for": "History for",
        "select_to_edit": "Select",
        "select_row_hint": "Tick a row in Select to edit below.",
        "clear_selection": "Clear selection",
        "edit_from_elroll": "Edit from El Roll",
        "db_mgmt": "Database Management",
        "clear_all_res": "Clear All Reservations",
        "clear_all_confirm": "Are you sure? This cannot be undone.",
        "reset_rooms": "Reset to Default Rooms",
        "reset_rooms_confirm": "Reset all rooms to configured defaults?",
        "rooms_reset": "Rooms reset to defaults!",
        "suggestions": "Suggestions",
        "open_guest": "Open",
        "register_success": "Register successful",
        "quick_actions": "Quick actions",
        "clear_search": "Clear search",
        "results": "Results",
        "no_res_for_guest": "No reservations found for this name.",
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
        "register_guests": "Registrar Huéspedes",
        "search_guests": "Buscar Huéspedes",
        "settings": "Ajustes",
        "logout": "Cerrar sesión",
        "admin_sensitive": "Admin (vista sensible)",
        "admin_mode_on": "Modo admin: ACTIVADO",
        "disable_admin": "Desactivar admin",
        "admin_password": "Contraseña admin",
        "unlock_admin": "Desbloquear admin",
        "type_admin_pass": "Escribe la contraseña admin…",
        "today": "Hoy",
        "prev": "◀",
        "next": "▶",
        "guest_name": "Nombre de la Reserva",
        "pax": "PAX",
        "tariff": "Tarifa",
        "observations": "Observaciones",
        "status": "Estado",
        "available": "Disponible",
        "room": "Habitación",
        "save": "Guardar",
        "update": "Actualizar",
        "delete": "Borrar",
        "edit": "Editar",
        "saved": "¡Guardado exitosamente!",
        "deleted": "¡Borrado exitosamente!",
        "search_placeholder": "Buscar huéspedes…",
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
        "guest_required": "El nombre de la reserva es obligatorio",
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
        "history_for": "Historial de",
        "select_to_edit": "Seleccionar",
        "select_row_hint": "Marca una fila en Seleccionar para editar abajo.",
        "clear_selection": "Borrar selección",
        "edit_from_elroll": "Editar desde El Roll",
        "db_mgmt": "Gestión de Base de Datos",
        "clear_all_res": "Borrar Todas las Reservas",
        "clear_all_confirm": "¿Seguro? Esto no se puede deshacer.",
        "reset_rooms": "Restablecer habitaciones",
        "reset_rooms_confirm": "¿Restablecer todas las habitaciones a los valores por defecto?",
        "rooms_reset": "¡Habitaciones restauradas!",
        "suggestions": "Sugerencias",
        "open_guest": "Abrir",
        "register_success": "Registro exitoso",
        "quick_actions": "Acciones rápidas",
        "clear_search": "Limpiar búsqueda",
        "results": "Resultados",
        "no_res_for_guest": "No hay reservas para este nombre.",
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("lang", "en")
    return TEXT.get(lang, TEXT["en"]).get(key, key)


# ----------------- DEFAULT ROOMS -----------------
def default_room_numbers() -> List[str]:
    nums: List[int] = []
    nums += list(range(101, 108))  # 101-107
    nums += list(range(201, 212))  # 201-211
    nums += list(range(214, 220))  # 214-219
    nums += list(range(221, 229))  # 221-228
    nums += list(range(301, 309))  # 301-308
    return [str(n) for n in nums]


# ----------------- DB HELPERS -----------------
@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()


def now_utc() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def iso(d: date) -> str:
    return d.isoformat()


def parse_iso(s: str) -> date:
    return date.fromisoformat(s)


def nights(ci: date, co: date) -> int:
    return (co - ci).days


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
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        conn.commit()
        row = conn.execute("SELECT value FROM settings WHERE key=?;", (key,)).fetchone()
        return row[0] if row else default


def set_setting(key: str, value: str):
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        conn.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value;",
            (key, value),
        )
        conn.commit()


def init_db():
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT NOT NULL UNIQUE
            );
            """
        )

        conn.execute(
            """
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
            """
        )

        ensure_column(conn, "reservations", "tariff REAL DEFAULT 0", "tariff")
        conn.commit()

        cur = conn.execute("SELECT COUNT(*) FROM rooms;")
        if cur.fetchone()[0] == 0:
            for num in default_room_numbers():
                conn.execute("INSERT OR IGNORE INTO rooms(number) VALUES (?);", (num,))
            conn.commit()


# ----------------- DATA FUNCTIONS -----------------
def normalize_guest_name(name: str) -> str:
    return " ".join((name or "").strip().split())


def get_rooms():
    with db() as conn:
        return conn.execute("SELECT id, number FROM rooms ORDER BY number;").fetchall()


def add_room(num: str):
    with db() as conn:
        conn.execute("INSERT INTO rooms(number) VALUES (?);", (num.strip(),))
        conn.commit()


def delete_room(rid: int):
    with db() as conn:
        conn.execute("DELETE FROM rooms WHERE id=?;", (rid,))
        conn.commit()


def get_reservations_for_date(selected_date: date):
    with db() as conn:
        return conn.execute(
            """
            SELECT r.id, rm.number, r.guest_name, r.num_guests, r.tariff, r.notes, r.status,
                   r.check_in, r.check_out
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.id
            WHERE r.check_in <= ? AND ? < r.check_out
            ORDER BY rm.number;
            """,
            (iso(selected_date), iso(selected_date)),
        ).fetchall()


def get_all_rooms_with_status(selected_date: date):
    rooms = get_rooms()
    reservations = get_reservations_for_date(selected_date)

    reservation_map = {}
    for res in reservations:
        room_number = res[1]
        reservation_map[room_number] = {
            "id": int(res[0]),
            "guest_name": res[2] or "",
            "num_guests": int(res[3] or 0),
            "tariff": float(res[4] or 0.0),
            "notes": res[5] or "",
            "status": res[6],
        }

    room_status = []
    for _, room_number in rooms:
        if room_number in reservation_map:
            res = reservation_map[room_number]
            room_status.append(
                {
                    "room_number": room_number,
                    "guest_name": res["guest_name"],
                    "num_guests": res["num_guests"],
                    "tariff": res["tariff"],
                    "notes": res["notes"],
                    "status": res["status"],
                    "reservation_id": res["id"],
                    "occupied": True,
                }
            )
        else:
            room_status.append(
                {
                    "room_number": room_number,
                    "guest_name": "",
                    "num_guests": 0,
                    "tariff": 0.0,
                    "notes": "",
                    "status": "available",
                    "reservation_id": None,
                    "occupied": False,
                }
            )
    return room_status


def get_reservation(res_id: int):
    with db() as conn:
        return conn.execute(
            """
            SELECT r.id, rm.number, r.guest_name, r.status, r.check_in, r.check_out,
                   r.notes, r.num_guests, r.tariff
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.id
            WHERE r.id = ?;
            """,
            (res_id,),
        ).fetchone()


def save_reservation(
    room_number: str,
    guest_name: str,
    check_in: date,
    check_out: date,
    num_guests: int,
    tariff: float,
    notes: str,
    status: str,
    reservation_id: Optional[int] = None,
) -> bool:
    guest_name = normalize_guest_name(guest_name)

    with db() as conn:
        room_row = conn.execute("SELECT id FROM rooms WHERE number = ?;", (room_number,)).fetchone()
        if not room_row:
            return False
        room_id = int(room_row[0])

        if reservation_id:
            conflict = conn.execute(
                """
                SELECT id FROM reservations
                WHERE room_id = ?
                  AND status NOT IN ('noshow', 'checkedout')
                  AND id != ?
                  AND check_in < ?
                  AND ? < check_out;
                """,
                (room_id, reservation_id, iso(check_out), iso(check_in)),
            ).fetchone()
        else:
            conflict = conn.execute(
                """
                SELECT id FROM reservations
                WHERE room_id = ?
                  AND status NOT IN ('noshow', 'checkedout')
                  AND check_in < ?
                  AND ? < check_out;
                """,
                (room_id, iso(check_out), iso(check_in)),
            ).fetchone()

        if conflict:
            return False

        tstamp = now_utc()
        if reservation_id:
            conn.execute(
                """
                UPDATE reservations
                SET guest_name=?, status=?, check_in=?, check_out=?, notes=?, num_guests=?, tariff=?, updated_at=?
                WHERE id=?;
                """,
                (
                    guest_name,
                    status,
                    iso(check_in),
                    iso(check_out),
                    notes,
                    int(num_guests),
                    float(tariff),
                    tstamp,
                    int(reservation_id),
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO reservations(room_id, guest_name, status, check_in, check_out,
                                       notes, num_guests, tariff, created_at, updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?);
                """,
                (
                    room_id,
                    guest_name,
                    status,
                    iso(check_in),
                    iso(check_out),
                    notes,
                    int(num_guests),
                    float(tariff),
                    tstamp,
                    tstamp,
                ),
            )

        conn.commit()
        return True


def delete_reservation(res_id: int):
    with db() as conn:
        conn.execute("DELETE FROM reservations WHERE id=?;", (res_id,))
        conn.commit()


def search_guests(query: str, limit: int = 10):
    if not query or len(query.strip()) < 2:
        return []
    q = query.strip()
    with db() as conn:
        results = conn.execute(
            """
            SELECT DISTINCT guest_name
            FROM reservations
            WHERE LOWER(guest_name) LIKE LOWER(?)
            ORDER BY guest_name
            LIMIT ?;
            """,
            (f"%{q}%", limit),
        ).fetchall()
        return [r[0] for r in results]


def get_guest_reservations(guest_name: str):
    with db() as conn:
        return conn.execute(
            """
            SELECT r.id, rm.number, r.status, r.check_in, r.check_out,
                   r.notes, r.num_guests, r.tariff, r.updated_at
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.id
            WHERE r.guest_name = ?
            ORDER BY r.check_in DESC;
            """,
            (guest_name,),
        ).fetchall()


def get_dashboard_stats(selected_date: date):
    with db() as conn:
        total_rooms = conn.execute("SELECT COUNT(*) FROM rooms;").fetchone()[0]
        occupied_rooms = conn.execute(
            """
            SELECT COUNT(DISTINCT r.room_id)
            FROM reservations r
            WHERE r.check_in <= ? AND ? < r.check_out
              AND r.status NOT IN ('noshow', 'checkedout');
            """,
            (iso(selected_date), iso(selected_date)),
        ).fetchone()[0]
        total_guests = conn.execute(
            """
            SELECT COALESCE(SUM(r.num_guests), 0)
            FROM reservations r
            WHERE r.check_in <= ? AND ? < r.check_out
              AND r.status NOT IN ('noshow', 'checkedout');
            """,
            (iso(selected_date), iso(selected_date)),
        ).fetchone()[0]

    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0.0
    return {
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_rooms,
        "total_guests": total_guests,
        "occupancy_rate": occupancy_rate,
    }


def status_display(db_status: str) -> str:
    if db_status == "available":
        return t("available")
    return STATUS_LABEL.get(db_status, db_status)


# ----------------- UI STYLES -----------------
st.set_page_config("Isla Verde Hotel Manager", layout="wide")

st.markdown(
    """
<style>
.iv-search-wrap{max-width:980px;margin:0 auto;}
.iv-search-card{
  border:1px solid rgba(255,255,255,0.10);
  border-radius:999px;
  padding:6px 14px;
  background:rgba(255,255,255,0.03);
  box-shadow:0 10px 30px rgba(0,0,0,0.18);
}
.iv-search-card:focus-within{
  border-color:rgba(99,102,241,0.45);
  box-shadow:0 12px 34px rgba(99,102,241,0.12);
}
.iv-search-row{display:flex;align-items:center;gap:10px;}
.iv-search-icon{width:18px;height:18px;opacity:0.9;}
div[data-testid="stTextInput"] > label {display:none;}
.iv-search-card div[data-testid="stTextInput"] input{
  border:none !important;background:transparent !important;
  padding:6px 4px !important;font-size:1.05rem !important;outline:none !important;
}
.iv-search-card div[data-testid="stTextInput"] input:focus{box-shadow:none !important;}
.iv-suggestions{
  max-width:980px;margin:0 auto;margin-top:10px;
  border:1px solid rgba(255,255,255,0.10);
  border-radius:16px;overflow:hidden;background:rgba(255,255,255,0.02);
}
.iv-suggestions .iv-sugg-header{
  padding:10px 14px;font-size:0.9rem;opacity:0.8;
  border-bottom:1px solid rgba(255,255,255,0.08);
}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------- APP INIT -----------------
init_db()

st.session_state.setdefault("authed", False)
st.session_state.setdefault("admin", False)
st.session_state.setdefault("admin_pw_key", 0)
st.session_state.setdefault("selected_date", date.today())
st.session_state.setdefault("register_toast", False)

# search page state
st.session_state.setdefault("search_active_name", None)
st.session_state.setdefault("search_last_input", "")
st.session_state.setdefault("delete_candidate", None)

# el roll selection
st.session_state.setdefault("elroll_selected_res_id", None)
st.session_state.setdefault("elroll_editor_key_n", 0)

# settings
if "lang" not in st.session_state:
    st.session_state.lang = get_setting("lang", "en")

st.session_state.simplified_mode = True  # always on


# ----------------- LOGIN -----------------
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


# ----------------- SIDEBAR NAV -----------------
st.sidebar.title(t("menu"))
view_options = [t("el_roll"), t("register_guests"), t("search_guests"), t("settings")]
view = st.sidebar.radio(t("go_to"), view_options, index=0)

VIEW_MAP = {
    t("el_roll"): "el_roll",
    t("register_guests"): "register_guests",
    t("search_guests"): "search_guests",
    t("settings"): "settings",
}
view_key = VIEW_MAP[view]

# ----------------- ADMIN SIDEBAR -----------------
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

st.sidebar.divider()
if st.sidebar.button(t("logout")):
    st.session_state.authed = False
    st.session_state.admin = False
    st.rerun()

# ----------------- MAIN HEADER -----------------
st.title(t("app_title"))


def show_register_toast_if_needed():
    if st.session_state.get("register_toast", False):
        st.toast(t("register_success"), icon="✅")
        st.session_state.register_toast = False


# ----------------- VIEWS -----------------
if view_key == "el_roll":
    show_register_toast_if_needed()
    # ... (El Roll unchanged from previous version to keep this reply focused)
    st.info("El Roll section unchanged here. Replace with your current El Roll block from v2.8.")

elif view_key == "register_guests":
    show_register_toast_if_needed()

    st.subheader(t("register_guests"))

    with st.form("reservation_form"):
        rooms = get_rooms()
        room_options = [r[1] for r in rooms]
        room_number = st.selectbox(t("room"), room_options, index=0)

        # ✅ Label the second bar as Reservation Name
        reservation_name = st.text_input(t("guest_name"), value="")

        col1, col2 = st.columns(2)
        with col1:
            check_in = st.date_input(t("checkin_date"), value=st.session_state.selected_date)
        with col2:
            check_out = st.date_input(t("checkout_date"), value=st.session_state.selected_date + timedelta(days=1))

        st.caption(f"{t('num_nights')}: {nights(check_in, check_out)}")

        col3, col4 = st.columns(2)
        with col3:
            num_guests = st.number_input(t("pax"), min_value=1, max_value=20, value=1)
        with col4:
            tariff = st.number_input(t("tariff"), min_value=0.0, value=0.0, step=10.0, format="%.2f")

        status_options = [s[0] for s in STATUSES]
        status = st.selectbox(t("status"), status_options, index=0, format_func=lambda x: STATUS_LABEL.get(x, x))

        notes = st.text_area(t("observations"), value="", height=100)

        submit = st.form_submit_button(t("save"), type="primary")
        if submit:
            if not reservation_name.strip():
                st.error(t("guest_required"))
            elif check_out <= check_in:
                st.error(t("date_range_error"))
            else:
                ok = save_reservation(
                    room_number=room_number,
                    guest_name=reservation_name,
                    check_in=check_in,
                    check_out=check_out,
                    num_guests=int(num_guests),
                    tariff=float(tariff),
                    notes=notes,
                    status=status,
                )
                if ok:
                    # ✅ green toast (auto dismiss ~3s)
                    st.session_state.register_toast = True
                    st.rerun()
                else:
                    st.error(t("room_occupied"))

elif view_key == "search_guests":
    show_register_toast_if_needed()

    st.subheader(t("search_guests"))

    # More user friendly: two columns for actions
    qa1, qa2, qa3 = st.columns([3, 1, 1])
    with qa1:
        st.markdown(f"**{t('quick_actions')}**")
    with qa2:
        if st.button("🧹 " + t("clear_search"), use_container_width=True):
            st.session_state.search_last_input = ""
            st.session_state.search_active_name = None
            st.rerun()
    with qa3:
        st.write("")

    # Search bar
    st.markdown('<div class="iv-search-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="iv-search-card"><div class="iv-search-row">', unsafe_allow_html=True)
    st.markdown(
        """
<svg class="iv-search-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M21 21L16.65 16.65M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        unsafe_allow_html=True,
    )
    search_input = st.text_input(
        "",
        value=st.session_state.search_last_input,
        placeholder=t("search_placeholder"),
        key="search_box_google",
    )
    st.markdown("</div></div></div>", unsafe_allow_html=True)

    st.session_state.search_last_input = search_input

    suggestions: List[str] = []
    if search_input and len(search_input.strip()) >= 2:
        suggestions = search_guests(search_input.strip(), limit=10)

    # Suggestions panel
    if suggestions:
        st.markdown('<div class="iv-suggestions">', unsafe_allow_html=True)
        st.markdown(f'<div class="iv-sugg-header">{t("suggestions")}</div>', unsafe_allow_html=True)

        for s in suggestions:
            colA, colB = st.columns([7, 2])
            with colA:
                if st.button("🔎 " + s, key=f"sugg_{s}", use_container_width=True):
                    st.session_state.search_active_name = s
                    st.rerun()
            with colB:
                if st.button(t("open_guest"), key=f"open_{s}", use_container_width=True):
                    st.session_state.search_active_name = s
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # Results
    active_name = st.session_state.search_active_name
    if active_name and len(active_name.strip()) >= 2:
        guest_name = active_name.strip()
        reservations = get_guest_reservations(guest_name)

        st.divider()
        st.subheader(f"{t('results')}: {guest_name}")

        if reservations:
            table_data = []
            total_revenue = 0.0
            total_nights = 0
            for res in reservations:
                _, room_number, status, check_in_str, check_out_str, notes, num_guests, tariff, updated_at = res
                check_in = parse_iso(check_in_str)
                check_out = parse_iso(check_out_str)
                nn = nights(check_in, check_out)
                total_nights += nn
                stay_revenue = float(tariff) * nn
                total_revenue += stay_revenue
                table_data.append(
                    {
                        "Room": room_number,
                        "Check-in": check_in,
                        "Check-out": check_out,
                        "Nights": nn,
                        "PAX": int(num_guests),
                        "Tariff": float(tariff),
                        "Total": stay_revenue,
                        "Status": STATUS_LABEL.get(status, status),
                        "Notes": notes,
                        "Updated": updated_at,
                    }
                )
            df = pd.DataFrame(table_data)

            st.dataframe(df, use_container_width=True, hide_index=True)

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Total Stays", len(reservations))
            with m2:
                st.metric("Total Nights", total_nights)
            with m3:
                st.metric("Total Revenue", f"€{total_revenue:.2f}")

            if st.button(t("export_csv")):
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=t("download_csv"),
                    data=csv,
                    file_name=f"guest_history_{guest_name}.csv",
                    mime="text/csv",
                )
        else:
            st.info(t("no_res_for_guest"))

elif view_key == "settings":
    show_register_toast_if_needed()
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
    if st.session_state.admin:
        st.markdown(f"### {t('db_mgmt')}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("clear_all_res"), type="secondary"):
                if st.checkbox(t("clear_all_confirm")):
                    with db() as conn:
                        conn.execute("DELETE FROM reservations;")
                        conn.commit()
                    st.success("OK")
                    st.rerun()
        with col2:
            if st.button(t("reset_rooms"), type="secondary"):
                if st.checkbox(t("reset_rooms_confirm")):
                    with db() as conn:
                        conn.execute("DELETE FROM rooms;")
                        for num in default_room_numbers():
                            conn.execute("INSERT OR IGNORE INTO rooms(number) VALUES (?);", (num,))
                        conn.commit()
                    st.success(t("rooms_reset"))
                    st.rerun()

    st.divider()
    st.markdown("### About")
    st.write("Isla Verde Hotel Manager v2.9")
    st.write("Simplified El Roll System (always on)")
    st.caption("© 2024 Hotel Isla Verde")
