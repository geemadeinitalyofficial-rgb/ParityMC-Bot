
<div align="center">

# ⚖️ SusMC Bot

**Il bot Discord tuttofare per il tuo server Minecraft.**
Ticket, moderazione, automod, economia, giochi, colloqui staff, canali temporanei, ferie staff e un pannello web completo — tutto in un unico bot.

![Python](https://img.shields.io/badge/Python-3.11%2B-b89416?style=flat-square&logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.3%2B-d3d3d3?style=flat-square&logo=discord&logoColor=333)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-b89416?style=flat-square&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/license-Private-d3d3d3?style=flat-square)

</div>

---

## 📌 Indice

- [Panoramica](#-panoramica)
- [Funzionalità](#-funzionalità)
  - [🎫 Sistema Ticket](#-sistema-ticket)
  - [📋 Candidature Staff](#-candidature-staff)
  - [🤝 Partnership](#-partnership)
  - [🛡️ Moderazione](#️-moderazione)
  - [🤖 Automod](#-automod)
  - [👋 Welcome & Goodbye](#-welcome--goodbye)
  - [🎭 Ruoli & Staff](#-ruoli--staff)
  - [⭐ Livelli & XP](#-livelli--xp)
  - [🏷️ Tag](#️-tag)
  - [🎉 Giveaway](#-giveaway)
  - [📊 Sondaggi](#-sondaggi)
  - [⏰ Reminder](#-reminder)
  - [🎙️ Supporto Vocale](#️-supporto-vocale)
  - [🔊 Tempvoice](#-tempvoice)
  - [🔢 Counting](#-counting)
  - [🎮 Chat Games](#-chat-games)
  - [🪙 Economy](#-economy)
  - [🏖️ Ferie Staff](#️-ferie-staff)
  - [🎉 Comandi Fun](#-comandi-fun)
  - [🌐 Pannello Web](#-pannello-web)
- [Installazione](#-installazione)
- [Configurazione (.env)](#-configurazione-env)
- [Struttura del progetto](#-struttura-del-progetto)
- [Identità visiva](#-identità-visiva)
- [Stack tecnico](#-stack-tecnico)

---

## 📖 Panoramica

SusMC è un bot Discord monolitico pensato per la gestione completa di un server Minecraft: supporto agli utenti (ticket + vocale), moderazione, automazioni, engagement della community (livelli, economia, giochi) e gestione interna dello staff (candidature, ferie, promozioni). Include anche un **pannello di amministrazione web** (Flask) che condivide lo stesso database SQLite del bot, per gestire tutto anche da browser.

- **Comandi slash** (`/comando`) per (quasi) tutto, con autocompletamento e scelte guidate.
- **Comandi con prefisso** (`!comando`) per poche funzioni rapide (`!ping`, `!help`, `!funzioni`, `!sync`).
- **Persistenza dati** su database SQLite condiviso tra bot e pannello web — nessuna perdita di dati ai riavvii.
- **Thread separati**: bot Discord e server web Flask girano in parallelo nello stesso processo.

---

## 🧩 Funzionalità

### 🎫 Sistema Ticket

Pannello con menu a tendina per aprire ticket in categorie diverse (Generale, Partnership, Candidatura, Donazioni, Servizi, Pagamenti), ciascuna con la propria descrizione visibile nel menu e — se configurato — la propria **categoria Discord dedicata**.

| Comando | Descrizione |
|---|---|
| `/ticket-panel` | [Admin] Invia il pannello con il menu a tendina |
| `/claim` | [Staff] Prende in carico il ticket |
| `/aggiungi` `/rimuovi` | [Staff] Aggiunge/rimuove un utente dal ticket |
| `/rename` | [Staff] Rinomina il canale ticket |
| `/sposta` | [Staff] Sposta il ticket in un'altra categoria (riapplica permessi e categoria Discord) |
| `/transcript` | Genera una trascrizione `.txt` della conversazione |
| `/chiudi` | Chiude il ticket (con conferma) |
| `/lista-ticket` | [Staff] Elenca tutti i ticket aperti |
| `/ticket-info` | Info sul ticket corrente |
| `/autoclose-ticket` | [Admin] Attiva/disattiva la chiusura automatica dei ticket inattivi |
| `/autoclose-ticket-ore` | [Admin] Imposta dopo quante ore di inattività chiudere un ticket |

I ticket delle categorie **Partnership** e **Candidatura** sono visibili solo al ruolo dedicato (Addetto Partnership / Addetto Provini) più gli Admin — non all'intero staff.

### 📋 Candidature Staff

Colloquio testuale "stile appy" **dentro il ticket** (mai in DM): il bot fa le domande una alla volta e aspetta la risposta del candidato.

| Comando | Descrizione |
|---|---|
| `/staff-apply` | Avvia il colloquio per Helper Screenshare / Helper Supporter / Builder / Developer |

Al termine pubblica un riepilogo per lo staff e salva la candidatura nel database.

### 🤝 Partnership

| Comando | Descrizione |
|---|---|
| `/partnership` | Crea un canale pubblico di partnership con embed dedicato |
| `/modifica-partnership` | Modifica testo/nome di una partnership esistente |
| `/elimina-partnership` | Elimina il canale di una partnership |

### 🛡️ Moderazione

| Comando | Descrizione |
|---|---|
| `/ban` `/unban` | Banna/sbanna un utente |
| `/kick` | Espelle un utente |
| `/mute` `/unmute` | Timeout temporaneo |
| `/warn` `/warns` `/clearwarn` | Sistema di avvertimenti persistente |
| `/purge` | Elimina più messaggi in blocco |
| `/slowmode` | Imposta la modalità lenta di un canale |
| `/lock` `/unlock` | Blocca/sblocca la scrittura in un canale |

### 🤖 Automod

Filtro automatico su parole vietate, link e spam, con timeout automatico. Gli utenti con permesso *Gestisci Messaggi* sono esenti dal filtro.

| Comando | Descrizione |
|---|---|
| `/automod-setup` | [Admin] Attiva/disattiva l'automod |
| `/automod-parole` | [Admin] Aggiunge/rimuove parole dalla blacklist |
| `/automod-status` | Mostra la configurazione attuale |

### 👋 Welcome & Goodbye

| Comando | Descrizione |
|---|---|
| `/welcome-setup` | [Admin] Canale e messaggio di benvenuto (`{mention} {name} {server} {count} {id}`) |
| `/goodbye-setup` | [Admin] Canale e messaggio di addio |
| `/welcome-test` | [Admin] Invia un messaggio di prova |

### 🎭 Ruoli & Staff

| Comando | Descrizione |
|---|---|
| `/reaction-role` | [Admin] Collega un'emoji a un ruolo su un messaggio |
| `/autorole` | [Admin] Ruolo assegnato automaticamente ai nuovi membri |
| `/ruolo-add` `/ruolo-remove` | [Staff] Assegna/rimuove manualmente un ruolo |
| `/pex` | [Admin] Promuove uno staff (ruolo vecchio → ruolo nuovo) e annuncia la promozione |
| `/depex` | [Admin] Retrocede uno staff (ruolo vecchio → ruolo nuovo) e annuncia la retrocessione |

`/pex` e `/depex` pubblicano l'annuncio nel canale `STAFF_NEWS_CHANNEL_ID` (o nel log, se non impostato).

### ⭐ Livelli & XP

Sistema di progressione automatico basato sui messaggi (15-30 XP/msg, cooldown 60s).

| Comando | Descrizione |
|---|---|
| `/rank` | Mostra livello, XP e barra di progresso |
| `/leaderboard` | Classifica dei primi 10 utenti |
| `/setxp` | [Admin] Imposta manualmente l'XP di un utente |
| `/level-channel` | [Admin] Canale per gli annunci di level-up |

### 🏷️ Tag

| Comando | Descrizione |
|---|---|
| `/tag-crea` | [Staff] Crea una risposta rapida riutilizzabile |
| `/tag` | Mostra un tag |
| `/tag-lista` | Elenca tutti i tag disponibili |
| `/tag-elimina` | [Staff] Elimina un tag |

### 🎉 Giveaway

| Comando | Descrizione |
|---|---|
| `/giveaway-start` | [Staff] Avvia un giveaway a tempo |
| `/giveaway-end` | [Staff] Termina subito un giveaway |
| `/giveaway-reroll` | [Staff] Riesegue l'estrazione |

### 📊 Sondaggi

| Comando | Descrizione |
|---|---|
| `/poll` | Crea un sondaggio con fino a 10 opzioni |
| `/poll-fine` | [Staff] Chiude un sondaggio e mostra i risultati |

### ⏰ Reminder

| Comando | Descrizione |
|---|---|
| `/reminder` | Imposta un promemoria personale |
| `/reminder-lista` | Mostra i tuoi reminder attivi |
| `/reminder-cancella` | Cancella un reminder |

### 🎙️ Supporto Vocale

Coda + matchmaking automatico: gli utenti in attesa vengono abbinati automaticamente allo staff disponibile in una vocale privata dedicata.

| Comando | Descrizione |
|---|---|
| `/status-supporto` | Stato della coda e dello staff disponibile |
| `/sessioni` | Elenca le sessioni di supporto attive |
| `/chiudi-sessione` | [Staff] Chiude forzatamente una sessione |
| `/help-supporto` | Guida rapida per gli utenti |

Lo stesso identico meccanismo è disponibile anche per i **colloqui vocali di candidatura** (`/status-candidature`, `/colloqui`, `/chiudi-colloquio`, `/help-candidature-voice`), che abbina i candidati agli Addetti Provini disponibili invece che allo staff di supporto.

### 🔊 Tempvoice

Canali vocali temporanei "entra per creare": un membro entra nel canale hub e ottiene automaticamente una vocale privata di cui è proprietario. **Si elimina da sola quando resta vuota** (con riconciliazione automatica anche dopo un riavvio del bot).

| Comando | Descrizione |
|---|---|
| `/tempvoice-setup` | [Admin] Imposta hub e categoria di destinazione |
| `/tempvoice-rename` | Rinomina la propria vocale |
| `/tempvoice-limit` | Imposta il limite utenti |
| `/tempvoice-lock` `/tempvoice-unlock` | Blocca/sblocca l'accesso |
| `/tempvoice-kick` | Espelle un utente dalla propria vocale |

### 🔢 Counting

Canale dove contare in sequenza: un errore, un doppio turno o un messaggio non numerico resettano il conteggio.

| Comando | Descrizione |
|---|---|
| `/counting-setup` | [Admin] Attiva il gioco in un canale |
| `/counting-status` | Mostra conteggio attuale e record |
| `/counting-reset` | [Admin] Reset manuale |

### 🎮 Chat Games

Mini-giochi in chat che premiano in valuta virtuale (vedi [Economy](#-economy)).

| Comando | Descrizione |
|---|---|
| `/indovina` | Indovina un numero 1-100 con indizi "più alto/più basso" |
| `/trivia` | Domande a tema Minecraft/generale, vince chi risponde prima |
| `/scramble` | Riordina le lettere di una parola mescolata |

### 🪙 Economy

Valuta virtuale del server.

| Comando | Descrizione |
|---|---|
| `/balance` | Mostra il saldo |
| `/daily` | Ricompensa giornaliera (cooldown 24h) |
| `/pay` | Trasferisci monete a un altro utente |
| `/economy-leaderboard` | Classifica dei più ricchi |
| `/economy-add` | [Admin] Aggiunge/rimuove monete manualmente |

### 🏖️ Ferie Staff

Richiesta, approvazione e gestione automatica dei periodi di ferie, con ruolo dedicato assegnato/rimosso in automatico alle date giuste. Tutti gli avvisi vanno in un canale dedicato.

| Comando | Descrizione |
|---|---|
| `/ferie-richiedi` | [Staff] Richiede un periodo (date GG/MM/AAAA + motivo) |
| `/ferie-approva` `/ferie-rifiuta` | [Admin] Decide sulla richiesta (notifica in DM) |
| `/ferie-lista` | Elenca le richieste per stato |
| `/ferie-mie` | Le proprie richieste |
| `/ferie-status` | Controlla se uno staff è attualmente in ferie |

### 🎉 Comandi Fun

| Comando | Descrizione |
|---|---|
| `/8ball` | Palla magica |
| `/moneta` | Testa o croce |
| `/dado` | Lancia un dado (facce configurabili) |
| `/scelta` | Sceglie a caso tra più opzioni |
| `/ship` | Percentuale di compatibilità tra due utenti |
| `/abbraccio` `/schiaffo` `/complimento` `/roast` | Interazioni giocose tra membri |
| `/rate` | Valutazione casuale da 0 a 10 |

### 🌐 Pannello Web

Dashboard di amministrazione accessibile via browser, protetta da login.

- **Dashboard**: statistiche live, log recenti, stato del bot
- **Ticket**: lista aperti/chiusi, chiusura da remoto
- **Sessioni**: sessioni di supporto vocale attive/storiche
- **Membri**: ricerca, ruoli, data di ingresso
- **Ruoli**: gestione autorole e reaction role
- **Livelli**: classifica XP
- **Giveaway / Sondaggi**: stato e gestione
- **Log eventi**: filtrabili per livello (OK / INFO / WARN / ERROR)
- **Configurazione**: welcome/goodbye/automod modificabili da browser

---

## 🚀 Installazione

```bash
git clone <repo-url> susmc-bot
cd susmc-bot
pip install -r requirements.txt --break-system-packages
cp .env.example .env   # poi compila le variabili (vedi sotto)
python main.py
```

Requisiti: **Python 3.11+**, un bot Discord con gli Intent privilegiati abilitati (Members, Message Content, Presence).

---

## ⚙️ Configurazione (.env)

| Variabile | Obbligatoria | Descrizione |
|---|---|---|
| `DISCORD_TOKEN` | ✅ | Token del bot |
| `GUILD_ID` | ✅ | ID del server Discord |
| `PREFIX` | | Prefisso comandi testuali (default `!`) |
| `SUPPORT_ROLE_ID`, `ADMIN_ROLE_ID` | | Ruoli staff base |
| `PARTNERSHIP_ROLE_ID`, `CANDIDATURA_ROLE_ID` | | Ruoli con accesso esclusivo ai ticket dedicati |
| `LOG_CHANNEL_ID` | | Canale log generale (fallback per ferie/staff news) |
| `TICKET_CATEGORY_ID` | | Categoria ticket di default |
| `TICKET_CATEGORY_GENERALE_ID` … `TICKET_CATEGORY_PAGAMENTI_ID` | | Categorie Discord dedicate per tipo di ticket (opzionali) |
| `PARTNERSHIP_CATEGORY_ID` | | Categoria canali partnership |
| `LEVEL_CHANNEL_ID` | | Canale annunci level-up di default |
| `WAITING_CHANNEL_ID`, `STAFF_CHANNEL_ID`, `SUPPORT_CATEGORY_ID` | | Supporto vocale |
| `CANDIDATURA_WAITING_CHANNEL_ID`, `CANDIDATURA_STAFF_CHANNEL_ID`, `CANDIDATURA_VOICE_CATEGORY_ID` | | Colloqui vocali candidature |
| `TEMPVOICE_HUB_CHANNEL_ID`, `TEMPVOICE_CATEGORY_ID` | | Tempvoice (configurabile anche via `/tempvoice-setup`) |
| `TICKET_AUTOCLOSE_HOURS` | | Ore di inattività prima della chiusura automatica (default 48) |
| `FERIE_ROLE_ID`, `FERIE_CHANNEL_ID` | | Ruolo e canale dedicato del sistema ferie |
| `STAFF_NEWS_CHANNEL_ID` | | Canale annunci `/pex` `/depex` |
| `WEB_HOST`, `WEB_PORT`, `WEB_SECRET`, `WEB_USERNAME`, `WEB_PASSWORD`, `WEB_PUBLIC_URL` | | Pannello web |

Tutte le variabili non contrassegnate come obbligatorie hanno un fallback sicuro se lasciate vuote.

---

## 📁 Struttura del progetto

```
susmc-bot/
├── main.py                        # Entry point, carica i cog, sync comandi slash
├── config.py                      # Lettura .env
├── database.py                    # Tutte le query SQLite (fonte dati condivisa col pannello web)
├── branding.py                    # Palette colori e nome brand centralizzati
├── matchmaking.py                 # Coda/matchmaking riutilizzabile (supporto vocale + candidature)
├── session_manager.py             # Sessioni vocali di supporto
├── candidatura_session_manager.py # Sessioni vocali di colloquio candidatura
├── bot_logger.py                  # Log unificato su canale Discord + tabella eventi
├── utils.py                       # Helper generici (durate, ID messaggio, ecc.)
├── cogs/                          # Un modulo per ogni funzionalità
│   ├── tickets.py, staff_apply.py, partnership.py
│   ├── moderation.py, automod.py, welcome.py
│   ├── roles.py, staffroles.py, levels.py, tags.py
│   ├── giveaway.py, polls.py, reminders.py
│   ├── vocal_support.py, vocal_views.py
│   ├── candidatura_voice.py, candidatura_views.py
│   ├── counting.py, chatgames.py, economy.py
│   ├── tempvoice.py, ferie.py, fun.py
│   └── stats.py
└── web/                           # Pannello di amministrazione Flask
    ├── app.py
    ├── templates/
    └── static/
```

---

## 🎨 Identità visiva

Palette definita centralmente in [`branding.py`](./branding.py):

| Ruolo | Colore | Hex |
|---|---|---|
| Primario | 🟡 Giallo scuro | `#B89416` |
| Primario chiaro | 🟨 Giallo | `#E0BA3C` |
| Secondario | ⬜ Grigio chiaro | `#D3D3D3` |
| Secondario scuro | ◻️ Grigio | `#8C8C8C` |

I colori semantici (verde = successo, rosso = errore/pericolo) restano invariati per non compromettere la leggibilità degli avvisi. La stessa palette è applicata sia agli embed Discord sia al tema del pannello web.

---

## 🛠️ Stack tecnico

- **[discord.py](https://discordpy.readthedocs.io/)** 2.3+ — libreria bot Discord
- **Flask** 3.0+ — pannello di amministrazione web
- **SQLite** — database condiviso tra bot e pannello, zero dipendenze esterne
- **python-dotenv** — configurazione via `.env`

---

<div align="center">

Fatto con 🟡 per la community di **SusMC**

</div>
MDEOF
cd /home/claude/bot/paritymc_final && wc -l README.md && echo "README scritto correttamente"