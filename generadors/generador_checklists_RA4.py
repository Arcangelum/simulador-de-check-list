#!/usr/bin/env python3
"""
Generador de checklists d'avaluació pràctica de Linux (SMX · RA4)

Rep una llista d'alumnes i genera un .zip amb un PDF per alumne amb
5 tasques (una de cada bloc A-E), repartides de manera equilibrada.

Requisits:  Python 3.8+  i  reportlab   (pip install reportlab)
Ús:         python3 generador_checklists.py
            python3 generador_checklists.py --cli alumnes.txt sortida.zip   (sense interfície)
"""
import io
import csv
import random
import re
import sys
import zipfile
import datetime
import unicodedata

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# ----------------------------------------------------------------------------
# Banc de tasques: (codi del bloc, nom del bloc, [(enunciat, com comprovar-ho), ...])
# ----------------------------------------------------------------------------
BLOCS = [('A',
  'Dispositius i discos',
  [('Mostra tots els discos i particions de la VM amb la mida i el sistema de fitxers.', 'lsblk -f'),
   ('Digues quin és el disc principal de la VM, quantes particions té i quina és la partició arrel.', 'lsblk; findmnt /'),
   ("Llista els dispositius PCI i identifica quin és l'adaptador de xarxa.", 'lspci | grep -i net'),
   ("Mostra els dispositius USB connectats (si no n'hi ha, explica què mostra la sortida).", 'lsusb'),
   ('Mostra el tipus de dispositiu (bloc o caràcter) de /dev/sda i de /dev/tty0 i explica la diferència.', 'ls -l /dev/sda /dev/tty0  → b / c'),
   ('Crea al segon disc (/dev/sdb) una taula de particions GPT amb una sola partició.', 'sudo fdisk -l /dev/sdb'),
   ("Dona format ext4 a /dev/sdb1 amb l'etiqueta DADES.", 'lsblk -f /dev/sdb'),
   ("Mostra l'UUID de totes les particions.", 'sudo blkid'),
   ("Crea amb dd un fitxer de 50 MB ple de zeros a ~/zeros.img i comprova'n la mida.", 'ls -lh ~/zeros.img'),
   ('Mostra la informació del nucli sobre el disc sda que hi ha a /sys/block.', 'ls /sys/block/sda; cat /sys/block/sda/size'),
   ('Mostra els missatges del nucli que parlen del disc sdb.', 'sudo dmesg | grep sdb'),
   ('Mostra quina CPU i quanta memòria detecta el sistema, sense fer servir top.', 'lscpu; cat /proc/meminfo | head -3')]),
 ('B',
  'Sistema de fitxers i muntatge',
  [('Munta /dev/sdb1 a /mnt/dades i crea-hi un fitxer.', 'findmnt /mnt/dades; ls /mnt/dades'),
   ('Desmunta /mnt/dades i comprova que el fitxer creat ja no es veu a la carpeta.', 'findmnt /mnt/dades; ls /mnt/dades'),
   ('Afegeix /dev/sdb1 a /etc/fstab (per UUID) perquè es munti a /mnt/dades i prova-ho sense reiniciar.', 'cat /etc/fstab; sudo mount -a; findmnt /mnt/dades'),
   ("Crea un enllaç simbòlic ~/logs que apunti a /var/log i explica què passa si s'esborra el destí.", 'ls -l ~/logs'),
   ("Crea un fitxer i un enllaç dur. Demostra que comparteixen l'inode.", 'ls -li'),
   ('Mostra quants inodes té lliures la partició arrel.', 'df -i /'),
   ("Mostra l'espai lliure de totes les particions i digues quina està més plena.", 'df -h'),
   ('Mostra les 5 carpetes que ocupen més dins de /var.', 'sudo du -h /var --max-depth=1 | sort -h | tail -5'),
   ("Crea un fitxer d'intercanvi (swap) de 256 MB, activa'l i comprova-ho.", 'swapon --show; free -h'),
   ('Comprova el sistema de fitxers de /dev/sdb1 (desmuntat) amb fsck.', 'sudo fsck -f /dev/sdb1'),
   ('Explica per a què serveixen /, /boot, /var i /tmp i mostra en quina partició és cadascuna.', 'findmnt; df -h /boot /var /tmp'),
   ('Mostra les opcions de muntatge de la partició arrel i digues si és de lectura i escriptura.', 'findmnt -o TARGET,OPTIONS /')]),
 ('C',
  'Arrencada i nucli',
  [('Mostra la versió del nucli en execució i els nuclis instal·lats a /boot.', 'uname -r; ls /boot/vmlinuz*'),
   ('Digues si la VM ha arrencat en mode UEFI o BIOS i com ho has sabut.', 'ls /sys/firmware/efi  (existeix = UEFI)'),
   ('Mostra el fitxer de configuració de GRUB i digues quants segons espera el menú.', 'grep TIMEOUT /etc/default/grub'),
   ("Canvia el temps d'espera de GRUB a 10 segons i aplica el canvi.", 'grep TIMEOUT /etc/default/grub; sudo update-grub'),
   ("Mostra quant ha trigat l'última arrencada i quins serveis han trigat més.", 'systemd-analyze; systemd-analyze blame | head'),
   ("Llista els mòduls del nucli carregats i busca'n un relacionat amb VirtualBox.", 'lsmod | grep -i vbox'),
   ("Mostra la informació d'un mòdul del nucli (descripció, fitxer, autor).", 'modinfo <mòdul>'),
   ("Carrega el mòdul <b>dummy</b>, comprova que hi és i descarrega'l.", 'lsmod | grep dummy'),
   ('Mostra els paràmetres amb què ha arrencat el nucli.', 'cat /proc/cmdline'),
   ("Mostra els primers missatges del nucli de l'arrencada actual.", 'sudo dmesg | head -20'),
   ('Mostra quant de temps fa que el sistema està engegat i la càrrega mitjana.', 'uptime'),
   ("Explica en ordre les fases de l'arrencada (firmware, GRUB, nucli, systemd) i mostra el procés PID 1.", 'ps -p 1')]),
 ('D',
  'Serveis (systemd) i tasques programades',
  [("Mostra l'estat del servei <b>cron</b> i digues si s'inicia automàticament.", 'systemctl status cron; systemctl is-enabled cron'),
   ("Atura el servei cron, comprova-ho i torna'l a engegar.", 'systemctl is-active cron'),
   ('Instal·la el servei <b>ssh</b> (openssh-server) i comprova que està actiu.', 'systemctl status ssh'),
   ("Desactiva l'inici automàtic del servei ssh sense aturar-lo.", 'systemctl is-enabled ssh; is-active ssh'),
   ('Llista els serveis que estan en execució ara mateix.', 'systemctl list-units --type=service --state=running'),
   ('Llista els serveis que han fallat.', 'systemctl --failed'),
   ('Mostra quin és el target per defecte del sistema i explica què vol dir.', 'systemctl get-default'),
   ('Crea una tasca de cron que cada minut afegeixi la data a ~/cron.log i comprova que funciona.', 'crontab -l; cat ~/cron.log'),
   ("Programa una tasca de cron que s'executi cada dilluns a les 8:30 (pot ser un echo).", 'crontab -l  → 30 8 * * 1'),
   ('Interpreta aquesta línia de cron: <b>0 */2 * * 1-5</b>.', 'Resposta oral: cada 2 h, de dilluns a divendres'),
   ("Mostra el fitxer d'unitat del servei cron i digues quin programa executa.", 'systemctl cat cron'),
   ("Programa una aturada del sistema d'aquí a 30 minuts i cancel·la-la.", 'sudo shutdown +30; sudo shutdown -c')]),
 ('E',
  'Monitorització i registres',
  [("Mostra quins processos consumeixen més CPU amb top i ordena'ls per memòria.", 'top → Maj+M'),
   ('Mostra la càrrega del sistema i explica què volen dir els tres números.', 'uptime  /  cat /proc/loadavg'),
   ("Mostra l'ús de memòria i d'intercanvi cada 2 segons, 5 vegades.", 'vmstat 2 5'),
   ('Mostra quins fitxers té oberts el procés de la teva shell.', 'lsof -p $$'),
   ('Mostra quin procés fa servir el port 22 (o un altre que indiqui el professor/a).', 'sudo ss -tlnp | grep :22'),
   ("Mostra els fils (threads) d'un procés.", 'ps -T -p <PID>  /  top -H'),
   ('Mostra les últimes 20 línies del registre del sistema.', 'sudo journalctl -n 20  /  tail -20 /var/log/syslog'),
   ("Mostra els registres del servei ssh (o cron) de l'última hora.", "journalctl -u cron --since '1 hour ago'"),
   ("Mostra els intents d'autenticació amb sudo que hi ha al registre.", 'sudo grep sudo /var/log/auth.log | tail'),
   ('Segueix en directe el registre del sistema i genera-hi un missatge amb logger.', "journalctl -f  +  logger 'prova SMX'"),
   ("Mostra només els missatges d'error de l'arrencada actual.", 'journalctl -b -p err'),
   ('Mostra la configuració de logrotate del registre auth i explica cada quan es rota.', 'cat /etc/logrotate.d/rsyslog')])]

# Equivalència entre tasques realitzades i nota
NOTES = {5: 10, 4: 8, 3: 6, 2: 3, 1: 1, 0: 0}


# ----------------------------------------------------------------------------
# Lògica
# ----------------------------------------------------------------------------
def llegir_alumnes(text):
    """Una línia per alumne. Ignora línies buides, duplicats i comentaris (#)."""
    vistos, alumnes = set(), []
    for linia in text.splitlines():
        nom = linia.strip().strip(";,")
        if not nom or nom.startswith("#"):
            continue
        if nom.lower() not in vistos:
            vistos.add(nom.lower())
            alumnes.append(nom)
    return alumnes


def assignar_tasques(alumnes, llavor=None):
    """Assigna una tasca de cada bloc a cada alumne de manera proporcionada:
    dins de cada bloc, totes les tasques es fan servir el mateix nombre de vegades
    (±1) abans de repetir-ne cap. A més, s'evita donar la mateixa combinació."""
    rng = random.Random(llavor)
    per_bloc = {}
    for codi, _, tasques in BLOCS:
        n = len(tasques)
        seq = []
        while len(seq) < len(alumnes):
            ronda = list(range(n))
            rng.shuffle(ronda)
            seq.extend(ronda)
        per_bloc[codi] = seq[:len(alumnes)]
    # Barreja l'ordre per bloc perquè les combinacions no segueixin cap patró
    for codi in per_bloc:
        rng.shuffle(per_bloc[codi])
    assignacio, usades = {}, set()
    for i, alumne in enumerate(alumnes):
        combo = tuple(per_bloc[c][i] for c, _, _ in BLOCS)
        intents = 0
        while combo in usades and intents < 50:   # intercanvia amb un altre alumne per evitar repeticions
            c = rng.choice([b[0] for b in BLOCS]); j = rng.randrange(len(alumnes))
            per_bloc[c][i], per_bloc[c][j] = per_bloc[c][j], per_bloc[c][i]
            combo = tuple(per_bloc[cc][i] for cc, _, _ in BLOCS); intents += 1
        usades.add(combo)
        assignacio[alumne] = [(codi, nom_bloc, idx + 1, tasques[idx]) for (codi, nom_bloc, tasques), idx in zip(BLOCS, combo)]
    return assignacio


def nom_fitxer(nom):
    s = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return s or "alumne"


def pdf_alumne(nom, tasques, titol, data, inclou_comprovacio=True):
    buf = io.BytesIO()
    base = ParagraphStyle("b", fontName="Helvetica", fontSize=10, leading=13)
    bold = ParagraphStyle("bb", parent=base, fontName="Helvetica-Bold")
    mono = ParagraphStyle("m", fontName="Courier", fontSize=8, leading=10, textColor=colors.HexColor("#475569"))
    h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=colors.HexColor("#4f46e5"), spaceAfter=4)
    sub = ParagraphStyle("s", parent=base, textColor=colors.HexColor("#475569"))
    blau = colors.HexColor("#e0f2fe")
    s = [Paragraph(titol, h1), Paragraph("Avaluació pràctica a la màquina virtual Ubuntu · 10–15 minuts", sub), Spacer(1, 8)]

    cap = Table([[Paragraph("<b>Alumne/a:</b>", base), Paragraph(f"<b>{esc(nom)}</b>", ParagraphStyle("n", parent=base, fontSize=12)),
                  Paragraph("<b>Data:</b>", base), Paragraph(esc(data), base)]], colWidths=[2.3 * cm, 9.2 * cm, 1.4 * cm, 4.1 * cm], rowHeights=[24])
    cap.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), .8, colors.grey), ("BACKGROUND", (0, 0), (0, 0), blau), ("BACKGROUND", (2, 0), (2, 0), blau), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    s += [cap, Spacer(1, 12)]

    capçalera = [Paragraph("<b>Codi</b>", base), Paragraph("<b>Tasca</b>", base), Paragraph("<b>Feta</b>", base), Paragraph("<b>No feta</b>", base)]
    files = [capçalera]
    for codi, nom_bloc, num, (enunciat, comprovar) in tasques:
        cel = [Paragraph(f"<font color='#64748b' size='8'>{esc(nom_bloc).upper()}</font>", base), Paragraph(enunciat, base)]
        if inclou_comprovacio:
            cel.append(Paragraph("Comprovació: " + esc(comprovar), mono))
        files.append([Paragraph(f"<b>{codi}{num}</b>", bold), cel, Casella(), Casella()])
    t = Table(files, colWidths=[1.5 * cm, 12.3 * cm, 1.5 * cm, 1.7 * cm], repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .5, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), blau), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("ALIGN", (2, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 1), (-1, -1), 7), ("BOTTOMPADDING", (0, 1), (-1, -1), 7)]))
    s += [t, Spacer(1, 14)]

    s.append(Paragraph("<b>Nota segons les tasques realitzades</b> (encercla-la)", base)); s.append(Spacer(1, 4))
    claus = [5, 4, 3, 2, 1, 0]
    nt = Table([["Tasques fetes"] + [str(k) for k in claus], ["Nota"] + [str(NOTES[k]) for k in claus]], colWidths=[3.2 * cm] + [2.3 * cm] * len(claus), rowHeights=[20, 26])
    nt.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .5, colors.grey), ("BACKGROUND", (0, 0), (0, -1), blau), ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                            ("FONTNAME", (1, 1), (-1, 1), "Helvetica-Bold"), ("FONTSIZE", (1, 1), (-1, 1), 13), ("ALIGN", (1, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    s += [nt, Spacer(1, 14)]

    fin = Table([[Paragraph("<b>Tasques fetes:</b> ____ / 5", base), Paragraph("<b>Nota final:</b> ______", base), Paragraph("<b>Signatura professor/a:</b>", base)],
                 [Paragraph("<b>Observacions:</b>", base), "", ""]], colWidths=[5 * cm, 5 * cm, 7 * cm], rowHeights=[26, 60])
    fin.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), .8, colors.grey), ("INNERGRID", (0, 0), (-1, 0), .5, colors.grey), ("SPAN", (0, 1), (-1, 1)), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    s.append(fin)

    def peu(c, d):
        c.setFont("Helvetica", 7.5); c.setFillColor(colors.grey)
        c.drawString(2 * cm, 1.2 * cm, "SMX · Sistemes operatius · RA4 Linux avançat · Checklist d'avaluació")
        c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, " ".join(f"{a[0]}{a[2]}" for a in tasques))
    SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm, title=f"Checklist {nom}").build(s, onFirstPage=peu, onLaterPages=peu)
    return buf.getvalue()


from reportlab.platypus.flowables import Flowable
class Casella(Flowable):
    """Quadre buit per marcar amb una creu."""
    def __init__(self, mida=14):
        super().__init__(); self.width = self.height = mida
    def draw(self):
        self.canv.setStrokeColor(colors.HexColor("#334155")); self.canv.setLineWidth(1.2)
        self.canv.rect(0, 0, self.width, self.height)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generar_zip(alumnes, ruta_zip, titol="Checklist · Linux avançat", data=None, llavor=None, inclou_comprovacio=True):
    data = data or datetime.date.today().strftime("%d/%m/%Y")
    assignacio = assignar_tasques(alumnes, llavor)
    resum = io.StringIO(); w = csv.writer(resum, delimiter=";")
    w.writerow(["Alumne"] + [f"Bloc {b[0]}" for b in BLOCS] + ["Tasques fetes", "Nota"])
    noms_usats = {}
    with zipfile.ZipFile(ruta_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for i, alumne in enumerate(alumnes, 1):
            tasques = assignacio[alumne]
            base = nom_fitxer(alumne)
            noms_usats[base] = noms_usats.get(base, 0) + 1
            if noms_usats[base] > 1:
                base += f"_{noms_usats[base]}"
            z.writestr(f"{i:02d}_{base}.pdf", pdf_alumne(alumne, tasques, titol, data, inclou_comprovacio))
            w.writerow([alumne] + [f"{t[0]}{t[2]}" for t in tasques] + ["", ""])
        z.writestr("resum_assignacions.csv", "\ufeff" + resum.getvalue())
    return assignacio


# ----------------------------------------------------------------------------
# Interfície gràfica
# ----------------------------------------------------------------------------
def gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    root = tk.Tk(); root.title("Generador de checklists · Linux avançat (SMX)"); root.geometry("820x700"); root.minsize(700, 560)
    frm = ttk.Frame(root, padding=12); frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Llista d'alumnes (un per línia):", font=("", 11, "bold")).grid(row=0, column=0, sticky="w")
    txt = tk.Text(frm, height=12, width=60, font=("", 11)); txt.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=4)
    sb = ttk.Scrollbar(frm, command=txt.yview); sb.grid(row=1, column=3, sticky="ns"); txt.configure(yscrollcommand=sb.set)
    comptador = ttk.Label(frm, text="0 alumnes"); comptador.grid(row=2, column=0, sticky="w")

    def actualitza(*_):
        comptador.config(text=f"{len(llegir_alumnes(txt.get('1.0', 'end')))} alumnes")
    txt.bind("<KeyRelease>", actualitza)

    def carregar():
        ruta = filedialog.askopenfilename(filetypes=[("Text o CSV", "*.txt *.csv"), ("Tots", "*.*")])
        if not ruta: return
        for enc in ("utf-8-sig", "latin-1"):
            try:
                with open(ruta, encoding=enc) as f: contingut = f.read(); break
            except UnicodeDecodeError: continue
        # CSV amb ; o tabulador: agafa la primera columna (les comes es mantenen: "Cognoms, Nom")
        linies = [re.split(r"[;\t]", l)[0] for l in contingut.splitlines()]
        txt.delete("1.0", "end"); txt.insert("1.0", "\n".join(linies)); actualitza()
    ttk.Button(frm, text="Carrega fitxer (.txt / .csv)…", command=carregar).grid(row=2, column=2, sticky="e")

    opc = ttk.LabelFrame(frm, text="Opcions", padding=8); opc.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)
    ttk.Label(opc, text="Títol:").grid(row=0, column=0, sticky="w")
    v_titol = tk.StringVar(value="Checklist · Linux avançat (RA4)"); ttk.Entry(opc, textvariable=v_titol, width=45).grid(row=0, column=1, columnspan=3, sticky="w")
    ttk.Label(opc, text="Data:").grid(row=1, column=0, sticky="w", pady=4)
    v_data = tk.StringVar(value=datetime.date.today().strftime("%d/%m/%Y")); ttk.Entry(opc, textvariable=v_data, width=14).grid(row=1, column=1, sticky="w")
    ttk.Label(opc, text="Llavor (opcional, per repetir el sorteig):").grid(row=1, column=2, sticky="e", padx=(16, 4))
    v_llavor = tk.StringVar(); ttk.Entry(opc, textvariable=v_llavor, width=10).grid(row=1, column=3, sticky="w")
    v_comp = tk.BooleanVar(value=True)
    ttk.Checkbutton(opc, text="Inclou la línia «Comprovació» (ordre per verificar cada tasca)", variable=v_comp).grid(row=2, column=0, columnspan=4, sticky="w")

    ttk.Label(frm, text="Nota: 5 tasques = 10 · 4 = 8 · 3 = 6 · 2 = 3 · 1 = 1 · 0 = 0", foreground="#4f46e5").grid(row=4, column=0, columnspan=3, sticky="w")

    def generar():
        alumnes = llegir_alumnes(txt.get("1.0", "end"))
        if not alumnes:
            messagebox.showwarning("Falten alumnes", "Escriu o carrega la llista d'alumnes."); return
        ruta = filedialog.asksaveasfilename(defaultextension=".zip", initialfile="checklists_linux_avancat.zip", filetypes=[("Fitxer ZIP", "*.zip")])
        if not ruta: return
        llavor = v_llavor.get().strip() or None
        try:
            generar_zip(alumnes, ruta, v_titol.get().strip() or "Checklist", v_data.get().strip(), llavor, v_comp.get())
        except Exception as e:
            messagebox.showerror("Error", str(e)); return
        messagebox.showinfo("Fet!", f"S'han generat {len(alumnes)} checklists a:\n{ruta}\n\nEl ZIP inclou també resum_assignacions.csv.")
    estil = ttk.Style(); estil.configure("Gran.TButton", font=("", 12, "bold"))
    ttk.Button(frm, text="▶  Genera el ZIP de checklists", style="Gran.TButton", command=generar).grid(row=5, column=0, columnspan=3, pady=12, ipadx=12, ipady=6)

    frm.columnconfigure(0, weight=1); frm.rowconfigure(1, weight=1)
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--cli":
        with open(sys.argv[2], encoding="utf-8-sig") as f:
            als = llegir_alumnes(f.read())
        generar_zip(als, sys.argv[3])
        print(f"Generats {len(als)} checklists a {sys.argv[3]}")
    else:
        gui()
