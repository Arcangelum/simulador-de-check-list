#!/usr/bin/env python3
"""
Generador de checklists d'avaluació pràctica de Linux (SMX · RA3)

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
  'Navegació i gestió de fitxers',
  [("Crea l'estructura <b>~/examen/{entrada,sortida,arxiu}</b> amb una sola ordre.", 'ls -d ~/examen/*'),
   ('Crea dins de ~/examen el fitxer ocult <b>.config_smx</b> i demostra que existeix.', 'ls -a ~/examen'),
   ('Copia tots els fitxers <b>.conf</b> de /etc que comencin per <b>h</b> a ~/examen/arxiu.', 'ls ~/examen/arxiu'),
   ('Crea els fitxers <b>dia1.log</b> a <b>dia7.log</b> amb una sola ordre i esborra només el dia3 i el dia5.', 'ls ~/examen'),
   ('Canvia el nom de la carpeta ~/examen/sortida a <b>resultats</b> sense crear-ne cap de nova.', 'ls ~/examen'),
   ("Situa't a /usr/share i, sense sortir-ne, crea el fitxer <b>prova.txt</b> a la teva carpeta personal fent servir una ruta relativa.", 'history | tail -3; ls ~/prova.txt'),
   ('Troba a quina carpeta és el programa <b>ls</b> i digues quin tipus de fitxer és.', 'which ls; file $(which ls)'),
   ('Busca tots els fitxers de /etc acabats en <b>.conf</b> que tinguin a la ruta la paraula <b>apt</b>.', "find /etc -path '*apt*' -name '*.conf'"),
   ('Mostra el contingut de /var/log ordenat per data de modificació, el més recent primer.', 'ls -lt /var/log'),
   ('Mostra la mida en format llegible de tots els fitxers de /etc/apt.', 'ls -lh /etc/apt'),
   ("Crea l'àlies <b>neteja</b> que executi <b>clear</b> i fes-lo servir.", 'alias'),
   ('Explica la diferència entre <b>/root</b> i <b>/</b> i entra a cadascuna (si es pot).', 'Resposta oral + cd')]),
 ('B',
  'Text, redireccions i filtres',
  [("Desa a ~/examen/usuaris.txt la llista de noms d'usuari del sistema ordenada alfabèticament.", 'cat ~/examen/usuaris.txt'),
   ('Compta quants usuaris del sistema tenen <b>/bin/bash</b> com a shell.', "grep -c '/bin/bash' /etc/passwd"),
   ('Executa <b>ls /etc /no_existeix</b> desant la sortida correcta a ok.txt i els errors a ko.txt.', 'cat ok.txt ko.txt'),
   ('Mostra només les línies 5 a 10 de /etc/passwd.', 'head -n 10 /etc/passwd | tail -n 6'),
   ('Mostra quants grups hi ha al sistema i desa el número a ~/examen/grups.txt i per pantalla alhora.', 'cat ~/examen/grups.txt'),
   ('Mostra el valor de les variables HOME, USER i SHELL en una sola línia.', 'echo $HOME $USER $SHELL'),
   ('Mostra totes les línies de /etc/services que continguin <b>ssh</b>, sense distingir majúscules, numerades.', 'grep -in ssh /etc/services'),
   ('Mostra les shells diferents que fan servir els usuaris de /etc/passwd i quants usuaris en fan servir cadascuna.', 'cut -d: -f7 /etc/passwd | sort | uniq -c'),
   ('Crea amb <b>nano</b> el fitxer notes.txt amb tres línies i afegeix-hi una quarta línia sense obrir cap editor.', 'cat notes.txt'),
   ("Crea amb <b>vim</b> el fitxer vim.txt amb el teu nom, desa'l i surt.", 'cat vim.txt'),
   ("Converteix a majúscules el contingut de /etc/hostname i desa'l a ~/examen/HOST.txt.", 'cat ~/examen/HOST.txt'),
   ('Mostra les línies de /etc/passwd que NO contenen <b>nologin</b> i compta-les.', 'grep -vc nologin /etc/passwd')]),
 ('C',
  'Usuaris i grups',
  [("Crea l'usuari <b>tecnic1</b> amb carpeta personal i comprova que existeix.", 'id tecnic1; ls /home'),
   ("Crea el grup <b>suport</b> i afegeix-hi l'usuari actual sense treure'l dels altres grups.", 'getent group suport'),
   ("Crea l'usuari <b>becari</b>, posa-li contrasenya i inicia sessió amb ell al terminal.", 'su - becari; whoami'),
   ("Mostra el UID, el GID i la carpeta personal de l'usuari actual a partir de /etc/passwd.", 'grep $USER /etc/passwd'),
   ("Crea l'usuari <b>temporal</b> i esborra'l juntament amb la seva carpeta personal.", 'id temporal; ls /home'),
   ("Crea els grups <b>web</b> i <b>bd</b> i l'usuari <b>dev1</b> que pertanyi a tots dos.", 'groups dev1'),
   ("Mostra a quins grups pertany l'usuari actual i digues quin li permet fer servir sudo.", 'groups'),
   ("Treu l'usuari <b>dev1</b> (o el que indiqui el professor/a) del grup <b>bd</b>.", 'groups dev1'),
   ("Bloqueja el compte de l'usuari <b>becari</b> i demostra que està bloquejat.", 'sudo passwd -S becari'),
   ("Canvia el shell de l'usuari <b>tecnic1</b> a <b>/bin/sh</b>.", 'grep tecnic1 /etc/passwd'),
   ("Explica per què no es pot llegir /etc/shadow sense sudo i mostra'n els permisos.", 'ls -l /etc/shadow'),
   ('Mostra els usuaris que tenen UID igual o superior a 1000 (usuaris humans).', "awk -F: '$3>=1000' /etc/passwd")]),
 ('D',
  'Permisos i propietaris',
  [('Crea el fitxer secret.txt i fes que només el propietari el pugui llegir i escriure (en números).', 'ls -l secret.txt  → -rw-------'),
   ("Crea un script <b>data.sh</b> que mostri la data, fes-lo executable i executa'l.", 'ls -l data.sh; ./data.sh'),
   ('Posa permisos <b>rwxr-x---</b> a la carpeta ~/examen fent servir lletres (u, g, o).', 'ls -ld ~/examen'),
   ('Crea el fitxer informe.txt i canvia el propietari a <b>tecnic1</b> i el grup a <b>suport</b>.', 'ls -l informe.txt'),
   ('Treu el permís de lectura a «altres» de tots els fitxers de ~/examen amb una sola ordre.', 'ls -l ~/examen'),
   ('Interpreta els permisos de /usr/bin/passwd i explica per a què serveix la <b>s</b>.', 'ls -l /usr/bin/passwd'),
   ('Crea la carpeta /srv/equip, del grup <b>suport</b>, on només el grup hi pugui entrar i escriure.', 'ls -ld /srv/equip → drwxrwx---'),
   ('Crea una carpeta on tothom pugui escriure però cadascú només pugui esborrar els seus fitxers.', 'ls -ld → drwxrwxrwt'),
   ("Mostra l'umask actual i calcula quins permisos tindrà un fitxer nou. Comprova-ho.", 'umask; touch x; ls -l x'),
   ('Crea una carpeta amb permisos 644 i intenta entrar-hi. Explica què passa i soluciona-ho.', 'ls -ld; cd'),
   ('Converteix a número els permisos de /etc/passwd, /etc/shadow i /tmp.', 'ls -ld /etc/passwd /etc/shadow /tmp'),
   ('Fes que el fitxer llista.txt només es pugui llegir (ningú no hi pot escriure) i demostra-ho intentant afegir-hi text.', 'ls -l; echo x >> llista.txt')]),
 ('E',
  'Processos, paquets i compressió',
  [("Executa <b>sleep 900</b> en segon pla, mostra'n el PID i atura'l.", 'jobs; pgrep sleep'),
   ('Mostra els 5 processos que consumeixen més memòria.', 'ps aux --sort=-%mem | head -6'),
   ("Executa <b>sleep 1000</b> en primer pla, pausa'l, envia'l al segon pla i després porta'l al primer pla i atura'l.", 'Ctrl+Z, bg, fg, Ctrl+C'),
   ('Mostra quin procés té el PID 1 i quin és el teu procés de shell.', 'ps -p 1; echo $$; ps -p $$'),
   ('Executa un procés amb prioritat 15 i mostra la seva prioritat amb ps.', 'ps -o pid,ni,cmd'),
   ("Instal·la el paquet <b>sl</b> (o el que indiqui el professor/a), executa'l i desinstal·la'l.", 'dpkg -l sl'),
   ("Busca un paquet que contingui la paraula <b>calculator</b> i mostra'n la descripció d'un.", 'apt search; apt show'),
   ('Digues quina versió del paquet <b>bash</b> hi ha instal·lada.', 'dpkg -l bash  /  apt show bash'),
   ('Mostra quants paquets hi ha instal·lats al sistema.', "dpkg -l | grep '^ii' | wc -l"),
   ("Crea una còpia comprimida de /etc/apt a ~/examen/apt.tar.gz i mostra'n el contingut sense extreure-la.", 'tar -tzf ~/examen/apt.tar.gz'),
   ('Extreu el fitxer apt.tar.gz a la carpeta ~/examen/restaurat.', 'ls -R ~/examen/restaurat'),
   ("Mostra la memòria lliure i l'espai lliure del disc en format llegible.", 'free -h; df -h')])]

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
        c.drawString(2 * cm, 1.2 * cm, "SMX · Sistemes operatius · RA3 Linux bàsic · Checklist d'avaluació")
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


def generar_zip(alumnes, ruta_zip, titol="Checklist · Linux bàsic", data=None, llavor=None, inclou_comprovacio=True):
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

    root = tk.Tk(); root.title("Generador de checklists · Linux bàsic (SMX)"); root.geometry("820x700"); root.minsize(700, 560)
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
    v_titol = tk.StringVar(value="Checklist · Linux bàsic (RA3)"); ttk.Entry(opc, textvariable=v_titol, width=45).grid(row=0, column=1, columnspan=3, sticky="w")
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
        ruta = filedialog.asksaveasfilename(defaultextension=".zip", initialfile="checklists_linux.zip", filetypes=[("Fitxer ZIP", "*.zip")])
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
