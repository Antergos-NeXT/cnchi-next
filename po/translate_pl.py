"""Batch-fill Polish translations for all untranslated msgid in pl.po"""

import re

po_path = '/home/xalatath/Antergos-NeXT-ISO/Cnchi/po/pl.po'

translations = {
    "Set accessibility feature on by default":
        "Włącz funkcję ułatwień dostępu domyślnie",
    "Sets the Desktop Environment that will be installed":
        "Ustawia środowisko graficzne, które zostanie zainstalowane",
    "Disables first screen's 'try it' option":
        "Wyłącza opcję 'Wypróbuj' na pierwszym ekranie",
    "Makes checks optional in check screen":
        "Sprawia, że sprawdzanie na ekranie kontrolnym jest opcjonalne",
    "Show Cnchi version and quit":
        "Pokaż wersję Cnchi i wyjdź",
    "Show options in development (use at your own risk!)":
        "Pokaż opcje w fazie rozwoju (używasz na własne ryzyko!)",
    "Cnchi files not found. Please, install Cnchi using pacman":
        "Nie znaleziono plików Cnchi. Zainstaluj Cnchi za pomocą pacmana",
    "Advanced power management":
        "Zaawansowane zarządzanie energią",
    "Flash plugins":
        "Wtyczki Flash",
    "Steam + PlayonLinux":
        "Steam + PlayOnLinux",
    "Graphic drivers (Proprietary)":
        "Sterowniki graficzne (zamknięte)",
    "Apache (or Nginx) + Mariadb + PHP":
        "Apache (lub Nginx) + MariaDB + PHP",
    "Kernel (LTS version)":
        "Jądro (wersja LTS)",
    "SSH Service":
        "Usługa SSH",
    "Useful packages for individuals who are blind or visually impaired.":
        "Przydatne pakiety dla osób niewidomych lub niedowidzących.",
    "The AUR is a community-driven repository for Arch users.":
        "AUR to społecznościowe repozytorium dla użytkowników Arch.",
    "Enables your system to make wireless connections via Bluetooth.":
        "Umożliwia bezprzewodowe połączenia przez Bluetooth.",
    "Brings you the benefits of advanced power management for Linux.":
        "Zapewnia korzyści zaawansowanego zarządzania energią dla Linuxa.",
    "Vivaldi is a free, fast web browser designed for power-users.":
        "Vivaldi to darmowa, szybka przeglądarka zaprojektowana dla zaawansowanych użytkowników.",
    "Freeware software normally used for multimedia.":
        "Darmowe oprogramowanie zwykle używane do multimediów.",
    "Installs AMD or Nvidia proprietary graphic driver.":
        "Instaluje zamknięty sterownik graficzny AMD lub Nvidia.",
    "Installs Steam and Playonlinux for gaming enthusiasts.":
        "Instaluje Steam i PlayOnLinux dla entuzjastów gier.",
    "Apache (or Nginx) + Mariadb + PHP installation and setup.":
        "Instalacja i konfiguracja Apache (lub Nginx) + MariaDB + PHP.",
    "Open source office suite. Supports editing MS Office files.":
        "Otwarty pakiet biurowy. Obsługuje edycję plików MS Office.",
    "Enables Secure SHell service.":
        "Włącza usługę Secure SHell.",
    "Long term support (LTS) Linux kernel and modules.":
        "Jądro Linux z długoterminowym wsparciem (LTS) i moduły.",
    "Next":
        "Dalej",
    "Back":
        "Wstecz",
    "HTTP proxy server:":
        "Serwer pośredniczący HTTP:",
    "HTTPS proxy server:":
        "Serwer pośredniczący HTTPS:",
    "FTP proxy server:":
        "Serwer pośredniczący FTP:",
    "SOCKS host server:":
        "Serwer hosta SOCKS:",
    "Use this proxy server for all protocols":
        "Użyj tego serwera pośredniczącego dla wszystkich protokołów",
    "Port:":
        "Port:",
    "Server":
        "Serwer",
    "Rate":
        "Prędkość",
    "Time":
        "Czas",
    "Error creating metalink for package {}. Installation will stop":
        "Błąd tworzenia metalinka dla pakietu {}. Instalacja zostanie zatrzymana",
    "Device {0} will be ":
        "Urządzenie {0} zostanie ",
    "not formatted":
        "nie sformatowane",
    "mounted as {0}":
        "zamontowane jako {0}",
    "and encrypted.":
        "i zaszyfrowane.",
    "and not encrypted.":
        "i niezaszyfrowane.",
    "Unknown filesystem type {0}":
        "Nieznany typ systemu plików {0}",
    "Mounting boot partition {0} into {1} directory":
        "Montowanie partycji rozruchowej {0} do katalogu {1}",
    "Mounting EFI partition {0} into {1} directory":
        "Montowanie partycji EFI {0} do katalogu {1}",
    "Mounting partition {0} into {1} directory":
        "Montowanie partycji {0} do katalogu {1}",
    "Installing using the '{0}' method":
        "Instalowanie przy użyciu metody '{0}'",
    "Creating a temporary pacman.conf for {0} architecture":
        "Tworzenie tymczasowego pacman.conf dla architektury {0}",
    "Updating package manager security. Please wait...":
        "Aktualizowanie bezpieczeństwa menedżera pakietów. Proszę czekać...",
    "Configuring LightDM desktop manager...":
        "Konfigurowanie menedżera wyświetlania LightDM...",
    "LightDM display manager configuration completed.":
        "Konfiguracja menedżera wyświetlania LightDM zakończona.",
    "Error while trying to configure the LightDM display manager":
        "Błąd podczas próby konfiguracji menedżera wyświetlania LightDM",
    "Building zfs modules...":
        "Budowanie modułów ZFS...",
    "Configuring keymap...":
        "Konfigurowanie układu klawiatury...",
    "Configuring hardware...":
        "Konfigurowanie sprzętu...",
    "Getting your disk(s) ready for Antergos...":
        "Przygotowywanie dysku(tów) dla Antergos NeXT...",
    "Adding '%s' bootloader packages":
        "Dodawanie pakietów programu rozruchowego '%s'",
    "Couldn't find %s bootloader packages!":
        "Nie można znaleźć pakietów programu rozruchowego %s!",
    "Special dirs are already mounted. Skipping.":
        "Katalogi specjalne są już zamontowane. Pomijanie.",
    "GRUB(2) will NOT be installed":
        "GRUB(2) NIE zostanie zainstalowany",
    "No OEM loader found in %s. Copying Grub(2) into dir.":
        "Nie znaleziono programu ładującego OEM w %s. Kopiowanie Gruba(2) do katalogu.",
    "Copying Grub(2) into OEM dir failed: %s":
        "Kopiowanie Gruba(2) do katalogu OEM nie powiodło się: %s",
    "%.1f KiB":
        "%.1f KiB",
    "%.2f MiB":
        "%.2f MiB",
    "Applying deltas to packages...":
        "Stosowanie delt do pakietów...",
    "Checking keys in keyring...":
        "Sprawdzanie kluczy w pęku kluczy...",
    "Downloading missing keys into the keyring...":
        "Pobieranie brakujących kluczy do pęku kluczy...",
    "Explicitly installed":
        "Zainstalowane jawnie",
    "Home partition cannot be NTFS or FAT32":
        "Partycja domowa nie może być NTFS ani FAT32",
    "As no /boot/efi is defined (yet), /boot needs to be fat32.":
        "Ponieważ /boot/efi nie jest (jeszcze) zdefiniowane, /boot musi być fat32.",
    "/boot/efi needs to be fat32.":
        "/boot/efi musi być fat32.",
    "{0} is already mounted as swap, to continue it will be unmounted.":
        "{0} jest już zamontowane jako swap, aby kontynuować zostanie odmontowane.",
    "{0} is already mounted in {1}, to continue it will be unmounted.":
        "{0} jest już zamontowane w {1}, aby kontynuować zostanie odmontowane.",
    "Couldn't format LUKS device '{0}' with label '{1}' as '{2}': {3}":
        "Nie można sformatować urządzenia LUKS '{0}' z etykietą '{1}' jako '{2}': {3}",
    "Couldn't format partition '{0}' with label '{1}' as '{2}': {3}":
        "Nie można sformatować partycji '{0}' z etykietą '{1}' jako '{2}': {3}",
    "Cannot commit your changes to disk: {0}":
        "Nie można zatwierdzić zmian na dysku: {0}",
    "I need help with an Antergos / Windows(tm) dual boot setup!":
        "Potrzebuję pomocy z konfiguracją podwójnego rozruchu Antergos / Windows!",
    "How would you like to proceed?":
        "Jak chcesz kontynuować?",
    "WARNING! This will overwrite everything currently on your drive!":
        "OSTRZEŻENIE! To nadpisze wszystko na twoim dysku!",
    "LUKS Password. We do not recommend using special characters or accents!":
        "Hasło LUKS. Nie zalecamy używania znaków specjalnych ani akcentów!",
    "Please, choose now the device (or partition) to use as cache.":
        "Wybierz teraz urządzenie (lub partycję) do wykorzystania jako pamięć podręczna.",
    "Device {} will be fully erased! Are you REALLY sure?":
        "Urządzenie {} zostanie całkowicie wymazane! Czy na PEWNO chcesz kontynuować?",
    "Cnchi is up to date":
        "Cnchi jest aktualne",
    "You must reboot before retrying again.":
        "Musisz uruchomić ponownie przed kolejną próbą.",
    "Do you want to install the Nginx server instead of the Apache server?":
        "Czy chcesz zainstalować serwer Nginx zamiast Apache?",
    "Can't match a keymap for country code '%s'":
        "Nie można dopasować układu klawiatury dla kodu kraju '%s'",
    "Set keyboard to '{0}' ({1}), variant '{2}' ({3})":
        "Ustaw klawiaturę na '{0}' ({1}), wariant '{2}' ({3})",
    "Set keyboard to '{0}' ({1})":
        "Ustaw klawiaturę na '{0}' ({1})",
    "Can't get country code from %s location":
        "Nie można uzyskać kodu kraju z lokalizacji %s",
    "Let Cnchi sort the mirrors lists (recommended)":
        "Pozwól Cnchi posortować listy mirrorów (zalecane)",
    "Leave the mirrors lists as they are (by default)":
        "Pozostaw listy mirrorów bez zmian (domyślnie)",
    "Let me manage the mirrors lists (advanced)":
        "Pozwól mi zarządzać listami mirrorów (zaawansowane)",
    "Please reference the following number when reporting this error: ":
        "Proszę podać następujący numer przy zgłaszaniu tego błędu: ",
    "Location":
        "Lokalizacja",
    "Keyboard":
        "Klawiatura",
    "Desktop Environment":
        "Środowisko graficzne",
    "Features":
        "Funkcje",
    "Layout: {0}":
        "Układ: {0}",
    "Variant: {0}":
        "Wariant: {0}",
    "Error getting changes from install screen":
        "Błąd pobierania zmian z ekranu instalacji",
    "Ranking mirrors":
        "Sortowanie mirrorów",
    "Cnchi is still updating and optimizing your mirror lists.":
        "Cnchi wciąż aktualizuje i optymalizuje listy mirrorów.",
    "Please be patient...":
        "Proszę być cierpliwym...",
    "Timezone (latitude %s, longitude %s) detected.":
        "Wykryto strefę czasową (szerokość %s, długość %s).",
    "Hostname":
        "Nazwa hosta",
    "Disk":
        "Dysk",
    "Disk ID":
        "ID dysku",
    "ZFS Setup":
        "Konfiguracja ZFS",
    "Pool type":
        "Typ puli",
    "Force ZFS 4k block size":
        "Wymuś rozmiar bloku ZFS 4k",
    "For the {0} pool_type, you must select at least two drives":
        "Dla typu puli {0} musisz wybrać co najmniej dwa dyski",
    "You must select at least {0} drives":
        "Musisz wybrać co najmniej {0} dyski",
    "An unknown error occurred while processing chosen ZFS options.":
        "Wystąpił nieznany błąd podczas przetwarzania wybranych opcji ZFS.",
    "'None' pool will use ZFS on a single selected disk.":
        "Pula 'None' użyje ZFS na pojedynczym wybranym dysku.",
    "Create {0} on device {1}":
        "Utwórz {0} na urządzeniu {1}",
    "Add device {0} to {1}":
        "Dodaj urządzenie {0} do {1}",
    "No devices were selected for the ZFS pool":
        "Nie wybrano urządzeń dla puli ZFS",
    "Using LUKS encryption will DELETE all partition contents!":
        "Użycie szyfrowania LUKS SPOWODUJE USUNIĘCIE zawartości partycji!",
    "LUKS passwords do not match! Encryption NOT enabled.":
        "Hasła LUKS nie są zgodne! Szyfrowanie NIE włączone.",
    "Volume name and password are mandatory! Encryption NOT enabled.":
        "Nazwa woluminu i hasło są wymagane! Szyfrowanie NIE włączone.",
    "Location:":
        "Lokalizacja:",
    "Can't label a {0} partition":
        "Nie można oznaczyć partycji {0}",
    "Cannot make a filesystem of type None in partition {0}":
        "Nie można utworzyć systemu plików typu None na partycji {0}",
    "Unknown filesystem {0} for partition {1}":
        "Nieznany system plików {0} dla partycji {1}",
    "Can't remove logical volume {0}":
        "Nie można usunąć woluminu logicznego {0}",
    "Can't remove volume group {0}":
        "Nie można usunąć grupy woluminów {0}",
    "Can't remove physical volume {0}":
        "Nie można usunąć woluminu fizycznego {0}",
    "*** %(file)s:%(lineno)s: Seen unexpected token \"%(token)s\"":
        "*** %(file)s:%(lineno)s: Nieoczekiwany token \"%(token)s\"",
    "# File: %(filename)s, line: %(lineno)d":
        "# Plik: %(filename)s, linia: %(lineno)d",
    " %(filename)s:%(lineno)d":
        " %(filename)s:%(lineno)d",
    "Invalid value for --style: %s":
        "Nieprawidłowa wartość dla --style: %s",
    "pygettext.py (xgettext for Python) %s":
        "pygettext.py (xgettext dla Pythona) %s",
    "--width argument must be an integer: %s":
        "Argument --width musi być liczbą całkowitą: %s",
    "Can't read --exclude-file: %s":
        "Nie można odczytać --exclude-file: %s",
    "Reading standard input":
        "Czytanie standardowego wejścia",
    "Working on %s":
        "Przetwarzanie %s",
    "*** Seen unexpected token \"%(token)s\"":
        "*** Nieoczekiwany token \"%(token)s\"",
    "morethanonestring":
        "więcejniżjedennapis",
}

with open(po_path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

i = 0
fixed = 0
while i < len(lines):
    line = lines[i]
    if line.startswith('msgid "') and not line.startswith('msgid ""'):
        msgid_match = re.match(r'^msgid "(.*)"$', line)
        if msgid_match:
            msgid = msgid_match.group(1)
            # Check if next line has empty msgstr
            if i + 1 < len(lines) and lines[i + 1] == 'msgstr ""':
                if msgid in translations:
                    lines[i + 1] = f'msgstr "{translations[msgid]}"'
                    fixed += 1
    i += 1

result = '\n'.join(lines)

with open(po_path, 'w', encoding='utf-8') as f:
    f.write(result)

print(f"Fixed {fixed} translations")
