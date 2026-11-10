#!/usr/bin/env python3
#
# tex2rst.py
#
# Copyright The Persistent-1 Contributors.
#
# Persistent-1 Documentation
#
# This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
# International License. To view a copy of this license,
# visit http://creativecommons.org/licenses/by-sa/4.0/.
#

"""Ad-hoc LaTeX -> reStructuredText converter for the Persistent-1 CDR sources.

Usage: tex2rst.py SRC_ROOT OUT_ROOT
Produces a first-pass RST per chapter plus a figures manifest (figures.json)
listing every image referenced (src path, out path, trim) for later copying.
"""
import json
import os
import re
import sys

SRC, OUT = sys.argv[1], sys.argv[2]

CHAPTERS = [
    ('chapters/introduction.tex', 'introduction'),
    ('chapters/management.tex', 'management'),
    ('chapters/conops.tex', 'conops'),
    ('chapters/requirements.tex', 'requirements'),
    ('chapters/budgets.tex', 'budgets'),
    ('chapters/design.tex', 'design'),
    ('chapters/subsystems.tex', 'subsystems'),
    ('chapters/ground-segment.tex', 'ground_segment'),
    ('appendices/link_budget.tex', 'link_budget'),
]

HEADER = """.. {name}.rst

    Copyright The Persistent-1 Contributors.

    Persistent-1 Documentation

    This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
    International License. To view a copy of this license,
    visit http://creativecommons.org/licenses/by-sa/4.0/.

"""

figures = []          # manifest
labels = {}           # label -> kind (fig, tab, eq, sec)


# ---------------------------------------------------------------- helpers
def strip_comments(t):
    out = []
    for line in t.split('\n'):
        m = re.search(r'(?<!\\)%', line)
        if m:
            line = line[:m.start()]
            if not line.strip():
                continue
        out.append(line)
    return '\n'.join(out)


def read_group(t, i, open_='{', close='}'):
    """t[i] == open_; return (content, index after close)."""
    assert t[i] == open_, (t[i:i + 30])
    depth = 0
    j = i
    while j < len(t):
        c = t[j]
        if c == '\\':
            j += 2
            continue
        if c == open_:
            depth += 1
        elif c == close:
            depth -= 1
            if depth == 0:
                return t[i + 1:j], j + 1
        j += 1
    raise ValueError('unbalanced group at ' + t[i:i + 60])


def skip_ws(t, i):
    while i < len(t) and t[i] in ' \t\n':
        i += 1
    return i


def read_args(t, i, n, opt=True):
    """read optional [..] then n {..} args starting at i."""
    optarg = None
    i2 = skip_ws(t, i)
    if opt and i2 < len(t) and t[i2] == '[':
        optarg, i = read_group(t, i2, '[', ']')
    args = []
    for _ in range(n):
        i = skip_ws(t, i)
        a, i = read_group(t, i)
        args.append(a)
    return optarg, args, i


def find_env_end(t, env, start):
    """start is index right after \\begin{env}; return (body, idx after \\end{env})."""
    depth = 1
    pat = re.compile(r'\\(begin|end)\{' + re.escape(env) + r'\}')
    for m in pat.finditer(t, start):
        depth += 1 if m.group(1) == 'begin' else -1
        if depth == 0:
            return t[start:m.start()], m.end()
    raise ValueError('no end for ' + env)


def split_top(t, sep):
    """split on sep at brace depth 0 (sep is '&' or '\\\\')."""
    parts, depth, cur, i = [], 0, [], 0
    while i < len(t):
        c = t[i]
        if c == '\\' and sep == '\\\\' and t.startswith('\\\\', i) and depth == 0:
            parts.append(''.join(cur))
            cur = []
            i += 2
            continue
        if c == '\\':
            cur.append(t[i:i + 2])
            i += 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        if c == sep and depth == 0:
            parts.append(''.join(cur))
            cur = []
        else:
            cur.append(c)
        i += 1
    parts.append(''.join(cur))
    return parts


def norm_label(l):
    return re.sub(r'[^A-Za-z0-9:_\-.]', '-', l.strip()).lower()


# ---------------------------------------------------------------- acronyms
ACRO = {}


def load_acronyms():
    for f in ('pretextual_pages/acronyms.tex', 'pretextual_pages/variables.tex'):
        t = strip_comments(open(os.path.join(SRC, f), encoding='utf-8').read())
        for m in re.finditer(r'\\acro\{([^}]*)\}\[', t):
            _, args, _ = None, None, None
            i = m.end() - 1
            short, i = read_group(t, i, '[', ']')
            i = skip_ws(t, i)
            long_, i = read_group(t, i)
            ACRO[m.group(1)] = (short, long_)


# ---------------------------------------------------------------- inline
SIMPLE = {
    r'\textcelsius': '°C', r'\textdegree': '°', r'\%': '%', r'\&': '&',
    r'\_': '_', r'\#': '#', r'\$': '$', r'\ldots': '...', r'\dots': '...',
    r'\textregistered': '®', r'\texttrademark': '™', r'\copyright': '©',
    r'\textmu': 'µ', r'\LaTeX': 'LaTeX', r'\,': ' ', r'\ ': ' ', r'\-': '',
    r'\newline': ' ', r'\linebreak': ' ', r'\centering': '', r'\noindent': '',
    r'\footnotesize': '', r'\small': '', r'\large': '', r'\Large': '',
    r'\normalsize': '', r'\scriptsize': '', r'\tiny': '', r'\par': ' ',
    r'\medskip': '', r'\smallskip': '', r'\bigskip': '', r'\hfill': '',
    r'\FloatBarrier': '', r'\newpage': '', r'\pagebreak': '', r'\clearpage': '',
    r'\cleardoublepage': '', r'\bfseries': '', r'\itshape': '', r'\raggedright': '',
    r'\arraybackslash': '', r'\hline': '', r'\toprule': '', r'\midrule': '',
    r'\bottomrule': '', r'\qquad': ' ', r'\quad': ' ', r'\textbackslash': '\\',
}

MARK = '\x00'   # placeholder boundary for rst inline constructs


def role(name, content):
    return MARK + ':%s:`%s`' % (name, content) + MARK


def wrap(mark, content):
    content = content.strip()
    if not content:
        return ''
    return MARK + mark + content + mark + MARK


def ref_role(lbl):
    lbl = norm_label(lbl)
    kind = labels.get(lbl, 'fig')
    if kind == 'eq':
        return role('eq', lbl)
    if kind == 'sec':
        return role('ref', lbl)
    return role('numref', lbl)


def inline(t):
    """Convert inline LaTeX to RST text (single paragraph-ish)."""
    out = []
    i = 0
    n = len(t)
    while i < n:
        c = t[i]
        if c == '$':
            if t.startswith('$$', i):
                j = t.index('$$', i + 2)
                out.append(role('math', t[i + 2:j].strip()))
                i = j + 2
                continue
            j = i + 1
            while t[j] != '$' or t[j - 1] == '\\':
                j += 1
            m = t[i + 1:j].strip()
            sup = re.fullmatch(r'\^\{?([0-9]+)\}?', m)
            if sup:
                out.append(''.join('⁰¹²³⁴⁵⁶⁷⁸⁹'[int(d)] for d in sup.group(1)))
            elif m in ('\\times',):
                out.append('×')
            elif m in ('\\pm',):
                out.append('±')
            elif m in ('\\sim', '\\approx'):
                out.append('≈')
            elif m in ('\\geq', '\\ge'):
                out.append('≥')
            elif m in ('\\leq', '\\le'):
                out.append('≤')
            elif m in ('<', '>'):
                out.append(m)
            elif m in ('\\circ', '^\\circ', '^{\\circ}'):
                out.append('°')
            elif m in ('\\mu',):
                out.append('µ')
            else:
                out.append(role('math', m))
            i = j + 1
            continue
        if c == '~':
            out.append(' ')
            i += 1
            continue
        if t.startswith('``', i):
            out.append('“')
            i += 2
            continue
        if t.startswith("''", i):
            out.append('”')
            i += 2
            continue
        if t.startswith('---', i):
            out.append('—')
            i += 3
            continue
        if t.startswith('--', i):
            out.append('–')
            i += 2
            continue
        if c in '{}':
            i += 1
            continue
        if c == '\\':
            if t.startswith('\\\\', i):
                out.append(' ')
                i += 2
                continue
            m = re.match(r'\\([A-Za-z]+\*?|.)', t[i:])
            cmd = '\\' + m.group(1)
            j = i + m.end()
            if cmd in SIMPLE:
                out.append(SIMPLE[cmd])
                i = j
                # consume a trailing {} (e.g. \textcelsius{})
                if t.startswith('{}', i):
                    i += 2
                continue
            name = m.group(1)
            if name in ('textbf', 'textit', 'emph', 'texttt', 'underline',
                        'textsc', 'textup', 'mathbf'):
                _, a, j = read_args(t, j, 1, opt=False)
                inner = inline(a[0])
                mk = {'textbf': '**', 'mathbf': '**', 'texttt': '``'}.get(name, '*')
                if name == 'texttt':
                    out.append(wrap('``', a[0].replace('\\_', '_')))
                elif MARK in inner:      # nested markup can't nest in rst
                    out.append(inner)
                else:
                    out.append(wrap(mk, inner))
                i = j
                continue
            if name in ('autoref', 'ref', 'cref', 'Cref', 'eqref', 'pageref'):
                _, a, j = read_args(t, j, 1, opt=False)
                out.append(ref_role(a[0]))
                i = j
                continue
            if name in ('cite', 'citep', 'citet'):
                _, a, j = read_args(t, j, 1)
                keys = ','.join(k.strip() for k in a[0].split(','))
                out.append(role('cite', keys))
                i = j
                continue
            if name in ('ac', 'acs', 'acl', 'acf', 'acp', 'acsp', 'aclp', 'Ac'):
                _, a, j = read_args(t, j, 1, opt=False)
                short, long_ = ACRO.get(a[0], (a[0].upper(), a[0]))
                if name in ('acl', 'aclp'):
                    txt = inline(long_)
                elif name == 'acf':
                    txt = inline(long_) + ' (' + inline(short) + ')'
                else:
                    txt = inline(short)
                if name in ('acp', 'acsp'):
                    txt += 's'
                out.append(txt)
                i = j
                continue
            if name == 'textcolor':
                _, a, j = read_args(t, j, 2, opt=False)
                inner = inline(a[1]).strip()
                out.append(wrap('**', inner) if MARK not in inner else inner)
                i = j
                continue
            if name in ('url',):
                _, a, j = read_args(t, j, 1, opt=False)
                out.append(a[0])
                i = j
                continue
            if name == 'href':
                _, a, j = read_args(t, j, 2, opt=False)
                out.append(MARK + '`%s <%s>`_' % (inline(a[1]).strip(), a[0]) + MARK)
                i = j
                continue
            if name in ('sup', 'textsuperscript'):
                _, a, j = read_args(t, j, 1, opt=False)
                s = a[0]
                if s.isdigit():
                    out.append(''.join('⁰¹²³⁴⁵⁶⁷⁸⁹'[int(d)] for d in s))
                else:
                    out.append(role('sup', s))
                i = j
                continue
            if name in ('si', 'SI', 'unit', 'qty'):
                optarg, a, j = read_args(t, j, 1)
                out.append(a[0].replace('\\', ''))
                i = j
                continue
            if name in ('label', 'vspace', 'hspace', 'footnotemark',
                        'addcontentsline', 'renewcommand', 'setlength',
                        'cellcolor', 'rowcolor', 'nomenclature', 'cmidrule'):
                # swallow args
                nargs = {'addcontentsline': 3, 'renewcommand': 2, 'setlength': 2,
                         'nomenclature': 2}.get(name, 1)
                if name == 'footnotemark':
                    nargs = 0
                try:
                    _, a, j = read_args(t, j, nargs)
                except Exception:
                    pass
                if name == 'cmidrule':
                    j2 = skip_ws(t, j)
                    if j2 < n and t[j2] == '(':
                        j = t.index(')', j2) + 1
                i = j
                continue
            if name == 'footnotetext':
                _, a, j = read_args(t, j, 1)
                out.append(' [' + inline(a[0]).strip() + ']')
                i = j
                continue
            if name == 'multicolumn':
                _, a, j = read_args(t, j, 3, opt=False)
                out.append(inline(a[2]))
                i = j
                continue
            if name == 'multirow':
                optarg, a, j = read_args(t, j, 2)
                j = skip_ws(t, j)
                if t[j] == '[':
                    _, j = read_group(t, j, '[', ']')
                    j = skip_ws(t, j)
                a3, j = read_group(t, j)
                out.append(inline(a3))
                i = j
                continue
            # unknown command: drop the command, keep args as text
            out.append('')
            i = j
            continue
        out.append(c)
        i += 1
    s = ''.join(out)
    return fix_marks(s)


def fix_marks(s):
    """Ensure RST inline markup is separated from adjacent word characters."""
    parts = s.split(MARK)
    # parts alternates text, markup, text, markup ... where markup at odd idx
    res = ''
    for k, p in enumerate(parts):
        if k % 2 == 1 and p:
            if res and not res[-1].isspace() and res[-1] not in '(["\'“/-–—':
                res += '\\ '
            res += p
            nxt = parts[k + 1] if k + 1 < len(parts) else ''
            if nxt and not nxt[0].isspace() and nxt[0] not in '.,;:!?)]"\'”/-–—':
                res += '\\ '
        else:
            res += p
    return res


def para(t):
    s = inline(t)
    s = re.sub(r'[ \t]*\n[ \t]*', ' ', s)
    s = re.sub(r' {2,}', ' ', s).strip()
    return s


# ---------------------------------------------------------------- blocks
SECT = {'chapter': ('*', True), 'chapter*': ('*', True), 'section': ('=', False),
        'section*': ('=', False), 'subsection': ('-', False), 'subsection*': ('-', False),
        'subsubsection': ('~', False), 'subsubsection*': ('~', False),
        'subsubsubsection': ('^', False), 'paragraph': ('^', False)}


def heading(title, ch):
    title = para(title)
    w = len(title)
    if ch[1]:
        return [ch[0] * w, title, ch[0] * w, '']
    return [title, ch[0] * w, '']


def width_of(opt):
    if not opt:
        return None
    m = re.search(r'width\s*=\s*([0-9.]*)\s*\\(textwidth|linewidth|columnwidth)', opt)
    if m:
        f = float(m.group(1) or 1)
        return '%d%%' % min(100, round(f * 100))
    m = re.search(r'scale\s*=\s*([0-9.]+)', opt)
    if m:
        return '%d%%' % min(100, round(float(m.group(1)) * 80))
    m = re.search(r'width\s*=\s*([0-9.]+)\s*cm', opt)
    if m:
        return '%d%%' % min(100, round(float(m.group(1)) / 16 * 100))
    return None


# Analysis plots go to curves/, every other image to a flat figures/ folder
# (same layout as the GOLDS-UFSC documentation).
CURVES = {'decay_orbits2U3U', 'Communication_perday_PCD',
          'Communication_perday_EMMN', 'CommunicationTime'}


def fig_out(path, trim):
    base, ext = os.path.splitext(path)
    ext = ext.lower()
    name = os.path.basename(base).replace(' ', '-')
    folder = 'curves' if ('power-budget/' in path or name in CURVES) else 'figures'
    out = '%s/%s%s' % (folder, name, '.png' if ext == '.pdf' else ext)
    figures.append({'src': path, 'out': out, 'trim': trim})
    return out


def find_images(body):
    """yield (opt, path, trim) for every includegraphics."""
    for m in re.finditer(r'\\includegraphics', body):
        opt, a, _ = read_args(body, m.end(), 1)
        trim = None
        if opt:
            tm = re.search(r'trim\s*=\s*\{([^}]*)\}', opt)
            if tm:
                trim = [float(x) for x in tm.group(1).split()]
        p = a[0].strip()
        if not os.path.splitext(p)[1]:
            for e in ('.png', '.pdf', '.jpg', '.PDF', '.PNG'):
                if os.path.exists(os.path.join(SRC, p + e)):
                    p += e
                    break
        yield opt, p, trim


def get_cmd_arg(body, cmd):
    m = re.search(r'\\' + cmd + r'(?![A-Za-z])', body)
    if not m:
        return None
    _, a, _ = read_args(body, m.end(), 1)
    return a[0]


def figure_block(body):
    lines = []
    subs = list(re.finditer(r'\\subfloat', body))
    caption = get_cmd_arg(body, 'caption')
    # labels after the caption (main label)
    lbls = [norm_label(x) for x in re.findall(r'\\label\{([^}]*)\}', body)]
    if subs:
        main_lbl = None
        sublabels = []
        for m in subs:
            opt, a, _ = read_args(body, m.end(), 1)
            sl = re.search(r'\\label\{([^}]*)\}', opt or '')
            sublabels.append(norm_label(sl.group(1)) if sl else None)
            subcap = re.sub(r'\\label\{[^}]*\}', '', opt or '')
            for o, p, trim in find_images(a[0]):
                out = fig_out(p, trim)
                lines += emit_figure(out, width_of(o),
                                     (para(caption) + ' ' if caption else '') +
                                     '(' + para(subcap).rstrip('.') + ')',
                                     sl and norm_label(sl.group(1)))
        rest = [l for l in lbls if l not in sublabels]
        if rest:
            # main label points to the first sub figure: add an extra target
            lines = ['.. _%s:' % rest[0], ''] + lines
        return lines
    imgs = list(find_images(body))
    for k, (o, p, trim) in enumerate(imgs):
        out = fig_out(p, trim)
        lines += emit_figure(out, width_of(o), para(caption) if caption else '',
                             lbls[0] if (lbls and k == 0) else None)
    return lines


def emit_figure(path, width, caption, label):
    lines = []
    if label:
        lines += ['.. _%s:' % label, '']
    lines.append('.. figure:: %s' % path)
    if width:
        lines.append('   :width: %s' % width)
    lines.append('   :align: center')
    if caption:
        alt = re.sub(r'[`*\\]|:[a-z]+:', '', caption)
        lines.append('   :alt: %s' % alt)
        lines += ['', '   ' + caption]
    lines.append('')
    return lines


def parse_rows(tab):
    """tab: tabular body without column spec; return (header_rows, rows)."""
    # longtable: drop heads/foots
    if '\\endlastfoot' in tab:
        tab = tab.split('\\endlastfoot', 1)[1]
    elif '\\endfirsthead' in tab:
        head, rest = tab.split('\\endfirsthead', 1)
        rest = rest.split('\\endhead', 1)[-1]
        rest = rest.split('\\endfoot', 1)[-1]
        tab = head + rest
    # remove captions inside longtable
    tab = re.sub(r'\\caption\{[^}]*\}\s*(\\\\)?', '', tab)
    header_rows = 0
    rows = []
    seen_mid = False
    for raw in split_top(tab, '\\\\'):
        if '\\midrule' in raw or '\\hline' in raw:
            if not seen_mid and rows:
                header_rows = len(rows)
                seen_mid = True
        r = re.sub(r'\\(toprule|midrule|bottomrule|hline)(\[[^\]]*\])?', '', raw)
        r = re.sub(r'\\cmidrule(\([^)]*\))?\{[^}]*\}', '', r)
        r = re.sub(r'\\(cellcolor|rowcolor)(\[[^\]]*\])?\{[^}]*\}', '', r)
        r = re.sub(r'\\(renewcommand)\{[^}]*\}\{[^}]*\}', '', r)
        if not r.strip():
            continue
        cells = split_top(r, '&')
        out = []
        for cell in cells:
            mc = re.match(r'\s*\\multicolumn\{(\d+)\}', cell)
            out.append(para(cell))
            if mc:
                out += [''] * (int(mc.group(1)) - 1)
        rows.append(out)
    return header_rows, rows


def table_rst(header_rows, rows, caption, label):
    if not rows:
        return []
    ncol = max(len(r) for r in rows)
    lines = []
    if label:
        lines += ['.. _%s:' % label, '']
    lines.append('.. list-table::%s' % ((' ' + caption) if caption else ''))
    if header_rows:
        lines.append('   :header-rows: %d' % header_rows)
    lines.append('')
    for r in rows:
        r = r + [''] * (ncol - len(r))
        for k, c in enumerate(r):
            # strip bold in header cells
            lines.append(('   * - ' if k == 0 else '     - ') + c)
    lines.append('')
    return lines


def table_block(body):
    caption = get_cmd_arg(body, 'caption')
    lbls = [norm_label(x) for x in re.findall(r'\\label\{([^}]*)\}', body)]
    lines = []
    tabs = list(re.finditer(r'\\begin\{(tabular\*?|tabularx|longtable)\}', body))
    if not tabs:
        return convert(body)
    for k, m in enumerate(tabs):
        env = m.group(1)
        tb, _ = find_env_end(body, env, m.end())
        # drop column spec
        i = 0
        if env in ('tabularx', 'tabular*'):
            _, i = read_group(tb, skip_ws(tb, 0))
        j = skip_ws(tb, i)
        if j < len(tb) and tb[j] == '[':
            _, j = read_group(tb, j, '[', ']')
            j = skip_ws(tb, j)
        _, j = read_group(tb, j)
        hr, rows = parse_rows(tb[j:])
        # captions inside minipages
        cap = caption
        lab = lbls[0] if k == 0 and lbls else None
        if len(tabs) > 1:
            # look for a caption between this tabular end and next
            seg_end = tabs[k + 1].start() if k + 1 < len(tabs) else len(body)
            seg = body[m.start():seg_end]
            c2 = get_cmd_arg(seg, 'caption')
            l2 = re.findall(r'\\label\{([^}]*)\}', seg)
            if c2:
                cap = c2
                lab = norm_label(l2[0]) if l2 else None
            elif k > 0:
                cap, lab = None, None
        if env == 'longtable':
            c2 = get_cmd_arg(tb, 'caption')
            if c2:
                cap = c2
        lines += table_rst(hr, rows, para(cap) if cap else None, lab)
    return lines


def math_block(body, env):
    lbls = [norm_label(x) for x in re.findall(r'\\label\{([^}]*)\}', body)]
    body = re.sub(r'\\label\{[^}]*\}', '', body)
    body = re.sub(r'\\(begin|end)\{split\}', '', body)
    body = body.replace('\\nonumber', '')
    lines = ['.. math::']
    if lbls:
        lines.append('   :label: %s' % lbls[0])
    lines.append('')
    eqs = [e.strip() for e in body.strip().split('\n') if e.strip()]
    if env.startswith('align') or '&' in body:
        lines.append('   \\begin{aligned}')
        lines += ['   ' + e for e in eqs]
        lines.append('   \\end{aligned}')
    else:
        lines += ['   ' + e for e in eqs]
    lines.append('')
    return lines


def list_block(body, env, depth=0):
    bullet = '#.' if env == 'enumerate' else '*'
    items = re.split(r'\\item(?![A-Za-z])', body)
    lines = []
    for it in items[1:]:
        it = it.strip()
        if it.startswith('['):
            lbl, k = read_group(it, 0, '[', ']')
            it = '**' + lbl + '** ' + it[k:]
        sub = convert(it)
        sub = [l for l in sub]
        while sub and not sub[-1].strip():
            sub.pop()
        pad = ' ' * (len(bullet) + 1)
        first = True
        for l in sub:
            if first:
                lines.append(bullet + ' ' + l)
                first = False
            else:
                lines.append((pad + l) if l.strip() else '')
        lines.append('')
    return lines


def convert(t):
    """Convert a block of LaTeX to list of rst lines."""
    lines = []
    buf = []

    def flush():
        txt = ''.join(buf)
        buf.clear()
        for p in re.split(r'\n\s*\n', txt):
            s = para(p)
            if s:
                lines.extend([s, ''])

    i = 0
    pat = re.compile(r'\\(begin)\{([A-Za-z*]+)\}|\\(chapter\*?|section\*?|subsection\*?|'
                     r'subsubsection\*?|subsubsubsection|paragraph)(?![A-Za-z])|'
                     r'\\(label)\{|\\\[')
    while True:
        m = pat.search(t, i)
        if not m:
            buf.append(t[i:])
            break
        buf.append(t[i:m.start()])
        if m.group(0) == '\\[':
            flush()
            j = t.index('\\]', m.end())
            lines += math_block(t[m.end():j], 'equation')
            i = j + 2
            continue
        if m.group(4):          # stray label -> section/other target
            _, a, j = read_args(t, m.start() + len('\\label'), 1, opt=False)
            flush()
            lab = norm_label(a[0])
            # attach to the previous heading if just emitted
            k = len(lines) - 1
            while k >= 0 and not lines[k].strip():
                k -= 1
            if k >= 1 and re.fullmatch(r'([=\-~^*])\1+', lines[k]):
                # insert label before the heading
                h = k - 1
                if h >= 1 and re.fullmatch(r'\*+', lines[h - 1] or ''):
                    h -= 1
                lines[h:h] = ['.. _%s:' % lab, '']
            else:
                lines += ['.. _%s:' % lab, '']
            i = j
            continue
        if m.group(3):
            flush()
            cmd = m.group(3)
            opt, a, j = read_args(t, m.end(), 1)
            lines += heading(a[0], SECT[cmd])
            i = j
            continue
        env = m.group(2)
        body, j = find_env_end(t, env, m.end())
        flush()
        if env == 'figure':
            lines += figure_block(body)
        elif env in ('table', 'table*'):
            lines += table_block(body)
        elif env in ('tabular', 'tabularx', 'longtable', 'tabular*'):
            lines += table_block('\\begin{%s}%s\\end{%s}' % (env, body, env))
        elif env in ('equation', 'equation*', 'align', 'align*', 'eqnarray', 'gather'):
            lines += math_block(body, env)
        elif env in ('itemize', 'enumerate', 'description'):
            lines += list_block(body, env)
        elif env == 'tcolorbox':
            b = body
            if b.lstrip().startswith('['):
                _, k = read_group(b, skip_ws(b, 0), '[', ']')
                b = b[k:]
            inner = convert(b)
            lines += ['.. epigraph::', ''] + ['   ' + l if l else '' for l in inner]
        elif env == 'minipage':
            b = body
            k = skip_ws(b, 0)
            if k < len(b) and b[k] == '[':
                _, k = read_group(b, k, '[', ']')
            k = skip_ws(b, k)
            _, k = read_group(b, k)
            lines += convert(b[k:])
        else:  # center, landscape, samepage, appendices, etc.
            b = body
            k = skip_ws(b, 0)
            if env == 'adjustbox':
                _, k = read_group(b, k)
                b = b[k:]
            lines += convert(b)
        i = j
    flush()
    return lines


def collect_labels(t):
    # figure / table / equation / section labels
    for env, kind in (('figure', 'fig'), ('table', 'tab'), ('longtable', 'tab'),
                      ('equation', 'eq'), ('align', 'eq'), ('align*', 'eq')):
        for m in re.finditer(r'\\begin\{' + re.escape(env) + r'\}', t):
            body, _ = find_env_end(t, env, m.end())
            for l in re.findall(r'\\label\{([^}]*)\}', body):
                labels.setdefault(norm_label(l), kind)
    for l in re.findall(r'\\label\{([^}]*)\}', t):
        labels.setdefault(norm_label(l), 'sec')


def main():
    load_acronyms()
    texts = {}
    for src, name in CHAPTERS:
        t = strip_comments(open(os.path.join(SRC, src), encoding='utf-8').read())
        texts[name] = t
        collect_labels(t)
    os.makedirs(OUT, exist_ok=True)
    for src, name in CHAPTERS:
        lines = convert(texts[name])
        txt = HEADER.format(name=name) + '\n'.join(lines).rstrip() + '\n'
        txt = re.sub(r'\n{3,}', '\n\n', txt)
        open(os.path.join(OUT, name + '.rst'), 'w', encoding='utf-8').write(txt)
    json.dump(figures, open(os.path.join(OUT, 'figures.json'), 'w'), indent=1)
    json.dump(ACRO, open(os.path.join(OUT, 'acronyms.json'), 'w'), indent=1,
              ensure_ascii=False)


main()
