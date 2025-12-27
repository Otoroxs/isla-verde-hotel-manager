import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Optional
from contextlib import contextmanager

# ----------------- CONFIG -----------------
DB_PATH = "hotel.db"

# Prefer secrets when available (recommended for deployment)
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "islaverde")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin000")

STATUSES = [
    ("reserved", "Reserved"),
    ("checkedin", "Checked In"),
    ("noshow", "No Show"),
    ("checkedout", "Checked Out"),
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
        "guest_name": "Guest Name",
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
        "search_placeholder": "Type guest name...",
        "no_results": "No results found",
        "select_date": "Select a date",
        "edit_reservation": "Edit Reservation",
        "checkin_date": "Check-in Date",
        "checkout_date": "Check-out Date",
        "num_nights": "Number of Nights",
        "cancel": "Cancel",
        "confirm_delete": "Confirm Delete",
        "delete_warning": "Are you sure you want to delete this reservation?",
        "room_occupied": "Room is already occupied on these dates",
        "date_range_error": "Check-out must be after check-in",
        "guest_required": "Guest name is required",
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
        "edit_row_hint": "Tick the Edit checkbox for the reservation you want to modify.",
        "clear_selection": "Clear selection",
        "edit_from_elroll": "Edit from El Roll",
        "delete_from_elroll": "Delete from El Roll",
        "confirm": "Confirm",
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
        "guest_name": "Nombre del Huésped",
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
        "search_placeholder": "Escribe nombre del huésped...",
        "no_results": "No se encontraron resultados",
        "select_date": "Selecciona una fecha",
        "edit_reservation": "Editar Reserva",
        "checkin_date": "Fecha de Entrada",
        "checkout_date": "Fecha de Salida",
        "num_nights": "Número de Noches",
        "cancel": "Cancelar",
        "confirm_delete": "Confirmar Borrado",
        "delete_warning": "¿Estás seguro de que quieres borrar esta reserva?",
        "room_occupied": "La habitación ya está ocupada en estas fechas",
        "date_range_error": "La salida debe ser después de la entrada",
        "guest_required": "El nombre del huésped es obligatorio",
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
        "edit_row_hint": "Marca la casilla Editar para la reserva que deseas modificar.",
        "clear_selection": "Borrar selección",
        "edit_from_elroll": "Editar desde El Roll",
        "delete_from_elroll": "Borrar desde El Roll",
        "confirm": "Confirmar",
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("lang", "en")
    return TEXT.get(lang, TEXT["en"]).get(key, key)


STATUS_LABEL = {k: v for k, v in STATUSES}


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
            for n in range(101, 111):
                conn.execute("INSERT OR IGNORE INTO rooms(number) VALUES (?);", (str(n),))
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
            "id": res[0],
            "guest_name": res[2],
            "num_guests": int(res[3] or 0),
            "tariff": float(res[4] or 0.0),
            "notes": res[5] or "",
            "status": res[6],
            "check_in": parse_iso(res[7]),
            "check_out": parse_iso(res[8]),
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
                (guest_name, status, iso(check_in), iso(check_out), notes, int(num_guests), float(tariff), tstamp, reservation_id),
            )
        else:
            conn.execute(
                """
                INSERT INTO reservations(room_id, guest_name, status, check_in, check_out,
                                       notes, num_guests, tariff, created_at, updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?);
                """,
                (room_id, guest_name, status, iso(check_in), iso(check_out), notes, int(num_guests), float(tariff), tstamp, tstamp),
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
    # Revenue removed from El Roll stats
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

    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
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


def status_from_display(display: str) -> str:
    if display == t("available"):
        return "available"
    # try exact match against localized labels (EN labels are stored in STATUS_LABEL)
    inv = {v: k for k, v in STATUS_LABEL.items()}
    return inv.get(display, display)


# ----------------- APP START -----------------
st.set_page_config("Isla Verde Hotel Manager", layout="wide")
init_db()

# session defaults
st.session_state.setdefault("authed", False)
st.session_state.setdefault("admin", False)
st.session_state.setdefault("admin_pw_key", 0)
st.session_state.setdefault("selected_date", date.today())
st.session_state.setdefault("search_query", "")
st.session_state.setdefault("search_suggestions", [])
st.session_state.setdefault("delete_candidate", None)

# El Roll editor selection
st.session_state.setdefault("elroll_edit_id", None)

# load settings from DB
if "lang" not in st.session_state:
    st.session_state.lang = get_setting("lang", "en")

# ✅ Simplified view is ALWAYS ON (main view). Switch removed.
st.session_state.simplified_mode = True

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

# logout
st.sidebar.divider()
if st.sidebar.button(t("logout")):
    st.session_state.authed = False
    st.session_state.admin = False
    st.rerun()

# ----------------- MAIN HEADER -----------------
st.title(t("app_title"))

# ----------------- VIEWS -----------------
if view_key == "el_roll":
    # Date controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    with col1:
        if st.button(t("prev")):
            st.session_state.selected_date -= timedelta(days=1)
            st.session_state.elroll_edit_id = None
            st.rerun()
    with col2:
        if st.button(t("today")):
            st.session_state.selected_date = date.today()
            st.session_state.elroll_edit_id = None
            st.rerun()
    with col3:
        st.markdown(f"### {st.session_state.selected_date.strftime('%A, %B %d, %Y')}")
    with col4:
        if st.button(t("next")):
            st.session_state.selected_date += timedelta(days=1)
            st.session_state.elroll_edit_id = None
            st.rerun()
    with col5:
        new_date = st.date_input(
            t("select_date"),
            value=st.session_state.selected_date,
            label_visibility="collapsed",
        )
        if new_date != st.session_state.selected_date:
            st.session_state.selected_date = new_date
            st.session_state.elroll_edit_id = None
            st.rerun()

    # Dashboard stats (Revenue removed)
    stats = get_dashboard_stats(st.session_state.selected_date)
    a, b, c = st.columns(3)
    with a:
        st.metric(t("total_rooms"), stats["total_rooms"])
    with b:
        st.metric(t("total_guests"), stats["total_guests"])
    with c:
        st.metric(t("occupancy_rate"), f"{stats['occupancy_rate']:.1f}%")

    st.divider()

    rooms_status = get_all_rooms_with_status(st.session_state.selected_date)

    # Build a table for display + choose row to edit
    rows = []
    for r in rooms_status:
        rows.append(
            {
                t("room"): r["room_number"],
                t("guest_name"): r["guest_name"],
                t("pax"): r["num_guests"] if r["num_guests"] else "",
                t("tariff"): r["tariff"] if r["tariff"] else 0.0,
                t("observations"): r["notes"],
                t("status"): status_display(r["status"]),
                "_reservation_id": r["reservation_id"],
                t("edit"): False,
            }
        )

    if not rows:
        st.info(t("no_results"))
    else:
        df = pd.DataFrame(rows)

        st.caption(t("edit_row_hint"))

        # Only allow toggling the Edit checkbox
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            disabled=[
                t("room"),
                t("guest_name"),
                t("pax"),
                t("tariff"),
                t("observations"),
                t("status"),
                "_reservation_id",
            ],
            column_config={
                t("room"): st.column_config.TextColumn(width="small"),
                t("guest_name"): st.column_config.TextColumn(width="medium"),
                t("pax"): st.column_config.NumberColumn(width="small"),
                t("tariff"): st.column_config.NumberColumn(format="€%.2f", width="small"),
                t("observations"): st.column_config.TextColumn(width="large"),
                t("status"): st.column_config.TextColumn(width="medium"),
                t("edit"): st.column_config.CheckboxColumn(width="small"),
                "_reservation_id": st.column_config.NumberColumn(width="small"),
            },
            key="elroll_table_selector",
        )

        # pick first checked row that has reservation id
        selected_ids = edited_df.loc[
            (edited_df[t("edit")] == True) & (edited_df["_reservation_id"].notna()),
            "_reservation_id",
        ].tolist()
        if selected_ids:
            st.session_state.elroll_edit_id = int(selected_ids[0])

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button(t("clear_selection")):
                st.session_state.elroll_edit_id = None
                st.session_state["elroll_table_selector"] = df
                st.rerun()
        with c2:
            if st.button(t("export_csv")):
                export_df = df.drop(columns=[t("edit"), "_reservation_id"], errors="ignore")
                csv = export_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=t("download_csv"),
                    data=csv,
                    file_name=f"el_roll_{st.session_state.selected_date}.csv",
                    mime="text/csv",
                )

        # Inline editor (Edit button behavior)
        if st.session_state.elroll_edit_id:
            reservation_data = get_reservation(int(st.session_state.elroll_edit_id))
            if not reservation_data:
                st.info(t("no_results"))
            else:
                res_id, room_number, guest_name, status, check_in_s, check_out_s, notes, num_guests, tariff = reservation_data
                check_in = parse_iso(check_in_s)
                check_out = parse_iso(check_out_s)

                st.divider()
                st.subheader(t("edit_from_elroll"))

                with st.form("elroll_inline_edit_form", clear_on_submit=False):
                    rooms = get_rooms()
                    room_options = [r[1] for r in rooms]
                    room_idx = room_options.index(room_number) if room_number in room_options else 0
                    room_number_new = st.selectbox(t("room"), room_options, index=room_idx)

                    guest_name_new = st.text_input(t("guest_name"), value=guest_name)

                    d1, d2 = st.columns(2)
                    with d1:
                        check_in_new = st.date_input(t("checkin_date"), value=check_in)
                    with d2:
                        check_out_new = st.date_input(t("checkout_date"), value=check_out)

                    st.caption(f"{t('num_nights')}: {nights(check_in_new, check_out_new)}")

                    e1, e2 = st.columns(2)
                    with e1:
                        pax_new = st.number_input(t("pax"), min_value=1, max_value=20, value=int(num_guests))
                    with e2:
                        tariff_new = st.number_input(
                            t("tariff"),
                            min_value=0.0,
                            value=float(tariff or 0.0),
                            step=10.0,
                            format="%.2f",
                        )

                    status_options = [s[0] for s in STATUSES]
                    status_idx = status_options.index(status) if status in status_options else 0
                    status_new = st.selectbox(
                        t("status"),
                        status_options,
                        index=status_idx,
                        format_func=lambda x: STATUS_LABEL.get(x, x),
                    )

                    notes_new = st.text_area(t("observations"), value=notes or "", height=100)

                    b1, b2, b3 = st.columns([1, 1, 2])
                    with b1:
                        save_btn = st.form_submit_button(t("update"), type="primary")
                    with b2:
                        cancel_btn = st.form_submit_button(t("cancel"))
                    with b3:
                        delete_btn = st.form_submit_button(f"🗑️ {t('delete')}")

                    if cancel_btn:
                        st.session_state.elroll_edit_id = None
                        st.rerun()

                    if save_btn:
                        if not guest_name_new.strip():
                            st.error(t("guest_required"))
                        elif check_out_new <= check_in_new:
                            st.error(t("date_range_error"))
                        else:
                            ok = save_reservation(
                                room_number=room_number_new,
                                guest_name=guest_name_new,
                                check_in=check_in_new,
                                check_out=check_out_new,
                                num_guests=int(pax_new),
                                tariff=float(tariff_new),
                                notes=notes_new,
                                status=status_new,
                                reservation_id=int(res_id),
                            )
                            if ok:
                                st.success(t("saved"))
                                st.session_state.elroll_edit_id = None
                                st.rerun()
                            else:
                                st.error(t("room_occupied"))

                    if delete_btn:
                        st.session_state.delete_candidate = int(res_id)
                        st.rerun()

                # Delete confirmation (outside form)
                if st.session_state.delete_candidate == int(res_id):
                    st.warning(t("delete_warning"))
                    x1, x2 = st.columns(2)
                    with x1:
                        if st.button(t("confirm_delete"), type="primary"):
                            delete_reservation(int(res_id))
                            st.session_state.delete_candidate = None
                            st.session_state.elroll_edit_id = None
                            st.success(t("deleted"))
                            st.rerun()
                    with x2:
                        if st.button(t("cancel")):
                            st.session_state.delete_candidate = None
                            st.rerun()

elif view_key == "register_guests":
    st.subheader(t("register_guests"))

    with st.form("reservation_form"):
        rooms = get_rooms()
        room_options = [r[1] for r in rooms]
        room_number = st.selectbox(t("room"), room_options, index=0)

        guest_name = st.text_input(t("guest_name"), value="")

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
            if not guest_name.strip():
                st.error(t("guest_required"))
            elif check_out <= check_in:
                st.error(t("date_range_error"))
            else:
                ok = save_reservation(
                    room_number=room_number,
                    guest_name=guest_name,
                    check_in=check_in,
                    check_out=check_out,
                    num_guests=int(num_guests),
                    tariff=float(tariff),
                    notes=notes,
                    status=status,
                    reservation_id=None,
                )
                if ok:
                    st.success(t("saved"))
                    st.rerun()
                else:
                    st.error(t("room_occupied"))

    if st.session_state.admin:
        st.divider()
        st.subheader(t("room_management"))

        c1, c2 = st.columns([2, 1])
        with c1:
            new_room = st.text_input(t("new_room"), placeholder="e.g., 201")
        with c2:
            if st.button(t("add_room")):
                if new_room.strip():
                    try:
                        add_room(new_room.strip())
                        st.success(t("room_added"))
                        st.rerun()
                    except Exception:
                        st.error(t("room_exists"))

        rooms = get_rooms()
        if rooms:
            st.write("**Existing Rooms:**")
            for room_id, room_number in rooms:
                a, b = st.columns([3, 1])
                with a:
                    st.write(f"• {room_number}")
                with b:
                    if st.button("🗑️", key=f"del_room_{room_id}"):
                        delete_room(room_id)
                        st.success(t("room_deleted"))
                        st.rerun()

elif view_key == "search_guests":
    st.subheader(t("search_guests"))

    with st.container():
        search_col1, search_col2 = st.columns([4, 1])
        with search_col1:
            search_input = st.text_input(
                "",
                value=st.session_state.search_query,
                placeholder=t("search_placeholder"),
                key="search_input_main",
            )
        with search_col2:
            if st.button("🔍", use_container_width=True):
                st.session_state.search_query = search_input
                st.rerun()

    if search_input and len(search_input) >= 2:
        suggestions = search_guests(search_input, limit=10)
        st.session_state.search_suggestions = suggestions
        if suggestions:
            st.write("**Suggestions:**")
            for suggestion in suggestions:
                if st.button(suggestion, key=f"sugg_{suggestion}"):
                    st.session_state.search_query = suggestion
                    st.rerun()

    if st.session_state.search_query and len(st.session_state.search_query.strip()) >= 2:
        guest_name = st.session_state.search_query.strip()
        reservations = get_guest_reservations(guest_name)

        if reservations:
            st.subheader(f"{t('history_for')} {guest_name}")

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
                        t("room"): room_number,
                        t("checkin_date"): check_in,
                        t("checkout_date"): check_out,
                        t("num_nights"): nn,
                        t("pax"): int(num_guests),
                        t("tariff"): float(tariff),
                        "total": stay_revenue,
                        t("status"): STATUS_LABEL.get(status, status),
                        t("observations"): notes,
                        "updated": updated_at,
                    }
                )

            df = pd.DataFrame(table_data)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    t("room"): st.column_config.TextColumn(width="small"),
                    t("checkin_date"): st.column_config.DateColumn(width="medium"),
                    t("checkout_date"): st.column_config.DateColumn(width="medium"),
                    t("num_nights"): st.column_config.NumberColumn(width="small"),
                    t("pax"): st.column_config.NumberColumn(width="small"),
                    t("tariff"): st.column_config.NumberColumn(format="€%.2f", width="small"),
                    "total": st.column_config.NumberColumn(format="€%.2f", width="small"),
                    t("status"): st.column_config.TextColumn(width="medium"),
                    t("observations"): st.column_config.TextColumn(width="large"),
                    "updated": st.column_config.DatetimeColumn(width="medium"),
                },
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Total Stays", len(reservations))
            with c2:
                st.metric("Total Nights", total_nights)
            with c3:
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
            st.info(t("no_results"))

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

    if st.session_state.admin:
        st.markdown("### Database Management")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear All Reservations", type="secondary"):
                if st.checkbox("Are you sure? This cannot be undone."):
                    with db() as conn:
                        conn.execute("DELETE FROM reservations;")
                        conn.commit()
                    st.success("All reservations cleared!")
                    st.rerun()

        with col2:
            if st.button("Reset to Default Rooms", type="secondary"):
                if st.checkbox("Reset all rooms to default (101-110)?"):
                    with db() as conn:
                        conn.execute("DELETE FROM rooms;")
                        for n in range(101, 111):
                            conn.execute("INSERT OR IGNORE INTO rooms(number) VALUES (?);", (str(n),))
                        conn.commit()
                    st.success("Rooms reset to default!")
                    st.rerun()

    st.divider()
    st.markdown("### About")
    st.write("Isla Verde Hotel Manager v2.4")
    st.write("Simplified El Roll System (always on)")
    # ✅ FIXED: properly terminated string literal
    st.caption("© 2024 Hotel Isla Verde")
