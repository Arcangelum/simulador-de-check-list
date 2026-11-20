# Sistemes operatius · SMX

Materials i eines per al mòdul de **Sistemes operatius monolloc** del cicle de Sistemes Microinformàtics i Xarxes (SMX): dossiers, presentacions, guies pràctiques i un simulador per preparar l'avaluació pràctica de Linux.

![Captures del simulador](docs/img/captures_simulador.png)

## Què hi ha

| Carpeta | Contingut |
|---|---|
| [`app/`](app/) | **Simulador de checklist** per als alumnes (mode Blitz, mode Simulador i Informe). |
| [`generadors/`](generadors/) | Programes per al professorat que generen un PDF de checklist per a cada alumne (RA3 i RA4). |
| [`materials/RA1/`](materials/RA1/) | Què és un sistema operatiu: dossiers i presentacions. |
| [`materials/RA2/`](materials/RA2/) | Instal·lació de sistemes operatius: teoria, guies i pràctiques guiades de Windows 10 i Ubuntu amb VirtualBox. |
| [`materials/RA3/`](materials/RA3/) | Linux bàsic: guia de treball amb Linux Journey (nivell Grasshopper), dossiers i presentacions. |
| [`materials/RA4/`](materials/RA4/) | Linux avançat: guia de treball amb Linux Journey (nivell Journeyman). |
| [`materials/virtualitzacio/`](materials/virtualitzacio/) | Teoria de la virtualització i guia pràctica de VirtualBox. |

Els PDF de teoria estan pensats també per carregar-los a eines com NotebookLM i estudiar-hi.

## Simulador de checklist (per als alumnes)

Aplicació d'escriptori per practicar les tasques de l'avaluació pràctica de Linux (60 tasques del RA3 i 60 del RA4, repartides en 5 blocs).

- **Mode Blitz:** tasques aleatòries amb cronòmetre, pistes i rècords personals.
- **Mode Simulador:** 5 tasques (una per bloc) i 15 minuts de compte enrere; al final, la nota.
- **Informe:** historial de sessions, mapa de tasques resoltes, gràfic de notes i exportació a HTML.

### Com executar-lo

Només cal tenir **Python 3** instal·lat ([python.org](https://www.python.org/downloads/)). No cal instal·lar cap llibreria.

1. Descarrega [`app/simulador_checklist.py`](app/simulador_checklist.py).
2. Obre un terminal a la carpeta on l'has desat i executa:

   ```
   py simulador_checklist.py          # Windows
   python3 simulador_checklist.py     # Linux / macOS
   ```

A Windows, si canvies l'extensió a `.pyw`, s'obre amb doble clic sense la finestra del terminal.

Les dades de cada alumne es desen a la seva carpeta d'usuari (`.simulador_checklist_smx.json`).

**Nota de nota:** 5 tasques = 10 · 4 = 8 · 3 = 6 · 2 = 3 · 1 = 1 · 0 = 0.

## Generadors de checklists (per al professorat)

Generen un `.zip` amb un PDF per alumne, amb 5 tasques aleatòries (una per bloc) repartides de manera equilibrada, caselles de «Feta / No feta» i la taula de notes.

```
py -m pip install reportlab
py generadors/generador_checklists_RA3.py
py generadors/generador_checklists_RA4.py
```

Enganxa la llista d'alumnes (un per línia) o carrega un `.txt` / `.csv` i prem **Genera el ZIP de checklists**.

## Curs de referència

Les guies del RA3 i el RA4 segueixen el curs gratuït [Linux Journey](https://labex.io/linuxjourney). Els exercicis i les tasques d'aquest repositori són propis.

## Llicència

- Codi (`app/`, `generadors/`): [MIT](LICENSE).
- Materials didàctics (`materials/`): [Creative Commons BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.ca).
