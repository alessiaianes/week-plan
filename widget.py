import os.path
import datetime
import tkinter as tk
from tkinter import ttk
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pytz  # Per gestire i fusi orari
import threading
from plyer import notification # Per le notifiche 



# Scopo dell'API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Ottieni il servizio Google Calendar
def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service

# Ottieni gli eventi della settimana corrente
def get_week_events(service, start_date, end_date):
    # Aggiungi un giorno alla data di fine per includere l'intera giornata di domenica
    end_date += datetime.timedelta(days=1)

    # Converti le date locali in UTC
    local_timezone = pytz.timezone('Europe/Rome')  # Sostituisci con il tuo fuso orario
    start_date_utc = local_timezone.localize(datetime.datetime.combine(start_date, datetime.time.min)).astimezone(pytz.utc)
    end_date_utc = local_timezone.localize(datetime.datetime.combine(end_date, datetime.time.min)).astimezone(pytz.utc)

    # Formatta le date con l'ora UTC
    start = start_date_utc.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    end = end_date_utc.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

    # Richiesta all'API Google Calendar
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return events

# Aggiorna il widget con gli eventi della settimana corrente
def update_widget():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # Mostra il titolo della settimana in grassetto
    week_label = tk.Label(scrollable_frame, text=f"Week: {current_week_start.strftime('%d %b %Y')} - {current_week_end.strftime('%d %b %Y')}", 
                          font=("Arial Rounded MT Bold", 12, "bold"), background="#e6e6fa", padx=10, pady=5, relief="groove", borderwidth=2)
    week_label.pack(fill="x", pady=5)

    # Ottieni gli eventi della settimana corrente
    events = get_week_events(service, current_week_start, current_week_end)

    # Raggruppa gli eventi per giorno
    events_by_day = {}
    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        if 'T' in start_time:
            day = datetime.datetime.strptime(start_time[:10], '%Y-%m-%d').date()
        else:
            day = datetime.datetime.strptime(start_time[:10], '%Y-%m-%d').date()
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event)

    # Genera tutti i giorni della settimana (da lunedì a domenica)
    week_dates = [current_week_start + datetime.timedelta(days=i) for i in range(7)]

    # Visualizza gli eventi raggruppati per giorno
    for day in week_dates:
        # Nome del giorno in inglese
        day_name = day.strftime('%A')
        day_label = tk.Label(scrollable_frame, text=f"{day_name} {day.strftime('%d %b %Y')}", 
                             font=("Arial Rounded MT Bold", 12, "bold"), background="#c8a2c8", padx=10, pady=5, relief="groove", borderwidth=2)
        day_label.pack(fill="x", pady=(10, 2))

        # Visualizza gli eventi del giorno (se presenti)
        if day in events_by_day:
            for event in events_by_day[day]:
                start_time = event['start'].get('dateTime', event['start'].get('date'))
                end_time = event['end'].get('dateTime', event['end'].get('date'))
                summary = event.get('summary', "No title")
                color_id = event.get('colorId', 'default')
                event_color = GOOGLE_CALENDAR_COLORS.get(color_id, "#d8bfd8")

                # Formatta le date/orari
                if 'T' in start_time:
                    start_formatted = datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S%z').strftime('%H:%M')
                    end_formatted = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S%z').strftime('%H:%M')
                else:
                    start_formatted = "All day"
                    end_formatted = ""

                # Crea un frame per l'evento con bordi arrotondati simulati
                event_frame = tk.Frame(scrollable_frame, background=event_color, relief="groove", borderwidth=2)
                event_frame.pack(fill="x", pady=2, padx=5)

                # Imposta una larghezza fissa per tutti gli eventi
                event_details = f"{summary}\n{start_formatted} - {end_formatted}"
                event_label = tk.Label(event_frame, text=event_details, font=("Arial Rounded MT Bold", 12), background=event_color, justify="left", padx=10, pady=5, wraplength=280)
                event_label.pack(side="left", fill="x", expand=True)
        else:
            # Se non ci sono eventi per il giorno, mostra un messaggio
            no_events_label = tk.Label(scrollable_frame, text="No events", font=("Arial Rounded MT Bold", 12), background="#e6e6fa", padx=10, pady=5)
            no_events_label.pack(fill="x", pady=(0, 5))

    # Aggiorna la scrollregion per includere tutto il contenuto
    canvas.update_idletasks()  # Assicura che tutte le modifiche siano applicate
    canvas.configure(scrollregion=canvas.bbox("all"))

    # Riporta lo scorrimento in cima
    canvas.yview_moveto(0)

# Scorri alla settimana precedente
def previous_week():
    global current_week_start, current_week_end
    current_week_start -= datetime.timedelta(days=7)
    current_week_end -= datetime.timedelta(days=7)
    update_widget()

# Scorri alla settimana successiva
def next_week():
    global current_week_start, current_week_end
    current_week_start += datetime.timedelta(days=7)
    current_week_end += datetime.timedelta(days=7)
    update_widget()

# Funzione per aggiornare il calendario
def refresh_calendar():
    update_widget()

# Funzione per spostare il widget
def start_move(event):
    global x, y
    x = event.x
    y = event.y

def stop_move(event):
    global x, y
    x = None
    y = None

def on_motion(event):
    deltax = event.x - x
    deltay = event.y - y
    new_x = root.winfo_x() + deltax
    new_y = root.winfo_y() + deltay
    root.geometry(f"+{new_x}+{new_y}")

# Gestione dello scorrimento con il touchpad/mouse
def on_mousewheel(event):
    if event.num == 4 or event.delta > 0:  # Scorrimento verso l'alto
        canvas.yview_scroll(-1, "units")
    elif event.num == 5 or event.delta < 0:  # Scorrimento verso il basso
        canvas.yview_scroll(1, "units")

def on_shift_mousewheel(event):
    canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")  # Scorrimento orizzontale

# Funzione per controllare le notifiche degli eventi
def check_for_notifications():
    while True:
        # Ottieni gli eventi della settimana corrente
        events = get_week_events(service, current_week_start, current_week_end)

        # Controlla ogni evento per vedere se ha reminder
        for event in events:
            start_time = event['start'].get('dateTime', event['start'].get('date'))
            if 'T' in start_time:  # Solo eventi con orario specifico
                event_time = datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S%z')
                current_time = datetime.datetime.now(pytz.utc)  # Ora corrente in UTC

                # Leggi i reminder dell'evento
                reminders = event.get('reminders', {}).get('overrides', [])
                use_default_reminders = event.get('reminders', {}).get('useDefault', False)

                # Se non ci sono reminder personalizzati, usa i default
                if not reminders and use_default_reminders:
                    reminders = [{"method": "popup", "minutes": 60}]  # Default: 1 ora prima

                # Controlla ogni reminder
                for reminder in reminders:
                    if reminder['method'] == 'popup':  # Consideriamo solo i reminder di tipo popup
                        reminder_minutes = reminder['minutes']
                        reminder_time = event_time - datetime.timedelta(minutes=reminder_minutes)

                        # Se siamo entro 1 minuto dalla notifica, invia la notifica
                        time_difference = (reminder_time - current_time).total_seconds()
                        if 0 <= time_difference <= 60:  # Invia la notifica entro 1 minuto dall'orario previsto
                            summary = event.get('summary', "No title")
                            notification.notify(
                                title="Reminder",
                                message=f"{summary}"+" "+f"{event_time.strftime('%H:%M')}",
                                timeout=10  # La notifica rimane visibile per 10 secondi
                            )

        # Attendi 1 minuto prima di controllare nuovamente
        threading.Event().wait(60)


# Configurazione della finestra
root = tk.Tk()
root.title("WeekPlan")


# Calcolo della posizione in alto a destra con margine
screen_width = root.winfo_screenwidth()  # Larghezza dello schermo
screen_height = root.winfo_screenheight()  # Altezza dello schermo
widget_width = 300  # Larghezza del widget (non modificata)
widget_height = 200  # Altezza del widget (non modificata)
margin = 10  # Margine dal bordo

# Calcola la posizione x e y
x_position = screen_width - widget_width - margin  # Distanza dal bordo destro con margine
y_position = margin  # Distanza dal bordo superiore con margine
# Imposta la geometria del widget
root.geometry(f"{widget_width}x{widget_height}+{x_position}+{y_position}")
root.attributes('-topmost', False)  # Non mantenere sempre in primo piano
root.overrideredirect(True)  # Rimuovi la barra del titolo
root.configure(background="#e6e6fa")

# Barra di trascinamento
title_bar = tk.Frame(root, bg="#d8bfd8", relief="raised", bd=1)
title_bar.pack(fill="x")
title_bar.bind("<ButtonPress-1>", start_move)
title_bar.bind("<ButtonRelease-1>", stop_move)
title_bar.bind("<B1-Motion>", on_motion)

# Pulsanti di chiusura e navigazione
close_button = tk.Button(title_bar, text="X", bg="#ff4d4d", fg="white", command=root.destroy, font=("Arial Rounded MT Bold", 10))
close_button.pack(side="right", padx=2, pady=1)

prev_button = tk.Button(title_bar, text="<< Prev.", bg="#4CAF50", fg="white", command=previous_week, font=("Arial Rounded MT Bold", 10))
prev_button.pack(side="left", padx=2, pady=1)

next_button = tk.Button(title_bar, text="Next >>", bg="#03A9F4", fg="white", command=next_week, font=("Arial Rounded MT Bold", 10))
next_button.pack(side="left", padx=2, pady=1)

# Pulsante di aggiornamento
refresh_button = tk.Button(title_bar, text="⟳", bg="#FFC107", fg="black", command=refresh_calendar, font=("Arial Rounded MT Bold", 10))
refresh_button.pack(side="left", padx=2, pady=1)

# Area scorrevole
canvas = tk.Canvas(root, bg="#e6e6fa", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

scrollable_frame = tk.Frame(canvas, bg="#e6e6fa")
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# Configurazione dello scorrimento
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.bind_all("<MouseWheel>", on_mousewheel)  # Scorrimento verticale
canvas.bind_all("<Shift-MouseWheel>", on_shift_mousewheel)  # Scorrimento orizzontale

# Aggiorna dinamicamente la larghezza del frame interno
def update_frame_width(event):
    canvas.itemconfig(window, width=event.width)

window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.bind('<Configure>', lambda e: canvas.itemconfig(window, width=e.width))

# Colori predefiniti di Google Calendar
GOOGLE_CALENDAR_COLORS = {
    "1": "#a4bdfc",  # Blu chiaro
    "2": "#7ae7bf",  # Verde acqua
    "3": "#dbadff",  # Viola chiaro
    "4": "#ff887c",  # Rosa
    "5": "#fbd75b",  # Giallo
    "6": "#ffb878",  # Arancione chiaro
    "7": "#46d6db",  # Turchese
    "8": "#e1e1e1",  # Grigio chiaro
    "9": "#5484ed",  # Blu scuro
    "10": "#51b749",  # Verde scuro
    "11": "#dc2127",  # Rosso
    "default": "#a4bdfc"  # Blu chiaro (default)
}

# Inizializza la settimana corrente
today = datetime.datetime.utcnow().date()
current_week_start = today - datetime.timedelta(days=today.weekday())
current_week_end = current_week_start + datetime.timedelta(days=6)

# Ottieni il servizio Google Calendar
service = get_calendar_service()
# Avvia il thread per le notifiche
notification_thread = threading.Thread(target=check_for_notifications, daemon=True)
notification_thread.start()

# Primo aggiornamento
update_widget()

root.mainloop()