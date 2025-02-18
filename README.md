# **WEEKPLAN: Google Calendar Widget**

Questo è un widget minimalista per visualizzare gli eventi settimana per settimana direttamente dal calendario Google. È progettato per essere semplice, intuitivo e facile da usare.

---

## **Funzionamento del Widget**

1. **Visualizzazione Eventi**:
   - Il widget mostra tutti gli eventi della settimana corrente, raggruppati per giorno.
   - Ogni giorno ha un'intestazione chiara con il nome del giorno (es. `Monday`, `Tuesday`) e la data.
   - Se un giorno non ha eventi, viene mostrato il messaggio `"No events"`.
   - Gli eventi visualizzati sono colorati in base a come sono stati salvati sul tuo calendario personale.

2. **Navigazione tra Settimane**:
   - Usa i pulsanti `<< Prev.` e `Next >>` per scorrere tra le settimane precedenti e successive.

3. **Refresh**:
   - Premi il pulsante `⟳` per aggiornare il contenuto del widget.

4. **Scorrimento**:
   - Usa la rotella del mouse o il touchpad per scorrere verticalmente.
   - Usa `Shift + Rotella del mouse` o il touchpad per scorrere orizzontalmente.

5. **Autenticazione**:
   - All'avvio, l'applicazione aprirà una finestra del browser per autenticarti con il tuo account Google.
   - Una volta autenticato, il widget accederà al tuo calendario Google per recuperare gli eventi.

---

## **Requisiti e Installazione**

### **1. Librerie Necessarie**
Per far funzionare il widget, devi installare le seguenti librerie Python:

- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`
- `google-api-python-client`
- `pytz`

Puoi installarle tutte insieme con il seguente comando:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pytz plyer
```

### **2. Creazione di un Ambiente Virtuale (Consigliato)**
Per evitare conflitti con altre librerie o versioni di Python, si consiglia di creare un ambiente virtuale:

```bash
# Crea un ambiente virtuale
python -m venv calendar-widget-env

# Attiva l'ambiente virtuale
# Su Windows:
calendar-widget-env\Scripts\activate
# Su macOS/Linux:
source calendar-widget-env/bin/activate

# Installa le dipendenze
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pytz plyer
```

### **3. File `credentials.json`**
Il file `credentials.json` non è incluso in questo repository perché contiene informazioni sensibili. Per far funzionare lo script, devi:
1. Creare un progetto su [Google Cloud Console](https://console.cloud.google.com/).
2. Abilitare l'API di Google Calendar.
3. Scaricare il file `credentials.json` e metterlo nella stessa cartella dello script.

> **Nota**: Non caricare mai il file `credentials.json` su un repository pubblico!

---

## **Come Convertire lo Script in App**

Per convertire lo script Python in un'applicazione eseguibile (`.exe` su Windows o `.app` su macOS), puoi usare **PyInstaller**.

### **Passaggi:**

1. **Installa PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Crea l'Eseguibile**:
     ```bash
     pyinstaller --onefile --windowed --hidden-import=plyer --hidden-import=plyer.platforms.win.notification --hidden-import=googleapiclient --hidden-import=google.oauth2 widget.py
     ```

3. **Risultato**:
   - L'applicazione sarà disponibile nella cartella `dist/` che verrà creata con il comando precedente.

---

## **Informazioni Aggiuntive**

- **Sviluppato in**: Visual Studio Code.
- **Sistema Operativo**: Windows.
- **Linguaggio**: Python 3.10.
- **Compatibilità**: Lo script è stato testato su Windows, ma può essere adattato facilmente per macOS o Linux.

---

## **Nota**

**File `token.json`**:
- Il file `token.json` viene generato automaticamente dopo la prima autenticazione. Non è necessario includerlo nel repository.

---

## **Licenza**

Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per ulteriori dettagli.

---
