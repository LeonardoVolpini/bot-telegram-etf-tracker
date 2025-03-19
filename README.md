# ETF Tracker Bot - @ETFtrackingBot

Il bot Telegram, @ETFtrackingBot, monitora automaticamente gli ETF e invia notifiche quando il prezzo scende di una percentuale specificata rispetto al massimo degli ultimi x giorni.

## Struttura del progetto

- `main.py` - Punto di ingresso dell'applicazione
- `bot.py` - Gestisce i comandi e i messaggi del bot Telegram
- `monitor.py` - Gestisce il monitoraggio periodico degli ETF in un thread separato
- `etf_service.py` - Funzioni per recuperare dati sugli ETF da Yahoo Finance tramite yfinance
- `database.py` - Funzioni per interagire con il database su Supabase
- `config.py` - Configurazioni e recupero variabili d'ambiente

## Comandi del bot

- `/start` - Avvia il bot
- `/help` - Mostra l'elenco dei comandi disponibili
- `/track <etf_symbol> <percentage_threshold> <days_back>` - Inizia a monitorare un ETF, impostando una soglia (in %) e un periodo
- `/etfs` - Elenca gli ETF attualmente monitorati, indicandone soglia e giorni impostati, prezzo massimo negli ultimi x giorni, prezzo attuale e perdita attuale
- `/remove <etf_symbol>` - Smetti di monitorare un ETF

## Hosting

Il bot è attualmente hostato su Railway

## Schema del database

### Tabella `Users`
- `id` (primario) - Id univoco
- `username` - Username dell'utente Telegram o ID della chat
- `chat_id` - ID della chat Telegram
- `created_at` - Data e ora di creazione

### Tabella `Etfs`
- `user` (chiave esterna) - Riferimento a Users.username
- `symbol` (primario) - Simbolo dell'ETF
- `price_max` - Prezzo massimo nel periodo monitorato
- `threshold` - Soglia percentuale di perdita
- `days` - Periodo di monitoraggio in giorni
- `created_at` - Data e ora di creazione
- `updated_at` - Data e ora dell'ultimo aggiornamento

### Tabella `EtfNotifications`
- `id` (primario) - Id univoco
- `user` - Riferimento a Users.username
- `etf_symbol` - Simbolo dell'ETF
- `loss_pct` - Perdita in percentuale
- `notified_at` - Data e ora dell'ultima notofica