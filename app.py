# ================= Isla Verde Hotel Manager (Fixed & Simplified) =================

import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Optional
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
        "select_date": "Select a date",
        "room": "Room",
        "guest_name": "Guest Name",
        "pax": "PAX",
        "tariff": "Tariff",
        "observations": "Observations",
        "status": "Status",
        "available": "Available",
        "save": "Save",
        "update": "Update",
        "delete": "Delete",
        "edit": "Edit",
        "cancel": "Cancel",
        "saved": "Saved successfully!",
        "deleted": "Deleted successfully!",
        "confirm_delete": "Confirm Delete",
        "delete_warning": "Are you sure you want to delete this reservation?",
        "no_results": "No results found",
        "checkin_date": "Check-in Date",
        "checkout_date": "Check-out Date",
        "num_nights": "Number of Nights",
        "guest_required": "Guest name is required",
        "date_range_error": "Check-out must be after check-in",
        "room_occupied": "Room is already occupied on these dates",
        "total_rooms": "Total Rooms",
        "total_guests": "Total Guests",
        "occupancy_rate": "Occupancy Rate",
        "history_for": "History for",
        "export_csv": "Export to CSV",
        "download_csv": "Download CSV",
        "language": "Language",
        "english": "English",
        "spanish": "Spanish",
        "choose_language": "Choose language",
        "save_language": "Save language",
        "lang_saved": "Language saved. Refreshing…",
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
        "select_date": "Selecciona una fecha",
        "room": "Habitación",
        "guest_name": "Nombre del Huésped",
        "pax": "PAX",
        "tariff": "Tarifa",
        "observations": "Observaciones",
        "status": "Estado",
        "available": "Disponible",
        "save": "Guardar",
        "update": "Actualizar",
        "delete": "Borrar",
        "edit": "Editar",
        "cancel": "Cancelar",
        "saved": "¡Guardado exitosamente!",
        "deleted": "¡Borrado exitosamente!",
        "confirm_delete": "Confirmar Borrado",
        "delete_warning": "¿Seguro que quieres borrar esta reserva?",
        "no_results": "No se encontraron resultados",
        "checkin_date": "Fecha de Entrada",
        "checkout_date": "Fecha de Salida",
        "num_nights": "Número de Noches",
        "guest_required": "El nombre del huésped es obligatorio",
        "date_range_error": "La salida debe ser después de la entrada",
        "room_occupied": "La habitación ya está ocupada en estas fechas",
        "total_rooms": "Habitaciones Totales",
        "total_guests": "Huéspedes Totales",
        "occupancy_rate": "Tasa de Ocupación",
        "history_for": "Historial de",
        "export_csv": "Exportar a CSV",
        "download_csv": "Descargar CSV",
        "language": "Idioma",
        "english": "Inglés",
        "spanish": "Español",
        "choose_language": "Elegir idioma",
        "save_language": "Guardar idioma",
        "lang_saved": "Idioma guardado. Actualizando…",
    },
}

def t(k): return TEXT.get(st.session_state.get("lang", "en"), TEXT["en"]).get(k, k)

# ----------------- DB -----------------
@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()

def iso(d): return d.isoformat()
def parse_iso(s): return date.fromisoformat(s)
def now(): return datetime.utcnow().isoformat(timespec="seconds")
def nights(ci, co): return (co - ci).days

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT UNIQUE NOT NULL);""")
        c.execute("""CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            guest_name TEXT NOT NULL,
            status TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL,
            notes TEXT DEFAULT "",
            num_guests INTEGER DEFAULT 1,
            tariff REAL DEFAULT 0,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);""")
        if c.execute("SELECT COUNT(*) FROM rooms").fetchone()[0] == 0:
            for n in range(101, 111):
                c.execute("INSERT OR IGNORE INTO rooms(number) VALUES (?)", (str(n),))
        c.commit()

# ----------------- DATA -----------------
def get_rooms():
    with db() as c:
        return c.execute("SELECT id, number FROM rooms ORDER BY number").fetchall()

def get_reservations_for_date(d):
    with db() as c:
        return c.execute("""
        SELECT r.id, rm.number, r.guest_name, r.num_guests, r.tariff,
               r.notes, r.status, r.check_in, r.check_out
        FROM reservations r JOIN rooms rm ON r.room_id = rm.id
        WHERE r.check_in <= ? AND ? < r.check_out
        ORDER BY rm.number
        """, (iso(d), iso(d))).fetchall()

def save_reservation(room_number, guest, ci, co, pax, tariff, notes, status, rid=None):
    with db() as c:
        room = c.execute("SELECT id FROM rooms WHERE number=?", (room_number,)).fetchone()
        if not room:
            return False
        room_id = room[0]

        if rid:
            conflict = c.execute("""
            SELECT id FROM reservations WHERE room_id=? AND id!=?
            AND status NOT IN ('noshow','checkedout')
            AND check_in < ? AND ? < check_out
            """, (room_id, rid, iso(co), iso(ci))).fetchone()
        else:
            conflict = c.execute("""
            SELECT id FROM reservations WHERE room_id=?
            AND status NOT IN ('noshow','checkedout')
            AND check_in < ? AND ? < check_out
            """, (room_id, iso(co), iso(ci))).fetchone()
        if conflict:
            return False

        ts = now()
        if rid:
            c.execute("""UPDATE reservations SET guest_name=?, status=?, check_in=?,
            check_out=?, notes=?, num_guests=?, tariff=?, updated_at=? WHERE id=?""",
            (guest, status, iso(ci), iso(co), notes, pax, tariff, ts, rid))
        else:
            c.execute("""INSERT INTO reservations
            (room_id, guest_name, status, check_in, check_out,
             notes, num_guests, tariff, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (room_id, guest, status, iso(ci), iso(co), notes, pax, tariff, ts, ts))
        c.commit()
        return True

def delete_reservation(rid):
    with db() as c:
        c.execute("DELETE FROM reservations WHERE id=?", (rid,))
        c.commit()

def dashboard(d):
    with db() as c:
        total = c.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
        occ = c.execute("""
        SELECT COUNT(DISTINCT room_id) FROM reservations
        WHERE check_in <= ? AND ? < check_out
        AND status NOT IN ('noshow','checkedout')
        """, (iso(d), iso(d))).fetchone()[0]
        guests = c.execute("""
        SELECT COALESCE(SUM(num_guests),0) FROM reservations
        WHERE check_in <= ? AND ? < check_out
        AND status NOT IN ('noshow','checkedout')
        """, (iso(d), iso(d))).fetchone()[0]
    return total, guests, (occ / total * 100 if total else 0)

# ----------------- APP -----------------
st.set_page_config("Isla Verde Hotel Manager", layout="wide")
init_db()

st.session_state.setdefault("authed", False)
st.session_state.setdefault("admin", False)
st.session_state.setdefault("lang", "en")
st.session_state.setdefault("selected_date", date.today())
st.session_state.setdefault("editing_reservation", None)
st.session_state.setdefault("delete_candidate", None)

if not st.session_state.authed:
    st.title(t("app_title"))
    pw = st.text_input(t("password"), type="password")
    if st.button(t("log_in")):
        if pw == APP_PASSWORD:
            st.session_state.authed = True
            st.rerun()
        else:
            st.error(t("incorrect_password"))
    st.stop()

# Sidebar
st.sidebar.title(t("menu"))
view = st.sidebar.radio(t("go_to"), [t("el_roll"), t("register_guests"), t("search_guests"), t("settings")])

VIEW = {
    t("el_roll"): "el",
    t("register_guests"): "reg",
    t("search_guests"): "search",
    t("settings"): "set"
}[view]

# Admin unlock
st.sidebar.divider()
if st.session_state.admin:
    st.sidebar.success(t("admin_mode_on"))
    if st.sidebar.button(t("disable_admin")):
        st.session_state.admin = False
        st.rerun()
else:
    pw = st.sidebar.text_input(t("admin_password"), type="password")
    if st.sidebar.button(t("unlock_admin")) and pw == ADMIN_PASSWORD:
        st.session_state.admin = True
        st.rerun()

if st.sidebar.button(t("logout")):
    st.session_state.authed = False
    st.session_state.admin = False
    st.rerun()

st.title(t("app_title"))

# ----------------- EL ROLL -----------------
if VIEW == "el":
    c1, c2, c3, c4, c5 = st.columns([1,1,2,1,1])
    with c1:
        if st.button(t("prev")):
            st.session_state.selected_date -= timedelta(days=1); st.rerun()
    with c2:
        if st.button(t("today")):
            st.session_state.selected_date = date.today(); st.rerun()
    with c3:
        st.markdown(f"### {st.session_state.selected_date.strftime('%A, %B %d, %Y')}")
    with c4:
        if st.button(t("next")):
            st.session_state.selected_date += timedelta(days=1); st.rerun()
    with c5:
        d = st.date_input(t("select_date"), st.session_state.selected_date)
        if d != st.session_state.selected_date:
            st.session_state.selected_date = d; st.rerun()

    total, guests, occ = dashboard(st.session_state.selected_date)
    m1, m2, m3 = st.columns(3)
    m1.metric(t("total_rooms"), total)
    m2.metric(t("total_guests"), guests)
    m3.metric(t("occupancy_rate"), f"{occ:.1f}%")

    st.divider()

    rows = get_reservations_for_date(st.session_state.selected_date)
    if rows:
        df = pd.DataFrame([{
            t("room"): r[1],
            t("guest_name"): r[2],
            t("pax"): r[3],
            t("tariff"): f"€{r[4]:.2f}",
            t("observations"): r[5],
            t("status"): dict(STATUSES).get(r[6], r[6])
        } for r in rows])
        st.dataframe(df, use_container_width=True, hide_index=True)

        if st.button(t("export_csv")):
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(t("download_csv"), csv, f"el_roll_{st.session_state.selected_date}.csv")
    else:
        st.info(t("no_results"))

# ----------------- SETTINGS -----------------
elif VIEW == "set":
    st.subheader(t("settings"))
    lang = st.selectbox(t("choose_language"), ["en", "es"],
                        format_func=lambda x: t("english") if x=="en" else t("spanish"))
    if st.button(t("save_language")):
        st.session_state.lang = lang
        st.success(t("lang_saved"))
        st.rerun()

# ----------------- OTHER VIEWS (UNCHANGED LOGIC) -----------------
# Register Guests and Search Guests can be kept from your current file
# if you want, I can also merge them fully here.
