diff --git a/app.py b/app.py
index 001018411122a2718eaec385b2105378a9dbbc5c..7fc4d56f2e1e5370a919f1c99b703fe3d1966bb0 100644
--- a/app.py
+++ b/app.py
@@ -13,153 +13,211 @@ DB_PATH = "hotel.db"
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
+        "calendar": "Calendar",
         "el_roll": "El Roll",
         "register_guests": "Register Guests",
         "search_guests": "Search Guests",
+        "room_calendar": "Room Calendar",
+        "guests": "Guests",
         "settings": "Settings",
         "logout": "Logout",
         "admin_sensitive": "Admin (sensitive view)",
         "admin_mode_on": "Admin mode: ON",
         "disable_admin": "Disable admin",
         "admin_password": "Admin password",
         "unlock_admin": "Unlock admin",
         "type_admin_pass": "Type admin pass…",
-        "calendar": "Calendar",
         "today": "Today",
         "prev": "◀",
         "next": "▶",
         "rooms": "Rooms",
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
         "saved": "Saved successfully!",
         "deleted": "Deleted successfully!",
+        "selected_date": "Selected date:",
+        "cal_header": "Calendar",
+        "cal_caption": "Click a date. • means reservation exists.",
+        "selected": "Selected:",
+        "rooms_header": "Rooms",
+        "rooms_caption": "Shows status + guest.",
+        "no_rooms_warn": "No rooms found. Go to Settings and add rooms.",
+        "res_details": "Reservation Details",
+        "select_room_hint": "Select a room from the left to create/edit a reservation.",
+        "checkin": "Check-in",
+        "checkout": "Check-out",
+        "num_guests": "Number of guests in room",
+        "nights": "Nights",
+        "all_res_for_room": "All reservations for this room",
+        "no_res_yet": "No reservations for this room yet.",
+        "roomcal_header": "Room Calendar",
+        "roomcal_caption": "Pick a room, browse months, select a date to see who was in the room that day.",
+        "select_room": "Select room",
+        "who_in_room": "Who was in",
+        "no_cov_day": "No reservation covers this day for this room.",
+        "guests_header": "Guests",
+        "guests_caption": "Search guest history.",
+        "search_guest": "Search guest",
+        "type_to_search": "Type a name above to search.",
+        "no_guests_found": "No guests found.",
+        "select_guest": "Select guest",
+        "history_for": "History for",
         "search_placeholder": "Type guest name...",
         "no_results": "No results found",
         "all_rooms": "All Rooms",
         "select_date": "Select a date",
         "add_reservation": "Add Reservation",
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
         "simplified_mode": "Simplified Mode",
         "simplified_mode_desc": "Show simplified El Roll interface",
         "simplified_mode_on": "Simplified mode: ON",
         "simplified_mode_off": "Simplified mode: OFF",
         "room_management": "Room Management",
         "add_room": "Add Room",
         "new_room": "New room number",
         "room_added": "Room added successfully",
         "room_exists": "Room already exists",
         "delete_room": "Delete Room",
         "room_deleted": "Room deleted successfully",
         "export_csv": "Export to CSV",
         "total_guests": "Total Guests",
         "total_rooms": "Total Rooms",
         "occupancy_rate": "Occupancy Rate",
         "revenue": "Revenue",
         "dashboard": "Dashboard",
     },
     "es": {
         "app_title": "Administrador del Hotel Isla Verde",
         "enter_password": "Introduce la contraseña para acceder.",
         "password": "Contraseña",
         "log_in": "Entrar",
         "incorrect_password": "Contraseña incorrecta.",
         "menu": "Menú",
         "go_to": "Ir a",
+        "calendar": "Calendario",
         "el_roll": "El Roll",
         "register_guests": "Registrar Huéspedes",
         "search_guests": "Buscar Huéspedes",
+        "room_calendar": "Calendario de Habitación",
+        "guests": "Huéspedes",
         "settings": "Ajustes",
         "logout": "Cerrar sesión",
         "admin_sensitive": "Admin (vista sensible)",
         "admin_mode_on": "Modo admin: ACTIVADO",
         "disable_admin": "Desactivar admin",
         "admin_password": "Contraseña admin",
         "unlock_admin": "Desbloquear admin",
         "type_admin_pass": "Escribe la contraseña admin…",
-        "calendar": "Calendario",
         "today": "Hoy",
         "prev": "◀",
         "next": "▶",
         "rooms": "Habitaciones",
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
         "saved": "¡Guardado exitosamente!",
         "deleted": "¡Borrado exitosamente!",
+        "selected_date": "Fecha seleccionada:",
+        "cal_header": "Calendario",
+        "cal_caption": "Haz clic en una fecha. • = hay reserva.",
+        "selected": "Seleccionado:",
+        "rooms_header": "Habitaciones",
+        "rooms_caption": "Muestra estado + huésped.",
+        "no_rooms_warn": "No hay habitaciones. Ve a Ajustes y añade habitaciones.",
+        "res_details": "Detalles de Reserva",
+        "select_room_hint": "Selecciona una habitación a la izquierda para crear/editar una reserva.",
+        "checkin": "Entrada",
+        "checkout": "Salida",
+        "num_guests": "Número de huéspedes en la habitación",
+        "nights": "Noches",
+        "all_res_for_room": "Todas las reservas de esta habitación",
+        "no_res_yet": "Aún no hay reservas para esta habitación.",
+        "roomcal_header": "Calendario de Habitación",
+        "roomcal_caption": "Elige una habitación, cambia de mes, selecciona un día para ver quién estuvo.",
+        "select_room": "Seleccionar habitación",
+        "who_in_room": "Quién estuvo en",
+        "no_cov_day": "Ninguna reserva cubre ese día para esta habitación.",
+        "guests_header": "Huéspedes",
+        "guests_caption": "Busca historial del huésped.",
+        "search_guest": "Buscar huésped",
+        "type_to_search": "Escribe un nombre arriba para buscar.",
+        "no_guests_found": "No se encontraron huéspedes.",
+        "select_guest": "Seleccionar huésped",
+        "history_for": "Historial de",
         "search_placeholder": "Escribe nombre del huésped...",
         "no_results": "No se encontraron resultados",
         "all_rooms": "Todas las habitaciones",
         "select_date": "Selecciona una fecha",
         "add_reservation": "Añadir Reserva",
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
         "simplified_mode": "Modo Simplificado",
         "simplified_mode_desc": "Mostrar interfaz simplificada El Roll",
         "simplified_mode_on": "Modo simplificado: ACTIVADO",
         "simplified_mode_off": "Modo simplificado: DESACTIVADO",
@@ -182,50 +240,55 @@ TEXT = {
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
 
+def month_grid(year: int, month: int):
+    first = date(year, month, 1)
+    start = first - timedelta(days=first.weekday())
+    return [start + timedelta(days=i) for i in range(42)]
+
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
@@ -374,50 +437,77 @@ def get_all_rooms_with_status(selected_date: date):
             room_status.append({
                 'room_number': room_number,
                 'guest_name': "",
                 'num_guests': 0,
                 'tariff': 0,
                 'notes': "",
                 'status': "available",
                 'reservation_id': None,
                 'occupied': False
             })
     
     return room_status
 
 def get_reservation(res_id: int):
     conn = db()
     reservation = conn.execute("""
         SELECT r.id, rm.number, r.guest_name, r.status, r.check_in, r.check_out,
                r.notes, r.num_guests, r.tariff
         FROM reservations r
         JOIN rooms rm ON r.room_id = rm.id
         WHERE r.id = ?;
     """, (res_id,)).fetchone()
     conn.close()
     return reservation
 
+def active_on(day_: date):
+    return db().execute("""
+        SELECT id, room_id, guest_name, status, check_in, check_out, notes, num_guests, tariff
+        FROM reservations
+        WHERE check_in <= ? AND ? < check_out
+          AND status NOT IN ('noshow', 'checkedout');
+    """, (iso(day_), iso(day_))).fetchall()
+
+def room_reservations_in_range(room_id: int, start: date, end: date):
+    return db().execute("""
+        SELECT id, guest_name, status, check_in, check_out, notes, num_guests, tariff
+        FROM reservations
+        WHERE room_id = ?
+          AND check_in < ? AND check_out > ?;
+    """, (room_id, iso(end), iso(start))).fetchall()
+
+def status_badge(status: str) -> str:
+    if status == "checkedin":
+        return "✅ Checked In" if st.session_state.lang == "en" else "✅ Check-in"
+    if status == "reserved":
+        return "🟧 Reserved" if st.session_state.lang == "en" else "🟧 Reservado"
+    if status == "noshow":
+        return "❌ No Show" if st.session_state.lang == "en" else "❌ No se presentó"
+    if status == "checkedout":
+        return "⬜ Checked Out" if st.session_state.lang == "en" else "⬜ Salida"
+    return "🟦 Available" if st.session_state.lang == "en" else "🟦 Disponible"
+
 def save_reservation(room_number: str, guest_name: str, check_in: date, check_out: date, 
                     num_guests: int, tariff: float, notes: str, status: str, reservation_id: Optional[int] = None):
     conn = db()
     
     # Get room_id from room number
     room_row = conn.execute("SELECT id FROM rooms WHERE number = ?;", (room_number,)).fetchone()
     if not room_row:
         conn.close()
         return False
     
     room_id = room_row[0]
     
     # Check if room is available for the given dates (excluding current reservation if editing)
     if reservation_id:
         # When editing, exclude the current reservation from conflict check
         conflict_check = conn.execute("""
             SELECT id FROM reservations 
             WHERE room_id = ? 
             AND status NOT IN ('noshow', 'checkedout')
             AND id != ?
             AND check_in < ? AND ? < check_out;
         """, (room_id, reservation_id, iso(check_out), iso(check_in))).fetchone()
     else:
         # When creating new reservation
         conflict_check = conn.execute("""
@@ -466,50 +556,61 @@ def search_guests(query: str, limit: int = 10):
     conn = db()
     results = conn.execute("""
         SELECT DISTINCT guest_name 
         FROM reservations 
         WHERE LOWER(guest_name) LIKE LOWER(?)
         ORDER BY guest_name
         LIMIT ?;
     """, (f"%{query}%", limit)).fetchall()
     conn.close()
     return [r[0] for r in results]
 
 def get_guest_reservations(guest_name: str):
     """Get all reservations for a specific guest"""
     conn = db()
     reservations = conn.execute("""
         SELECT r.id, rm.number, r.status, r.check_in, r.check_out,
                r.notes, r.num_guests, r.tariff, r.updated_at
         FROM reservations r
         JOIN rooms rm ON r.room_id = rm.id
         WHERE r.guest_name = ?
         ORDER BY r.check_in DESC;
     """, (guest_name,)).fetchall()
     conn.close()
     return reservations
 
+def reservations_overlapping(start: date, end: date):
+    """Return all reservations overlapping the [start, end) interval."""
+    conn = db()
+    rows = conn.execute("""
+        SELECT check_in, check_out
+        FROM reservations
+        WHERE check_in < ? AND check_out > ?;
+    """, (iso(end), iso(start))).fetchall()
+    conn.close()
+    return rows
+
 def get_dashboard_stats(selected_date: date):
     """Get dashboard statistics for a specific date"""
     conn = db()
     
     # Total rooms
     total_rooms = conn.execute("SELECT COUNT(*) FROM rooms;").fetchone()[0]
     
     # Occupied rooms
     occupied_rooms = conn.execute("""
         SELECT COUNT(DISTINCT r.room_id)
         FROM reservations r
         WHERE r.check_in <= ? AND ? < r.check_out
         AND r.status NOT IN ('noshow', 'checkedout');
     """, (iso(selected_date), iso(selected_date))).fetchone()[0]
     
     # Total guests
     total_guests = conn.execute("""
         SELECT COALESCE(SUM(r.num_guests), 0)
         FROM reservations r
         WHERE r.check_in <= ? AND ? < r.check_out
         AND r.status NOT IN ('noshow', 'checkedout');
     """, (iso(selected_date), iso(selected_date))).fetchone()[0]
     
     # Revenue
     revenue = conn.execute("""
@@ -595,488 +696,251 @@ if st.session_state.admin:
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
 st.title(t("app_title"))
 
-# ----------------- VIEWS -----------------
 if view_key == "el_roll":
-    # Calendar navigation
-    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
-    
-    with col1:
-        if st.button(t("prev")):
-            st.session_state.selected_date -= timedelta(days=1)
-            st.rerun()
-    
-    with col2:
-        if st.button(t("today")):
-            st.session_state.selected_date = date.today()
-            st.rerun()
-    
-    with col3:
-        st.markdown(f"### {st.session_state.selected_date.strftime('%A, %B %d, %Y')}")
-    
-    with col4:
-        if st.button(t("next")):
-            st.session_state.selected_date += timedelta(days=1)
-            st.rerun()
-    
-    with col5:
-        # Date picker
-        new_date = st.date_input(
-            t("select_date"),
-            value=st.session_state.selected_date,
-            label_visibility="collapsed"
-        )
-        if new_date != st.session_state.selected_date:
-            st.session_state.selected_date = new_date
-            st.rerun()
-    
-    # Dashboard stats
-    stats = get_dashboard_stats(st.session_state.selected_date)
-    
-    col1, col2, col3, col4 = st.columns(4)
-    with col1:
-        st.metric(t("total_rooms"), stats['total_rooms'])
-    with col2:
-        st.metric(t("total_guests"), stats['total_guests'])
-    with col3:
-        st.metric(t("occupancy_rate"), f"{stats['occupancy_rate']:.1f}%")
-    with col4:
-        st.metric(t("revenue"), f"€{stats['revenue']:.2f}")
-    
+    if not st.session_state.simplified_mode:
+        st.info(t("simplified_mode_off"))
+        st.stop()
+
+    # Simplified calendar grid for El Roll
+    if "month_cursor" not in st.session_state:
+        st.session_state.month_cursor = st.session_state.selected_date.replace(day=1)
+    mc: date = st.session_state.month_cursor
+
+    nav1, nav2, nav3, nav4 = st.columns([1, 1, 2, 1])
+    if nav1.button(t("prev")):
+        y, m = mc.year, mc.month - 1
+        if m == 0:
+            y, m = y - 1, 12
+        st.session_state.month_cursor = date(y, m, 1)
+        st.rerun()
+    if nav2.button(t("today")):
+        st.session_state.selected_date = date.today()
+        st.session_state.month_cursor = date.today().replace(day=1)
+        st.rerun()
+    nav3.markdown(f"### {mc.strftime('%B %Y')}")
+    if nav4.button(t("next")):
+        y, m = mc.year, mc.month + 1
+        if m == 13:
+            y, m = y + 1, 1
+        st.session_state.month_cursor = date(y, m, 1)
+        st.rerun()
+
+    grid = month_grid(mc.year, mc.month)
+    dows = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
+    header = st.columns(7)
+    for i, name in enumerate(dows):
+        header[i].markdown(f"**{name}**")
+
+    booked_days = set()
+    for ci_s, co_s in reservations_overlapping(grid[0], grid[-1] + timedelta(days=1)):
+        ci = parse_iso(ci_s)
+        co = parse_iso(co_s)
+        d = ci
+        while d < co:
+            booked_days.add(d)
+            d += timedelta(days=1)
+
+    for week in range(6):
+        cols = st.columns(7)
+        for i in range(7):
+            d = grid[week * 7 + i]
+            in_month = (d.month == mc.month)
+            label = str(d.day)
+            if d in booked_days:
+                label += " •"
+            if d == st.session_state.selected_date:
+                label = "✅ " + label
+            if cols[i].button(label, disabled=not in_month, use_container_width=True,
+                              key=f"cal_{mc.year}_{mc.month}_{week}_{i}_{d.isoformat()}"):
+                st.session_state.selected_date = d
+                st.rerun()
+
+    st.info(f"{t('selected_date')} {st.session_state.selected_date.strftime('%A, %B %d, %Y')}")
     st.divider()
-    
-    # Get rooms with status for selected date
+
     rooms_status = get_all_rooms_with_status(st.session_state.selected_date)
-    
-    # Create table data
     table_data = []
     for room in rooms_status:
         status_text = dict(STATUSES).get(room['status'], room['status'])
         if room['status'] == 'available':
             status_text = t('available')
-        
+
         table_data.append({
             t('room'): room['room_number'],
             t('guest_name'): room['guest_name'],
             t('pax'): room['num_guests'] if room['num_guests'] > 0 else "",
-            t('tariff'): f"€{room['tariff']:.2f}" if room['tariff'] > 0 else "",
+            t('tariff'): "" if room['tariff'] == 0 else f"{room['tariff']:.2f}",
             t('observations'): room['notes'],
             t('status'): status_text,
-            'reservation_id': room['reservation_id'],
-            'occupied': room['occupied']
         })
-    
-    # Display as DataFrame with formatting
+
     if table_data:
-        df = pd.DataFrame(table_data)
-        
-        # Apply styling based on status
-        def color_status(val):
-            if val == t('available'):
-                return 'background-color: #d4edda; color: #155724;'  # Green
-            elif 'Checked In' in val or 'Check-in' in val:
-                return 'background-color: #cce5ff; color: #004085;'  # Blue
-            elif 'Reserved' in val or 'Reservado' in val:
-                return 'background-color: #fff3cd; color: #856404;'  # Yellow
-            elif 'No Show' in val:
-                return 'background-color: #f8d7da; color: #721c24;'  # Red
-            else:
-                return ''
-        
-        # Format the DataFrame display
-        styled_df = df.style.applymap(color_status, subset=[t('status')])
-        
-        # Display the table
-        st.dataframe(
-            styled_df,
-            use_container_width=True,
-            hide_index=True,
-            column_config={
-                t('room'): st.column_config.TextColumn(width="small"),
-                t('guest_name'): st.column_config.TextColumn(width="medium"),
-                t('pax'): st.column_config.NumberColumn(width="small"),
-                t('tariff'): st.column_config.TextColumn(width="small"),
-                t('observations'): st.column_config.TextColumn(width="large"),
-                t('status'): st.column_config.TextColumn(width="medium"),
-            }
-        )
-        
-        # Add action buttons for each reservation
-        st.divider()
-        st.subheader(t("edit_reservation"))
-        
-        # Get all reservations for the day
-        reservations = get_reservations_for_date(st.session_state.selected_date)
-        
-        if reservations:
-            for res in reservations:
-                res_id, room_number, guest_name, num_guests, tariff, notes, status, check_in, check_out = res
-                
-                col1, col2, col3 = st.columns([2, 1, 1])
-                with col1:
-                    st.write(f"**{room_number}** - {guest_name} ({num_guests} PAX) - {dict(STATUSES).get(status, status)}")
-                    if notes:
-                        st.caption(f"📝 {notes}")
-                
-                with col2:
-                    if st.button(f"✏️ {t('edit')}", key=f"edit_{res_id}"):
-                        st.session_state.editing_reservation = res_id
-                        st.session_state.selected_date = parse_iso(check_in)
-                        st.rerun()
-                
-                with col3:
-                    if st.button(f"🗑️ {t('delete')}", key=f"delete_{res_id}"):
-                        if st.checkbox(t("confirm_delete"), key=f"confirm_delete_{res_id}"):
-                            delete_reservation(res_id)
-                            st.success(t("deleted"))
-                            st.rerun()
-                
-                st.divider()
-        else:
-            st.info(t("no_results"))
-        
-        # Export button
-        if st.button(t("export_csv")):
-            csv = df.to_csv(index=False).encode('utf-8')
-            st.download_button(
-                label="Download CSV",
-                data=csv,
-                file_name=f"el_roll_{st.session_state.selected_date}.csv",
-                mime="text/csv"
-            )
+        st.table(pd.DataFrame(table_data))
     else:
         st.info(t("no_results"))
 
 elif view_key == "register_guests":
+    if not st.session_state.simplified_mode:
+        st.info(t("simplified_mode_off"))
+        st.stop()
+
     st.subheader(t("register_guests"))
-    
-    # Check if we're editing an existing reservation
-    editing_res_id = st.session_state.editing_reservation
-    reservation_data = None
-    
-    if editing_res_id:
-        reservation_data = get_reservation(editing_res_id)
-        st.info(f"{t('edit_reservation')}: {reservation_data[1]} - {reservation_data[2]}")
-    
+
     with st.form("reservation_form"):
-        # Room selection
         rooms = get_rooms()
         room_options = [r[1] for r in rooms]
-        
-        if reservation_data:
-            default_room_index = room_options.index(reservation_data[1]) if reservation_data[1] in room_options else 0
-        else:
-            default_room_index = 0
-        
         room_number = st.selectbox(
             t("room"),
             room_options,
-            index=default_room_index
+            index=0 if room_options else None,
         )
-        
-        # Guest name
-        if reservation_data:
-            default_name = reservation_data[2]
-        else:
-            default_name = ""
-        
-        guest_name = st.text_input(t("guest_name"), value=default_name)
-        
+
+        guest_name = st.text_input(t("guest_name"))
+
         col1, col2 = st.columns(2)
-        
         with col1:
-            if reservation_data:
-                default_checkin = parse_iso(reservation_data[4])
-            else:
-                default_checkin = st.session_state.selected_date
-            
-            check_in = st.date_input(t("checkin_date"), value=default_checkin)
-        
+            num_guests = st.number_input(t("pax"), min_value=1, max_value=20, value=1)
         with col2:
-            if reservation_data:
-                default_checkout = parse_iso(reservation_data[5])
-            else:
-                default_checkout = st.session_state.selected_date + timedelta(days=1)
-            
-            check_out = st.date_input(t("checkout_date"), value=default_checkout)
-        
-        # Calculate nights
-        num_nights = nights(check_in, check_out)
-        st.caption(f"{t('num_nights')}: {num_nights}")
-        
-        col3, col4 = st.columns(2)
-        
-        with col3:
-            if reservation_data:
-                default_pax = reservation_data[7]
-            else:
-                default_pax = 1
-            
-            num_guests = st.number_input(t("pax"), min_value=1, max_value=20, value=default_pax)
-        
-        with col4:
-            if reservation_data:
-                default_tariff = float(reservation_data[8])
-            else:
-                default_tariff = 0.0
-            
             tariff = st.number_input(
                 t("tariff"),
                 min_value=0.0,
-                value=default_tariff,
-                step=10.0,
-                format="%.2f"
+                value=0.0,
+                step=1.0,
+                format="%.2f",
             )
-        
-        # Status
-        status_options = [s[0] for s in STATUSES]
-        status_labels = [dict(STATUSES)[s] for s in status_options]
-        
-        if reservation_data:
-            default_status_index = status_options.index(reservation_data[3]) if reservation_data[3] in status_options else 0
-        else:
-            default_status_index = 0
-        
+
         status = st.selectbox(
             t("status"),
-            status_options,
-            index=default_status_index,
-            format_func=lambda x: dict(STATUSES)[x]
+            [s[0] for s in STATUSES],
+            format_func=lambda x: dict(STATUSES)[x],
         )
-        
-        # Observations
-        if reservation_data:
-            default_notes = reservation_data[6]
-        else:
-            default_notes = ""
-        
-        notes = st.text_area(t("observations"), value=default_notes, height=100)
-        
-        # Form buttons
-        col5, col6 = st.columns(2)
-        
-        with col5:
-            submit_button = st.form_submit_button(
-                t("update") if editing_res_id else t("save"),
-                type="primary"
-            )
-        
-        with col6:
-            if st.form_submit_button(t("cancel")):
-                st.session_state.editing_reservation = None
-                st.rerun()
-        
+
+        notes = st.text_area(t("observations"), height=100)
+
+        st.caption(f"{t('selected_date')} {st.session_state.selected_date} (1 night)")
+
+        submit_button = st.form_submit_button(t("save"), type="primary")
+
         if submit_button:
-            # Validation
             if not guest_name.strip():
                 st.error(t("guest_required"))
-            elif check_out <= check_in:
-                st.error(t("date_range_error"))
             else:
-                # Save reservation
+                check_in = st.session_state.selected_date
+                check_out = st.session_state.selected_date + timedelta(days=1)
                 success = save_reservation(
                     room_number=room_number,
                     guest_name=guest_name.strip(),
                     check_in=check_in,
                     check_out=check_out,
                     num_guests=num_guests,
                     tariff=tariff,
                     notes=notes,
                     status=status,
-                    reservation_id=editing_res_id if editing_res_id else None
+                    reservation_id=None,
                 )
-                
                 if success:
                     st.success(t("saved"))
-                    st.session_state.editing_reservation = None
                     st.rerun()
                 else:
                     st.error(t("room_occupied"))
-    
-    # Room management section (admin only)
-    if st.session_state.admin:
-        st.divider()
-        st.subheader(t("room_management"))
-        
-        col1, col2 = st.columns([2, 1])
-        
-        with col1:
-            new_room = st.text_input(t("new_room"), placeholder="e.g., 201")
-        
-        with col2:
-            if st.button(t("add_room")):
-                if new_room.strip():
-                    try:
-                        add_room(new_room.strip())
-                        st.success(t("room_added"))
-                        st.rerun()
-                    except:
-                        st.error(t("room_exists"))
-        
-        # List of rooms with delete option
-        rooms = get_rooms()
-        if rooms:
-            st.write("**Existing Rooms:**")
-            for room_id, room_number in rooms:
-                col1, col2 = st.columns([3, 1])
-                with col1:
-                    st.write(f"• {room_number}")
-                with col2:
-                    if st.button(f"🗑️", key=f"del_room_{room_id}"):
-                        delete_room(room_id)
-                        st.success(t("room_deleted"))
-                        st.rerun()
 
 elif view_key == "search_guests":
+    if not st.session_state.simplified_mode:
+        st.info(t("simplified_mode_off"))
+        st.stop()
+
     st.subheader(t("search_guests"))
-    
-    # Search bar with autocomplete
-    search_container = st.container()
-    
-    with search_container:
-        search_col1, search_col2 = st.columns([4, 1])
-        
-        with search_col1:
-            search_input = st.text_input(
-                "",
-                value=st.session_state.search_query,
-                placeholder=t("search_placeholder"),
-                key="search_input_main"
-            )
-        
-        with search_col2:
-            if st.button("🔍", use_container_width=True):
-                st.session_state.search_query = search_input
-                st.rerun()
-    
-    # Show autocomplete suggestions
-    if search_input and len(search_input) >= 2:
-        suggestions = search_guests(search_input, limit=10)
-        st.session_state.search_suggestions = suggestions
-        
-        if suggestions:
-            st.write("**Suggestions:**")
-            for suggestion in suggestions:
-                if st.button(suggestion, key=f"sugg_{suggestion}"):
-                    st.session_state.search_query = suggestion
-                    st.rerun()
-    
-    # Display search results
-    if st.session_state.search_query and len(st.session_state.search_query.strip()) >= 2:
-        guest_name = st.session_state.search_query.strip()
+
+    search_input = st.text_input(
+        "",
+        value=st.session_state.search_query,
+        placeholder=t("search_placeholder"),
+        key="search_input_main",
+    )
+    st.session_state.search_query = search_input
+
+    suggestions = search_guests(search_input, limit=10)
+    if suggestions:
+        chosen = st.radio("Suggestions", suggestions, index=0, key="suggestion_radio")
+        if chosen and chosen != st.session_state.search_query:
+            st.session_state.search_query = chosen
+            search_input = chosen
+
+    if search_input and len(search_input.strip()) >= 2:
+        guest_name = search_input.strip()
         reservations = get_guest_reservations(guest_name)
-        
+
         if reservations:
             st.subheader(f"{t('history_for')} {guest_name}")
-            
-            # Create table data
+
             table_data = []
-            total_revenue = 0
-            
             for res in reservations:
                 res_id, room_number, status, check_in_str, check_out_str, notes, num_guests, tariff, updated_at = res
                 check_in = parse_iso(check_in_str)
                 check_out = parse_iso(check_out_str)
                 num_nights = nights(check_in, check_out)
-                stay_revenue = tariff * num_nights
-                total_revenue += stay_revenue
-                
+
                 table_data.append({
                     t('room'): room_number,
                     t('checkin_date'): check_in_str,
                     t('checkout_date'): check_out_str,
                     t('num_nights'): num_nights,
                     t('pax'): num_guests,
-                    t('tariff'): f"€{tariff:.2f}",
-                    'total': f"€{stay_revenue:.2f}",
+                    t('tariff'): f"{tariff:.2f}",
                     t('status'): dict(STATUSES).get(status, status),
                     t('observations'): notes,
-                    'updated': updated_at
                 })
-            
-            # Display as DataFrame
+
             df = pd.DataFrame(table_data)
-            st.dataframe(
-                df,
-                use_container_width=True,
-                hide_index=True,
-                column_config={
-                    t('room'): st.column_config.TextColumn(width="small"),
-                    t('checkin_date'): st.column_config.DateColumn(width="medium"),
-                    t('checkout_date'): st.column_config.DateColumn(width="medium"),
-                    t('num_nights'): st.column_config.NumberColumn(width="small"),
-                    t('pax'): st.column_config.NumberColumn(width="small"),
-                    t('tariff'): st.column_config.TextColumn(width="small"),
-                    'total': st.column_config.TextColumn(width="small"),
-                    t('status'): st.column_config.TextColumn(width="medium"),
-                    t('observations'): st.column_config.TextColumn(width="large"),
-                    'updated': st.column_config.DatetimeColumn(width="medium"),
-                }
-            )
-            
-            # Summary
-            col1, col2, col3 = st.columns(3)
-            with col1:
-                st.metric("Total Stays", len(reservations))
-            with col2:
-                st.metric("Total Nights", sum([nights(parse_iso(r[3]), parse_iso(r[4])) for r in reservations]))
-            with col3:
-                st.metric("Total Revenue", f"€{total_revenue:.2f}")
-            
-            # Export button
-            if st.button(t("export_csv")):
-                csv = df.to_csv(index=False).encode('utf-8')
-                st.download_button(
-                    label="Download CSV",
-                    data=csv,
-                    file_name=f"guest_history_{guest_name}.csv",
-                    mime="text/csv"
-                )
+            st.table(df)
         else:
             st.info(t("no_results"))
+    else:
+        st.info(t("type_to_search"))
 
 elif view_key == "settings":
     st.subheader(t("settings"))
     
     # Language settings
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
     
     # Simplified mode toggle
     st.markdown(f"### {t('simplified_mode')}")
     simplified_mode = st.checkbox(
