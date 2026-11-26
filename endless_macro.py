"""
Endless Macro - Modern, hafif ve açık kaynak fare / klavye macro programı.
Modern, lightweight open-source mouse / keyboard macro program.
"""

import ctypes
import json
import math
import os
import queue
import sys
import threading
import time
from dataclasses import dataclass, field

import customtkinter as ctk
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from pynput import keyboard, mouse

APP_NAME = "Endless Macro"
VERSION = "1.2"

# ----------------------------------------------------------------------------
# Dil Sözlüğü (Tüm diller için tam ve eksiksiz arayüz metinleri)
# ----------------------------------------------------------------------------
LANG = {
    "tr": {
        "nav_mouse": "Fare",
        "nav_kb": "Klavye",
        "nav_both": "Fare + Klavye",
        "nav_guide": "Kılavuz",
        "help_tip": "Takıldığın yerde ? düğmesine\nveya Kılavuz'a tıkla.",
        "mouse_title": "Fare",
        "left_click": "Sol tık",
        "right_click": "Sağ tık",
        "middle_click": "Orta tekerlek",
        "spam": "Spam",
        "hold": "Basılı tut",
        "cps_unit": "tık / sn",
        "kb_title": "Klavye",
        "seq_switch": "Sırayla bas",
        "seq_off": "Kapalı: slotlar aynı anda çalışır",
        "seq_on": "Açık: slotlar 1 → 2 → 3 → 4 → 5 sırayla basılır",
        "empty_slot": "Boş (atlanır)",
        "unit_interval": "sn aralık",
        "unit_wait": "sn sonra bekle",
        "set_title": "Ayarlar",
        "trigger_key": "Tetik tuşu",
        "work_mode": "Çalışma biçimi",
        "auto": "Oto",
        "manual": "Manuel",
        "delay_label": "Başlama gecikmesi (sn)",
        "duration_label": "Otomatik durdur (sn, 0 = kapalı)",
        "topmost_label": "Hep üstte",
        "auto_hint": "Oto: tetik tuşuna bir kez bas, başlasın. Tekrar bas, dursun.",
        "manual_hint": "Manuel: tetik tuşunu basılı tuttukça çalışır, bırakınca durur (gecikme yok).",
        "start": "Başlat",
        "stop": "Durdur",
        "ready": "Hazır",
        "running": "Çalışıyor...",
        "total": "Toplam: ",
        "press_key": "Bir tuşa bas…  (Esc = iptal)",
        "press_hotkey": "Bir tuşa bas…",
        "err_stop": "Önce macroyu durdur.",
        "err_same_key": "Tetik tuşuyla aynı tuş seçilemez.",
        "err_not_found": "Tuş tanınamadı, tekrar seç.",
        "help_close": "Kapat"
    },
    "en": {
        "nav_mouse": "Mouse",
        "nav_kb": "Keyboard",
        "nav_both": "Mouse + Keyboard",
        "nav_guide": "Guide",
        "help_tip": "Click ? or Guide if you\nneed any help.",
        "mouse_title": "Mouse",
        "left_click": "Left click",
        "right_click": "Right click",
        "middle_click": "Middle click",
        "spam": "Spam",
        "hold": "Hold",
        "cps_unit": "clicks / sec",
        "kb_title": "Keyboard",
        "seq_switch": "Sequence",
        "seq_off": "Off: slots run simultaneously",
        "seq_on": "On: slots run in 1 → 2 → 3 → 4 → 5 order",
        "empty_slot": "Empty (skipped)",
        "unit_interval": "sec interval",
        "unit_wait": "sec wait after",
        "set_title": "Settings",
        "trigger_key": "Trigger key",
        "work_mode": "Mode",
        "auto": "Auto",
        "manual": "Manual",
        "delay_label": "Start delay (sec)",
        "duration_label": "Auto stop (sec, 0 = off)",
        "topmost_label": "Always on top",
        "auto_hint": "Auto: press trigger once to start, press again to stop.",
        "manual_hint": "Manual: runs while holding trigger, stops when released (no delay).",
        "start": "Start",
        "stop": "Stop",
        "ready": "Ready",
        "running": "Running...",
        "total": "Total: ",
        "press_key": "Press a key…  (Esc = cancel)",
        "press_hotkey": "Press a key…",
        "err_stop": "Stop the macro first.",
        "err_same_key": "Cannot use the trigger key as a slot key.",
        "err_not_found": "Key not recognized, choose again.",
        "help_close": "Close"
    },
    "de": {
        "nav_mouse": "Maus",
        "nav_kb": "Tastatur",
        "nav_both": "Maus + Tastatur",
        "nav_guide": "Anleitung",
        "help_tip": "Klicke auf ? oder Anleitung\nwenn du Hilfe brauchst.",
        "mouse_title": "Maus",
        "left_click": "Linksklick",
        "right_click": "Rechtsklick",
        "middle_click": "Mittelklick",
        "spam": "Spam",
        "hold": "Halten",
        "cps_unit": "Klicks / Sek",
        "kb_title": "Tastatur",
        "seq_switch": "Sequenz",
        "seq_off": "Aus: Slots laufen gleichzeitig",
        "seq_on": "Ein: Slots laufen in Reihenfolge 1 → 2 → 3 → 4 → 5",
        "empty_slot": "Leer (übersprungen)",
        "unit_interval": "Sek Intervall",
        "unit_wait": "Sek Warten danach",
        "set_title": "Einstellungen",
        "trigger_key": "Auslöser",
        "work_mode": "Modus",
        "auto": "Auto",
        "manual": "Manuell",
        "delay_label": "Startverzögerung (Sek)",
        "duration_label": "Auto-Stopp (Sek, 0 = aus)",
        "topmost_label": "Immer im Vordergrund",
        "auto_hint": "Auto: Einmal drücken zum Starten, nochmal zum Stoppen.",
        "manual_hint": "Manuell: Läuft beim Halten, stoppt beim Loslassen.",
        "start": "Start",
        "stop": "Stopp",
        "ready": "Bereit",
        "running": "Läuft...",
        "total": "Gesamt: ",
        "press_key": "Drücke eine Taste…  (Esc = Abbrechen)",
        "press_hotkey": "Drücke eine Taste…",
        "err_stop": "Stoppe zuerst das Makro.",
        "err_same_key": "Auslöser kann nicht als Slot-Taste verwendet werden.",
        "err_not_found": "Taste nicht erkannt, bitte neu wählen.",
        "help_close": "Schließen"
    },
    "es": {
        "nav_mouse": "Ratón",
        "nav_kb": "Teclado",
        "nav_both": "Ratón + Teclado",
        "nav_guide": "Guía",
        "help_tip": "Haz clic en ? o Guía si\nnecesitas ayuda.",
        "mouse_title": "Ratón",
        "left_click": "Clic izq.",
        "right_click": "Clic der.",
        "middle_click": "Clic medio",
        "spam": "Spam",
        "hold": "Mantener",
        "cps_unit": "clics / seg",
        "kb_title": "Teclado",
        "seq_switch": "Secuencia",
        "seq_off": "Apagado: ranuras simultáneas",
        "seq_on": "Encendido: orden 1 → 2 → 3 → 4 → 5",
        "empty_slot": "Vacío (omitido)",
        "unit_interval": "seg intervalo",
        "unit_wait": "seg espera",
        "set_title": "Ajustes",
        "trigger_key": "Tecla de activación",
        "work_mode": "Modo",
        "auto": "Auto",
        "manual": "Manual",
        "delay_label": "Retraso inicial (seg)",
        "duration_label": "Parada automática (seg, 0 = off)",
        "topmost_label": "Siempre visible",
        "auto_hint": "Auto: presiona una vez para iniciar, otra para parar.",
        "manual_hint": "Manual: se ejecuta al mantener presionada la tecla.",
        "start": "Iniciar",
        "stop": "Detener",
        "ready": "Listo",
        "running": "Ejecutando...",
        "total": "Total: ",
        "press_key": "Presiona una tecla…  (Esc = cancelar)",
        "press_hotkey": "Presiona una tecla…",
        "err_stop": "Detén el macro primero.",
        "err_same_key": "No se puede usar la tecla de activación.",
        "err_not_found": "Tecla no reconocida.",
        "help_close": "Cerrar"
    },
    "fr": {
        "nav_mouse": "Souris",
        "nav_kb": "Clavier",
        "nav_both": "Souris + Clavier",
        "nav_guide": "Guide",
        "help_tip": "Cliquez sur ? ou Guide si\nvous avez besoin d'aide.",
        "mouse_title": "Souris",
        "left_click": "Clic gauche",
        "right_click": "Clic droit",
        "middle_click": "Clic milieu",
        "spam": "Spam",
        "hold": "Maintenir",
        "cps_unit": "clics / s",
        "kb_title": "Clavier",
        "seq_switch": "Séquence",
        "seq_off": "Désactivé: simultané",
        "seq_on": "Activé: ordre 1 → 2 → 3 → 4 → 5",
        "empty_slot": "Vide (ignoré)",
        "unit_interval": "s intervalle",
        "unit_wait": "s attente après",
        "set_title": "Paramètres",
        "trigger_key": "Touche déclencheur",
        "work_mode": "Mode",
        "auto": "Auto",
        "manual": "Manuel",
        "delay_label": "Délai de démarrage (s)",
        "duration_label": "Arrêt auto (s, 0 = off)",
        "topmost_label": "Toujours au premier plan",
        "auto_hint": "Auto: appuyez une fois pour démarrer, à nouveau pour arrêter.",
        "manual_hint": "Manuel: fonctionne en maintanant la touche.",
        "start": "Démarrer",
        "stop": "Arrêter",
        "ready": "Prêt",
        "running": "En cours...",
        "total": "Total : ",
        "press_key": "Appuyez sur une touche…  (Esc = annuler)",
        "press_hotkey": "Appuyez sur une touche…",
        "err_stop": "Arrêtez d'abord la macro.",
        "err_same_key": "Impossible d'utiliser la touche déclencheur.",
        "err_not_found": "Touche non reconnue.",
        "help_close": "Fermer"
    },
    "ru": {
        "nav_mouse": "Мышь",
        "nav_kb": "Клавиатура",
        "nav_both": "Мышь + Клавиатура",
        "nav_guide": "Гид",
        "help_tip": "Нажмите ? или Гид,\nесли нужна помощь.",
        "mouse_title": "Мышь",
        "left_click": "ЛКМ",
        "right_click": "ПКМ",
        "middle_click": "СКМ",
        "spam": "Спам",
        "hold": "Удержание",
        "cps_unit": "кликов/сек",
        "kb_title": "Клавиатура",
        "seq_switch": "Порядок",
        "seq_off": "Выкл: одновременный запуск",
        "seq_on": "Вкл: порядок 1 → 2 → 3 → 4 → 5",
        "empty_slot": "Пусто (пропуск)",
        "unit_interval": "сек интервал",
        "unit_wait": "сек задержка",
        "set_title": "Настройки",
        "trigger_key": "Клавиша пуска",
        "work_mode": "Режим",
        "auto": "Авто",
        "manual": "Вручную",
        "delay_label": "Задержка старта (сек)",
        "duration_label": "Автостоп (сек, 0 = выкл)",
        "topmost_label": "Поверх окон",
        "auto_hint": "Авто: нажмите раз для старта, еще раз для стопа.",
        "manual_hint": "Вручную: работает пока зажата клавиша.",
        "start": "Старт",
        "stop": "Стоп",
        "ready": "Готово",
        "running": "Работает...",
        "total": "Всего: ",
        "press_key": "Нажмите клавишу…  (Esc = отмена)",
        "press_hotkey": "Нажмите клавишу…",
        "err_stop": "Сначала остановите макрос.",
        "err_same_key": "Нельзя использовать клавишу пуска.",
        "err_not_found": "Клавиша не распознана.",
        "help_close": "Закрыть"
    },
    "pt": {
        "nav_mouse": "Rato",
        "nav_kb": "Teclado",
        "nav_both": "Rato + Teclado",
        "nav_guide": "Guia",
        "help_tip": "Clique em ? ou Guia se\nprecisar de ajuda.",
        "mouse_title": "Rato",
        "left_click": "Clique esq.",
        "right_click": "Clique dir.",
        "middle_click": "Clique do meio",
        "spam": "Spam",
        "hold": "Segurar",
        "cps_unit": "cliques / seg",
        "kb_title": "Teclado",
        "seq_switch": "Sequência",
        "seq_off": "Desligado: simultâneo",
        "seq_on": "Ligado: ordem 1 → 2 → 3 → 4 → 5",
        "empty_slot": "Vazio (ignorado)",
        "unit_interval": "seg intervalo",
        "unit_wait": "seg espera",
        "set_title": "Definições",
        "trigger_key": "Tecla de gatilho",
        "work_mode": "Modo",
        "auto": "Auto",
        "manual": "Manual",
        "delay_label": "Atraso inicial (seg)",
        "duration_label": "Paragem auto (seg, 0 = off)",
        "topmost_label": "Sempre no topo",
        "auto_hint": "Auto: prima uma vez para iniciar, de novo para parar.",
        "manual_hint": "Manual: funciona enquanto mantiver premido.",
        "start": "Iniciar",
        "stop": "Parar",
        "ready": "Pronto",
        "running": "A executar...",
        "total": "Total: ",
        "press_key": "Prima uma tecla…  (Esc = cancelar)",
        "press_hotkey": "Prima uma tecla…",
        "err_stop": "Pare a macro primeiro.",
        "err_same_key": "Não pode usar a tecla de gatilho.",
        "err_not_found": "Tecla não reconhecida.",
        "help_close": "Fechar"
    }
}

# ----------------------------------------------------------------------------
# Kılavuz Metinleri (Tüm 7 dil için tam ve detaylı rehber içerikleri)
# ----------------------------------------------------------------------------
HELP = {
    "mouse": {
        "tr": """FARE

Kullanmak istediğin fare düğmesinin anahtarını aç: Sol tık, Sağ tık, Orta tekerlek. Kapalı olanlar çalışmaz. İstersen üçünü aynı anda açabilirsin.

Spam: Düğmeye saniyede yazdığın sayı kadar tıklar.
Basılı tut: Düğmeye basılı tutar, durdurunca bırakır. Hız kutusu pasif olur.

Hız (tık/sn): İstediğin sayıyı yaz, üst sınır yok. Ondalık da yazabilirsin (0,5 = 2 saniyede bir tık).

Önemli: Gerçek hız bilgisayarına ve açık programa bağlıdır. Çok yüksek değerler bilgisayarı yavaşlatabilir ve bazı oyunlar bu kadar hızlı girdiyi yok sayar. Durdurma tuşu her zaman çalışır.""",
        "en": """MOUSE

Turn on the switch of the mouse button you want to use: Left click, Right click, Middle click. Disabled ones won't work. You can turn on all three at once.

Spam: Clicks the button as many times per second as specified.
Hold: Holds the button down until stopped. Speed box becomes inactive.

Speed (clicks/sec): Type any number, no upper limit. You can also write decimals (0.5 = one click every 2 seconds).

Important: Actual speed depends on your computer and open program. Extremely high values may slow down your computer and some games ignore such fast inputs. The stop key always works.""",
        "de": """MAUS

Schalte den Schalter der gewünschten Maustaste ein: Linksklick, Rechtsklick, Mittelklick. Deaktivierte funktionieren nicht. Du kannst alle drei gleichzeitig aktivieren.

Spam: Klickt die Taste so oft pro Sekunde wie angegeben.
Halten: Hält die Taste gedrückt, bis gestoppt wird. Geschwindigkeitsfeld wird inaktiv.

Geschwindigkeit (Klicks/Sek): Gib eine beliebige Zahl ein, keine Obergrenze. Dezimalzahlen sind möglich (0.5 = ein Klick alle 2 Sekunden).

Wichtig: Die tatsächliche Geschwindigkeit hängt von Ihrem Computer und dem aktiven Programm ab. Extrem hohe Werte können Ihren PC verlangsamen.""",
        "es": """RATÓN

Activa el botón del ratón que quieras usar: Clic izq., Clic der., Clic medio. Los desactivados no funcionarán. Puedes activar los tres a la vez.

Spam: Hace clic tantas veces por segundo como se especifique.
Mantener: Mantiene presionado el botón hasta que se detenga.

Velocidad (clics/seg): Escribe cualquier número, sin límite superior. Puedes usar decimales (0.5 = un clic cada 2 segundos).

Importante: La velocidad real depende de tu ordenador y del programa abierto.""",
        "fr": """SOURIS

Activez le bouton de la souris souhaité: Clic gauche, Clic droit, Clic milieu. Ceux désactivés ne fonctionneront pas. Vous pouvez les activer tous les trois.

Spam: Clique autant de fois par seconde que spécifié.
Maintenir: Maintient le bouton enfoncé jusqu'à l'arrêt.

Vitesse (clics/sec): Tapez n'est pas limitée. Les décimales sont prises en charge (0.5 = un clic toutes les 2 secondes).

Important: La vitesse réelle dépend de votre ordinateur et du programme actif.""",
        "ru": """МЫШЬ

Включите нужную кнопку мыши: ЛКМ, ПКМ, СКМ. Отключенные не работают. Вы можете включить все три одновременно.

Спам: Кликает кнопку указанное количество раз в секунду.
Удержание: Удерживает кнопку до остановки.

Скорость (кликов/сек): Введите любое число, верхнего предела нет. Можно использовать десятичные дроби (0.5 = клик каждые 2 секунды).

Важно: Фактическая скорость зависит от вашего компьютера и активной программы.""",
        "pt": """RATO

Ligue o interruptor do botão do rato que deseja usar: Clique esq., Clique dir., Clique do meio. Os desativados não funcionam. Pode ligar os três de uma vez.

Spam: Clica o botão tantas vezes por segundo quanto especificado.
Segurar: Mantém o botão premido até parar.

Velocidade (cliques/seg): Digite qualquer número, sem limite superior. Pode usar decimais (0.5 = um clique a cada 2 segundos).

Importante: A velocidade real depende do seu computador e do programa aberto."""
    },
    "kb": {
        "tr": """KLAVYE

5 slot var. Slot düğmesine tıkla, sonra istediğin tuşa bas. Esc iptal eder. Kullanmayacağın slotu boş bırak, atlanır. Sağdaki X slotu temizler.

Spam: Tuşa belirlenen aralıkla tekrar tekrar basar.
Basılı tut: Tuşu basılı tutar, durdurunca bırakır.

Sırayla bas KAPALI (varsayılan): Her slot kendi aralığıyla ayrı çalışır, yani aynı anda basılabilir.
Sırayla bas AÇIK: Slotlar sırayla basılır: 1. slot, bekle, 2. slot, bekle, ... sonra başa döner. Bu durumda her slottaki sayı "o tuşa bastıktan sonra kaç saniye bekle" demektir. Basılı tut seçili slotlar sıraya girmez, hep basılı kalır.

Aralık saniye cinsindendir ve sınır yoktur (0,05 = saniyede 20 basış). Sırayla basma gerçekte yaklaşık saniyede 1000 basışa kadar çıkabilir.""",
        "en": """KEYBOARD

There are 5 slots. Click the slot button, then press the key you want. Esc cancels. Leave unused slots empty, they will be skipped. The X on the right clears the slot.

Spam: Presses the key repeatedly at the specified interval.
Hold: Holds the key down, releases when stopped.

Sequence OFF (default): Each slot works separately with its own interval, meaning they can be pressed at the same time.
Sequence ON: Slots are pressed in order: 1st slot, wait, 2nd slot, wait, ... then loops back to start. In this case, the number in each slot means "how many seconds to wait after pressing that key". Hold-selected slots do not enter the sequence, they stay held.

Interval is in seconds and there is no limit (0.05 = 20 presses per second). Sequence pressing can actually reach up to about 1000 presses per second.""",
        "de": """TASTATUR

Es gibt 5 Slots. Klicke auf einen Slot und drücke die gewünschte Taste. Esc bricht ab. Ungenutzte Slots leer lassen.

Spam: Drückt die Taste wiederholt im angegebenen Intervall.
Halten: Hält die Taste gedrückt.

Sequenz AUS (Standard): Jeder Slot arbeitet separat mit seinem eigenen Intervall.
Sequenz EIN: Slots werden nacheinander ausgeführt (1 → 2 → 3 → 4 → 5) und kehren dann zum Anfang zurück.

Intervall ist in Sekunden ohne Limit (0.05 = 20 Anschläge pro Sekunde).""",
        "es": """TECLADO

Hay 5 ranuras. Haz clic en el botón de la ranura y presiona la tecla que desees. Esc cancela. Deja las ranuras sin usar vacías.

Spam: Presiona la tecla repetidamente al intervalo especificado.
Mantener: Mantiene la tecla presionada.

Secuencia APAGADA (por defecto): Cada ranura funciona por separado.
Secuencia ENCENDIDA: Las ranuras se presionan en orden (1 al 5) y luego se repite.

El intervalo está en segundos sin límite (0.05 = 20 pulsaciones por segundo).""",
        "fr": """CLAVIER

Il y a 5 emplacements. Cliquez sur le bouton de l'emplacement et appuyez sur la touche souhaitée. Esc annule. Laissez les emplacements vides.

Spam: Appuie sur la touche à l'intervalle spécifié.
Maintenir: Maintient la touche enfoncée.

Séquence DÉSACTIVÉE (par défaut): Chaque emplacement fonctionne séparément.
Séquence ACTIVÉE: Les emplacements sont pressés dans l'ordre (1 à 5) puis bouclent.

L'intervalle est en secondes sans limite (0.05 = 20 pressions par seconde).""",
        "ru": """КЛАВИАТУРА

Есть 5 слотов. Нажмите на слот и выберите клавишу. Esc отменяет. Неиспользуемые слоты оставьте пустыми.

Спам: Нажимает клавишу с заданным интервалом.
Удержание: Удерживает клавишу.

Порядок ВЫКЛ (по умолчанию): Каждый слот работает отдельно.
Порядок ВКЛ: Слоты нажимаются по очереди (1 → 2 → 3 → 4 → 5), затем цикл повторяется.

Интервал в секундах без ограничений (0.05 = 20 нажатий в секунду).""",
        "pt": """TECLADO

Existem 5 slots. Clique no slot e prima a tecla pretendida. Esc cancela. Deixe os slots não utilizados vazios.

Spam: Prima a tecla repetidamente no intervalo especificado.
Segurar: Mantém a tecla premida.

Sequência DESLIGADA (padrão): Cada slot funciona separadamente.
Sequência LIGADA: Os slots são premidos por ordem (1 a 5) e depois repetem.

O intervalo é em segundos sem limite (0.05 = 20 pressões por segundo)."""
    },
    "set": {
        "tr": """AYARLAR

Tetik tuşu: Düğmeye tıkla, sonra istediğin tuşa bas (örneğin sol Alt, F6). Macro bu tuşla başlar ve durur. Slotlara atadığın tuşlardan biri olamaz.

Çalışma biçimi:
Oto: Tetik tuşuna bir kez bas, macro başlar. Tekrar bas, durur.
Manuel: Tetik tuşunu basılı tuttukça macro çalışır, bırakınca durur (gecikme uygulanmaz).

Başlama gecikmesi: Oto biçimde başladıktan kaç saniye sonra çalışmaya başlayacağını belirler. İmleci yerleştirmek için kullanışlıdır.

Otomatik durdur: Kaç saniye sonra kendiliğinden dursun. 0 = kapalı.

Hep üstte: Pencere diğer programların üstünde kalır.

Not: Sol Alt gibi bazı tuşlar programlarda menüyü açabilir. Sorun çıkarırsa Caps Lock veya F7 gibi başka bir tuş seç.""",
        "en": """SETTINGS

Trigger key: Click the button, then press the key you want (e.g., left Alt, F6). The macro starts and stops with this key. It cannot be one of the keys assigned to slots.

Working mode:
Auto: Press the trigger key once, the macro starts. Press again, it stops.
Manual: The macro runs as long as you hold the trigger key, stops when released (no delay applied).

Start delay: Determines how many seconds after starting in Auto mode it will begin running. Useful for placing the cursor.

Auto stop: Stops automatically after how many seconds. 0 = off.

Always on top: Window stays on top of other programs.

Note: Some keys like left Alt can open menus in programs. If it causes issues, choose another key like Caps Lock or F7.""",
        "de": """EINSTELLUNGEN

Auslöser: Klicke auf die Taste und drücke deine Wunschtaste (z.B. F6). Das Makro startet und stoppt damit.
Arbeitsmodus: Auto (Einmal drücken zum Starten/Stoppen) oder Manuell (Halten zum Ausführen).
Startverzögerung & Auto-Stopp ebenfalls einstellbar.
Immer im Vordergrund: Hält das Fenster im Blickfeld.""",
        "es": """AJUSTES

Tecla de activación: Haz clic y presiona la tecla deseada (ej. F6). El macro se inicia y se detiene con esta tecla.
Modo de trabajo: Auto o Manual.
Retraso inicial y parada automática disponibles.
Siempre visible: Mantiene la ventana por encima de otras aplicaciones.""",
        "fr": """PARAMÈTRES

Touche déclencheur: Cliquez et appuyez sur la touche souhaitée (ex. F6).
Mode de travail: Auto ou Manuel.
Délai de démarrage et arrêt auto disponibles.
Toujours au premier plan: Maintient la fenêtre au-dessus des autres.""",
        "ru": """НАСТРОЙКИ

Клавиша пуска: Нажмите кнопку и выберите клавишу (например, F6). Макрос запускается и останавливается ей.
Режим работы: Авто или Вручную.
Задержка старта и автостоп доступны.
Поверх окон: Окно остается поверх других приложений.""",
        "pt": """DEFINIÇÕES

Tecla de gatilho: Clique e prima a tecla pretendida (ex. F6). A macro inicia e para com esta tecla.
Modo de trabalho: Auto ou Manual.
Atraso inicial e paragem automática disponíveis.
Sempre no topo: A janela fica acima de outras aplicações."""
    },
    "all": {
        "tr": """ENDLESS MACRO KILAVUZU

HIZLI BAŞLANGIÇ
1. Soldan modu seç: Fare, Klavye veya Fare + Klavye.
2. Fare için kullanmak istediğin düğmeyi aç ve hızı yaz. Klavye için bir slota tıklayıp tuşa bas.
3. Ayarlar kartından tetik tuşunu seç (varsayılan F6) ve Oto veya Manuel biçimini belirle.
4. Tetik tuşuna ya da alttaki Başlat düğmesine bas. Durdurmak için tekrar bas.

FARE
Sol, sağ ve orta düğmeyi ayrı ayrı açıp kapatabilirsin. Spam seçersen saniyede yazdığın kadar tıklar, Basılı tut seçersen düğmeyi basılı tutar. Hız sınırı yoktur, istediğin sayıyı yazabilirsin.

KLAVYE
5 slotun her birine tuş ata, kullanmadıklarını boş bırak. Spam veya Basılı tut seç, aralığı saniye olarak yaz. "Sırayla bas" anahtarını açarsan slotlar aynı anda değil, 1-2-3-4-5 sırasıyla basılır ve aralık kutusu "sonra bekle" anlamına gelir.

AYARLAR
Tetik tuşu: istediğin tuşu seç. Oto: bir bas başlasın, bir daha bas dursun. Manuel: basılı tuttukça çalışsın, bırakınca durur. Başlama gecikmesi, Otomatik durdur ve Hep üstte seçenekleri de burada.

İPUÇLARI VE SORUN GİDERME
- Macro kullandığın oyun veya program yönetici olarak çalışıyorsa, Endless Macro'yu da sağ tık ile "Yönetici olarak çalıştır" diyerek aç.
- Çok yüksek hızlarda bilgisayar yavaşlayabilir. Önce düşük bir değerle dene, sonra artır. Durdurma tuşu her zaman çalışır.
- Bazı oyunların hile korumaları macro programlarını engelleyebilir. Kullanım sorumluluğu sana aittir.
- Windows "Bilgisayarınızı korudu" derse "Ek bilgi" ve "Yine de çalıştır" seç. Bazı antivirüsler fare ve klavye dinleyen programlara yanlış uyarı verebilir.
- Ayarlar otomatik kaydedilir (%APPDATA%\\EndlessMacro klasörü).""",
        "en": """ENDLESS MACRO GUIDE

QUICK START
1. Select mode from the left: Mouse, Keyboard, or Mouse + Keyboard.
2. Turn on the switch of the mouse button you want to use and type the speed. Click a slot for Keyboard and press a key.
3. Select the trigger key from the Settings card (default F6) and set Auto or Manual mode.
4. Press the trigger key or the Start button below. Press again to stop.

MOUSE
You can turn the left, right, and middle buttons on and off individually. If you select Spam, it clicks as many times per second as you type; if you select Hold, it holds the button down. There is no speed limit, you can write any number you want.

KEYBOARD
Assign a key to each of the 5 slots, leave unused ones blank. Choose Spam or Hold, type the interval in seconds. If you turn on the "Sequence" switch, the slots are pressed in 1-2-3-4-5 order instead of simultaneously, and the interval box means "wait after".

SETTINGS
Trigger key: select the key you want. Auto: press once to start, press again to stop. Manual: runs while held, stops when released. Start delay, Auto stop, and Always on top options are also here.

TIPS AND TROUBLESHOOTING
- If the game or program you are using macros in runs as administrator, run Endless Macro as "Run as administrator" by right-clicking.
- Computers may slow down at very high speeds. Try a low value first, then increase. The stop key always works.
- Some games' anti-cheat systems may block macro programs. Usage responsibility belongs to you.
- If Windows says "Windows protected your PC", select "More info" and "Run anyway". Some antiviruses may give false warnings to programs listening to mouse and keyboard.
- Settings are saved automatically (%APPDATA%\\EndlessMacro folder).""",
        "de": """ENDLESS MACRO ANLEITUNG

SCHNELLSTART
1. Wähle links den Modus: Maus, Tastatur oder Maus + Tastatur.
2. Aktiviere die gewünschte Maustaste oder weise Tastatur-Slots zu.
3. Wähle den Auslöser (Standard F6) und den Modus (Auto/Manuell).
4. Drücke die Auslösertaste oder den Start-Button.

MAUS & TASTATUR
Du kannst alle Maustasten individuell konfigurieren. Für die Tastatur stehen 5 Slots zur Verfügung, die auch im Sequenzmodus (1 → 5) nacheinander ausgeführt werden können.

TIPPS UND FEHLERBEHEBUNG
- Als Administrator ausführen, falls das Spiel Administratorrechte erfordert.
- Zu hohe Geschwindigkeiten können die CPU belasten.""",
        "es": """GUÍA DE ENDLESS MACRO

INICIO RÁPIDO
1. Selecciona el modo a la izquierda: Ratón, Teclado o Ratón + Teclado.
2. Activa los botones del ratón o asigna las ranuras del teclado.
3. Elige la tecla de activación y el modo (Auto/Manual).
4. Presiona la tecla de activación o el botón Iniciar.

RATÓN Y TECLADO
Puedes configurar los botones del ratón individualmente y usar hasta 5 ranuras en el teclado con opción de secuencia.

CONSEJOS Y SOLUCIÓN DE PROBLEMAS
- Ejecuta como administrador si tu juego lo requiere.
- Comienza con valores de velocidad bajos.""",
        "fr": """GUIDE ENDLESS MACRO

GUIDE DE DÉMARRAGE RAPIDE
1. Sélectionnez le mode à gauche: Souris, Clavier ou Souris + Clavier.
2. Activez les boutons de la souris ou assignez les touches du clavier.
3. Choisissez la touche déclencheur et le mode (Auto/Manuel).
4. Appuyez sur la touche déclencheur ou sur le bouton Démarrer.

SOURIS & CLAVIER
Configurez individuellement les boutons de la souris et utilisez 5 emplacements pour le clavier avec mode séquentiel.

CONSEILS ET DÉPANNAGE
- Exécutez en tant qu'administrateur si votre jeu le nécessite.""",
        "ru": """РУКОВОДСТВО ENDLESS MACRO

БЫСТРЫЙ СТАРТ
1. Выберите режим слева: Мышь, Клавиатура или Мышь + Клавиатура.
2. Включите нужные кнопки мыши или назначьте слоты клавиатуры.
3. Выберите клавишу пуска и режим (Авто/Вручную).
4. Нажмите клавишу пуска или кнопку Старт.

МЫШЬ И КЛАВИАТУРА
Настраивайте кнопки мыши и используйте 5 слотов клавиатуры с возможностью последовательного запуска.

СОВЕТЫ И УСТРАНЕНИЕ НЕПОЛАДОК
- Запускайте от имени администратора, если игра требует.""",
        "pt": """GUIA DO ENDLESS MACRO

INÍCIO RÁPIDO
1. Selecione o modo à esquerda: Rato, Teclado ou Rato + Teclado.
2. Ative os botões do rato ou atribua slots do teclado.
3. Escolha a tecla de gatilho e o modo (Auto/Manual).
4. Prima a tecla de gatilho ou o botão Iniciar.

RATO E TECLADO
Configure individualmente os botões do rato e utilize 5 slots no teclado com opção de sequência.

DICAS E RESOLUÇÃO DE PROBLEMAS
- Execute como administrador, caso o seu jogo o exija."""
    }
}


def _config_dir():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    d = os.path.join(base, "EndlessMacro")
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        pass
    return d


def resource_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


CONFIG_PATH = os.path.join(_config_dir(), "ayarlar.json")

TICK = 0.002
MIN_CPS = 0.001
MIN_INTERVAL = 0.0001

GRAD_TOP = (8, 30, 56)
GRAD_BOTTOM = (10, 68, 98)
CARD = "#0c3150"
CARD_BORDER = "#25688f"
INPUT_BG = "#082a42"
INPUT_BORDER = "#1f6a90"
NAV_HOVER = "#12466b"
ACCENT = "#2dd4e6"
ACCENT_HOVER = "#1ab3c4"
TEXT = "#e8f8ff"
MUTED = "#8fbdd1"
DANGER = "#ff6b7a"
FONT = "Segoe UI"

WIN_W, WIN_H = 1120, 720
PAD, GAP = 14, 12
SIDEBAR_W = 220
CONTENT_X = PAD + SIDEBAR_W + GAP
CONTENT_W = WIN_W - CONTENT_X - PAD
H_MOUSE, H_KB, H_SET, H_BOTTOM = 164, 246, 156, 84


def grad_rgb(y):
    t = max(0.0, min(1.0, y / (WIN_H - 1)))
    return tuple(int(GRAD_TOP[i] + (GRAD_BOTTOM[i] - GRAD_TOP[i]) * t) for i in range(3))


def grad_hex(y):
    r, g, b = grad_rgb(y)
    return f"#{r:02x}{g:02x}{b:02x}"


def make_background(w, h):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=grad_rgb(y))

    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for cx, cy, r, col in [(110, h - 90, 120, (0, 95, 125)), (w + 60, 110, 150, (0, 105, 135)),
                           (w // 2, h + 70, 260, (0, 120, 150)), (-40, 120, 110, (0, 85, 115))]:
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    glow = glow.filter(ImageFilter.GaussianBlur(55))
    img = ImageChops.screen(img, glow).convert("RGBA")

    waves = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    wd = ImageDraw.Draw(waves)
    for k, (amp, base, alpha) in enumerate([(14, h - 60, 30), (16, h - 36, 45), (12, h - 12, 60)]):
        pts = [(x, base + amp * math.sin((x / w) * math.pi * 5 + k * 1.3)) for x in range(0, w + 8, 8)]
        wd.polygon(pts + [(w, h), (0, h)], fill=(120, 220, 240, alpha))
    waves = waves.filter(ImageFilter.GaussianBlur(4))
    return Image.alpha_composite(img, waves).convert("RGB").filter(ImageFilter.GaussianBlur(1.2))


def key_to_str(k):
    if isinstance(k, keyboard.Key):
        return "Key." + k.name
    if isinstance(k, keyboard.KeyCode):
        if k.char:
            return k.char.lower()
        if k.vk is not None:
            return f"vk:{k.vk}"
    return None


def str_to_key(s):
    if not s:
        return None
    if s.startswith("Key."):
        return getattr(keyboard.Key, s[4:], None)
    if s.startswith("vk:"):
        return keyboard.KeyCode.from_vk(int(s[3:]))
    if len(s) == 1:
        return keyboard.KeyCode.from_char(s)
    return None


def pretty(s):
    if not s:
        return ""
    if s.startswith("Key."):
        return s[4:].upper().replace("_", " ")
    if s.startswith("vk:"):
        return f"VK {s[3:]}"
    return s.upper()


def to_num(text, default):
    try:
        v = float(str(text).strip().replace(",", "."))
        return v if math.isfinite(v) else default
    except ValueError:
        return default


@dataclass
class Task:
    kind: str
    target: object
    hold: bool
    interval: float
    eff: float = field(init=False, default=0.0)
    burst: int = field(init=False, default=1)
    nxt: float = field(init=False, default=0.0)

    def __post_init__(self):
        self.eff = max(self.interval, TICK)
        self.burst = max(1, round(self.eff / self.interval))


class Runner:
    def __init__(self, on_finish):
        self.mouse = mouse.Controller()
        self.kb = keyboard.Controller()
        self.on_finish = on_finish
        self.stop_evt = threading.Event()
        self.thread = None
        self.running = False
        self.phase = "idle"
        self.count = 0

    def start(self, tasks, delay, duration):
        self.stop_evt.clear()
        self.running = True
        self.phase = "delay" if delay > 0 else "run"
        self.count = 0
        self.thread = threading.Thread(target=self._run, args=(tasks, delay, duration), daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_evt.set()

    def _tap(self, key):
        try:
            self.kb.press(key)
            self.kb.release(key)
            self.count += 1
        except Exception:
            pass

    def _fire(self, t):
        try:
            left = t.burst
            while left > 0 and not self.stop_evt.is_set():
                n = min(left, 200)
                if t.kind == "mouse":
                    self.mouse.click(t.target, n)
                else:
                    for _ in range(n):
                        self.kb.press(t.target)
                        self.kb.release(t.target)
                left -= n
                self.count += n
        except Exception:
            pass

    def _hold(self, t, down):
        try:
            ctl = self.mouse if t.kind == "mouse" else self.kb
            (ctl.press if down else ctl.release)(t.target)
        except Exception:
            pass

    def _run(self, tasks, delay, duration):
        held = [t for t in tasks if t.hold]
        spam = [t for t in tasks if not t.hold]
        try:
            if delay > 0 and self.stop_evt.wait(delay):
                return
            self.phase = "run"
            for t in held:
                self._hold(t, True)
            t0 = time.perf_counter()
            for t in spam:
                t.nxt = t0
            while not self.stop_evt.is_set():
                now = time.perf_counter()
                if duration and now - t0 >= duration:
                    break
                nearest = now + 0.05
                for t in spam:
                    if now >= t.nxt:
                        if t.kind == "seq":
                            key, wait = t.steps[t.idx]
                            self._tap(key)
                            t.idx = (t.idx + 1) % len(t.steps)
                            t.nxt += wait
                            if now - t.nxt > 0.25:
                                t.nxt = now + wait
                        else:
                            self._fire(t)
                            t.nxt += t.eff
                            if now - t.nxt > 0.25:
                                t.nxt = now + t.eff
                    nearest = min(nearest, t.nxt)
                wait = nearest - time.perf_counter()
                if wait > 0:
                    self.stop_evt.wait(wait)
                else:
                    time.sleep(0)
        finally:
            for t in held:
                self._hold(t, False)
            self.running = False
            self.phase = "idle"
            self.on_finish()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)

        self.lang = "tr"  # Varsayılan dil Türkçe
        self.events = queue.Queue()
        self.capture_cb = None
        self.hotkey = "Key.f6"
        self.slot_keys = [""] * 5
        self._hotkey_down = False
        self.help_win = None
        self.runner = Runner(on_finish=lambda: self.events.put(("finished",)))

        bg = make_background(WIN_W, WIN_H)
        self.bg_img = ctk.CTkImage(light_image=bg, dark_image=bg, size=(WIN_W, WIN_H))
        ctk.CTkLabel(self, image=self.bg_img, text="").place(x=0, y=0)

        self._build_vars()
        self._build_sidebar()
        self._build_mouse_card()
        self._build_keyboard_card()
        self._build_settings_card()
        self._build_bottom()

        self.refresh_all()
        self.set_mode("Fare")

        self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self.listener.daemon = True
        self.listener.start()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(250, lambda: self._set_icon(self))
        self.after(30, self.poll)

    def _set_icon(self, win):
        try:
            win.iconbitmap(resource_path("icon.ico"))
        except Exception:
            pass

    def _build_vars(self):
        self.mode_var = ctk.StringVar(value="Fare")
        self.m = {n: {"on": ctk.BooleanVar(value=(n == "left")), "mode": ctk.StringVar(value="Spam"),
                      "cps": ctk.StringVar(value="10")} for n in ("left", "right", "middle")}
        self.k_mode = [ctk.StringVar(value="Spam") for _ in range(5)]
        self.k_interval = [ctk.StringVar(value="0.1") for _ in range(5)]
        self.seq_var = ctk.BooleanVar(value=False)
        self.kb_unit = ctk.StringVar(value="sn aralık")
        self.delay_var = ctk.StringVar(value="3")
        self.duration_var = ctk.StringVar(value="0")
        self.topmost_var = ctk.BooleanVar(value=False)
        self.trigger_mode = ctk.StringVar(value="Oto")

    def _card(self, w, h):
        f = ctk.CTkFrame(self, width=w, height=h, corner_radius=22, fg_color=CARD,
                         border_width=1, border_color=CARD_BORDER)
        f.grid_propagate(False)
        return f

    def _entry(self, parent, var, width=84):
        return ctk.CTkEntry(parent, textvariable=var, width=width, height=30, corner_radius=12,
                            fg_color=INPUT_BG, border_color=INPUT_BORDER, text_color=TEXT,
                            justify="center", font=(FONT, 13))

    def _segment(self, parent, var, values, command=None, width=190):
        return ctk.CTkSegmentedButton(
            parent, values=values, variable=var, command=command, width=width, height=30,
            corner_radius=12, fg_color=INPUT_BG, selected_color=ACCENT, selected_hover_color=ACCENT_HOVER,
            unselected_color=INPUT_BG, unselected_hover_color=NAV_HOVER, text_color=TEXT,
            font=(FONT, 12, "bold"))

    def _button(self, parent, text, command, width=130, height=30):
        return ctk.CTkButton(parent, text=text, command=command, width=width, height=height, corner_radius=12,
                             fg_color=INPUT_BG, hover_color=NAV_HOVER, border_width=1,
                             border_color=INPUT_BORDER, text_color=TEXT, font=(FONT, 13))

    def _switch(self, parent, text, var, command=None, width=150):
        return ctk.CTkSwitch(parent, text=text, variable=var, command=command, width=width,
                             progress_color=ACCENT, button_color="#d8f6ff", button_hover_color="#ffffff",
                             fg_color=INPUT_BG, text_color=TEXT, font=(FONT, 13))

    def _title(self, parent, text_key):
        lbl = ctk.CTkLabel(parent, text=LANG[self.lang][text_key], font=(FONT, 16, "bold"), text_color=TEXT)
        lbl.grid(row=0, column=0, columnspan=6, sticky="w", padx=20, pady=(12, 4))
        return lbl

    def _help_btn(self, card, key):
        ctk.CTkButton(card, text="?", width=30, height=30, corner_radius=15, fg_color=INPUT_BG,
                      hover_color=NAV_HOVER, border_width=1, border_color=INPUT_BORDER, text_color=ACCENT,
                      font=(FONT, 14, "bold"), command=lambda: self.show_help(key)
                      ).place(x=CONTENT_W - 46, y=10)

    def _build_sidebar(self):
        self.brand = self._card(SIDEBAR_W, 92)
        try:
            ico = Image.open(resource_path("icon.ico")).convert("RGBA")
            self.logo = ctk.CTkImage(ico, size=(44, 44))
            ctk.CTkLabel(self.brand, image=self.logo, text="").place(x=12, y=24)
        except Exception:
            pass
        
        ctk.CTkLabel(self.brand, text="Endless", font=(FONT, 18, "bold"), text_color=TEXT).place(x=62, y=18)
        ctk.CTkLabel(self.brand, text="MACRO", font=(FONT, 11, "bold"), text_color=ACCENT).place(x=64, y=42)

        self.nav = self._card(SIDEBAR_W, 200)
        self.nav_title = ctk.CTkLabel(self.nav, text="MOD", font=(FONT, 12, "bold"), text_color=MUTED)
        self.nav_title.place(x=22, y=14)
        
        self.nav_buttons = {}
        self.nav_keys = [("Fare", "nav_mouse"), ("Klavye", "nav_kb"), ("Fare + Klavye", "nav_both")]
        for i, (name, _) in enumerate(self.nav_keys):
            b = ctk.CTkButton(self.nav, text=name, width=SIDEBAR_W - 32, height=44, corner_radius=14, anchor="w",
                              font=(FONT, 14, "bold"), fg_color="transparent", hover_color=NAV_HOVER,
                              text_color=TEXT, command=lambda n=name: self.set_mode(n))
            b.place(x=16, y=40 + i * 50)
            self.nav_buttons[name] = b

        # Dil Seçim Kartı (OptionMenu)
        self.lang_card = self._card(SIDEBAR_W, 90)
        self.lang_title = ctk.CTkLabel(self.lang_card, text="DİL / LANGUAGE", font=(FONT, 11, "bold"), text_color=MUTED)
        self.lang_title.place(x=22, y=12)

        self.lang_menu = ctk.CTkOptionMenu(
            self.lang_card, values=["Türkçe (TR)", "English (EN)", "Deutsch (DE)", "Español (ES)", "Français (FR)", "Русский (RU)", "Português (PT)"],
            width=SIDEBAR_W - 32, height=36, corner_radius=12,
            fg_color=INPUT_BG, button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            dropdown_fg_color=CARD, dropdown_text_color=TEXT, dropdown_hover_color=NAV_HOVER,
            text_color=TEXT, font=(FONT, 12, "bold"), command=self.change_language_dropdown
        )
        self.lang_menu.set("Türkçe (TR)")
        self.lang_menu.place(x=16, y=38)

        self.helpcard = self._card(SIDEBAR_W, 124)
        self.guide_btn = ctk.CTkButton(self.helpcard, text="Kılavuz", width=SIDEBAR_W - 32, height=44, corner_radius=14,
                                       font=(FONT, 14, "bold"), fg_color=INPUT_BG, hover_color=NAV_HOVER, border_width=1,
                                       border_color=INPUT_BORDER, text_color=ACCENT,
                                       command=lambda: self.show_help("all"))
        self.guide_btn.place(x=16, y=16)
        
        self.help_lbl = ctk.CTkLabel(self.helpcard, text="", justify="left", font=(FONT, 11), text_color=MUTED)
        self.help_lbl.place(x=18, y=66)

        y = PAD
        sidebar_items = ((self.brand, 92), (self.nav, 200), (self.lang_card, 90), (self.helpcard, 124))
        for card, h in sidebar_items:
            card.configure(bg_color=grad_hex(y + h / 2))
            card.place(x=PAD, y=y)
            y += h + GAP

    def change_language_dropdown(self, val):
        mapping = {
            "Türkçe (TR)": "tr",
            "English (EN)": "en",
            "Deutsch (DE)": "de",
            "Español (ES)": "es",
            "Français (FR)": "fr",
            "Русский (RU)": "ru",
            "Português (PT)": "pt"
        }
        self.lang = mapping.get(val, "tr")
        t = LANG[self.lang]

        self.nav_title.configure(text="MODE" if self.lang == "en" else ("MOD" if self.lang in ["tr", "de", "es", "fr", "pt"] else "РЕЖИМ"))
        for name, key in self.nav_keys:
            self.nav_buttons[name].configure(text=t[key])
        self.guide_btn.configure(text=t["nav_guide"])
        self.help_lbl.configure(text=t["help_tip"])

        self.refresh_all()

    def _build_mouse_card(self):
        self.mouse_card = self._card(CONTENT_W, H_MOUSE)
        self.mouse_title_lbl = self._title(self.mouse_card, "mouse_title")
        self._help_btn(self.mouse_card, "mouse")
        self.mouse_card.grid_columnconfigure(0, minsize=180)
        self.mouse_entries = {}
        self.mouse_switches = {}
        
        items = (("left", "left_click"), ("right", "right_click"), ("middle", "middle_click"))
        for i, (name, l_key) in enumerate(items):
            v = self.m[name]
            sw = self._switch(self.mouse_card, LANG[self.lang][l_key], v["on"])
            sw.grid(row=i + 1, column=0, sticky="w", padx=(20, 8), pady=3)
            self.mouse_switches[name] = (sw, l_key)
            
            seg = self._segment(self.mouse_card, v["mode"], ["Spam", "Hold"], command=lambda _v: self.refresh_all())
            seg.grid(row=i + 1, column=1, padx=8, pady=3)
            
            e = self._entry(self.mouse_card, v["cps"])
            e.grid(row=i + 1, column=2, padx=(18, 6), pady=3)
            self.mouse_entries[name] = e
            
            ctk.CTkLabel(self.mouse_card, text=LANG[self.lang]["cps_unit"], text_color=MUTED, font=(FONT, 13)).grid(
                row=i + 1, column=3, sticky="w", padx=4)

    def _build_keyboard_card(self):
        self.kb_card = self._card(CONTENT_W, H_KB)
        self.kb_title_lbl = self._title(self.kb_card, "kb_title")
        self._help_btn(self.kb_card, "kb")
        
        self.seq_switch_widget = ctk.CTkSwitch(self.kb_card, text="", variable=self.seq_var, command=self.refresh_all, width=46,
                                              progress_color=ACCENT, button_color="#d8f6ff", button_hover_color="#ffffff",
                                              fg_color=INPUT_BG)
        self.seq_switch_widget.place(x=125, y=14)
        
        self.seq_text_lbl = ctk.CTkLabel(self.kb_card, text="", font=(FONT, 13, "bold"), text_color=TEXT)
        self.seq_text_lbl.place(x=183, y=13)
        
        self.seq_hint = ctk.CTkLabel(self.kb_card, text="", font=(FONT, 12), text_color=ACCENT)
        self.seq_hint.place(x=290, y=14)
        
        self.kb_card.grid_columnconfigure(0, minsize=70)
        self.key_buttons, self.k_entries, self.kb_unit_labels = [], [], []
        
        for i in range(5):
            r = i + 1
            ctk.CTkLabel(self.kb_card, text=f"Slot {i + 1}", text_color=MUTED, font=(FONT, 13)).grid(
                row=r, column=0, sticky="w", padx=(20, 4), pady=3)
            
            b = self._button(self.kb_card, LANG[self.lang]["empty_slot"], lambda i=i: self.capture_slot(i), width=190)
            b.grid(row=r, column=1, padx=8, pady=3)
            self.key_buttons.append(b)
            
            self._segment(self.kb_card, self.k_mode[i], ["Spam", "Hold"], command=lambda _v: self.refresh_all()).grid(
                row=r, column=2, padx=8, pady=3)
            
            e = self._entry(self.kb_card, self.k_interval[i])
            e.grid(row=r, column=3, padx=(18, 6), pady=3)
            self.k_entries.append(e)
            
            unit_l = ctk.CTkLabel(self.kb_card, textvariable=self.kb_unit, text_color=MUTED, font=(FONT, 13), width=110, anchor="w")
            unit_l.grid(row=r, column=4, sticky="w", padx=4)
            self.kb_unit_labels.append(unit_l)
            
            self._button(self.kb_card, "✕", lambda i=i: self.clear_slot(i), width=34).grid(
                row=r, column=5, padx=(10, 6), pady=3)

    def _build_settings_card(self):
        self.set_card = self._card(CONTENT_W, H_SET)
        self.set_title_lbl = self._title(self.set_card, "set_title")
        self._help_btn(self.set_card, "set")
        
        lab = lambda t: ctk.CTkLabel(self.set_card, text=t, text_color=MUTED, font=(FONT, 13))

        self.l_trig = lab("Tetik tuşu")
        self.l_trig.grid(row=1, column=0, sticky="w", padx=(20, 8), pady=3)
        
        self.hotkey_btn = self._button(self.set_card, "F6", self.capture_hotkey, width=150)
        self.hotkey_btn.grid(row=1, column=1, padx=6, pady=3)
        
        self.l_mode = lab("Çalışma biçimi")
        self.l_mode.grid(row=1, column=2, sticky="w", padx=(30, 8), pady=3)
        
        self.trigger_seg = self._segment(self.set_card, self.trigger_mode, ["Oto", "Manuel"], command=lambda _v: self.refresh_all(), width=170)
        self.trigger_seg.grid(row=1, column=3, columnspan=2, sticky="w", padx=6, pady=3)

        self.l_delay = lab("Başlama gecikmesi (sn)")
        self.l_delay.grid(row=2, column=0, sticky="w", padx=(20, 8), pady=3)
        self._entry(self.set_card, self.delay_var, width=80).grid(row=2, column=1, padx=6, pady=3)
        
        self.l_dur = lab("Otomatik durdur (sn, 0 = kapalı)")
        self.l_dur.grid(row=2, column=2, sticky="w", padx=(30, 8), pady=3)
        self._entry(self.set_card, self.duration_var, width=80).grid(row=2, column=3, sticky="w", padx=6, pady=3)
        
        self.topmost_switch = self._switch(self.set_card, "Hep üstte", self.topmost_var, command=self.apply_topmost, width=110)
        self.topmost_switch.grid(row=2, column=4, sticky="w", padx=(20, 6), pady=3)

        self.mode_hint = ctk.CTkLabel(self.set_card, text="", text_color=ACCENT, font=(FONT, 12), anchor="w")
        self.mode_hint.grid(row=3, column=0, columnspan=6, sticky="w", padx=20, pady=(2, 0))

    def _build_bottom(self):
        self.bottom = self._card(CONTENT_W, H_BOTTOM)
        self.start_btn = ctk.CTkButton(self.bottom, text="Başlat", command=self.toggle, width=250, height=50,
                                       corner_radius=20, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                                       text_color="#04283a", font=(FONT, 18, "bold"))
        self.start_btn.place(x=18, y=17)
        
        self.status = ctk.CTkLabel(self.bottom, text="Hazır", text_color=TEXT, font=(FONT, 15, "bold"), anchor="w")
        self.status.place(x=296, y=16)
        
        self.counter = ctk.CTkLabel(self.bottom, text="Toplam: 0", text_color=MUTED, font=(FONT, 13), anchor="w")
        self.counter.place(x=296, y=46)
        
        y = WIN_H - PAD - H_BOTTOM
        self.bottom.configure(bg_color=grad_hex(y + H_BOTTOM / 2))
        self.bottom.place(x=CONTENT_X, y=y)

    def set_mode(self, mode):
        self.mode_var.set(mode)
        for name, b in self.nav_buttons.items():
            if name == mode:
                b.configure(fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#04283a")
            else:
                b.configure(fg_color="transparent", hover_color=NAV_HOVER, text_color=TEXT)
        show_mouse = mode in ("Fare", "Fare + Klavye")
        show_kb = mode in ("Klavye", "Fare + Klavye")
        y = PAD
        for card, h, visible in ((self.mouse_card, H_MOUSE, show_mouse), (self.kb_card, H_KB, show_kb),
                                 (self.set_card, H_SET, True)):
            if not visible:
                card.place_forget()
                continue
            card.configure(bg_color=grad_hex(y + h / 2))
            card.place(x=CONTENT_X, y=y)
            y += h + GAP

    def refresh_all(self):
        t = LANG[self.lang]
        
        self.help_lbl.configure(text=t["help_tip"])
        self.seq_text_lbl.configure(text=t["seq_switch"])
        self.l_trig.configure(text=t["trigger_key"])
        self.l_mode.configure(text=t["work_mode"])
        self.l_delay.configure(text=t["delay_label"])
        self.l_dur.configure(text=t["duration_label"])
        self.topmost_switch.configure(text=t["topmost_label"])

        for name, (sw, l_key) in self.mouse_switches.items():
            sw.configure(text=t[l_key])

        for name, e in self.mouse_entries.items():
            e.configure(state="disabled" if self.m[name]["mode"].get() == "Hold" else "normal")
            
        for i in range(5):
            self.k_entries[i].configure(state="disabled" if self.k_mode[i].get() == "Hold" else "normal")
            txt = pretty(self.slot_keys[i]) if self.slot_keys[i] else t["empty_slot"]
            self.key_buttons[i].configure(text=txt)

        self.kb_unit.set(t["unit_wait"] if self.seq_var.get() else t["unit_interval"])
        if self.seq_var.get():
            self.seq_hint.configure(text=t["seq_on"], text_color=ACCENT)
        else:
            self.seq_hint.configure(text=t["seq_off"], text_color=MUTED)

        self.hotkey_btn.configure(text=pretty(self.hotkey))
        
        if not self.runner.running:
            self.start_btn.configure(text=f"{t['start']}  ({pretty(self.hotkey)})")
            
        if self.trigger_mode.get() == "Manuel":
            self.mode_hint.configure(text=t["manual_hint"])
        else:
            self.mode_hint.configure(text=t["auto_hint"])

    def apply_topmost(self):
        self.attributes("-topmost", bool(self.topmost_var.get()))

    def show_help(self, key):
        t = LANG[self.lang]
        if self.help_win is not None and self.help_win.winfo_exists():
            self.help_win.destroy()
        w = ctk.CTkToplevel(self)
        w.title(f"{APP_NAME} - {t['nav_guide']}")
        w.geometry("580x560")
        w.configure(fg_color="#08243c")
        w.attributes("-topmost", True)
        
        box = ctk.CTkTextbox(w, fg_color=CARD, text_color=TEXT, corner_radius=18, font=(FONT, 14), wrap="word",
                             border_width=1, border_color=CARD_BORDER)
        box.pack(fill="both", expand=True, padx=16, pady=(16, 8))
        box.insert("1.0", HELP[key][self.lang] if self.lang in HELP[key] else HELP[key]["en"])
        box.configure(state="disabled")
        
        ctk.CTkButton(w, text=t["help_close"], width=140, height=36, corner_radius=14, fg_color=ACCENT,
                      hover_color=ACCENT_HOVER, text_color="#04283a", font=(FONT, 14, "bold"),
                      command=w.destroy).pack(pady=(0, 14))
        self.help_win = w
        w.after(250, lambda: self._set_icon(w))

    def capture_slot(self, i):
        t = LANG[self.lang]
        if self.runner.running:
            self.set_status(t["err_stop"], DANGER)
            return
        self.key_buttons[i].configure(text=t["press_key"])

        def done(s):
            if s is not None:
                self.slot_keys[i] = s
            self.refresh_all()

        self.capture_cb = done

    def clear_slot(self, i):
        self.slot_keys[i] = ""
        self.refresh_all()

    def capture_hotkey(self):
        t = LANG[self.lang]
        if self.runner.running:
            self.set_status(t["err_stop"], DANGER)
            return
        self.hotkey_btn.configure(text=t["press_hotkey"])

        def done(s):
            if s is not None:
                self.hotkey = s
            self.refresh_all()

        self.capture_cb = done

    def _on_press(self, key):
        s = key_to_str(key)
        if s is None:
            return
        if self.capture_cb is not None:
            cb, self.capture_cb = self.capture_cb, None
            self.events.put(("capture", cb, None if s == "Key.esc" else s))
            return
        if s == self.hotkey and not self._hotkey_down:
            self._hotkey_down = True
            self.events.put(("hotkey_down",))

    def _on_release(self, key):
        if key_to_str(key) == self.hotkey:
            self._hotkey_down = False
            self.events.put(("hotkey_up",))

    def build_tasks(self):
        t = LANG[self.lang]
        mode = self.mode_var.get()
        tasks = []
        if mode in ("Fare", "Fare + Klavye"):
            for name, btn in (("left", mouse.Button.left), ("right", mouse.Button.right),
                              ("middle", mouse.Button.middle)):
                v = self.m[name]
                if not v["on"].get():
                    continue
                cps = max(to_num(v["cps"].get(), 10), MIN_CPS)
                v["cps"].set(f"{cps:g}")
                tasks.append(Task("mouse", btn, v["mode"].get() == "Hold", 1.0 / cps))
                
        if mode in ("Klavye", "Fare + Klavye"):
            steps = []
            for i in range(5):
                s = self.slot_keys[i]
                if not s:
                    continue
                if s == self.hotkey:
                    raise ValueError(t["err_same_key"])
                key = str_to_key(s)
                if key is None:
                    raise ValueError(t["err_not_found"])
                iv = max(to_num(self.k_interval[i].get(), 0.1), 0.0)
                self.k_interval[i].set(f"{iv:g}")
                if self.k_mode[i].get() == "Hold":
                    tasks.append(Task("key", key, True, 1.0))
                elif self.seq_var.get():
                    steps.append((key, iv))
                else:
                    tasks.append(Task("key", key, False, max(iv, MIN_INTERVAL)))
                    
            if steps:
                tasks.append(Task("seq", steps, False, 0.0))
        return tasks

    def set_status(self, text, color=TEXT):
        self.status.configure(text=text, text_color=color)

    def toggle(self):
        t = LANG[self.lang]
        if self.runner.running:
            self.runner.stop()
            self.start_btn.configure(text=f"{t['start']}  ({pretty(self.hotkey)})", fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#04283a")
            self.set_status(t["ready"])
        else:
            try:
                tasks = self.build_tasks()
            except ValueError as e:
                self.set_status(str(e), DANGER)
                return
            if not tasks:
                self.set_status("Hiçbir görev seçilmedi." if self.lang == "tr" else "No tasks selected.", DANGER)
                return
            delay = max(to_num(self.delay_var.get(), 0.0), 0.0)
            duration = max(to_num(self.duration_var.get(), 0.0), 0.0)
            self.runner.start(tasks, delay, duration)
            self.start_btn.configure(text=f"{t['stop']}  ({pretty(self.hotkey)})", fg_color=DANGER, hover_color=DANGER_HOVER, text_color=TEXT)
            self.set_status(t["running"] if delay == 0 else f"Gecikme {delay:g}s..." if self.lang == "tr" else f"Delay {delay:g}s...")

    def poll(self):
        t = LANG[self.lang]
        while not self.events.empty():
            ev = self.events.get()
            if ev[0] == "capture":
                _, cb, s = ev
                cb(s)
            elif ev[0] == "hotkey_down":
                if self.trigger_mode.get() == "Oto":
                    self.toggle()
                else:
                    if not self.runner.running:
                        try:
                            tasks = self.build_tasks()
                        except ValueError as e:
                            self.set_status(str(e), DANGER)
                            continue
                        if tasks:
                            self.runner.start(tasks, 0.0, 0.0)
                            self.start_btn.configure(text=f"{t['stop']}  ({pretty(self.hotkey)})", fg_color=DANGER, hover_color=DANGER_HOVER, text_color=TEXT)
                            self.set_status(t["running"])
            elif ev[0] == "hotkey_up":
                if self.trigger_mode.get() == "Manuel" and self.runner.running:
                    self.runner.stop()
                    self.start_btn.configure(text=f"{t['start']}  ({pretty(self.hotkey)})", fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#04283a")
                    self.set_status(t["ready"])
            elif ev[0] == "finished":
                self.start_btn.configure(text=f"{t['start']}  ({pretty(self.hotkey)})", fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#04283a")
                self.set_status(t["ready"])

        if self.runner.running:
            self.counter.configure(text=f"{t['total']}{self.runner.count}")

        self.after(30, self.poll)

    def on_close(self):
        try:
            self.listener.stop()
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()