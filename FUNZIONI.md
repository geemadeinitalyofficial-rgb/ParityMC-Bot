# ⚖️ ParityMC Bot — Lista completa funzioni

---

## 🎫 TICKET SYSTEM
| Comando | Tipo | Descrizione |
|---|---|---|
| `/ticket-panel` | Slash (Admin) | Invia il pannello con menu a tendina nel canale |
| `/chiudi` | Slash + Bottone | Chiude il ticket con conferma |
| `/transcript` | Slash + Bottone | Genera trascrizione `.txt` dell'intera chat |
| `/claim` | Slash + Bottone | Staff prende in carico il ticket |
| `/aggiungi @utente` | Slash (Staff) | Aggiunge un utente al canale ticket |
| `/rimuovi @utente` | Slash (Staff) | Rimuove un utente dal canale ticket |
| `/rename <nome>` | Slash (Staff) | Rinomina il canale ticket |
| `/lista-ticket` | Slash (Admin) | Lista tutti i ticket aperti |
| `/ticket-info` | Slash | Info dettagliate sul ticket corrente |

**Categorie:** Generale · Partnership · Donazioni · Servizi · Pagamenti  
**Persistenza:** Dati salvati su SQLite, sopravvive ai riavvii  
**Log automatico:** Ogni apertura/chiusura viene loggata nel canale configurato

---

## 🤝 PARTNERSHIP
| Comando | Tipo | Descrizione |
|---|---|---|
| `/partnership <nome> <testo>` | Slash (nel ticket) | Crea canale `🤝｜nome` solo-lettura con embed |
| `/modifica-partnership <nome> <testo>` | Slash (Staff) | Modifica embed e rinomina il canale |
| `/elimina-partnership` | Slash (Staff) | Elimina il canale partnership |

---

## 🛡️ MODERAZIONE
| Comando | Tipo | Descrizione |
|---|---|---|
| `/ban @utente [motivo] [giorni]` | Slash + `!ban` | Banna un utente ed elimina messaggi recenti |
| `/unban <user_id>` | Slash | Rimuove il ban |
| `/kick @utente [motivo]` | Slash + `!kick` | Espelle un utente |
| `/mute @utente [minuti] [motivo]` | Slash + `!mute` | Timeout Discord nativo |
| `/unmute @utente` | Slash + `!unmute` | Rimuove il timeout |
| `/warn @utente [motivo]` | Slash + `!warn` | Aggiunge un warn (salvato su DB) |
| `/warns @utente` | Slash | Mostra tutti i warn di un utente |
| `/clearwarn @utente` | Slash (Staff) | Azzera i warn di un utente |
| `/purge <n>` | Slash + `!purge` | Elimina fino a 100 messaggi |
| `/slowmode <secondi>` | Slash | Imposta/disabilita slowmode |
| `/lock` | Slash + `!lock` | Blocca il canale corrente |
| `/unlock` | Slash + `!unlock` | Sblocca il canale corrente |

---

## 🤖 AUTOMOD
| Comando | Tipo | Descrizione |
|---|---|---|
| `/automod-setup <true/false>` | Slash (Admin) | Attiva/disattiva automod |
| `/automod-parole <parola> <add/remove>` | Slash (Admin) | Gestisce la blacklist parole |
| `/automod-status` | Slash (Admin) | Mostra stato e configurazione |
| *(automatico)* | Listener | Filtra parole, link, spam (timeout 1 min) |

**Web Panel:** Configurabile anche dal pannello web → sezione Configurazione

---

## 👋 BENVENUTO & ADDIO
| Comando | Tipo | Descrizione |
|---|---|---|
| `/welcome-setup #canale [messaggio]` | Slash (Admin) | Configura il messaggio di benvenuto |
| `/goodbye-setup #canale [messaggio]` | Slash (Admin) | Configura il messaggio di addio |
| `/welcome-test` | Slash (Admin) | Testa il messaggio di benvenuto |
| *(automatico)* | Listener | Invia embed alla join/leave |

**Variabili messaggio:** `{mention}` `{name}` `{server}` `{count}` `{id}`

---

## 🎭 RUOLI
| Comando | Tipo | Descrizione |
|---|---|---|
| `/reaction-role <msg_id> <emoji> @ruolo` | Slash (Admin) | Collega emoji→ruolo su un messaggio |
| `/autorole @ruolo <add/remove>` | Slash (Admin) | Ruolo assegnato automaticamente alla join |
| `/ruolo-add @utente @ruolo` | Slash (Staff) | Aggiunge un ruolo manualmente |
| `/ruolo-remove @utente @ruolo` | Slash (Staff) | Rimuove un ruolo manualmente |
| *(automatico)* | Listener | Reaction add/remove gestisce i ruoli |

---

## ⭐ LIVELLI & XP
| Comando | Tipo | Descrizione |
|---|---|---|
| `/rank [@utente]` | Slash | Mostra livello, XP, barra progresso |
| `/leaderboard` | Slash | Top 10 utenti per XP |
| `/setxp @utente <xp>` | Slash (Admin) | Imposta XP manualmente |
| `/level-channel #canale` | Slash (Admin) | Canale per i messaggi di level up |
| *(automatico)* | Listener | +15-30 XP per messaggio (cooldown 60s) |

---

## 🏷️ TAG / RISPOSTE RAPIDE
| Comando | Tipo | Descrizione |
|---|---|---|
| `/tag-crea <nome> <contenuto>` | Slash (Staff) | Crea un tag |
| `/tag <nome>` | Slash + `!tag` | Mostra un tag |
| `/tag-lista` | Slash | Lista tutti i tag con contatore usi |
| `/tag-elimina <nome>` | Slash (Staff) | Elimina un tag |

---

## 🎉 GIVEAWAY
| Comando | Tipo | Descrizione |
|---|---|---|
| `/giveaway-start <durata> <vincitori> <premio>` | Slash (Staff) | Avvia giveaway (durata: 1h, 2d, 30m...) |
| `/giveaway-end <message_id>` | Slash (Staff) | Termina subito il giveaway |
| `/giveaway-reroll <message_id>` | Slash (Staff) | Riesegue l'estrazione |
| *(automatico)* | Task | Controlla ogni 10s, chiude allo scadere |

---

## 📊 SONDAGGI
| Comando | Tipo | Descrizione |
|---|---|---|
| `/poll <domanda> <opzioni>` | Slash | Crea sondaggio (opzioni separate da `\|`) |
| `/poll-fine <message_id>` | Slash (Staff) | Chiude e mostra risultati con barre |

**Max opzioni:** 10 · **Reazioni automatiche** aggiunte dal bot

---

## ⏰ REMINDER
| Comando | Tipo | Descrizione |
|---|---|---|
| `/reminder <durata> <testo>` | Slash | Imposta un promemoria personale |
| `/reminder-lista` | Slash | Mostra i tuoi reminder attivi |
| `/reminder-cancella <numero>` | Slash | Cancella un reminder |
| *(automatico)* | Task | Controlla ogni 10s e notifica |

---

## 🎙️ SUPPORTO VOCALE
| Comando | Tipo | Descrizione |
|---|---|---|
| `/status-supporto` | Slash | Coda utenti, staff disponibili, sessioni attive |
| `/sessioni` | Slash | Lista sessioni vocali aperte |
| `/chiudi-sessione #canale` | Slash (Staff) | Chiude forzatamente una sessione |
| `/help-supporto` | Slash | Guida per gli utenti |
| *(automatico)* | Listener | Matchmaking FIFO al join dei canali |

**Pannello per-sessione (bottoni):**
- 🛑 Chiudi assistenza
- ✏️ Rinomina canale (modal)
- 🔒 Blocca/Sblocca auto-chiusura
- ℹ️ Info sessione (durata, utente, staff)

**Features avanzate:**
- Coda FIFO con `asyncio.Lock` (no race condition)
- Auto-chiusura canale vuoto (timeout configurabile)
- Recovery sessioni dopo riavvio bot
- Persistenza su SQLite

---

## 📈 STATISTICHE
| Comando | Tipo | Descrizione |
|---|---|---|
| `/serverinfo` | Slash | Info complete del server |
| `/userinfo [@utente]` | Slash | Info su un membro |
| `/botinfo` | Slash | Uptime, latenza, versione |
| `/stats` | Slash | Statistiche rapide server |
| `!ping` | Prefisso | Latenza bot |
| `!help` | Prefisso | Lista comandi |
| `!sync` | Prefisso (Admin) | Forza sync comandi slash |

---

## 🌐 WEB PANEL (http://IP:8080)

| Sezione | Funzioni |
|---|---|
| 📊 Dashboard | Stats live (auto-refresh 5s), log recenti, latenza bot |
| 🎫 Ticket | Lista aperti/chiusi, chiusura remota con conferma |
| 🎙️ Sessioni Vocali | Sessioni attive con durata, storico, chiusura remota |
| 👥 Membri | Lista con avatar, ricerca live, ruoli, data join |
| 🎭 Ruoli & RR | Lista ruoli, gestione autorole, lista reaction roles |
| ⭐ Livelli XP | Classifica top 50 con avatar, XP, livello, messaggi |
| 🎉 Giveaway | Lista con stato, terminazione manuale |
| 📊 Sondaggi | Lista sondaggi aperti/chiusi |
| 📋 Log eventi | Filtro per livello (OK/INFO/WARN/ERROR) |
| ⚙️ Configurazione | Welcome/goodbye, automod tutto dal browser |
| 🔌 API JSON | `/api/stats` `/api/logs` per integrazioni esterne |

**Sicurezza:** Login con username+password, sessione Flask, accesso solo da IP autorizzato  
**Wispbyte:** Bind su `0.0.0.0:8080`, apri la porta nel firewall del panel Wispbyte

---

## 📦 SISTEMA
- **Persistenza:** SQLite (no dipendenze esterne)
- **Prefisso comandi:** `!` (configurabile)
- **Comandi slash:** sincronizzati sul server specifico (istantanei)
- **Logging:** console + canale Discord + database
- **Recovery:** sessioni vocali e pannelli persistenti sopravvivono ai riavvii
- **Thread separati:** bot Discord + web Flask in parallelo
