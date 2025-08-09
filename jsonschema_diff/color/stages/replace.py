# color/replace_generic_stage.py
from __future__ import annotations
import re, difflib, click
from typing import Tuple

# --- ANSI helpers ---
RE_SGR = re.compile(r'\x1b\[[0-9;]*m')

def _strip_ansi_with_map(s: str) -> tuple[str, list[int]]:
    clean, cmap = [], []
    i = 0
    while i < len(s):
        m = RE_SGR.match(s, i)
        if m:
            i = m.end()
            continue
        clean.append(s[i]); cmap.append(i); i += 1
    return "".join(clean), cmap

def _orig_span(cmap: list[int], s_idx: int, e_idx: int, src_len: int) -> tuple[int, int]:
    if not cmap:
        return s_idx, e_idx
    if s_idx >= len(cmap):
        return src_len, src_len
    start = cmap[s_idx]
    end = cmap[e_idx-1] + 1 if e_idx > s_idx else start
    return start, end

# --- colors ---
ANSI_RGB = {
    "black": (0,0,0), "red": (205,0,0), "green": (0,205,0), "yellow": (205,205,0),
    "blue": (0,0,205), "magenta": (205,0,205), "cyan": (0,205,205), "white": (229,229,229),
    "bright_black": (127,127,127), "bright_red": (255,85,85), "bright_green": (85,255,85),
    "bright_yellow": (255,255,85), "bright_blue": (85,85,255), "bright_magenta": (255,85,255),
    "bright_cyan": (85,255,255), "bright_white": (255,255,255),
}
def _clamp01(x: float) -> float: return 0.0 if x < 0 else 1.0 if x > 1 else x
def _clamp255(x: int) -> int: return 0 if x < 0 else 255 if x > 255 else x
def _lighten(rgb: Tuple[int,int,int], pct: float) -> Tuple[int,int,int]:
    pct = _clamp01(pct)
    r,g,b = rgb
    return (_clamp255(int(r + (255-r)*pct)),
            _clamp255(int(g + (255-g)*pct)),
            _clamp255(int(b + (255-b)*pct)))

class ReplaceGenericHighlighter:
    """
    Универсальная подсветка replace: '…: OLD -> NEW'
    - берём ХВОСТ после ПЕРВОГО ':' (а не последнего);
    - diff на «чистом» тексте (без ANSI), сборка поверх исходного;
    - подсвечиваем ТОЛЬКО различия фоном; неизменное не трогаем (никакого dim).
    """

    _re_tail = re.compile(
        r'(?P<lws>\s*)'          # пробелы слева
        r'(?P<old>.*?)'          # OLD
        r'(?P<mws>\s*)'          # пробелы перед стрелкой
        r'(?P<arrow>->)'         # САМА СТРЕЛКА (именованная!)
        r'(?P<nws>\s*)'          # пробелы после стрелки
        r'(?P<new>.*?)'          # NEW
        r'(?P<ews>\s*)$'         # завершающие пробелы
    )

    def __init__(self,
                 *,
                 base_fg: str = "cyan",
                 lighten_pct: float = 0.28,   # 0..1
                 bg_fallback: str = "bright_black",
                 case_sensitive: bool = True,
                 underline_changes: bool = False) -> None:
        self.base_fg = base_fg
        self.lighten_pct = lighten_pct
        self.bg_fallback = bg_fallback
        self.case_sensitive = case_sensitive
        self.underline_changes = underline_changes

    def _bg(self):
        rgb = ANSI_RGB.get(self.base_fg.lower())
        return _lighten(rgb, self.lighten_pct) if rgb else self.bg_fallback

    @staticmethod
    def _style(s: str, *, fg=None, bg=None, underline=False) -> str:
        return click.style(s, fg=fg, bg=bg, underline=underline)

    def _render_diff(self, a: str, b: str, *, old_side: bool) -> str:
        """Рендерим diff между a и b. Неизменные фрагменты возвращаем без изменений стиля."""
        aa = a if self.case_sensitive else a.lower()
        bb = b if self.case_sensitive else b.lower()
        sm = difflib.SequenceMatcher(a=aa, b=bb)
        fg = self.base_fg
        bg = self._bg()
        out: list[str] = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                # ВАЖНО: не трогаем стиль — пусть остаётся от предыдущих стадий
                part = a[i1:i2] if old_side else b[j1:j2]
                out.append(part)
            elif tag == "replace":
                part = a[i1:i2] if old_side else b[j1:j2]
                out.append(self._style(part, fg=fg, bg=bg, underline=self.underline_changes))
            elif tag == "delete" and old_side:
                out.append(self._style(a[i1:i2], fg=fg, bg=bg, underline=self.underline_changes))
            elif tag == "insert" and not old_side:
                out.append(self._style(b[j1:j2], fg=fg, bg=bg, underline=self.underline_changes))
        return "".join(out)

    def colorize_line(self, line: str) -> str:
        clean, cmap = _strip_ansi_with_map(line)

        # ---- ВАЖНО: делим по ПЕРВОМУ ':' ----
        colon = clean.find(':')
        if colon == -1:
            return line
        head_c = clean[:colon+1]           # включает сам ':'
        tail_c = clean[colon+1:]           # всё после первого ':'

        # в хвосте ищем 'OLD -> NEW'
        m = re.search(r'^\s*(?P<old>.*?)\s*(?P<mid>->)\s*(?P<new>.*?)\s*$', tail_c)
        if not m:
            return line

        old_c, mid_c, new_c = m.group("old", "mid", "new")

        # позиции old/new (в clean) -> в исходную строку
        # head_c длиной colon+1
        o_s = len(head_c) + (len(tail_c) - len(tail_c.lstrip()))
        o_e = o_s + len(old_c.strip())
        # вычислим точнее, чтобы не терять пробелы вокруг
        # разберём хвост по кускам: left_ws + old + mid_ws + '->' + right_ws + new + end_ws
        tail_m = self._re_tail.match(tail_c)
        if not tail_m:
            return line  # хвост не в формате "OLD -> NEW" — пропускаем

        lws  = tail_m.group("lws")
        old_txt = tail_m.group("old")
        mws  = tail_m.group("mws")
        arrow = tail_m.group("arrow")  # "->"
        nws  = tail_m.group("nws")
        new_txt = tail_m.group("new")
        ews  = tail_m.group("ews")

        # границы в clean
        o_s = len(head_c) + len(lws)
        o_e = o_s + len(old_txt)
        n_s = o_e + len(mws) + len(arrow) + len(nws)
        n_e = n_s + len(new_txt)

        o0, o1 = _orig_span(cmap, o_s, o_e, len(line))
        n0, n1 = _orig_span(cmap, n_s, n_e, len(line))

        head_raw = line[:o0]
        mid_raw  = line[o1:n0]   # это « -> » с возможными ANSI от предыдущих стадий
        tail_raw = line[n1:]

        old_col = self._render_diff(old_txt, new_txt, old_side=True)
        new_col = self._render_diff(old_txt, new_txt, old_side=False)

        # Можно перерисовать стрелку унифицированно, чтобы цвет был базовый:
        mid_render = self._style(" -> ", fg=self.base_fg)

        return f"{head_raw}{old_col}{mid_render}{new_col}{tail_raw}"

    def colorize_lines(self, text: str) -> str:
        return "".join(self.colorize_line(ch) for ch in text.splitlines(keepends=True))
