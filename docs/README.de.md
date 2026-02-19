# MTGA

<picture>
    <img alt="MTGA" src="https://github.com/BiFangKNT/mtga/blob/gui/icons/hero-img_f0bb32.png?raw=true">
</picture>

[![English](https://img.shields.io/badge/docs-English-purple)](README.en.md) [![简体中文](https://img.shields.io/badge/文档-简体中文-yellow)](../README.md) [![日本語](https://img.shields.io/badge/ドキュ-日本語-b7003a)](README.ja.md) [![한국어 문서](https://img.shields.io/badge/docs-한국어-green)](README.ko.md) [![Documentación en Español](https://img.shields.io/badge/docs-Español-orange)](README.es.md) [![Documentation en Français](https://img.shields.io/badge/docs-Français-blue)](README.fr.md) [![Documentação em Português (Brasil)](https://img.shields.io/badge/docs-Português-purple)](README.pt.md) [![Dokumentation auf Deutsch](https://img.shields.io/badge/docs-Deutsch-darkgreen)](README.de.md) [![Документация на русском языке](https://img.shields.io/badge/доки-Русский-darkblue)](README.ru.md)

## Einführung

MTGA ist eine auf einem lokalen Proxy basierende IDE-Lösung für feste Modellanbieter, die für Windows und macOS geeignet ist.

**Hinweis: Dieses Projekt unterstützt derzeit nur APIs im OpenAI-Format. Bitte stellen Sie sicher, dass Sie dieses verwenden. Andere Formate können vor der Nutzung in das OpenAI-Format konvertiert werden.**

<details>
  <summary>Du siehst nichts~~</summary>
  <br>
  <p>MTGA steht für Make T Great Again!</p>
 </details>

## Inhaltsverzeichnis

- [MTGA](#mtga)
  - [Einführung](#einführung)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Changelog](#changelog)
    - [v1.2.0 (Neueste)](#v120-neueste)
    - [v1.1.1](#v111)
    - [v1.1.0](#v110)
    - [v1.0.0](#v100)
  - [Schnellstart](#schnellstart)
    - [Windows-Benutzer (GUI-Ein-Klick-Start)](#windows-benutzer-gui-ein-klick-start)
    - [macOS-Benutzer (Anwendungsinstallation)](#macos-benutzer-anwendungsinstallation)
      - [Installationsmethode](#installationsmethode)
      - [Verwendungsmethode](#verwendungsmethode)
  - [macOS Lösung für das Problem „Paket ist beschädigt“](#macos-lösung-für-das-problem-paket-ist-beschädigt)
    - [Grafische Lösung](#grafische-lösung)
    - [CLI-Lösung](#cli-lösung)
  - [Vom Skript starten](#vom-skript-starten)
    - [Schritt 0: Umgebungsvorbereitung](#schritt-0-umgebungsvorbereitung)
      - [Windows](#windows)
        - [Schritt 1: Selbstsigniertes Zertifikat generieren](#schritt-1-selbstsigniertes-zertifikat-generieren)
        - [Schritt 2: CA-Zertifikat unter Windows vertrauen](#schritt-2-ca-zertifikat-unter-windows-vertrauen)
        - [Schritt 3: Hosts-Datei anpassen](#schritt-3-hosts-datei-anpassen)
        - [Schritt 4: Lokalen Proxy-Server (Python) starten](#schritt-4-lokalen-proxy-server-python-starten)
        - [Schritt 5: Trae IDE konfigurieren](#schritt-5-trae-ide-konfigurieren)
      - [macOS](#macos)
  - [😎 Auf dem neuesten Stand bleiben](#-auf-dem-neuesten-stand-bleiben)
  - [Referenzen](#referenzen)

---

## Changelog

### v1.2.0 (Neueste)

- 🔄 **Umstrukturierung der Modellzuordnungsarchitektur** – von "Eins-zu-Eins-Zuordnung" zu einer "einheitlichen Modellzuordnungsarchitektur"
  - Der trae-Endpunkt verwendet eine einheitliche Zuordnungsmodell-ID, MTGA wechselt über die Konfigurationsgruppe das tatsächliche Backend-Modell
  - Der Proxy-Server unterstützt Modell-ID-Zuordnung und MTGA Authentifizierungsprüfung
  - Globale Konfiguration unterstützt Einstellungen der Zuordnungsmodell-ID und MTGA Authentifizierungs-Key
- ⚡ **Optimierung der Konfigurationsgruppenverwaltung** – Umstrukturierung der Felder und Validierungslogik der Konfigurationsgruppe
  - Der Name der Konfigurationsgruppe ist optional, API-URL, tatsächliche Modell-ID und API-Key sind Pflichtfelder
  - Feld für Zielmodell-ID entfernt, stattdessen globale Zuordnungs-Konfiguration
  - Kopfzeile der Konfigurationsgruppen wurde umbenannt, abwärtskompatibel mit alten Konfigurationsdateien
- 🧪 **Neue automatisierte Testfunktion** – Vollständiges Modellverbindungstestsystem
  - Nach dem Speichern der Konfiguration wird die Modellverbindung automatisch getestet (GET `/v1/models/{Modell-id}`)
  - Manuelle Lebendigkeitstestfunktion, unterstützt Chat-Vervollständigungstest (POST `/v1/chat/completions`)
  - Detaillierte Testprotokolle inkl. Antwortinhalt und Token-Verbrauchsstatistik
- 🎯 **Verbesserte Benutzererfahrung** – Neuer Lebendigkeitstest-Button und ausführliche Hinweise
  - Der Lebendigkeitstest-Button unterstützt Tooltip-Hinweise, die vor Tokenverbrauch warnen
  - Asynchrone Tests verhindern UI-Blockaden, verbesserte Fehlerbehandlung
  - Sichere Anzeige des API-Keys (Maskierung)

<details>
<summary>Historische Versionen</summary>

### v1.1.1

- 🐛 **Problem mit der Hosts-Änderungsfunktion behoben** - Behebt das Problem mit abnormalen Zeilenumbrüchen bei der Änderung der Hosts-Datei

### v1.1.0

- ✨ **Neue Benutzerdatenverwaltungsfunktion** - Einzeldatei-Version unterstützt persistente Speicherung von Benutzerdaten
  - Datenspeicherort: Windows `%APPDATA%\MTGA\`, macOS/Linux `~/.mtga/`
  - Unterstützt Backup, Wiederherstellung und Löschen von Benutzerdaten
  - Konfigurationsdateien, SSL-Zertifikate, Hosts-Backups werden automatisch persistent gespeichert
- 🔧 **Einzeldatei-Build optimiert** - Verbessert `build_onefile.bat`, unterstützt variabilisierte Versionsnummern
- 🎯 **Benutzeroberfläche verbessert** - Hinzugefügt: Aktualisierungsschaltfläche für Konfigurationsgruppenliste, optimiertes Oberflächendesign
- 📖 **Dokumentation vervollständigt** - Neue Anleitung für Einzeldatei-Builds, Projekt dokumentation aktualisiert

### v1.0.0

- ✅ **Anpassung für Mac OS** - Unterstützt macOS-Anwendungsinstallationsmethode
- 🔄 **Standardanbieter geändert** - Von DeepSeek zu OpenAI geändert
- 📦 **Dateirestrukturierung** - DS-bezogene Dateien umbenannt in `*_ds.*` Format archiviert
- 🌐 **API-URL-Format geändert** - Von `https://your-api.example.com/v1` zu `https://your-api.example.com` geändert

</details>

---

## Schnellstart

### Windows-Benutzer (GUI-Ein-Klick-Start)

1. Laden Sie die neueste Version von `MTGA_GUI-v{Versionsnummer}-x64.exe` von [GitHub Releases](https://github.com/BiFangKNT/mtga/releases) herunter
2. Führen Sie die heruntergeladene exe-Datei durch Doppelklick aus (Administratorrechte erforderlich)
3. Füllen Sie in der geöffneten grafischen Oberfläche die API-URL und die Modell-ID aus
   - **API-URL muss nur die Domain enthalten (Portnummer optional, nicht ausfüllen wenn unsicher), keine nachfolgenden Routen, z.B.: `https://your-api.example.com`**
   - **Wenn Sie multimodale Fähigkeiten aktivieren möchten, können Sie den Modellnamen auf den integrierten multimodalen Modellnamen abbilden:**
   - <img width="247" height="76" alt="model mapping" src="../images/model-mapping.png?raw=true" />
   - <img width="380" height="141" alt="model mapping effects" src="../images/model-mapping-effects.png?raw=true" />
4. Klicken Sie auf den Button "Alle Dienste mit einem Klick starten"
5. Warten Sie, bis das Programm automatisch folgende Aktionen durchführt:
   - Generierung und Installation des Zertifikats
   - Änderung der hosts-Datei
   - Start des Proxy-Servers
6. Nach Abschluss führen Sie die IDE-Konfiguration gemäß [Schritt 5: Trae IDE konfigurieren](#第-5-步配置-trae-ide) durch

> [!NOTE]
>
> - Bei der ersten Ausführung müssen möglicherweise Firewall-Zugriffsberechtigungen erteilt werden
> - Die Einzeldatei-Version unterstützt persistente Speicherung von Benutzerdaten, Konfigurationen und Zertifikate werden automatisch gespeichert

### macOS-Benutzer (Anwendungsinstallation)

#### Installationsmethode

1. Laden Sie die neueste Version von `MTGA_GUI-v{Versionsnummer}-aarch64.dmg` von [GitHub Releases](https://github.com/BiFangKNT/mtga/releases) herunter
2. Doppelklicken Sie auf die DMG-Datei, das System mountet das Installationspaket automatisch
3. Ziehen Sie `MTGA_GUI.app` in den `Applications`-Ordner
4. Starten Sie die Anwendung vom Launchpad oder Applications-Ordner

#### Verwendungsmethode

1. Starten Sie `MTGA_GUI.app` (bei erstmaliger Ausführung möglicherweise in den Systemeinstellungen die Ausführung erlauben)
2. Füllen Sie in der grafischen Oberfläche aus:
   - **API-URL**: Ihre API-Service-Adresse (z.B.: `https://your-api.example.com`)
   - **Wenn Sie multimodale Fähigkeiten aktivieren möchten, können Sie den Modellnamen auf den integrierten multimodalen Modellnamen abbilden:**
   - <img width="247" height="76" alt="model mapping" src="../images/model-mapping.png?raw=true" />
   - <img width="380" height="141" alt="model mapping effects" src="../images/model-mapping-effects.png?raw=true" />
3. Klicken Sie auf den Button "Alle Dienste mit einem Klick starten"
4. Das Programm führt automatisch durch:
   - Generierung und Installation des SSL-Zertifikats in den System-Schlüsselbund
   - Änderung der `/etc/hosts`-Datei (Administratorrechte erforderlich)
5. Manuell im geöffneten Schlüsselbund-Fenster das generierte Zertifikat vertrauen, Standardname ist `MTGA_CA`
6. Lokalen Proxy-Server starten
7. Führen Sie die Einrichtung gemäß der untenstehenden [Trae IDE Konfiguration](#第-5-步配置-trae-ide) ab

> [!NOTE]
>
> - Die Installation des Zertifikats und die Änderung der Hosts erfordern Administratorrechte
> - Wenn die Meldung „Paket ist beschädigt“ erscheint, siehe [macOS Lösung für das Problem „Paket ist beschädigt“](#macos-lösung-für-das-problem-paket-ist-beschädigt)

## macOS Lösung für das Problem „Paket ist beschädigt“

Wenn beim Start von `MTGA_GUI.app` die folgende Meldung erscheint:

<img width="244" height="223" alt="app corrupted" src="../images/app-corrupted.png?raw=true" />

**Klicken Sie auf „Abbrechen“**. Folgen Sie dann den nächsten Schritten zur Lösung:

### Grafische Lösung

1. Laden Sie `Sentinel.dmg` von [Sentinel Releases](https://github.com/alienator88/Sentinel/releases/latest) herunter.
2. Doppelklicken Sie auf die `Sentinel.dmg`-Datei und ziehen Sie `Sentinel.app` in den Ordner „Programme“ (Applications).
3. Starten Sie `Sentinel.app` über das Launchpad oder den Programme-Ordner.
4. Ziehen Sie `MTGA_GUI.app` aus diesem Projekt in das linke Fenster von `Sentinel.app`.
   - <img width="355.33" height="373.33" alt="sentinel add app" src="../images/sentinel-add-app.png?raw=true" />

`MTGA_GUI.app` wird automatisch verarbeitet und gestartet.

### CLI-Lösung

1. Finden Sie den vollständigen Pfad von `MTGA_GUI.app`, zum Beispiel `/Applications/MTGA_GUI.app`.
2. Öffnen Sie das Terminal.
3. Führen Sie den folgenden Befehl aus, um `MTGA_GUI.app` zu signieren:
   ```zsh
   xattr -d com.apple.quarantine <vollständiger Pfad der Anwendung>
   ```
   Dies entfernt das `com.apple.quarantine`-Erweiterungsattribut von `MTGA_GUI.app`.
4. Starten Sie `MTGA_GUI.app`.

---

## Vom Skript starten

### Schritt 0: Umgebungsvorbereitung

#### Windows

- System: Windows 10 oder höher
- Administratorrechte erforderlich
- Python-Umgebung installieren, empfohlen Python 3.10 oder höher
- Git installieren

##### Schritt 1: Selbstsigniertes Zertifikat generieren

Git Bash öffnen:

```bash
# Wechseln Sie in das ca-Verzeichnis
cd "mtga/ca"

# 1. CA-Zertifikat generieren (ca.crt und ca.key)
./genca.sh
```

Bei Ausführung von `./genca.sh` wird gefragt: "Do you want to generate ca cert and key? [yes/no]". Eingabe `y` und Enter drücken. Anschließend werden einige Informationen abgefragt:

- `Country Name (2 letter code) []`: `CN` eingeben (oder anderer Ländercode)
- Andere Felder (wie State, Locality, Organization, Common Name for CA) können nach Bedarf ausgefüllt oder leer gelassen werden, `X` wird empfohlen. Common Name kann z.B. `MTGA_CA` sein. E-Mail kann leer bleiben.

```bash
# 2. SSL-Zertifikat für api.openai.com generieren (api.openai.com.crt und api.openai.com.key)
# Dieses Skript verwendet die Konfigurationsdateien api.openai.com.subj und api.openai.com.cnf im selben Verzeichnis
./gencrt.sh api.openai.com
```

Nach Abschluss finden Sie im Verzeichnis `mtga\ca` folgende wichtige Dateien:

- `ca.crt` (Ihr benutzerdefiniertes CA-Zertifikat)
- `ca.key` (Ihr benutzerdefinierter CA-Private Key - **nicht weitergeben**)
- `api.openai.com.crt` (SSL-Zertifikat für lokalen Proxy-Server)
- `api.openai.com.key` (SSL-Private Key für lokalen Proxy-Server - **nicht weitergeben**)

##### Schritt 2: CA-Zertifikat unter Windows vertrauen

1.  Datei `mtga\ca\ca.crt` finden.
2.  Doppelklick auf `ca.crt` öffnet Zertifikatsanzeige.
3.  "Zertifikat installieren..." Button klicken.
4.  "Aktueller Benutzer" oder "Lokaler Computer" wählen. "Lokaler Computer" empfohlen (erfordert Admin-Rechte), gilt für alle Benutzer.
5.  Im nächsten Dialog "Alle Zertifikate in folgendem Speicher speichern" wählen, dann "Durchsuchen..." klicken.
6.  "Vertrauenswürdige Stammzertifizierungsstellen" auswählen, dann "OK".
7.  "Weiter" klicken, dann "Fertigstellen". Bei Sicherheitswarnung "Ja" wählen.

##### Schritt 3: Hosts-Datei anpassen

**⚠️ Warnung: Nach diesem Schritt ist der ursprüngliche OpenAI-API-Zugriff nicht mehr möglich. Webseitennutzung bleibt unbeeinflusst.**

Hosts-Datei mit Admin-Rechten bearbeiten, um `api.openai.com` auf localhost umzuleiten.

1.  Hosts-Datei-Pfad: `C:\Windows\System32\drivers\etc\hosts`
2.  Datei mit Editor (Notepad oder andere Textverarbeitung) als Administrator öffnen.
3.  Folgende Zeile am Ende hinzufügen:
    ```
    127.0.0.1 api.openai.com
    ```
4.  Datei speichern.

##### Schritt 4: Lokalen Proxy-Server (Python) starten

**Vor dem Start des Proxy-Servers:**

1.  **Abhängigkeiten installieren**:
    ```bash
    pip install Flask requests
    ```
2.  **Skript konfigurieren**:
    - Öffnen Sie die Datei `trae_proxy.py`.
    - **Ändern Sie `TARGET_API_BASE_URL`**: Ersetzen Sie diese durch die Basis-URL der OpenAI-formatieren API der Website, mit der Sie sich tatsächlich verbinden möchten (z.B.: `"https://your-api.example.com"`).
    - **Zertifikatspfad bestätigen**: Das Skript liest standardmäßig `api.openai.com.crt` und `api.openai.com.key` aus `mtga\ca`. Wenn sich Ihre Zertifikate nicht in diesem Pfad befinden, ändern Sie bitte die Werte für `CERT_FILE` und `KEY_FILE`, oder kopieren Sie diese beiden Dateien in das vom Skript angegebene `CERT_DIR`.

**Proxy-Server ausführen:**

Öffnen Sie die Eingabeaufforderung (cmd) oder PowerShell **als Administrator** (da Port 443 abgehört wird) und führen Sie dann aus:

```bash
python trae_proxy.py
```

Wenn alles reibungslos verläuft, sollten Sie die Startprotokolle des Servers sehen.

##### Schritt 5: Trae IDE konfigurieren

1.  Öffnen und melden Sie sich bei der Trae IDE an.
2.  Klicken Sie im KI-Dialogfeld unten rechts auf das Modellsymbol und wählen Sie am Ende "Modell hinzufügen".
3.  **Anbieter**: Wählen Sie `OpenAI`.
4.  **Modell**: Wählen Sie "Benutzerdefiniertes Modell".
5.  **Modell-ID**: Geben Sie den Wert ein, den Sie im Python-Skript unter `CUSTOM_MODEL_ID` definiert haben (z.B.: `my-custom-local-model`).
6.  **API-Schlüssel**:
    - Wenn Ihre Ziel-API einen API-Schlüssel benötigt und Trae diesen über `Authorization: Bearer <key>` übergibt, wird der hier eingegebene Schlüssel vom Python-Proxy weitergeleitet.
    - Bei der Konfiguration von OpenAI in Trae hängt der API-Schlüssel mit der `remove_reasoning_content`-Konfiguration zusammen. Unser Python-Proxy verarbeitet diese Logik nicht, er leitet den Authorization-Header einfach weiter. Sie können versuchen, den für Ihre Ziel-API erforderlichen Schlüssel oder einen beliebigen Schlüssel im Format `sk-xxxx` einzugeben.

7.  Klicken Sie auf "Modell hinzufügen".
8.  Kehren Sie zum KI-Chatfeld zurück und wählen Sie unten rechts Ihr soeben hinzugefügtes benutzerdefiniertes Modell aus.

Wenn Sie nun über Trae mit diesem benutzerdefinierten Modell interagieren, sollten die Anfragen über Ihren lokalen Python-Proxy geleitet und an die von Ihnen konfigurierte `TARGET_API_BASE_URL` weitergeleitet werden.

**Hinweise zur Fehlerbehebung:**

- **Portkonflikte**: Wenn Port 443 bereits belegt ist (z.B. durch IIS, Skype oder andere Dienste), schlägt das Starten des Python-Skripts fehl. Sie müssen den Dienst beenden, der den Port belegt, oder das Python-Skript und Nginx (falls verwendet) so ändern, dass sie einen anderen Port überwachen (dies ist jedoch komplexer, da Trae den Zugriff auf `https://api.openai.com` über Port 443 hartkodiert).
- **Firewall**: Stellen Sie sicher, dass die Windows-Firewall eingehende Verbindungen an Port 443 für Python zulässt (obwohl es sich um eine lokale Verbindung `127.0.0.1` handelt, ist normalerweise keine spezielle Firewall-Konfiguration erforderlich, aber eine Überprüfung ist dennoch ratsam).
- **Zertifikatsprobleme**: Wenn Trae SSL/TLS-bezogene Fehler meldet, überprüfen Sie sorgfältig, ob das CA-Zertifikat korrekt unter "Vertrauenswürdige Stammzertifizierungsstellen" installiert ist und ob der Python-Proxy `api.openai.com.crt` und `.key` korrekt lädt.
- **Proxy-Protokolle**: Das Python-Skript gibt einige Protokolle aus, die bei der Problemdiagnose helfen können.

Diese Lösung ist etwas integrierter als der direkte Ansatz mit vproxy + nginx, da sowohl die TLS-Terminierung als auch die Proxy-Logik in einem Python-Skript zusammengefasst sind, was sie besser für schnelle Prototypenvalidierungen unter Windows geeignet macht.

#### macOS

-> [Startmethode für Mac OS-Skript](https://github.com/BiFangKNT/mtga/blob/gui/docs/README_macOS_cli.md)

---

## 😎 Auf dem neuesten Stand bleiben

Klicken Sie auf den Star- und Watch-Button oben rechts im Repository, um über die neuesten Entwicklungen auf dem Laufenden zu bleiben.

![star to keep latest](https://github.com/BiFangKNT/mtga/blob/gui/images/star-to-keep-latest.gif?raw=true)

---

## Referenzen

Das `ca`-Verzeichnis wurde aus dem Repository `wkgcass/vproxy` übernommen, vielen Dank an den großen Meister!
