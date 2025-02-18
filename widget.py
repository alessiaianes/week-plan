import os.path
import datetime
import tkinter as tk
from tkinter import ttk
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

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
    # Formatta le date con l'ora UTC
    start = start_date.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    end = end_date.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

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

    # Genera tutti i giorni della settimana
    week_dates = [current_week_start + datetime.timedelta(days=i) for i in range(7)]

    # Visualizza gli eventi raggruppati per giorno
    for day in week_dates:
        # Nome del giorno in inglese
        day_name = day.strftime('%A')
        day_label = tk.Label(scrollable_frame, text=f"{day_name} {day.strftime('%d %b %Y')}", 
                             font=("Arial Rounded MT Bold", 10, "bold"), background="#c8a2c8", padx=10, pady=5, relief="groove", borderwidth=2)
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

                # Etichetta con i dettagli dell'evento (titolo in grassetto)
                event_details = f"{summary}\n{start_formatted} - {end_formatted}"
                event_label = tk.Label(event_frame, text=event_details, font=("Arial Rounded MT Bold", 10), background=event_color, justify="left", padx=10, pady=5, wraplength=280)
                event_label.pack(side="left")
        else:
            # Se non ci sono eventi per il giorno, mostra un messaggio
            no_events_label = tk.Label(scrollable_frame, text="No events", font=("Arial Rounded MT Bold", 10), background="#e6e6fa", padx=10, pady=5)
            no_events_label.pack(fill="x", pady=(0, 5))

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
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")  # Scorrimento verticale

def on_shift_mousewheel(event):
    canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")  # Scorrimento orizzontale

# Configurazione della finestra
root = tk.Tk()
root.title("Google Calendar Widget")
root.geometry("300x200+100+100")  # Ridotto al 50% dell'altezza
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
close_button = tk.Button(title_bar, text="X", bg="#ff4d4d", fg="white", command=root.destroy, font=("Arial Rounded MT Bold", 8))
close_button.pack(side="right", padx=2, pady=1)

prev_button = tk.Button(title_bar, text="<< Prev.", bg="#4CAF50", fg="white", command=previous_week, font=("Arial Rounded MT Bold", 8))
prev_button.pack(side="left", padx=2, pady=1)

next_button = tk.Button(title_bar, text="Next >>", bg="#03A9F4", fg="white", command=next_week, font=("Arial Rounded MT Bold", 8))
next_button.pack(side="left", padx=2, pady=1)

# Pulsante di aggiornamento
refresh_button = tk.Button(title_bar, text="⟳", bg="#FFC107", fg="black", command=refresh_calendar, font=("Arial Rounded MT Bold", 8))
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
    "default": "#a4bdfc"  # Lilla (default)
}

# Inizializza la settimana corrente
today = datetime.datetime.utcnow().date()
current_week_start = today - datetime.timedelta(days=today.weekday())
current_week_end = current_week_start + datetime.timedelta(days=6)

# Ottieni il servizio Google Calendar
service = get_calendar_service()

# Primo aggiornamento
update_widget()

root.mainloop()