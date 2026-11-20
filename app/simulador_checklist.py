#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIMULADOR DE CHECKLIST · LINUX (SMX)
====================================
Aplicació per practicar les tasques de l'avaluació pràctica de Linux
(RA3 · Linux bàsic i RA4 · Linux avançat).

  · Mode Blitz:      tasques aleatòries una darrere l'altra, amb cronòmetre.
  · Mode Simulador:  5 tasques (una per bloc) i 15 minuts de compte enrere.
  · Informe:         historial de totes les sessions i tasques resoltes.

Només necessita Python 3 (tkinter ja hi va inclòs). No cal instal·lar res més.
Executa:   py simulador_checklist.py      (Windows)
           python3 simulador_checklist.py (Linux / macOS)

Les dades es desen a la carpeta de l'usuari: .simulador_checklist_smx.json
"""
import tkinter as tk
from tkinter import font as tkfont, filedialog
import json
import random
import time
import math
import re
import html
import datetime
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# BANC DE TASQUES  (nivell -> blocs -> [enunciat, com es comprova, pista])
# ---------------------------------------------------------------------------
BANKS = {'RA3': {'titol': 'Linux bàsic',
         'blocs': [['A',
                    'Navegació i gestió de fitxers',
                    [["Crea l'estructura <b>~/examen/{entrada,sortida,arxiu}</b> amb una sola ordre.",
                      'ls -d ~/examen/*',
                      "Fes servir mkdir amb l'opció que crea carpetes intermèdies (-p) i les claus { } per crear-ne diverses alhora."],
                     ['Crea dins de ~/examen el fitxer ocult <b>.config_smx</b> i demostra que existeix.',
                      'ls -a ~/examen',
                      "Els fitxers ocults comencen per un punt. Per veure'ls, ls necessita una opció (-a)."],
                     ['Copia tots els fitxers <b>.conf</b> de /etc que comencin per <b>h</b> a ~/examen/arxiu.',
                      'ls ~/examen/arxiu',
                      'cp accepta comodins: pensa en un patró que comenci per h i acabi en .conf.'],
                     ['Crea els fitxers <b>dia1.log</b> a <b>dia7.log</b> amb una sola ordre i esborra només el dia3 i el dia5.',
                      'ls ~/examen',
                      'touch amb claus {1..7} crea una sèrie de fitxers; rm accepta diversos noms alhora.'],
                     ['Canvia el nom de la carpeta ~/examen/sortida a <b>resultats</b> sense crear-ne cap de nova.', 'ls ~/examen', 'Canviar el nom és el mateix que moure: mv origen destí.'],
                     ["Situa't a /usr/share i, sense sortir-ne, crea el fitxer <b>prova.txt</b> a la teva carpeta personal fent servir una ruta relativa.",
                      'history | tail -3; ls ~/prova.txt',
                      'Compta quants nivells has de pujar amb .. fins a / i després baixa fins a home/el_teu_usuari.'],
                     ['Troba a quina carpeta és el programa <b>ls</b> i digues quin tipus de fitxer és.',
                      'which ls; file $(which ls)',
                      'Hi ha una ordre que diu on és un programa (which) i una altra que diu de quin tipus és un fitxer (file).'],
                     ['Busca tots els fitxers de /etc acabats en <b>.conf</b> que tinguin a la ruta la paraula <b>apt</b>.',
                      "find /etc -path '*apt*' -name '*.conf'",
                      'find té opcions per filtrar pel nom (-name) i per la ruta (-path).'],
                     ['Mostra el contingut de /var/log ordenat per data de modificació, el més recent primer.', 'ls -lt /var/log', 'Mira al manual de ls quina opció ordena per data (time).'],
                     ['Mostra la mida en format llegible de tots els fitxers de /etc/apt.', 'ls -lh /etc/apt', "Busca l'opció de ls que mostra les mides en format llegible (human-readable)."],
                     ["Crea l'àlies <b>neteja</b> que executi <b>clear</b> i fes-lo servir.", 'alias', "La sintaxi és alias nom='ordre', sense espais al voltant de l'=."],
                     ['Explica la diferència entre <b>/root</b> i <b>/</b> i entra a cadascuna (si es pot).',
                      'Resposta oral + cd',
                      "/ és l'arrel de tot el sistema; /root és la carpeta personal de l'administrador. Per entrar a /root caldrà sudo."]]],
                   ['B',
                    'Text, redireccions i filtres',
                    [["Desa a ~/examen/usuaris.txt la llista de noms d'usuari del sistema ordenada alfabèticament.",
                      'cat ~/examen/usuaris.txt',
                      "El primer camp de /etc/passwd és el nom d'usuari. Combina cut (separador :) amb sort i redirigeix amb >."],
                     ['Compta quants usuaris del sistema tenen <b>/bin/bash</b> com a shell.',
                      "grep -c '/bin/bash' /etc/passwd",
                      'grep té una opció que compta les línies en lloc de mostrar-les (-c).'],
                     ['Executa <b>ls /etc /no_existeix</b> desant la sortida correcta a ok.txt i els errors a ko.txt.',
                      'cat ok.txt ko.txt',
                      'La sortida normal es redirigeix amb > i els errors amb 2>.'],
                     ['Mostra només les línies 5 a 10 de /etc/passwd.', 'head -n 10 /etc/passwd | tail -n 6', 'Combina head i tail amb una canonada |.'],
                     ['Mostra quants grups hi ha al sistema i desa el número a ~/examen/grups.txt i per pantalla alhora.',
                      'cat ~/examen/grups.txt',
                      'Els grups són a /etc/group. Compta les línies amb wc -l i fes servir tee per veure-ho i desar-ho alhora.'],
                     ['Mostra el valor de les variables HOME, USER i SHELL en una sola línia.', 'echo $HOME $USER $SHELL', 'Les variables es mostren amb echo i el símbol $ davant del nom.'],
                     ['Mostra totes les línies de /etc/services que continguin <b>ssh</b>, sense distingir majúscules, numerades.',
                      'grep -in ssh /etc/services',
                      'grep: una opció ignora majúscules (-i) i una altra numera les línies (-n).'],
                     ['Mostra les shells diferents que fan servir els usuaris de /etc/passwd i quants usuaris en fan servir cadascuna.',
                      'cut -d: -f7 /etc/passwd | sort | uniq -c',
                      'La shell és el camp 7 de /etc/passwd. Després: sort | uniq -c.'],
                     ['Crea amb <b>nano</b> el fitxer notes.txt amb tres línies i afegeix-hi una quarta línia sense obrir cap editor.',
                      'cat notes.txt',
                      "Per afegir una línia sense editor: echo 'text' >> fitxer."],
                     ["Crea amb <b>vim</b> el fitxer vim.txt amb el teu nom, desa'l i surt.", 'cat vim.txt', 'A vim: i per escriure, Esc per sortir del mode inserció i :wq per desar i sortir.'],
                     ["Converteix a majúscules el contingut de /etc/hostname i desa'l a ~/examen/HOST.txt.",
                      'cat ~/examen/HOST.txt',
                      'tr pot convertir de minúscules a majúscules (a-z A-Z). Envia-li el fitxer amb < o amb cat |.'],
                     ['Mostra les línies de /etc/passwd que NO contenen <b>nologin</b> i compta-les.',
                      'grep -vc nologin /etc/passwd',
                      'grep té una opció que inverteix la cerca (-v) i una altra que compta (-c).']]],
                   ['C',
                    'Usuaris i grups',
                    [["Crea l'usuari <b>tecnic1</b> amb carpeta personal i comprova que existeix.", 'id tecnic1; ls /home', "A Ubuntu, adduser crea l'usuari amb carpeta personal i et fa preguntes."],
                     ["Crea el grup <b>suport</b> i afegeix-hi l'usuari actual sense treure'l dels altres grups.",
                      'getent group suport',
                      "addgroup per crear el grup; usermod amb -aG per afegir-hi l'usuari sense treure'l d'altres grups."],
                     ["Crea l'usuari <b>becari</b>, posa-li contrasenya i inicia sessió amb ell al terminal.",
                      'su - becari; whoami',
                      "adduser crea l'usuari i demana la contrasenya. Per canviar d'usuari: su - nom."],
                     ["Mostra el UID, el GID i la carpeta personal de l'usuari actual a partir de /etc/passwd.",
                      'grep $USER /etc/passwd',
                      'Busca la teva línia a /etc/passwd amb grep i la variable $USER. UID = camp 3, GID = camp 4, carpeta = camp 6.'],
                     ["Crea l'usuari <b>temporal</b> i esborra'l juntament amb la seva carpeta personal.",
                      'id temporal; ls /home',
                      'deluser té una opció per esborrar també la carpeta personal (--remove-home).'],
                     ["Crea els grups <b>web</b> i <b>bd</b> i l'usuari <b>dev1</b> que pertanyi a tots dos.",
                      'groups dev1',
                      'Crea els grups amb addgroup i fes servir usermod -aG grup1,grup2 usuari.'],
                     ["Mostra a quins grups pertany l'usuari actual i digues quin li permet fer servir sudo.",
                      'groups',
                      "L'ordre groups mostra els teus grups. A Ubuntu, el grup d'administradors es diu igual que l'ordre que fas servir per administrar."],
                     ["Treu l'usuari <b>dev1</b> (o el que indiqui el professor/a) del grup <b>bd</b>.",
                      'groups dev1',
                      "gpasswd -d usuari grup treu un usuari d'un grup (també: deluser usuari grup)."],
                     ["Bloqueja el compte de l'usuari <b>becari</b> i demostra que està bloquejat.",
                      'sudo passwd -S becari',
                      "passwd -l bloqueja un compte i passwd -S en mostra l'estat (L = bloquejat)."],
                     ["Canvia el shell de l'usuari <b>tecnic1</b> a <b>/bin/sh</b>.", 'grep tecnic1 /etc/passwd', "usermod té una opció -s per canviar la shell (o l'ordre chsh)."],
                     ["Explica per què no es pot llegir /etc/shadow sense sudo i mostra'n els permisos.",
                      'ls -l /etc/shadow',
                      "Mira els permisos amb ls -l. Qui n'és el propietari? Quins permisos té «altres»?"],
                     ['Mostra els usuaris que tenen UID igual o superior a 1000 (usuaris humans).',
                      "awk -F: '$3>=1000' /etc/passwd",
                      'El camp 3 de /etc/passwd és el UID. Pots fer servir awk -F: amb una condició sobre $3.']]],
                   ['D',
                    'Permisos i propietaris',
                    [['Crea el fitxer secret.txt i fes que només el propietari el pugui llegir i escriure (en números).',
                      'ls -l secret.txt  → -rw-------',
                      'Llegir = 4, escriure = 2, executar = 1. Només el propietari: el grup i els altres a 0.'],
                     ["Crea un script <b>data.sh</b> que mostri la data, fes-lo executable i executa'l.",
                      'ls -l data.sh; ./data.sh',
                      "L'script pot començar amb #!/bin/bash i contenir l'ordre date. Després chmod u+x i executa'l amb ./"],
                     ['Posa permisos <b>rwxr-x---</b> a la carpeta ~/examen fent servir lletres (u, g, o).', 'ls -ld ~/examen', 'chmod amb lletres: u=rwx,g=rx,o= (sense espais).'],
                     ['Crea el fitxer informe.txt i canvia el propietari a <b>tecnic1</b> i el grup a <b>suport</b>.',
                      'ls -l informe.txt',
                      'chown pot canviar el propietari i el grup alhora amb usuari:grup (amb sudo).'],
                     ['Treu el permís de lectura a «altres» de tots els fitxers de ~/examen amb una sola ordre.', 'ls -l ~/examen', 'chmod o-r amb un comodín (*) aplica el canvi a tots els fitxers.'],
                     ['Interpreta els permisos de /usr/bin/passwd i explica per a què serveix la <b>s</b>.',
                      'ls -l /usr/bin/passwd',
                      "La s on hi hauria la x del propietari és el bit setuid: el programa s'executa amb els permisos del propietari."],
                     ['Crea la carpeta /srv/equip, del grup <b>suport</b>, on només el grup hi pugui entrar i escriure.',
                      'ls -ld /srv/equip → drwxrwx---',
                      'Crea la carpeta amb sudo, canvia-li el grup amb chgrp i posa permisos 770.'],
                     ['Crea una carpeta on tothom pugui escriure però cadascú només pugui esborrar els seus fitxers.',
                      'ls -ld → drwxrwxrwt',
                      'És el sticky bit: chmod +t o un 1 davant del número (1777).'],
                     ["Mostra l'umask actual i calcula quins permisos tindrà un fitxer nou. Comprova-ho.",
                      'umask; touch x; ls -l x',
                      "L'umask es resta dels permisos per defecte (666 per a fitxers). Amb umask 002, un fitxer nou queda 664."],
                     ['Crea una carpeta amb permisos 644 i intenta entrar-hi. Explica què passa i soluciona-ho.',
                      'ls -ld; cd',
                      'Per entrar en una carpeta cal el permís x. Afegeix-lo amb chmod +x o posa 755.'],
                     ['Converteix a número els permisos de /etc/passwd, /etc/shadow i /tmp.',
                      'ls -ld /etc/passwd /etc/shadow /tmp',
                      'r = 4, w = 2, x = 1: suma per a cada grup de tres. La t de /tmp és el sticky bit.'],
                     ['Fes que el fitxer llista.txt només es pugui llegir (ningú no hi pot escriure) i demostra-ho intentant afegir-hi text.',
                      'ls -l; echo x >> llista.txt',
                      "Treu el permís w a tothom (chmod a-w o 444) i prova d'afegir-hi text amb echo >>."]]],
                   ['E',
                    'Processos, paquets i compressió',
                    [["Executa <b>sleep 900</b> en segon pla, mostra'n el PID i atura'l.",
                      'jobs; pgrep sleep',
                      "Posa & al final per enviar-lo al segon pla. jobs o pgrep per veure'l i kill per aturar-lo."],
                     ['Mostra els 5 processos que consumeixen més memòria.',
                      'ps aux --sort=-%mem | head -6',
                      "ps aux té l'opció --sort; un - davant de %mem ordena de més a menys. Limita la sortida amb head."],
                     ["Executa <b>sleep 1000</b> en primer pla, pausa'l, envia'l al segon pla i després porta'l al primer pla i atura'l.",
                      'Ctrl+Z, bg, fg, Ctrl+C',
                      "Ctrl+Z el pausa, bg el reprèn en segon pla, fg el porta al primer pla i Ctrl+C l'atura."],
                     ['Mostra quin procés té el PID 1 i quin és el teu procés de shell.',
                      'ps -p 1; echo $$; ps -p $$',
                      'ps -p mostra un procés concret. La variable $$ conté el PID de la teva shell.'],
                     ['Executa un procés amb prioritat 15 i mostra la seva prioritat amb ps.', 'ps -o pid,ni,cmd', 'nice -n valor ordre &. Després ps -o pid,ni,cmd per veure la columna NI.'],
                     ["Instal·la el paquet <b>sl</b> (o el que indiqui el professor/a), executa'l i desinstal·la'l.",
                      'dpkg -l sl',
                      'sudo apt install, executa el programa pel seu nom i després sudo apt remove.'],
                     ["Busca un paquet que contingui la paraula <b>calculator</b> i mostra'n la descripció d'un.",
                      'apt search; apt show',
                      'apt search busca paquets i apt show en mostra la descripció.'],
                     ['Digues quina versió del paquet <b>bash</b> hi ha instal·lada.', 'dpkg -l bash  /  apt show bash', 'dpkg -l nom_paquet o apt show nom_paquet mostren la versió instal·lada.'],
                     ['Mostra quants paquets hi ha instal·lats al sistema.',
                      "dpkg -l | grep '^ii' | wc -l",
                      "dpkg -l llista els paquets; els instal·lats comencen per 'ii'. Compta'ls amb grep i wc -l."],
                     ["Crea una còpia comprimida de /etc/apt a ~/examen/apt.tar.gz i mostra'n el contingut sense extreure-la.",
                      'tar -tzf ~/examen/apt.tar.gz',
                      'tar: c crear, z gzip, v detall, f fitxer. Per llistar el contingut, t en lloc de c.'],
                     ['Extreu el fitxer apt.tar.gz a la carpeta ~/examen/restaurat.',
                      'ls -R ~/examen/restaurat',
                      "tar amb x per extreure i l'opció -C per indicar la carpeta de destí (que ha d'existir)."],
                     ["Mostra la memòria lliure i l'espai lliure del disc en format llegible.", 'free -h; df -h', 'free per a la memòria i df per al disc, tots dos amb -h.']]]]},
 'RA4': {'titol': 'Linux avançat',
         'blocs': [['A',
                    'Dispositius i discos',
                    [['Mostra tots els discos i particions de la VM amb la mida i el sistema de fitxers.', 'lsblk -f', 'lsblk té una opció (-f) que afegeix el sistema de fitxers.'],
                     ['Digues quin és el disc principal de la VM, quantes particions té i quina és la partició arrel.',
                      'lsblk; findmnt /',
                      "lsblk mostra discos i particions; findmnt / et diu quina partició està muntada a l'arrel."],
                     ["Llista els dispositius PCI i identifica quin és l'adaptador de xarxa.", 'lspci | grep -i net', "lspci llista els dispositius PCI; filtra amb grep -i per 'net' o 'ethernet'."],
                     ["Mostra els dispositius USB connectats (si no n'hi ha, explica què mostra la sortida).",
                      'lsusb',
                      'lsusb llista els dispositius USB. A la VM potser només hi ha controladors virtuals (root hub).'],
                     ['Mostra el tipus de dispositiu (bloc o caràcter) de /dev/sda i de /dev/tty0 i explica la diferència.',
                      'ls -l /dev/sda /dev/tty0  → b / c',
                      'Amb ls -l, la primera lletra indica el tipus: b (bloc) o c (caràcter).'],
                     ['Crea al segon disc (/dev/sdb) una taula de particions GPT amb una sola partició.',
                      'sudo fdisk -l /dev/sdb',
                      "sudo fdisk /dev/sdb: g crea una taula GPT, n una partició nova i w desa. Assegura't que és sdb!"],
                     ["Dona format ext4 a /dev/sdb1 amb l'etiqueta DADES.", 'lsblk -f /dev/sdb', "mkfs.ext4 té una opció -L per posar l'etiqueta. Sempre sobre /dev/sdb1."],
                     ["Mostra l'UUID de totes les particions.", 'sudo blkid', "blkid (amb sudo) mostra l'UUID i el tipus de cada partició. lsblk -f també."],
                     ["Crea amb dd un fitxer de 50 MB ple de zeros a ~/zeros.img i comprova'n la mida.", 'ls -lh ~/zeros.img', 'dd if=/dev/zero of=fitxer bs=1M count=…'],
                     ['Mostra la informació del nucli sobre el disc sda que hi ha a /sys/block.',
                      'ls /sys/block/sda; cat /sys/block/sda/size',
                      'A /sys/block/sda hi ha fitxers amb informació del disc; size dona la mida en sectors de 512 bytes.'],
                     ['Mostra els missatges del nucli que parlen del disc sdb.', 'sudo dmesg | grep sdb', 'dmesg mostra els missatges del nucli (amb sudo); filtra amb grep.'],
                     ['Mostra quina CPU i quanta memòria detecta el sistema, sense fer servir top.',
                      'lscpu; cat /proc/meminfo | head -3',
                      'lscpu per a la CPU; /proc/meminfo o free per a la memòria.']]],
                   ['B',
                    'Sistema de fitxers i muntatge',
                    [['Munta /dev/sdb1 a /mnt/dades i crea-hi un fitxer.', 'findmnt /mnt/dades; ls /mnt/dades', 'Crea la carpeta de muntatge amb mkdir i fes sudo mount dispositiu carpeta.'],
                     ['Desmunta /mnt/dades i comprova que el fitxer creat ja no es veu a la carpeta.',
                      'findmnt /mnt/dades; ls /mnt/dades',
                      'sudo umount carpeta. Quan no hi ha res muntat, la carpeta mostra el que hi ha al disc principal.'],
                     ['Afegeix /dev/sdb1 a /etc/fstab (per UUID) perquè es munti a /mnt/dades i prova-ho sense reiniciar.',
                      'cat /etc/fstab; sudo mount -a; findmnt /mnt/dades',
                      "Copia l'UUID amb blkid i afegeix a /etc/fstab: UUID=… /mnt/dades ext4 defaults 0 2. Prova-ho amb sudo mount -a."],
                     ["Crea un enllaç simbòlic ~/logs que apunti a /var/log i explica què passa si s'esborra el destí.", 'ls -l ~/logs', 'ln -s destí nom_enllaç crea un enllaç simbòlic.'],
                     ["Crea un fitxer i un enllaç dur. Demostra que comparteixen l'inode.", 'ls -li', "ln sense -s crea un enllaç dur. ls -i mostra el número d'inode."],
                     ['Mostra quants inodes té lliures la partició arrel.', 'df -i /', "df té una opció -i per mostrar inodes en lloc d'espai."],
                     ["Mostra l'espai lliure de totes les particions i digues quina està més plena.", 'df -h', "df -h mostra l'espai en format llegible; fixa't en la columna Use%."],
                     ['Mostra les 5 carpetes que ocupen més dins de /var.', 'sudo du -h /var --max-depth=1 | sort -h | tail -5', 'du -h amb --max-depth=1 i ordena amb sort -h.'],
                     ["Crea un fitxer d'intercanvi (swap) de 256 MB, activa'l i comprova-ho.", 'swapon --show; free -h', 'fallocate -l 256M fitxer (o dd), chmod 600, mkswap i swapon.'],
                     ['Comprova el sistema de fitxers de /dev/sdb1 (desmuntat) amb fsck.', 'sudo fsck -f /dev/sdb1', 'Primer desmunta la partició. fsck -f força la comprovació.'],
                     ['Explica per a què serveixen /, /boot, /var i /tmp i mostra en quina partició és cadascuna.',
                      'findmnt; df -h /boot /var /tmp',
                      'findmnt o df mostren on està muntada cada carpeta.'],
                     ['Mostra les opcions de muntatge de la partició arrel i digues si és de lectura i escriptura.',
                      'findmnt -o TARGET,OPTIONS /',
                      'findmnt -o TARGET,OPTIONS /. Busca rw (lectura i escriptura) o ro (només lectura).']]],
                   ['C',
                    'Arrencada i nucli',
                    [['Mostra la versió del nucli en execució i els nuclis instal·lats a /boot.',
                      'uname -r; ls /boot/vmlinuz*',
                      'uname -r mostra la versió en execució; els fitxers vmlinuz són a /boot.'],
                     ['Digues si la VM ha arrencat en mode UEFI o BIOS i com ho has sabut.',
                      'ls /sys/firmware/efi  (existeix = UEFI)',
                      'Si existeix la carpeta /sys/firmware/efi, el sistema ha arrencat en mode UEFI.'],
                     ['Mostra el fitxer de configuració de GRUB i digues quants segons espera el menú.',
                      'grep TIMEOUT /etc/default/grub',
                      'La configuració és a /etc/default/grub; busca la variable GRUB_TIMEOUT.'],
                     ["Canvia el temps d'espera de GRUB a 10 segons i aplica el canvi.",
                      'grep TIMEOUT /etc/default/grub; sudo update-grub',
                      'Edita /etc/default/grub amb sudo nano i després executa sudo update-grub.'],
                     ["Mostra quant ha trigat l'última arrencada i quins serveis han trigat més.",
                      'systemd-analyze; systemd-analyze blame | head',
                      'systemd-analyze mostra el temps total i systemd-analyze blame, el de cada servei.'],
                     ["Llista els mòduls del nucli carregats i busca'n un relacionat amb VirtualBox.", 'lsmod | grep -i vbox', 'lsmod llista els mòduls carregats; filtra amb grep -i vbox.'],
                     ["Mostra la informació d'un mòdul del nucli (descripció, fitxer, autor).", 'modinfo <mòdul>', "modinfo nom_del_mòdul. Agafa'n un de la llista de lsmod."],
                     ["Carrega el mòdul <b>dummy</b>, comprova que hi és i descarrega'l.", 'lsmod | grep dummy', 'sudo modprobe carrega un mòdul i sudo modprobe -r el descarrega.'],
                     ['Mostra els paràmetres amb què ha arrencat el nucli.', 'cat /proc/cmdline', "Els paràmetres d'arrencada del nucli són a /proc/cmdline."],
                     ["Mostra els primers missatges del nucli de l'arrencada actual.", 'sudo dmesg | head -20', 'dmesg (amb sudo) mostra els missatges del nucli; combina-ho amb head.'],
                     ['Mostra quant de temps fa que el sistema està engegat i la càrrega mitjana.', 'uptime', 'uptime mostra el temps engegat i la càrrega mitjana.'],
                     ["Explica en ordre les fases de l'arrencada (firmware, GRUB, nucli, systemd) i mostra el procés PID 1.",
                      'ps -p 1',
                      "Firmware → gestor d'arrencada → nucli → init. ps -p 1 et diu quin és l'init."]]],
                   ['D',
                    'Serveis (systemd) i tasques programades',
                    [["Mostra l'estat del servei <b>cron</b> i digues si s'inicia automàticament.",
                      'systemctl status cron; systemctl is-enabled cron',
                      "systemctl status mostra l'estat; systemctl is-enabled diu si s'inicia sol."],
                     ["Atura el servei cron, comprova-ho i torna'l a engegar.", 'systemctl is-active cron', 'sudo systemctl stop / start, i systemctl is-active per comprovar-ho.'],
                     ['Instal·la el servei <b>ssh</b> (openssh-server) i comprova que està actiu.', 'systemctl status ssh', 'El paquet es diu openssh-server. Després, systemctl status ssh.'],
                     ["Desactiva l'inici automàtic del servei ssh sense aturar-lo.", 'systemctl is-enabled ssh; is-active ssh', "systemctl disable treu l'inici automàtic però no atura el servei."],
                     ['Llista els serveis que estan en execució ara mateix.', 'systemctl list-units --type=service --state=running', 'systemctl list-units amb --type=service i --state=running.'],
                     ['Llista els serveis que han fallat.', 'systemctl --failed', 'systemctl té una opció per llistar les unitats que han fallat (--failed).'],
                     ['Mostra quin és el target per defecte del sistema i explica què vol dir.',
                      'systemctl get-default',
                      "systemctl get-default. Un target és un grup d'unitats que defineix un estat del sistema."],
                     ['Crea una tasca de cron que cada minut afegeixi la data a ~/cron.log i comprova que funciona.',
                      'crontab -l; cat ~/cron.log',
                      'crontab -e. Cinc asteriscs vol dir cada minut; >> afegeix al fitxer.'],
                     ["Programa una tasca de cron que s'executi cada dilluns a les 8:30 (pot ser un echo).", 'crontab -l  → 30 8 * * 1', 'Camps de cron: minut hora dia mes dia_setmana. Dilluns = 1.'],
                     ['Interpreta aquesta línia de cron: <b>0 */2 * * 1-5</b>.',
                      'Resposta oral: cada 2 h, de dilluns a divendres',
                      "*/2 al camp de l'hora vol dir cada 2 hores; 1-5 al dia de la setmana vol dir de dilluns a divendres."],
                     ["Mostra el fitxer d'unitat del servei cron i digues quin programa executa.",
                      'systemctl cat cron',
                      "systemctl cat nom_servei mostra el fitxer d'unitat. Busca la línia ExecStart."],
                     ["Programa una aturada del sistema d'aquí a 30 minuts i cancel·la-la.", 'sudo shutdown +30; sudo shutdown -c', "shutdown +minuts programa l'aturada; shutdown -c la cancel·la."]]],
                   ['E',
                    'Monitorització i registres',
                    [["Mostra quins processos consumeixen més CPU amb top i ordena'ls per memòria.", 'top → Maj+M', 'Dins de top, Maj+M ordena per memòria i Maj+P per CPU.'],
                     ['Mostra la càrrega del sistema i explica què volen dir els tres números.', 'uptime  /  cat /proc/loadavg', "uptime o /proc/loadavg. Són la càrrega mitjana d'1, 5 i 15 minuts."],
                     ["Mostra l'ús de memòria i d'intercanvi cada 2 segons, 5 vegades.", 'vmstat 2 5', 'vmstat interval vegades (per exemple, vmstat 2 5).'],
                     ['Mostra quins fitxers té oberts el procés de la teva shell.', 'lsof -p $$', 'lsof -p PID. La variable $$ és el PID de la teva shell.'],
                     ['Mostra quin procés fa servir el port 22 (o un altre que indiqui el professor/a).',
                      'sudo ss -tlnp | grep :22',
                      'ss -tlnp (amb sudo) mostra els ports oberts i el procés. Filtra amb grep.'],
                     ["Mostra els fils (threads) d'un procés.", 'ps -T -p <PID>  /  top -H', "ps -T -p PID o top -H mostren els fils d'un procés."],
                     ['Mostra les últimes 20 línies del registre del sistema.', 'sudo journalctl -n 20  /  tail -20 /var/log/syslog', 'journalctl -n 20 o tail -n 20 /var/log/syslog.'],
                     ["Mostra els registres del servei ssh (o cron) de l'última hora.", "journalctl -u cron --since '1 hour ago'", "journalctl -u nom_servei --since '1 hour ago'."],
                     ["Mostra els intents d'autenticació amb sudo que hi ha al registre.",
                      'sudo grep sudo /var/log/auth.log | tail',
                      "Els intents d'autenticació són a /var/log/auth.log. Filtra per sudo amb grep."],
                     ['Segueix en directe el registre del sistema i genera-hi un missatge amb logger.',
                      "journalctl -f  +  logger 'prova SMX'",
                      "journalctl -f segueix el registre en directe. En un altre terminal: logger 'missatge'."],
                     ["Mostra només els missatges d'error de l'arrencada actual.", 'journalctl -b -p err', 'journalctl -b (arrencada actual) i -p err (només errors).'],
                     ['Mostra la configuració de logrotate del registre auth i explica cada quan es rota.',
                      'cat /etc/logrotate.d/rsyslog',
                      'Les configuracions de logrotate són a /etc/logrotate.d/. Busca la que inclou auth.log (rsyslog).']]]]}}

NOTES = {5: 10, 4: 8, 3: 6, 2: 3, 1: 1, 0: 0}
SIM_SEGONS = 15 * 60
DATA_FILE = Path.home() / ".simulador_checklist_smx.json"

# ---------------------------------------------------------------------------
# ESTIL
# ---------------------------------------------------------------------------
W, H = 1120, 720
BG = "#0b1020"; CARD = "#151e36"; CARD2 = "#1d2848"; LINE = "#2b3966"
TEXT = "#e8eefc"; MUTED = "#8d9abf"; BOLDTXT = "#8fdcff"
ACC = "#7c5cff"; ACC2 = "#22d3ee"; OK = "#22c55e"; WARN = "#facc15"; BAD = "#f43f5e"; ORANGE = "#fb923c"
BLOC_COL = {"A": "#3b82f6", "B": "#8b5cf6", "C": "#f97316", "D": "#f43f5e", "E": "#14b8a6"}
DARK_FG = {OK: "#06240f", WARN: "#2b2100", ACC2: "#04222b", ORANGE: "#2a1203"}


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    A, B = hx(a), hx(b)
    return "#%02x%02x%02x" % tuple(int(A[i] + (B[i] - A[i]) * t) for i in range(3))


def ease(t):
    return 1 - (1 - max(0.0, min(1.0, t))) ** 3


def fmt(s):
    s = max(0, int(round(s)))
    return f"{s // 60:02d}:{s % 60:02d}"


def fmt_d(s):
    s = max(0.0, s)
    return f"{int(s // 60):02d}:{s % 60:04.1f}"


def strip_tags(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t))


def rich_parts(t):
    out = []
    for m in re.split(r"(<b>.*?</b>)", t):
        if m:
            out.append((strip_tags(m), m.startswith("<b>")))
    return out


def slug(t):
    s = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_") or "alumne"


def round_rect(cv, x1, y1, x2, y2, r=16, **kw):
    r = max(1, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2,
           x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return cv.create_polygon(pts, smooth=True, **kw)


def build_tasks(bank):
    out = {}
    for codi, nom, tasks in bank["blocs"]:
        for i, (en, comp, pista) in enumerate(tasks, 1):
            out[f"{codi}{i}"] = {"bloc": codi, "nom_bloc": nom, "enunciat": en, "comprova": comp, "pista": pista}
    return out


def ara():
    return datetime.datetime.now().isoformat(timespec="seconds")


def data_curta(iso):
    try:
        return datetime.datetime.fromisoformat(iso).strftime("%d/%m %H:%M")
    except Exception:
        return iso


# ---------------------------------------------------------------------------
# DADES
# ---------------------------------------------------------------------------
class Store:
    def __init__(self):
        self.d = {"actual": None, "nivell": "RA3", "alumnes": {}}
        try:
            self.d.update(json.loads(DATA_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
        if self.d.get("nivell") not in BANKS:
            self.d["nivell"] = next(iter(BANKS))

    def save(self):
        try:
            DATA_FILE.write_text(json.dumps(self.d, ensure_ascii=False, indent=1), encoding="utf-8")
        except Exception as e:
            print("No s'han pogut desar les dades:", e)

    @property
    def nom(self):
        return self.d.get("actual")

    @property
    def nivell(self):
        return self.d.get("nivell", "RA3")

    def set_nom(self, n):
        self.d["actual"] = n
        self.d["alumnes"].setdefault(n, {"sessions": []})
        self.save()

    def noms(self):
        return list(self.d["alumnes"].keys())

    def sessions(self, nivell=None):
        s = self.d["alumnes"].get(self.nom, {}).get("sessions", [])
        return [x for x in s if nivell is None or x.get("nivell") == nivell]

    def add(self, ses):
        self.d["alumnes"].setdefault(self.nom, {"sessions": []})["sessions"].append(ses)
        self.save()

    def stats(self, nivell):
        ss = self.sessions(nivell)
        per = {}
        temps = []
        for s in ss:
            for t in s["tasques"]:
                p = per.setdefault(t["id"], {"fetes": 0, "intents": 0, "millor": None, "sense_pista": False, "pistes": 0})
                p["intents"] += 1
                p["pistes"] += t.get("pistes", 0)
                if t["feta"]:
                    p["fetes"] += 1
                    if t.get("pistes", 0) == 0:
                        p["sense_pista"] = True
                    if s["tipus"] == "blitz" and t.get("temps"):
                        temps.append(t["temps"])
                        p["millor"] = t["temps"] if p["millor"] is None else min(p["millor"], t["temps"])
        notes = [s["nota"] for s in ss if s["tipus"] == "simulador" and s.get("nota") is not None]
        return {"per": per, "blitz": sum(1 for s in ss if s["tipus"] == "blitz"), "sim": len(notes), "notes": notes,
                "resoltes": sum(1 for p in per.values() if p["fetes"]),
                "sense_pista": sum(1 for p in per.values() if p["sense_pista"]),
                "temps_mitja": (sum(temps) / len(temps)) if temps else None, "sessions": ss}


# ---------------------------------------------------------------------------
# APLICACIÓ
# ---------------------------------------------------------------------------
class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulador de Checklist · Linux (SMX)")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{W}x{H}+{max(0, (sw - W) // 2)}+{max(0, (sh - H) // 2 - 30)}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        fams = set(tkfont.families(self.root))
        pick = lambda *c: next((f for f in c if f in fams), "TkDefaultFont")
        self.ff = pick("Segoe UI", "SF Pro Display", "Helvetica Neue", "Ubuntu", "Cantarell", "Noto Sans", "DejaVu Sans", "Arial")
        self.fm = pick("Cascadia Mono", "Consolas", "Menlo", "Ubuntu Mono", "DejaVu Sans Mono", "Courier New")
        self._fonts = {}
        self.cv = tk.Canvas(self.root, width=W, height=H, bg=BG, highlightthickness=0, bd=0)
        self.cv.pack(fill="both", expand=True)
        self.store = Store()
        self.tasks = {nv: build_tasks(b) for nv, b in BANKS.items()}
        self.after_ids = set()
        self.widgets = []
        self.keymap = {}
        self.btns = {}
        self._uid = 0
        self._fade_jobs = {}
        self._toast_tok = 0
        self.close_hook = None
        self.hist_cv = None
        self.bz = None
        self.sm = None
        self.draw_bg()
        self.init_particles()
        self.root.bind("<Key>", self.on_key)
        self.root.bind_all("<MouseWheel>", self.on_wheel)
        self.root.bind_all("<Button-4>", lambda e: self.on_wheel(e, -1))
        self.root.bind_all("<Button-5>", lambda e: self.on_wheel(e, 1))
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        if self.store.nom and self.store.nom in self.store.d["alumnes"]:
            self.menu()
        else:
            self.welcome()

    # ------------------------------------------------------------ utilitats
    def F(self, size, bold=False, mono=False):
        return (self.fm if mono else self.ff, -int(size), "bold" if bold else "normal")

    def fobj(self, size, bold=False, mono=False):
        k = (size, bold, mono)
        if k not in self._fonts:
            self._fonts[k] = tkfont.Font(root=self.root, family=self.fm if mono else self.ff, size=-int(size), weight="bold" if bold else "normal")
        return self._fonts[k]

    def uid(self, p="u"):
        self._uid += 1
        return f"{p}{self._uid}"

    def later(self, ms, fn):
        ref = []

        def run():
            if ref:
                self.after_ids.discard(ref[0])
            fn()
        a = self.root.after(ms, run)
        ref.append(a)
        self.after_ids.add(a)
        return a

    def T(self, x, y, text, size=16, color=TEXT, bold=False, anchor="center", mono=False, tags=("scr",), **kw):
        return self.cv.create_text(x, y, text=text, font=self.fobj(size, bold, mono), fill=color, anchor=anchor, tags=tags, **kw)

    def R(self, x1, y1, x2, y2, r=18, fill=CARD, outline="", width=1, tags=("scr",)):
        return round_rect(self.cv, x1, y1, x2, y2, r, fill=fill, outline=outline, width=width, tags=tags)

    def rich(self, x, y, width, text, size=18, color=TEXT, tags=("scr",), lh=1.32, bcolor=BOLDTXT):
        fN, fB = self.fobj(size), self.fobj(size, True)
        space = fN.measure(" ")
        line_h = int(fN.metrics("linespace") * lh)
        cx, cy = x, y
        for seg, bold in rich_parts(text):
            for w in re.split(r"(\s+)", seg):
                if not w:
                    continue
                if w.isspace():
                    if cx > x:
                        cx += space
                    continue
                f = fB if bold else fN
                ww = f.measure(w)
                if cx + ww > x + width and cx > x:
                    cx, cy = x, cy + line_h
                self.cv.create_text(cx, cy, text=w, font=f, fill=bcolor if bold else color, anchor="nw", tags=tags)
                cx += ww
        return cy + line_h - y

    def fit_rich(self, x, y, width, maxh, text, sizes, color=TEXT, tags=("scr",)):
        tmp = self.uid("fit")
        for size in sizes:
            h = self.rich(x, y, width, text, size, color, tags=tuple(tags) + (tmp,))
            if h <= maxh or size == sizes[-1]:
                return h
            self.cv.delete(tmp)

    def pointer_in(self, tag):
        try:
            x = self.cv.winfo_pointerx() - self.cv.winfo_rootx()
            y = self.cv.winfo_pointery() - self.cv.winfo_rooty()
        except tk.TclError:
            return False
        items = [i for i in self.cv.find_overlapping(x, y, x, y) if not ({"pt", "bg", "conf", "toast"} & set(self.cv.gettags(i)))]
        return bool(items) and tag in self.cv.gettags(items[-1])

    def fade(self, item, to, attr="fill", steps=7):
        try:
            cur = self.cv.itemcget(item, attr)
        except tk.TclError:
            return
        key = (item, attr)
        if key in self._fade_jobs:
            try:
                self.root.after_cancel(self._fade_jobs.pop(key))
            except Exception:
                pass
        if not cur or not cur.startswith("#") or len(cur) != 7:
            try:
                self.cv.itemconfig(item, **{attr: to})
            except tk.TclError:
                pass
            return

        def step(i):
            if not self.cv.type(item):
                self._fade_jobs.pop(key, None)
                return
            self.cv.itemconfig(item, **{attr: mix(cur, to, ease(i / steps))})
            if i < steps:
                self._fade_jobs[key] = self.root.after(16, step, i + 1)
            else:
                self._fade_jobs.pop(key, None)
        step(1)

    # ------------------------------------------------------------ fons i efectes
    def draw_bg(self):
        n = 48
        for i in range(n):
            self.cv.create_rectangle(0, i * H / n, W, (i + 1) * H / n + 1, fill=mix("#090e1d", "#141a3c", i / (n - 1)), outline="", tags=("bg",))
        for (x, y, r, c, a) in [(1010, -40, 300, ACC, .16), (90, 790, 330, ACC2, .10)]:
            for k in range(10):
                rr = r * (1 - k / 10)
                self.cv.create_oval(x - rr, y - rr, x + rr, y + rr, fill=mix("#0d1330", c, a * (k + 1) / 10 * 1.4), outline="", tags=("bg",))

    def init_particles(self):
        self.pts = []
        for _ in range(42):
            x, y, r = random.uniform(0, W), random.uniform(0, H), random.uniform(1, 2.6)
            c = mix(BG, random.choice([ACC, ACC2, "#ffffff"]), random.uniform(.25, .6))
            it = self.cv.create_oval(x - r, y - r, x + r, y + r, fill=c, outline="", tags=("pt",))
            self.pts.append([it, random.uniform(-.12, .12), random.uniform(-.5, -.12)])
        self.cv.tag_raise("pt", "bg")
        self._tick_pts()

    def _tick_pts(self):
        for it, vx, vy in self.pts:
            self.cv.move(it, vx, vy)
            x1, y1, x2, y2 = self.cv.coords(it)
            if y2 < 0:
                self.cv.move(it, 0, H + 8)
            if x2 < 0:
                self.cv.move(it, W + 6, 0)
            elif x1 > W:
                self.cv.move(it, -W - 6, 0)
        self.root.after(45, self._tick_pts)

    def slide_in(self, tag="scr", dx=40, frames=11):
        self.cv.move(tag, dx, 0)
        st = {"off": dx}

        def step(i):
            target = dx * (1 - ease(i / frames))
            self.cv.move(tag, target - st["off"], 0)
            st["off"] = target
            if i < frames:
                self.later(16, lambda: step(i + 1))
        step(1)

    def toast(self, msg, color=OK, icon="✓"):
        self._toast_tok += 1
        tok = self._toast_tok
        self.cv.delete("toast")
        f = self.fobj(16, True)
        w = f.measure(msg) + 90
        x1 = (W - w) / 2
        g = ("toast",)
        round_rect(self.cv, x1, -62, x1 + w, -10, 26, fill=CARD2, outline=color, width=2, tags=g)
        self.cv.create_oval(x1 + 14, -50, x1 + 42, -22, fill=color, outline="", tags=g)
        self.cv.create_text(x1 + 28, -36, text=icon, fill="#0b1020", font=self.fobj(15, True), tags=g)
        self.cv.create_text(x1 + 54, -36, text=msg, fill=TEXT, font=f, anchor="w", tags=g)
        self.cv.tag_raise("toast")
        st = {"off": 0}

        def move_to(target, frames, then=None, i=1):
            if tok != self._toast_tok:
                return
            v = st["off"] + (target - st["off"]) * ease(i / frames) if i < frames else target
            self.cv.move("toast", 0, v - st["off"])
            st["off"] = v
            if i < frames:
                self.root.after(16, move_to, target, frames, then, i + 1)
            elif then:
                then()
        move_to(80, 12, lambda: self.root.after(1900, lambda: move_to(0, 12, lambda: tok == self._toast_tok and self.cv.delete("toast"))))

    def confetti(self, n=110, x=None, y=None, spread=7.5):
        cols = [ACC, ACC2, OK, WARN, BAD, ORANGE, "#ffffff"]
        parts = []
        for _ in range(n):
            px = x if x is not None else random.uniform(W * .2, W * .8)
            py = y if y is not None else H * .3
            s = random.uniform(4, 9)
            it = self.cv.create_rectangle(px, py, px + s, py + s * .6, fill=random.choice(cols), outline="", tags=("conf",))
            parts.append([it, random.uniform(-spread, spread), random.uniform(-12, -3)])
        self.cv.tag_raise("conf")

        def step(k):
            for p in parts:
                self.cv.move(p[0], p[1], p[2])
                p[1] *= .985
                p[2] += .42
            if k < 75:
                self.root.after(28, step, k + 1)
            else:
                for p in parts:
                    self.cv.delete(p[0])
        step(0)

    # ------------------------------------------------------------ botons
    def button(self, x, y, w, h, text, cmd, color=ACC, fg="#ffffff", size=17, tags=("scr",), r=None, bold=True):
        t = self.uid("b")
        tg = tuple(tags) + (t,)
        rect = self.R(x, y, x + w, y + h, r if r is not None else h / 2, fill=color, tags=tg)
        txt = self.T(x + w / 2, y + h / 2, text, size, fg, bold, tags=tg)
        self.btns[t] = {"rect": rect, "txt": txt, "color": color, "hover": mix(color, "#ffffff", .17), "cmd": cmd,
                        "enabled": True, "fg": fg, "lift": False, "busy": False}
        self.cv.tag_bind(t, "<Enter>", lambda e: self._hover(t, True))
        self.cv.tag_bind(t, "<Leave>", lambda e: self.root.after(25, lambda: self._unhover(t)))
        self.cv.tag_bind(t, "<Button-1>", lambda e: self._press(t))
        return t

    def _hover(self, t, on):
        st = self.btns.get(t)
        if not st or not self.cv.find_withtag(t) or not st["enabled"]:
            return
        self.cv.config(cursor="hand2" if on else "")
        if on != st["lift"]:
            self.cv.move(t, 0, -2 if on else 2)
            st["lift"] = on
        self.fade(st["rect"], st["hover"] if on else st["color"])

    def _unhover(self, t):
        if self.btns.get(t) and not self.pointer_in(t):
            self._hover(t, False)

    def _press(self, t):
        st = self.btns.get(t)
        if not st or not st["enabled"] or st["busy"]:
            return
        st["busy"] = True
        self.cv.move(t, 0, 2)

        def up():
            if self.cv.find_withtag(t):
                self.cv.move(t, 0, -2)
            st["busy"] = False
            st["cmd"]()
        self.root.after(80, up)

    def set_enabled(self, t, en):
        st = self.btns.get(t)
        if not st:
            return
        st["enabled"] = en
        self.cv.itemconfig(st["rect"], fill=st["color"] if en else mix(st["color"], BG, .65))
        self.cv.itemconfig(st["txt"], fill=st["fg"] if en else mix(st["fg"], BG, .5))

    def clickable(self, tag, rect, fn, base, hov, ol, olh, lift=4):
        st = {"lift": False}

        def enter(e):
            self.cv.config(cursor="hand2")
            if not st["lift"]:
                self.cv.move(tag, 0, -lift)
                st["lift"] = True
            self.fade(rect, hov)
            self.fade(rect, olh, "outline")

        def leave():
            if self.pointer_in(tag) or not self.cv.find_withtag(tag):
                return
            self.cv.config(cursor="")
            if st["lift"]:
                self.cv.move(tag, 0, lift)
                st["lift"] = False
            self.fade(rect, base)
            self.fade(rect, ol, "outline")
        self.cv.tag_bind(tag, "<Enter>", enter)
        self.cv.tag_bind(tag, "<Leave>", lambda e: self.root.after(25, leave))
        self.cv.tag_bind(tag, "<Button-1>", lambda e: fn())

    # ------------------------------------------------------------ pantalles: comú
    def clear(self):
        for a in list(self.after_ids):
            try:
                self.root.after_cancel(a)
            except Exception:
                pass
        self.after_ids.clear()
        self.cv.delete("scr")
        self._toast_tok += 1
        self.cv.delete("toast")
        for w in self.widgets:
            try:
                w.destroy()
            except Exception:
                pass
        self.widgets = []
        self.keymap = {}
        self.btns = {}
        self.close_hook = None
        self.hist_cv = None
        self.cv.config(cursor="")

    def on_key(self, e):
        if isinstance(e.widget, tk.Entry):
            return
        fn = self.keymap.get(e.keysym.lower())
        if fn:
            fn()

    def on_wheel(self, e, direction=None):
        if self.hist_cv is None:
            return
        try:
            d = direction if direction is not None else (-1 if e.delta > 0 else 1)
            self.hist_cv.yview_scroll(d, "units")
        except tk.TclError:
            pass

    def on_close(self):
        if self.close_hook:
            try:
                self.close_hook()
            except Exception:
                pass
        self.root.destroy()

    def topbar(self, title, color, back=None, level=True, back_label="←  Menú"):
        if back:
            self.button(40, 26, 130, 44, back_label, back, color=CARD2, fg=TEXT, size=15)
        self.T(W / 2, 48, title, 24, TEXT, True)
        if level:
            nv = self.store.nivell
            lab = f"{nv} · {BANKS[nv]['titol']}"
            wp = self.fobj(14, True).measure(lab) + 32
            self.R(W - 40 - wp, 30, W - 40, 66, 18, fill=CARD2, outline=color, width=2)
            self.T(W - 40 - wp / 2, 48, lab, 14, color, True)

    def level_selector(self, xr, y, on_change):
        labs = [(nv, f"{nv} · {BANKS[nv]['titol']}") for nv in BANKS]
        f = self.fobj(14, True)
        ws = [f.measure(l) + 36 for _, l in labs]
        x0 = xr - sum(ws) - 8
        self.R(x0, y - 23, xr, y + 23, 23, fill=CARD2)
        x = x0 + 4
        for (nv, lab), w in zip(labs, ws):
            act = nv == self.store.nivell

            def pick(nv=nv):
                if nv != self.store.nivell:
                    self.store.d["nivell"] = nv
                    self.store.save()
                    on_change()
            self.button(x, y - 19, w, 38, lab, pick, color=ACC if act else CARD2, fg="#ffffff" if act else MUTED, size=14)
            x += w

    def icon(self, kind, cx, cy, col, tags):
        if kind == "bolt":
            pts = [cx + 6, cy - 27, cx - 13, cy + 3, cx - 1, cy + 3, cx - 6, cy + 27, cx + 13, cy - 5, cx + 1, cy - 5]
            self.cv.create_polygon(pts, fill=col, outline="", tags=tags)
        elif kind == "clock":
            self.cv.create_oval(cx - 24, cy - 24, cx + 24, cy + 24, outline=col, width=5, tags=tags)
            self.cv.create_line(cx, cy, cx, cy - 14, fill=col, width=5, capstyle="round", tags=tags)
            self.cv.create_line(cx, cy, cx + 11, cy + 6, fill=col, width=5, capstyle="round", tags=tags)
        elif kind == "bars":
            for i, hh in enumerate([18, 32, 46]):
                x = cx - 22 + i * 16
                self.cv.create_rectangle(x, cy + 23 - hh, x + 11, cy + 23, fill=col, outline="", tags=tags)

    def countup(self, item, target, fmt_fn=str, frames=30):
        def step(i):
            if not self.cv.type(item):
                return
            self.cv.itemconfig(item, text=fmt_fn(round(target * ease(i / frames))))
            if i < frames:
                self.later(16, lambda: step(i + 1))
        step(0)

    def dialog(self, title, msg, buttons, color=ACC):
        self.cv.delete("dlg")
        g = ("scr", "dlg")
        self.cv.create_rectangle(0, 0, W, H, fill="#000000", stipple="gray50", outline="", tags=g)
        w, h = 580, 250
        x1, y1 = (W - w) / 2, (H - h) / 2
        self.R(x1, y1, x1 + w, y1 + h, 24, fill=CARD, outline=color, width=2, tags=g)
        self.T(W / 2, y1 + 46, title, 22, TEXT, True, tags=g)
        self.T(W / 2, y1 + 106, msg, 16, MUTED, tags=g, width=w - 70, justify="center")
        bw, gap = 168, 14
        bx = (W - (len(buttons) * bw + (len(buttons) - 1) * gap)) / 2
        prev = self.keymap

        def close():
            self.cv.delete("dlg")
            self.keymap = prev
        for i, (lab, col, fn) in enumerate(buttons):
            def act(fn=fn):
                close()
                if fn:
                    fn()
            self.button(bx + i * (bw + gap), y1 + h - 78, bw, 50, lab, act, color=col, fg=DARK_FG.get(col, TEXT), size=15, tags=g)
        self.keymap = {"escape": close}

    # ------------------------------------------------------------ BENVINGUDA
    def welcome(self):
        self.clear()
        self.T(W / 2, 128, "Simulador de Checklist", 42, TEXT, True)
        self.T(W / 2, 176, "Linux  ·  Sistemes operatius  ·  SMX", 18, ACC2, True)
        self.R(310, 225, 810, 535, 28, fill=CARD, outline=LINE, width=2)
        self.T(W / 2, 270, "Com et dius?", 24, TEXT, True)
        self.T(W / 2, 308, "Escriu el teu nom i cognoms. Les teves sessions es desaran amb aquest nom.", 14, MUTED, width=420, justify="center")
        e = tk.Entry(self.root, font=self.fobj(20), bg=CARD2, fg=TEXT, insertbackground=TEXT, relief="flat",
                     highlightthickness=2, highlightbackground=LINE, highlightcolor=ACC, justify="center")
        self.widgets.append(e)
        ent = self.cv.create_window(W / 2, 382, window=e, width=400, height=52, tags=("scr", "ent"))

        def go():
            n = re.sub(r"\s+", " ", e.get()).strip()
            if not n:
                self.toast("Escriu el teu nom per començar", BAD, "!")
                self.shake(ent)
                return
            self.store.set_nom(n)
            self.menu()
        self.button(410, 440, 300, 58, "Comença  ▶", go, color=ACC, size=19)
        e.bind("<Return>", lambda ev: go())
        noms = [n for n in self.store.noms()][-8:]
        if noms:
            self.T(W / 2, 575, "O continua com:", 14, MUTED)
            f = self.fobj(14, True)
            ws = [min(220, f.measure(n) + 34) for n in noms]
            x = (W - (sum(ws) + 10 * (len(ws) - 1))) / 2
            for n, w in zip(noms, ws):
                def pick(n=n):
                    self.store.set_nom(n)
                    self.menu()
                lab = n if f.measure(n) + 34 <= 220 else n[:18] + "…"
                self.button(x, 598, w, 40, lab, pick, color=CARD2, fg=TEXT, size=14)
                x += w + 10
        self.slide_in()
        e.focus_set()

    def shake(self, item):
        seq = [10, -20, 16, -12, 8, -2]

        def step(i):
            if i < len(seq):
                self.cv.move(item, seq[i], 0)
                self.later(30, lambda: step(i + 1))
        step(0)

    # ------------------------------------------------------------ MENÚ
    def menu(self):
        self.clear()
        nv = self.store.nivell
        self.R(60, 38, 126, 104, 20, fill=ACC)
        self.T(93, 71, ">_", 26, "#ffffff", True, mono=True)
        self.T(146, 58, "Simulador de Checklist", 30, TEXT, True, anchor="w")
        self.T(148, 92, f"Hola, {self.store.nom}!  Prepara't per a l'avaluació pràctica.", 16, MUTED, anchor="w")
        self.level_selector(W - 60, 70, self.menu)
        specs = [("Mode Blitz", "Tasques aleatòries una darrere l'altra, amb cronòmetre. Guanya velocitat i fes ratxes!", ORANGE, "bolt", self.blitz),
                 ("Mode Simulador", "5 tasques com a l'avaluació real i 15 minuts de compte enrere. Al final, la nota.", ACC2, "clock", self.sim_intro),
                 ("Informe", "Els teus intents, les tasques resoltes i l'evolució de les notes de totes les sessions.", OK, "bars", self.informe)]
        for i, (title, desc, col, ic, fn) in enumerate(specs):
            x, y, w, h = 60 + i * 340, 140, 320, 320
            tag = f"card{i}"
            tg = ("scr", tag)
            rect = self.R(x, y, x + w, y + h, 26, fill=CARD, outline=LINE, width=2, tags=tg)
            self.R(x + 30, y + 30, x + 104, y + 104, 22, fill=mix(CARD, col, .2), tags=tg)
            self.icon(ic, x + 67, y + 67, col, tg)
            self.T(x + 30, y + 142, title, 24, TEXT, True, anchor="w", tags=tg)
            self.T(x + 30, y + 168, desc, 15, MUTED, anchor="nw", width=w - 60, tags=tg)
            self.T(x + 30, y + h - 38, "Entra  →", 16, col, True, anchor="w", tags=tg)
            self.T(x + w - 30, y + h - 38, f"tecla {i + 1}", 12, mix(MUTED, CARD, .4), anchor="e", tags=tg)
            self.clickable(tag, rect, fn, CARD, mix(CARD, col, .1), LINE, col)
        st = self.store.stats(nv)
        n = len(self.tasks[nv])
        best = max(st["notes"]) if st["notes"] else None
        tiles = [("Tasques resoltes", st["resoltes"], lambda v: f"{v}/{n}", OK),
                 ("Millor nota (simulador)", best, str, ACC2),
                 ("Simulacres fets", st["sim"], str, ACC),
                 ("Sessions Blitz", st["blitz"], str, ORANGE)]
        for i, (lab, val, fn, col) in enumerate(tiles):
            x = 60 + i * 255
            self.R(x, 482, x + 235, 566, 20, fill=CARD, outline=LINE)
            self.R(x, 500, x + 6, 548, 3, fill=col)
            self.T(x + 24, 506, lab, 13, MUTED, anchor="w")
            it = self.T(x + 24, 538, "–" if val is None else fn(0), 26, TEXT, True, anchor="w")
            if val is not None:
                self.countup(it, val, fn)
        self.button(60, 610, 200, 44, "Canvia d'alumne", self.welcome, color=CARD2, fg=TEXT, size=14)
        self.button(W - 180, 610, 120, 44, "Surt", self.on_close, color=CARD2, fg=TEXT, size=14)
        self.T(W / 2, 632, "Fes les tasques a la teva màquina virtual Ubuntu.", 13, MUTED)
        self.keymap = {"1": self.blitz, "2": self.sim_intro, "3": self.informe}
        self.slide_in()

    # ------------------------------------------------------------ MODE BLITZ
    def blitz(self):
        self.clear()
        self.bz = {"nv": self.store.nivell, "deck": [], "done": [], "cur": None, "t0": None, "pistes": 0,
                   "streak": 0, "inici": time.time(), "lock": False, "saved": False}
        self.topbar("Mode Blitz", ORANGE, back=self.blitz_exit)
        self.bz_stats = {}
        for i, (k, lab, val, col) in enumerate([("fetes", "Fetes", "0", OK), ("salt", "Saltades", "0", MUTED),
                                                 ("mitja", "Temps mitjà", "--:--", ACC2), ("ratxa", "Ratxa", "0", WARN)]):
            x = 60 + i * 255
            self.R(x, 90, x + 235, 138, 24, fill=CARD, outline=LINE)
            self.T(x + 22, 114, lab, 14, MUTED, anchor="w")
            self.bz_stats[k] = self.T(x + 213, 114, val, 19, col, True, anchor="e")
        self.bz_card = self.R(60, 156, 1060, 540, 28, fill=CARD, outline=LINE, width=2)
        self.cv.create_line(770, 186, 770, 510, fill=LINE, tags="scr")
        cx, cy = 915, 330
        self.cv.create_oval(cx - 112, cy - 112, cx + 112, cy + 112, fill=mix(CARD, BG, .4), outline="", tags="scr")
        self.cv.create_oval(cx - 96, cy - 96, cx + 96, cy + 96, outline=LINE, width=12, tags="scr")
        self.bz_arc = self.cv.create_arc(cx - 96, cy - 96, cx + 96, cy + 96, start=90, extent=-.1, style="arc", outline=OK, width=12, tags="scr")
        self.bz_time = self.T(cx, cy - 6, "00:00.0", 32, TEXT, True, mono=True)
        self.T(cx, cy + 30, "temps", 14, MUTED)
        self.bz_best = self.T(cx, cy + 145, "", 14, MUTED, width=280, justify="center")
        self.button(250, 562, 240, 62, "✓  Tasca feta", self.blitz_done, color=OK, fg=DARK_FG[OK], size=19)
        self.button(510, 562, 180, 62, "?  Pista", self.blitz_hint, color=WARN, fg=DARK_FG[WARN], size=19)
        self.button(710, 562, 160, 62, "»  Salta", self.blitz_skip, color=CARD2, fg=TEXT, size=19)
        self.T(W / 2, 655, "Retorn = tasca feta   ·   P = pista   ·   S = salta   ·   Esc = tornar al menú", 13, MUTED)
        self.keymap = {"return": self.blitz_done, "p": self.blitz_hint, "s": self.blitz_skip, "escape": self.blitz_exit}
        self.close_hook = self.blitz_save
        self.slide_in()
        self.blitz_next(first=True)
        self.blitz_tick()

    def best_time(self, nv, tid):
        best = None
        for s in self.store.sessions(nv):
            if s["tipus"] == "blitz":
                for t in s["tasques"]:
                    if t["id"] == tid and t["feta"] and t.get("temps"):
                        best = t["temps"] if best is None else min(best, t["temps"])
        if self.bz and self.bz["nv"] == nv and not self.bz["saved"]:
            for t in self.bz["done"]:
                if t["id"] == tid and t["feta"]:
                    best = t["temps"] if best is None else min(best, t["temps"])
        return best

    def blitz_next(self, first=False):
        b = self.bz
        if not b["deck"]:
            ids = list(self.tasks[b["nv"]].keys())
            random.shuffle(ids)
            if b["cur"] and ids[0] == b["cur"] and len(ids) > 1:
                ids.append(ids.pop(0))
            b["deck"] = ids
        tid = b["deck"].pop(0)
        b.update(cur=tid, pistes=0, t0=time.monotonic(), lock=False)
        self.cv.delete("task")
        t = self.tasks[b["nv"]][tid]
        col = BLOC_COL[t["bloc"]]
        tg = ("scr", "task")
        lab = f"{tid}   ·   {t['nom_bloc']}"
        wp = self.fobj(14, True).measure(lab) + 40
        self.R(100, 190, 100 + wp, 228, 19, fill=col, tags=tg)
        self.T(120, 209, lab, 14, "#ffffff", True, anchor="w", tags=tg)
        h = self.fit_rich(100, 250, 630, 130, t["enunciat"], [24, 21, 19], tags=tg)
        self.bz_hint_y = 250 + h + 16
        best = self.best_time(b["nv"], tid)
        self.cv.itemconfig(self.bz_best, text=f"Millor temps: {fmt_d(best)}" if best else "Primera vegada amb aquesta tasca")
        self.fade(self.bz_card, LINE, "outline")
        if not first:
            self.slide_in("task", 34, 9)

    def blitz_tick(self):
        b = self.bz
        if b["t0"] is not None and not b["lock"]:
            s = time.monotonic() - b["t0"]
            self.cv.itemconfig(self.bz_time, text=fmt_d(s))
            col = OK if s < 90 else (WARN if s < 180 else BAD)
            self.cv.itemconfig(self.bz_arc, extent=-max(.1, 359.9 * ((s % 60) / 60)), outline=col)
        self.later(100, self.blitz_tick)

    def blitz_hint(self):
        b = self.bz
        if b["lock"]:
            return
        if b["pistes"] >= 2:
            self.toast("Ja has vist totes les pistes d'aquesta tasca", WARN, "!")
            return
        b["pistes"] += 1
        t = self.tasks[b["nv"]][b["cur"]]
        self.cv.delete("hint")
        tg = ("scr", "task", "hint")
        y = self.bz_hint_y
        cy = y + 16
        self.T(124, cy, "PISTA", 12, WARN, True, anchor="nw", tags=tg)
        cy += 22
        cy += self.rich(124, cy, 590, t["pista"], 16, TEXT, tags=tg) + 4
        if b["pistes"] == 2:
            self.T(124, cy, "COM ES COMPROVA", 12, ACC2, True, anchor="nw", tags=tg)
            cy += 22
            it = self.T(124, cy, t["comprova"], 15, TEXT, mono=True, anchor="nw", width=590, tags=tg)
            cy = self.cv.bbox(it)[3] + 6
        rect = self.R(100, y, 740, cy + 10, 16, fill=CARD2, outline=WARN if b["pistes"] == 1 else ACC2, width=2, tags=tg)
        self.cv.tag_lower(rect, "hint")
        if b["pistes"] == 1:
            self.slide_in("hint", 0, 1)
        self.toast("Pista 1 de 2" if b["pistes"] == 1 else "Pista 2 de 2: ja saps com comprovar-ho", WARN, "?")

    def blitz_done(self):
        b = self.bz
        if b["lock"] or b["cur"] is None:
            return
        b["lock"] = True
        s = round(time.monotonic() - b["t0"], 1)
        prev = self.best_time(b["nv"], b["cur"])
        b["done"].append({"id": b["cur"], "feta": True, "temps": s, "pistes": b["pistes"]})
        b["streak"] += 1
        self.blitz_update()
        self.cv.itemconfig(self.bz_card, outline=OK)
        if prev is not None and s < prev:
            self.toast(f"Nou rècord personal!  {fmt_d(s)}", WARN, "★")
            self.confetti(60, 915, 330, 6)
        else:
            self.toast(f"Tasca feta en {fmt_d(s)}", OK, "✓")
        if b["streak"] in (5, 10, 15, 20, 30):
            self.later(250, lambda: (self.confetti(), self.toast(f"Ratxa de {b['streak']} tasques!", ORANGE, "⚡")))
        self.later(600, self.blitz_next)

    def blitz_skip(self):
        b = self.bz
        if b["lock"] or b["cur"] is None:
            return
        b["lock"] = True
        b["done"].append({"id": b["cur"], "feta": False, "temps": round(time.monotonic() - b["t0"], 1), "pistes": b["pistes"]})
        b["streak"] = 0
        self.blitz_update()
        self.cv.itemconfig(self.bz_card, outline=MUTED)
        self.toast("Tasca saltada. Torna-hi més endavant!", MUTED, "»")
        self.later(450, self.blitz_next)

    def blitz_update(self):
        d = self.bz["done"]
        fetes = [x for x in d if x["feta"]]
        self.cv.itemconfig(self.bz_stats["fetes"], text=str(len(fetes)))
        self.cv.itemconfig(self.bz_stats["salt"], text=str(len(d) - len(fetes)))
        self.cv.itemconfig(self.bz_stats["mitja"], text=fmt(sum(x["temps"] for x in fetes) / len(fetes)) if fetes else "--:--")
        self.cv.itemconfig(self.bz_stats["ratxa"], text=str(self.bz["streak"]))

    def blitz_save(self):
        b = self.bz
        if not b or not b["done"] or b["saved"]:
            return
        b["saved"] = True
        self.store.add({"tipus": "blitz", "nivell": b["nv"], "data": ara(), "durada": round(time.time() - b["inici"]), "tasques": b["done"]})

    def blitz_exit(self):
        self.blitz_save()
        if self.bz["done"]:
            self.blitz_summary()
        else:
            self.menu()

    def blitz_summary(self):
        b = self.bz
        self.clear()
        self.topbar("Sessió Blitz acabada", ORANGE, back=self.menu)
        done = [d for d in b["done"] if d["feta"]]
        times = [d["temps"] for d in done]
        tiles = [("Tasques fetes", str(len(done)), OK), ("Saltades", str(len(b["done"]) - len(done)), MUTED),
                 ("Temps mitjà", fmt_d(sum(times) / len(times)) if times else "--", ACC2),
                 ("Millor temps", fmt_d(min(times)) if times else "--", WARN)]
        for i, (lab, val, col) in enumerate(tiles):
            x = 60 + i * 255
            self.R(x, 92, x + 235, 182, 22, fill=CARD, outline=LINE)
            self.T(x + 24, 118, lab, 14, MUTED, anchor="w")
            self.T(x + 24, 154, val, 28, col, True, anchor="w")
        self.R(60, 200, 1060, 600, 26, fill=CARD, outline=LINE)
        self.T(90, 230, "Tasques d'aquesta sessió", 17, TEXT, True, anchor="w")
        for k, d in enumerate(list(reversed(b["done"]))[:9]):
            y = 266 + k * 36
            t = self.tasks[b["nv"]][d["id"]]
            col = BLOC_COL[t["bloc"]]
            self.R(90, y - 13, 140, y + 13, 13, fill=col)
            self.T(115, y, d["id"], 13, "#ffffff", True)
            txt = strip_tags(t["enunciat"])
            self.T(156, y, txt if len(txt) < 92 else txt[:90] + "…", 14, TEXT, anchor="w")
            self.T(905, y, fmt_d(d["temps"]), 14, MUTED, mono=True, anchor="e")
            if d["pistes"]:
                self.T(960, y, f"{d['pistes']}?", 13, WARN, True)
            self.T(1020, y, "✓" if d["feta"] else "»", 18, OK if d["feta"] else MUTED, True)
        self.button(260, 625, 230, 54, "↻  Una altra sessió", self.blitz, color=ORANGE, fg=DARK_FG[ORANGE], size=16)
        self.button(510, 625, 170, 54, "Informe", self.informe, color=OK, fg=DARK_FG[OK], size=16)
        self.button(700, 625, 160, 54, "←  Menú", self.menu, color=CARD2, fg=TEXT, size=16)
        self.keymap = {"escape": self.menu, "return": self.blitz}
        self.slide_in()
        if len(done) >= 5:
            self.later(300, self.confetti)

    # ------------------------------------------------------------ MODE SIMULADOR
    def sim_intro(self):
        self.clear()
        self.topbar("Mode Simulador", ACC2, back=self.menu)
        self.R(200, 88, 920, 700, 30, fill=CARD, outline=LINE, width=2)
        self.R(523, 108, 597, 190, 22, fill=mix(CARD, ACC2, .2))
        self.icon("clock", 560, 145, ACC2, ("scr",))
        self.T(W / 2, 212, "Simulacre d'avaluació", 28, TEXT, True)
        regles = ["Tindràs <b>5 tasques</b>, una de cada bloc, com a l'avaluació real.",
                  "Tens <b>15 minuts</b>. El compte enrere comença quan premis «Comença».",
                  "Fes les tasques a la teva <b>màquina virtual</b> i marca tu mateix/a les que hagis fet.",
                  "Pots demanar <b>pistes</b>: no resten nota, però queden a l'informe.",
                  "Quan s'acabi el temps (o quan lliuris), veuràs la nota."]
        y = 248
        for r in regles:
            self.cv.create_oval(262, y + 7, 272, y + 17, fill=ACC2, outline="", tags="scr")
            y += self.rich(290, y, 570, r, 17, TEXT) + 8
        self.T(W / 2, y + 22, "Nota segons les tasques fetes", 14, MUTED)
        x0 = W / 2 - (6 * 82 + 5 * 10) / 2
        for i, k in enumerate([5, 4, 3, 2, 1, 0]):
            x = x0 + i * 92
            col = OK if NOTES[k] >= 8 else ACC2 if NOTES[k] >= 5 else WARN if NOTES[k] >= 3 else BAD
            self.R(x, y + 42, x + 82, y + 112, 16, fill=CARD2, outline=col)
            self.T(x + 41, y + 62, f"{k} tasques", 12, MUTED)
            self.T(x + 41, y + 92, str(NOTES[k]), 24, col, True)
        self.button(W / 2 - 140, y + 136, 280, 56, "Comença  ▶", self.sim_countdown, color=ACC2, fg=DARK_FG[ACC2], size=19)
        self.keymap = {"return": self.sim_countdown, "escape": self.menu}
        self.slide_in()

    def sim_countdown(self):
        self.clear()
        seq = ["3", "2", "1", "Som-hi!"]
        ring = self.cv.create_oval(W / 2, H / 2, W / 2, H / 2, outline=ACC2, width=6, tags="scr")
        item = self.T(W / 2, H / 2, "", 150, ACC2, True)

        def show(k):
            if k >= len(seq):
                self.sim_start()
                return
            base = 160 if k < 3 else 96
            col = ACC2 if k < 3 else OK
            frames = 16

            def fr(i):
                t = ease(i / frames)
                self.cv.itemconfig(item, text=seq[k], font=self.F(base * (1.6 - .6 * t), True), fill=mix(BG, col, min(1, i / frames * 2)))
                r = 80 + 170 * t
                self.cv.coords(ring, W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r)
                self.cv.itemconfig(ring, outline=mix(col, BG, t))
                if i < frames:
                    self.later(16, lambda: fr(i + 1))
                else:
                    self.later(600, lambda: show(k + 1))
            fr(0)
        show(0)
        self.keymap = {"escape": self.menu}

    def sim_start(self):
        nv = self.store.nivell
        per = self.store.stats(nv)["per"]
        ids = []
        for codi, nom, tasks in BANKS[nv]["blocs"]:
            cand = [f"{codi}{i + 1}" for i in range(len(tasks))]
            pes = [1 / (1 + per.get(c, {}).get("fetes", 0)) for c in cand]   # les menys practicades surten més
            ids.append(random.choices(cand, weights=pes)[0])
        self.sm = {"nv": nv, "ids": ids, "fet": [False] * 5, "pistes": [0] * 5, "marca": [None] * 5,
                   "t0": time.monotonic(), "fi": False, "rows": [], "warn": set()}
        self.sim_screen()

    def sim_screen(self):
        self.clear()
        s = self.sm
        self.topbar("Mode Simulador", ACC2, back=self.sim_back)
        for i, tid in enumerate(s["ids"]):
            y = 96 + i * 106
            t = self.tasks[s["nv"]][tid]
            col = BLOC_COL[t["bloc"]]
            tg = ("scr", f"row{i}")
            card = self.R(40, y, 800, y + 98, 20, fill=CARD, outline=LINE, width=2, tags=tg)
            self.R(52, y + 16, 58, y + 82, 3, fill=col, tags=tg)
            self.T(102, y + 36, tid, 26, col, True, tags=tg)
            self.T(102, y + 66, t["nom_bloc"].split(" ")[0].rstrip(",:"), 11, MUTED, tags=tg)
            self.fit_rich(150, y + 14, 470, 74, t["enunciat"], [16, 15, 14, 13], tags=tg)
            self.button(640, y + 26, 46, 46, "?", lambda i=i: self.sim_hint(i), color=CARD2, fg=WARN, size=21, r=23, tags=tg)
            ctag = f"chk{i}"
            box = self.R(712, y + 17, 776, y + 81, 16, fill=CARD2, outline=LINE, width=2, tags=tg + (ctag,))
            mark = self.T(744, y + 49, "", 34, "#06240f", True, tags=tg + (ctag,))
            self.T(744, y + 92, "", 1, MUTED, tags=tg)
            self.cv.tag_bind(ctag, "<Button-1>", lambda e, i=i: self.sim_toggle(i))
            self.cv.tag_bind(ctag, "<Enter>", lambda e: self.cv.config(cursor="hand2"))
            self.cv.tag_bind(ctag, "<Leave>", lambda e: self.cv.config(cursor=""))
            s["rows"].append({"card": card, "box": box, "mark": mark})
        self.R(830, 96, 1080, 618, 26, fill=CARD, outline=LINE, width=2)
        cx, cy = 955, 212
        self.cv.create_oval(cx - 104, cy - 104, cx + 104, cy + 104, fill=mix(CARD, BG, .4), outline="", tags="scr")
        self.cv.create_oval(cx - 88, cy - 88, cx + 88, cy + 88, outline=LINE, width=14, tags="scr")
        self.sm_arc = self.cv.create_arc(cx - 88, cy - 88, cx + 88, cy + 88, start=90, extent=-359.9, style="arc", outline=ACC2, width=14, tags="scr")
        self.sm_time = self.T(cx, cy - 4, "15:00", 34, TEXT, True, mono=True)
        self.T(cx, cy + 32, "temps restant", 13, MUTED)
        self.T(cx, 340, "Tasques fetes", 13, MUTED)
        self.sm_dots = [self.cv.create_oval(cx - 62 + k * 26, 358, cx - 46 + k * 26, 374, fill=CARD2, outline=LINE, tags="scr") for k in range(5)]
        self.sm_cnt = self.T(cx, 400, "0 / 5", 22, TEXT, True)
        self.T(cx, 442, "Nota si lliures ara", 13, MUTED)
        self.sm_nota = self.T(cx, 478, "0", 32, BAD, True)
        self.sm_pist = self.T(cx, 518, "Pistes: 0", 13, MUTED)
        self.button(855, 548, 200, 52, "Lliura  ✓", self.sim_deliver, color=ACC2, fg=DARK_FG[ACC2], size=17)
        self.T(W / 2, 660, "Fes les tasques a la VM i marca-les tu mateix/a.   Tecles 1–5 = marcar   ·   Esc = sortir", 13, MUTED)
        self.keymap = {"escape": self.sim_back}
        for k in range(5):
            self.keymap[str(k + 1)] = (lambda k=k: self.sim_toggle(k))
        self.slide_in()
        self.sim_tick()

    def sim_update(self):
        s = self.sm
        n = sum(s["fet"])
        for k, d in enumerate(self.sm_dots):
            self.cv.itemconfig(d, fill=OK if k < n else CARD2, outline=OK if k < n else LINE)
        self.cv.itemconfig(self.sm_cnt, text=f"{n} / 5")
        nota = NOTES[n]
        self.cv.itemconfig(self.sm_nota, text=str(nota), fill=OK if nota >= 8 else ACC2 if nota >= 5 else WARN if nota >= 3 else BAD)
        self.cv.itemconfig(self.sm_pist, text=f"Pistes: {sum(1 for p in s['pistes'] if p)}")

    def sim_toggle(self, i):
        s = self.sm
        if s["fi"] or self.cv.find_withtag("dlg"):
            return
        s["fet"][i] = not s["fet"][i]
        r = s["rows"][i]
        if s["fet"][i]:
            s["marca"][i] = round(time.monotonic() - s["t0"])
            self.fade(r["box"], OK)
            self.fade(r["box"], OK, "outline")
            self.fade(r["card"], OK, "outline")
            sizes = [12, 22, 32, 42, 36]

            def pop(k):
                if k < len(sizes) and self.cv.type(r["mark"]):
                    self.cv.itemconfig(r["mark"], text="✓", font=self.F(sizes[k], True))
                    self.later(25, lambda: pop(k + 1))
            pop(0)
            bb = self.cv.bbox(r["box"])
            self.confetti(22, (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2, 4)
        else:
            s["marca"][i] = None
            self.cv.itemconfig(r["mark"], text="")
            self.fade(r["box"], CARD2)
            self.fade(r["box"], LINE, "outline")
            self.fade(r["card"], LINE, "outline")
        self.sim_update()

    def sim_tick(self):
        s = self.sm
        if s["fi"]:
            return
        el = time.monotonic() - s["t0"]
        rem = SIM_SEGONS - el
        if rem <= 0:
            self.sim_finish(timeout=True)
            return
        col = ACC2 if rem > 300 else (WARN if rem > 60 else BAD)
        wdt = 14 if rem > 60 else 14 + 4 * abs(math.sin(el * 4))
        self.cv.itemconfig(self.sm_arc, extent=-max(.1, 359.9 * rem / SIM_SEGONS), outline=col, width=wdt)
        self.cv.itemconfig(self.sm_time, text=fmt(math.ceil(rem)), fill=TEXT if rem > 60 else BAD)
        for lim, msg, c in [(300, "Queden 5 minuts", WARN), (60, "Queda 1 minut!", BAD)]:
            if rem <= lim and lim not in s["warn"]:
                s["warn"].add(lim)
                self.toast(msg, c, "!")
        self.later(200, self.sim_tick)

    def sim_hint(self, i):
        s = self.sm
        if s["fi"]:
            return
        if s["pistes"][i] == 0:
            s["pistes"][i] = 1
        self.sim_update()
        self.cv.delete("dlg")
        tid = s["ids"][i]
        t = self.tasks[s["nv"]][tid]
        g = ("scr", "dlg")
        self.cv.create_rectangle(0, 0, W, H, fill="#000000", stipple="gray50", outline="", tags=g)
        x1, x2, y1 = 250, 870, 150
        items_top = self.T(x1 + 34, y1 + 30, f"Pista · {tid}", 20, WARN, True, anchor="nw", tags=g)
        y = y1 + 72
        y += self.rich(x1 + 34, y, x2 - x1 - 68, t["enunciat"], 15, MUTED, tags=g) + 14
        self.cv.create_line(x1 + 34, y, x2 - 34, y, fill=LINE, tags=g)
        y += 16
        y += self.rich(x1 + 34, y, x2 - x1 - 68, t["pista"], 18, TEXT, tags=g) + 12
        if s["pistes"][i] >= 2:
            self.T(x1 + 34, y, "COM ES COMPROVA", 12, ACC2, True, anchor="nw", tags=g)
            it = self.T(x1 + 34, y + 22, t["comprova"], 16, TEXT, mono=True, anchor="nw", width=x2 - x1 - 68, tags=g)
            y = self.cv.bbox(it)[3] + 12
        y += 70
        card = self.R(x1, y1, x2, y, 24, fill=CARD, outline=WARN, width=2, tags=g)
        self.cv.tag_lower(card, items_top)
        prev = {"escape": self.sim_back}
        for k in range(5):
            prev[str(k + 1)] = (lambda k=k: self.sim_toggle(k))

        def close():
            self.cv.delete("dlg")
            self.keymap = prev

        def more():
            s["pistes"][i] = 2
            self.sim_hint(i)
        bx = x2 - 34
        self.button(bx - 130, y - 64, 130, 46, "Tanca", close, color=CARD2, fg=TEXT, size=15, tags=g)
        if s["pistes"][i] < 2:
            self.button(bx - 130 - 14 - 230, y - 64, 230, 46, "Com es comprova?", more, color=ACC2, fg=DARK_FG[ACC2], size=15, tags=g)
        self.keymap = {"escape": close}

    def sim_back(self):
        if self.sm["fi"]:
            return
        self.dialog("Vols sortir del simulador?", "Si lliures ara, es posarà la nota amb les tasques que has marcat. Si surts sense desar, l'intent no comptarà.",
                    [("Lliura", ACC2, self.sim_finish), ("Surt sense desar", BAD, self.menu), ("Continua", CARD2, None)], ACC2)

    def sim_deliver(self):
        s = self.sm
        if s["fi"]:
            return
        rem = SIM_SEGONS - (time.monotonic() - s["t0"])
        self.dialog("Vols lliurar el simulacre?", f"Encara et queden {fmt(rem)}. Has marcat {sum(s['fet'])} de 5 tasques.",
                    [("Lliura", ACC2, self.sim_finish), ("Continua", CARD2, None)], ACC2)

    def sim_finish(self, timeout=False):
        s = self.sm
        if s["fi"]:
            return
        s["fi"] = True
        el = min(SIM_SEGONS, time.monotonic() - s["t0"])
        n = sum(s["fet"])
        ses = {"tipus": "simulador", "nivell": s["nv"], "data": ara(), "durada": round(el), "nota": NOTES[n], "temps_esgotat": timeout,
               "tasques": [{"id": tid, "feta": s["fet"][i], "pistes": s["pistes"][i], "marcada_als": s["marca"][i]} for i, tid in enumerate(s["ids"])]}
        self.store.add(ses)
        s["ses"] = ses
        self.keymap = {}
        if timeout:
            self.cv.delete("dlg")
            g = ("scr", "dlg")
            self.cv.create_rectangle(0, 0, W, H, fill="#000000", stipple="gray50", outline="", tags=g)
            it = self.T(W / 2, H / 2, "Temps esgotat!", 64, BAD, True, tags=g)

            def pulse(i):
                if self.cv.type(it):
                    self.cv.itemconfig(it, font=self.F(64 + 8 * math.sin(i / 3), True))
                    if i < 40:
                        self.later(30, lambda: pulse(i + 1))
            pulse(0)
            self.later(1700, self.sim_results)
        else:
            self.sim_results()

    def sim_results(self):
        s = self.sm
        ses = s["ses"]
        self.clear()
        self.topbar("Resultat del simulacre", ACC2, back=self.menu)
        nota = ses["nota"]
        n = sum(1 for t in ses["tasques"] if t["feta"])
        col = OK if nota >= 8 else ACC2 if nota >= 5 else WARN if nota >= 3 else BAD
        self.R(60, 92, 520, 606, 28, fill=CARD, outline=LINE, width=2)
        cx, cy = 290, 290
        self.cv.create_oval(cx - 140, cy - 140, cx + 140, cy + 140, fill=mix(CARD, col, .08), outline="", tags="scr")
        self.cv.create_oval(cx - 120, cy - 120, cx + 120, cy + 120, outline=LINE, width=18, tags="scr")
        arc = self.cv.create_arc(cx - 120, cy - 120, cx + 120, cy + 120, start=90, extent=-.1, style="arc", outline=col, width=18, tags="scr")
        gt = self.T(cx, cy - 12, "0", 92, col, True)
        self.T(cx, cy + 58, "nota sobre 10", 15, MUTED)
        msgs = {10: ("Perfecte!", "Has fet les 5 tasques. Estàs preparat/da per a l'avaluació."),
                8: ("Molt bé!", "Només t'ha faltat una tasca. Practica-la al mode Blitz."),
                6: ("Aprovat", "Vas bé, però repassa les tasques que t'han faltat."),
                3: ("Cal practicar més", "Fes sessions de Blitz per guanyar seguretat i velocitat."),
                1: ("Encara no", "Torna a la guia i practica cada bloc amb el mode Blitz."),
                0: ("Encara no", "Torna a la guia i practica cada bloc amb el mode Blitz.")}
        m1, m2 = msgs[nota]
        t1 = self.T(cx, 478, m1, 24, TEXT, True)
        t2 = self.T(cx, 516, m2, 15, MUTED, width=380, justify="center")
        self.T(cx, 572, f"{n} de 5 tasques   ·   temps {fmt(ses['durada'])}" + ("   ·   temps esgotat" if ses["temps_esgotat"] else ""), 13, MUTED)
        for it in (t1, t2):
            self.cv.itemconfig(it, fill=CARD)
        self.R(540, 92, 1060, 606, 28, fill=CARD, outline=LINE, width=2)
        self.T(570, 124, "Les teves tasques", 18, TEXT, True, anchor="w")
        for k, tk_ in enumerate(ses["tasques"]):
            y = 156 + k * 88
            t = self.tasks[ses["nivell"]][tk_["id"]]
            ok = tk_["feta"]
            self.R(566, y, 1036, y + 78, 18, fill=mix(CARD, OK if ok else BAD, .1), outline=mix(CARD, OK if ok else BAD, .5))
            self.cv.create_oval(580, y + 23, 612, y + 55, fill=OK if ok else BAD, outline="", tags="scr")
            self.T(596, y + 39, "✓" if ok else "✗", 17, "#ffffff", True)
            self.T(628, y + 22, tk_["id"], 15, BLOC_COL[t["bloc"]], True, anchor="w")
            txt = strip_tags(t["enunciat"])
            self.T(628, y + 38, txt if len(txt) < 100 else txt[:98] + "…", 13, TEXT, anchor="nw", width=392)
            if tk_["pistes"]:
                self.R(976, y + 10, 1026, y + 34, 12, fill=mix(CARD, WARN, .25))
                self.T(1001, y + 22, f"{tk_['pistes']} ?", 12, WARN, True)
        self.button(250, 628, 210, 54, "↻  Torna-hi", self.sim_intro, color=ACC2, fg=DARK_FG[ACC2], size=16)
        self.button(480, 628, 170, 54, "Informe", self.informe, color=OK, fg=DARK_FG[OK], size=16)
        self.button(670, 628, 170, 54, "←  Menú", self.menu, color=CARD2, fg=TEXT, size=16)
        self.keymap = {"escape": self.menu, "return": self.sim_intro}
        self.slide_in()

        def anim(i, frames=48):
            t = ease(i / frames)
            self.cv.itemconfig(gt, text=str(round(nota * t)))
            self.cv.itemconfig(arc, extent=-max(.1, 359.9 * nota / 10 * t))
            if i < frames:
                self.later(16, lambda: anim(i + 1))
            else:
                self.fade(t1, TEXT)
                self.fade(t2, MUTED)
                if nota >= 8:
                    self.confetti(140 if nota == 10 else 90)
                    if nota == 10:
                        self.later(500, lambda: self.confetti(100))
        self.later(250, lambda: anim(0))

    # ------------------------------------------------------------ INFORME
    def informe(self):
        self.clear()
        nv = self.store.nivell
        self.topbar(f"Informe · {self.store.nom}", OK, back=self.menu, level=False)
        self.cv.itemconfig(self.cv.find_withtag("scr")[-1], anchor="w")
        self.cv.coords(self.cv.find_withtag("scr")[-1], 196, 48)
        self.level_selector(W - 40, 48, self.informe)
        st = self.store.stats(nv)
        n = len(self.tasks[nv])
        notes = st["notes"]
        tiles = [("Tasques resoltes", f"{st['resoltes']}/{n}", f"{round(100 * st['resoltes'] / n)} % del banc", OK),
                 ("Resoltes sense pista", str(st["sense_pista"]), "tasques", ACC2),
                 ("Simulacres", str(st["sim"]), f"millor nota: {max(notes)}" if notes else "encara cap", ACC),
                 ("Nota mitjana", f"{sum(notes) / len(notes):.1f}" if notes else "–", "dels simulacres", WARN),
                 ("Sessions Blitz", str(st["blitz"]), f"temps mitjà {fmt(st['temps_mitja'])}" if st["temps_mitja"] else "encara cap", ORANGE)]
        for i, (lab, val, sub, col) in enumerate(tiles):
            x = 60 + i * 203
            self.R(x, 88, x + 188, 178, 20, fill=CARD, outline=LINE)
            self.R(x, 104, x + 6, 162, 3, fill=col)
            self.T(x + 22, 108, lab, 13, MUTED, anchor="w")
            self.T(x + 22, 138, val, 26, TEXT, True, anchor="w")
            self.T(x + 22, 164, sub, 12, col, anchor="w")
        # mapa de tasques
        self.R(60, 192, 604, 472, 24, fill=CARD, outline=LINE)
        self.T(84, 218, "Mapa de tasques", 17, TEXT, True, anchor="w")
        self.T(580, 218, "passa el ratolí per sobre", 12, MUTED, anchor="e")
        per = st["per"]
        for bi, (codi, nom, tasks) in enumerate(BANKS[nv]["blocs"]):
            y = 250 + bi * 40
            self.T(96, y + 14, codi, 17, BLOC_COL[codi], True)
            for j in range(len(tasks)):
                tid = f"{codi}{j + 1}"
                p = per.get(tid)
                if not p:
                    c, tc = CARD2, MUTED
                elif not p["fetes"]:
                    c, tc = mix(CARD2, BAD, .45), TEXT
                elif not p["sense_pista"]:
                    c, tc = WARN, DARK_FG[WARN]
                else:
                    c, tc = OK, DARK_FG[OK]
                x = 120 + j * 39
                ctag = f"cell{tid}"
                self.R(x, y, x + 34, y + 28, 8, fill=c, tags=("scr", ctag))
                self.T(x + 17, y + 14, str(j + 1), 12, tc, True, tags=("scr", ctag))
                self.cv.tag_bind(ctag, "<Enter>", lambda e, tid=tid, x=x, y=y: self.tip(tid, x, y))
                self.cv.tag_bind(ctag, "<Leave>", lambda e: self.cv.delete("tip"))
        lx = 90
        for c, lab in [(CARD2, "Sense fer"), (mix(CARD2, BAD, .45), "Intentada"), (WARN, "Feta amb pista"), (OK, "Feta sense pista")]:
            self.R(lx, 448, lx + 16, 462, 4, fill=c)
            lx += 24
            it = self.T(lx, 455, lab, 12, MUTED, anchor="w")
            lx = self.cv.bbox(it)[2] + 20
        # gràfic de notes
        self.R(620, 192, 1060, 472, 24, fill=CARD, outline=LINE)
        self.T(644, 218, "Notes dels simulacres", 17, TEXT, True, anchor="w")
        gx1, gx2, gy1, gy2 = 676, 1036, 250, 420
        for v in (0, 5, 10):
            y = gy2 - (gy2 - gy1) * v / 10
            self.cv.create_line(gx1, y, gx2, y, fill=LINE, dash=(3, 4) if v else None, tags="scr")
            self.T(gx1 - 12, y, str(v), 11, MUTED, anchor="e")
        sims = [s for s in st["sessions"] if s["tipus"] == "simulador"][-10:]
        if not sims:
            self.T((gx1 + gx2) / 2, (gy1 + gy2) / 2, "Encara no has fet cap simulacre.", 15, MUTED)
        else:
            slot = (gx2 - gx1) / 10
            bw = min(26, slot * .6)
            bars = []
            for k, s in enumerate(sims):
                x = gx1 + slot * k + (slot - bw) / 2
                v = s["nota"]
                col = OK if v >= 8 else ACC2 if v >= 5 else WARN if v >= 3 else BAD
                rect = self.cv.create_rectangle(x, gy2, x + bw, gy2, fill=col, outline="", tags="scr")
                lab = self.T(x + bw / 2, gy2 - 10, str(v), 12, col, True)
                self.T(x + bw / 2, gy2 + 16, data_curta(s["data"])[:5], 10, MUTED)
                bars.append((rect, lab, x, v))

            def grow(i, frames=30):
                t = ease(i / frames)
                for rect, lab, x, v in bars:
                    top = gy2 - (gy2 - gy1) * v / 10 * t
                    self.cv.coords(rect, x, min(top, gy2 - 2), x + bw, gy2)
                    self.cv.coords(lab, x + bw / 2, min(top, gy2 - 2) - 10)
                if i < frames:
                    self.later(16, lambda: grow(i + 1))
            self.later(150, lambda: grow(0))
        # historial
        self.R(60, 486, 1060, 650, 24, fill=CARD, outline=LINE)
        self.T(84, 510, "Historial de sessions", 17, TEXT, True, anchor="w")
        self.T(1036, 510, f"{len(st['sessions'])} sessions", 12, MUTED, anchor="e")
        hc = tk.Canvas(self.root, bg=CARD, highlightthickness=0, bd=0)
        self.widgets.append(hc)
        self.cv.create_window(80, 528, window=hc, anchor="nw", width=960, height=112, tags="scr")
        self.hist_cv = hc
        rows = list(reversed(st["sessions"]))
        if not rows:
            hc.create_text(480, 50, text="Encara no hi ha cap sessió. Comença amb el mode Blitz!", fill=MUTED, font=self.fobj(14))
        for k, s in enumerate(rows):
            y = 14 + k * 30
            hc.create_text(6, y, text=data_curta(s["data"]), fill=MUTED, font=self.fobj(13, mono=True), anchor="w")
            blitz = s["tipus"] == "blitz"
            col = ORANGE if blitz else ACC2
            round_rect(hc, 130, y - 11, 236, y + 11, 11, fill=mix(CARD, col, .25), outline="")
            hc.create_text(183, y, text="BLITZ" if blitz else "SIMULADOR", fill=col, font=self.fobj(11, True))
            if blitz:
                f = [t for t in s["tasques"] if t["feta"]]
                avg = sum(t["temps"] for t in f) / len(f) if f else None
                desc = f"{len(f)} fetes · {len(s['tasques']) - len(f)} saltades" + (f" · temps mitjà {fmt_d(avg)}" if avg else "") + f" · durada {fmt(s['durada'])}"
            else:
                f = sum(1 for t in s["tasques"] if t["feta"])
                pi = sum(1 for t in s["tasques"] if t.get("pistes"))
                desc = f"Nota {s['nota']} · {f}/5 tasques · {pi} amb pista · {fmt(s['durada'])}" + (" · temps esgotat" if s.get("temps_esgotat") else "")
                hc.create_text(950, y, text=str(s["nota"]), fill=OK if s["nota"] >= 8 else ACC2 if s["nota"] >= 5 else WARN if s["nota"] >= 3 else BAD,
                               font=self.fobj(15, True), anchor="e")
            hc.create_text(252, y, text=desc, fill=TEXT, font=self.fobj(14), anchor="w")
        hc.configure(scrollregion=(0, 0, 960, max(112, 14 + len(rows) * 30)))
        self.button(W - 60 - 290, 662, 290, 44, "⇩  Exporta l'informe (HTML)", self.exporta, color=ACC, size=15)
        self.T(60, 684, "Pots exportar l'informe i enviar-lo al professor/a.", 13, MUTED, anchor="w")
        self.keymap = {"escape": self.menu}
        self.slide_in()

    def tip(self, tid, x, y):
        self.cv.delete("tip")
        nv = self.store.nivell
        t = self.tasks[nv][tid]
        p = self.store.stats(nv)["per"].get(tid)
        g = ("scr", "tip")
        lines = strip_tags(t["enunciat"])
        if p:
            info = f"Feta {p['fetes']} de {p['intents']} vegades" + (f" · millor temps {fmt_d(p['millor'])}" if p["millor"] else "")
        else:
            info = "Encara no l'has practicada"
        tx = x + 44 if x < 380 else x - 324
        a = self.T(tx + 14, y - 6, f"{tid} · {t['nom_bloc']}", 13, BLOC_COL[t["bloc"]], True, anchor="nw", tags=g)
        b = self.T(tx + 14, y + 16, lines, 13, TEXT, anchor="nw", width=270, tags=g)
        bb = self.cv.bbox(b)
        c = self.T(tx + 14, bb[3] + 6, info, 12, MUTED, anchor="nw", width=270, tags=g)
        bb2 = self.cv.bbox(c)
        rect = self.R(tx, y - 18, tx + 300, bb2[3] + 12, 14, fill=CARD2, outline=BLOC_COL[t["bloc"]], width=2, tags=g)
        self.cv.tag_lower(rect, a)
        self.cv.tag_raise("tip")

    def exporta(self):
        nv = self.store.nivell
        st = self.store.stats(nv)
        nom = self.store.nom
        path = filedialog.asksaveasfilename(parent=self.root, defaultextension=".html", initialfile=f"informe_{slug(nom)}_{nv}.html",
                                            filetypes=[("Pàgina web", "*.html")], title="Desa l'informe")
        if not path:
            return
        e = html.escape
        notes = st["notes"]
        files = []
        for tid, t in self.tasks[nv].items():
            p = st["per"].get(tid)
            if not p:
                estat, cls = "Sense fer", "none"
            elif not p["fetes"]:
                estat, cls = "Intentada", "bad"
            elif not p["sense_pista"]:
                estat, cls = "Feta amb pista", "warn"
            else:
                estat, cls = "Feta sense pista", "ok"
            files.append(f"<tr><td><b>{tid}</b></td><td>{e(t['nom_bloc'])}</td><td>{e(strip_tags(t['enunciat']))}</td>"
                         f"<td>{p['fetes'] if p else 0}/{p['intents'] if p else 0}</td><td>{fmt_d(p['millor']) if p and p['millor'] else '–'}</td>"
                         f"<td><span class='{cls}'>{estat}</span></td></tr>")
        ses = []
        for s in reversed(st["sessions"]):
            if s["tipus"] == "blitz":
                f = sum(1 for t in s["tasques"] if t["feta"])
                d = f"Blitz · {f} fetes · {len(s['tasques']) - f} saltades · durada {fmt(s['durada'])}"
            else:
                f = sum(1 for t in s["tasques"] if t["feta"])
                d = f"Simulador · <b>nota {s['nota']}</b> · {f}/5 tasques ({', '.join(t['id'] + ('✓' if t['feta'] else '✗') for t in s['tasques'])}) · {fmt(s['durada'])}"
            ses.append(f"<li><span class='d'>{data_curta(s['data'])}</span> {d}</li>")
        doc = f"""<!DOCTYPE html><html lang="ca"><head><meta charset="utf-8"><title>Informe {e(nom)} · {nv}</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;background:#0b1020;color:#e8eefc;max-width:1000px;margin:30px auto;padding:0 20px}}
h1{{color:#7c5cff}}h2{{color:#22d3ee;margin-top:30px}}.tiles{{display:flex;gap:12px;flex-wrap:wrap}}.t{{background:#151e36;border-radius:14px;padding:14px 18px;min-width:150px}}
.t b{{display:block;font-size:26px}}table{{width:100%;border-collapse:collapse;background:#151e36;border-radius:12px;overflow:hidden}}td,th{{padding:7px 10px;border-bottom:1px solid #2b3966;font-size:14px;text-align:left}}
span{{padding:2px 8px;border-radius:8px;font-size:12px;white-space:nowrap}}.ok{{background:#22c55e;color:#06240f}}.warn{{background:#facc15;color:#2b2100}}.bad{{background:#7f1d2d}}.none{{background:#1d2848;color:#8d9abf}}
li{{margin:6px 0}}.d{{color:#8d9abf;font-family:Consolas,monospace;margin-right:8px}}</style></head><body>
<h1>Informe del simulador · {e(nom)}</h1><p>{nv} · {e(BANKS[nv]['titol'])} · generat el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
<div class="tiles"><div class="t">Tasques resoltes<b>{st['resoltes']}/{len(self.tasks[nv])}</b></div><div class="t">Sense pista<b>{st['sense_pista']}</b></div>
<div class="t">Simulacres<b>{st['sim']}</b></div><div class="t">Nota mitjana<b>{(f"{sum(notes) / len(notes):.1f}") if notes else '–'}</b></div>
<div class="t">Millor nota<b>{max(notes) if notes else '–'}</b></div><div class="t">Sessions Blitz<b>{st['blitz']}</b></div></div>
<h2>Tasques</h2><table><tr><th>Codi</th><th>Bloc</th><th>Tasca</th><th>Fetes/intents</th><th>Millor temps</th><th>Estat</th></tr>{''.join(files)}</table>
<h2>Sessions</h2><ul>{''.join(ses) or '<li>Cap sessió</li>'}</ul></body></html>"""
        try:
            Path(path).write_text(doc, encoding="utf-8")
            self.toast("Informe desat correctament", OK, "✓")
        except Exception as ex:
            self.toast(f"No s'ha pogut desar: {ex}", BAD, "!")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
