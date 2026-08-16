"""
Convert ref/image.jpg to ASCII art and generate dark_mode.svg + light_mode.svg
for ldanh270 GitHub profile — inspired by Andrew6rant style.
"""

from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import math

# ── ASCII character palettes ─────────────────────────────────────────────────
# Ordered from dense/bright to light/sparse
# For dark bg: bright face pixels → dense chars ($@B), dark bg → space
# For light bg: dark face pixels → dense chars, bright bg → space
CHARS = r'$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`\'. '

def img_to_ascii(path: str, cols: int = 70, rows: int = 40, light: bool = False) -> list[str]:
    """Return ASCII lines representing the image."""
    n = len(CHARS) - 1

    img = Image.open(path).convert("RGB")

    # ── Very tight crop: fill the frame with the subject ──
    w, h = img.size
    # Crop aggressively: no wasted whitespace around the person
    img = img.crop((
        int(w * 0.12),   # trim left margin
        int(h * 0.00),   # include very top of head
        int(w * 0.88),   # trim right margin
        int(h * 0.68),   # just below chest
    ))

    # ── Segment bg: brighten near-white/grey bg pixels to 255 (white)
    # On dark mode: white (255) → will map to space (end of chars array) ✓
    # On light mode: white (255) → will map to space ✓
    # Both modes: face pixels (mid-tone) → dense chars ✓
    rgb_arr = img.load()
    cw, ch = img.size
    for y in range(ch):
        for x in range(cw):
            r, g, b = rgb_arr[x, y]
            luminance  = 0.299*r + 0.587*g + 0.114*b
            saturation = max(r, g, b) - min(r, g, b)
            if luminance > 185 and saturation < 30:
                rgb_arr[x, y] = (255, 255, 255)  # make bg pure white

    # ── Convert to grayscale, enhance ──
    img = img.convert("L")
    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = ImageEnhance.Brightness(img).enhance(1.0)

    # ── Resize to target cols×rows ──
    img = img.resize((cols, rows), Image.LANCZOS)

    pixels = list(img.getdata())
    # For dark bg: we want:
    #   white/bright bg (255) → space (invisible on dark bg)
    #   face/hair/jacket (dark areas, 0-150) → dense chars
    # For light bg: we want:
    #   white/bright bg (255) → space (invisible on light bg)
    #   face/hair/jacket (0-150) → dense chars
    # Both modes: the char density logic is the same! Bright bg = space, dark pixels = dense.
    # Difference is just which chars look "good" on dark vs light background.
    
    # Simple chars set tuned for portrait ASCII art:
    # dark mode: use bright chars on dark bg — '$@B%8&WM#*oahk...'
    # light mode: use dark chars on light bg — same set is fine since bg is white
    
    lines = []
    for r in range(rows):
        row = pixels[r * cols : (r + 1) * cols]
        line_chars = []
        for p in row:
            # Map: 255 (white/bg) → space, darker pixels → denser chars
            # Apply gamma to compress midtones
            norm = p / 255.0
            # Gamma correction: darken midtones to improve contrast
            gamma = norm ** 0.45
            idx = int(gamma * n)
            # Both dark and light modes: white bg → space, face → dense chars
            # For dark mode: we use the chars directly (dense at low gamma = dark pixel = face)
            # For light mode: same mapping works! White=space, dark=dense
            char_idx = idx   # bright pixel → dense (near 0), dark pixel → space? No...
            # CORRECT: CHARS[0]='$' (dense), CHARS[-1]=' ' (space)
            # We want: p=255 (bright bg) → CHARS[n]=' ', p=0 (dark face) → CHARS[0]='$'
            # So: char_idx = idx directly (gamma(1.0)=1.0 → n → space, gamma(0)=0 → 0 → $)
            line_chars.append(CHARS[idx])
        lines.append("".join(line_chars))
    return lines



from datetime import datetime, timezone, timedelta

# ── Giờ Việt Nam (UTC+7) & Ngày sinh (27/02/2005 06:45:00) ────────────────────
VN_TZ = timezone(timedelta(hours=7))
BIRTH_DATE = datetime(2005, 2, 27, 6, 45, 0, tzinfo=VN_TZ)

def get_uptime(birth: datetime) -> str:
    now = datetime.now(VN_TZ)
    years = now.year - birth.year
    if (now.month, now.day, now.hour, now.minute) < (birth.month, birth.day, birth.hour, birth.minute):
        years -= 1
    try:
        last_anniv = birth.replace(year=now.year)
        if last_anniv > now:
            last_anniv = birth.replace(year=now.year - 1)
    except ValueError:
        last_anniv = birth.replace(year=now.year, day=28)
        if last_anniv > now:
            last_anniv = birth.replace(year=now.year - 1, day=28)
    
    diff = now - last_anniv
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    return f"{years}y {days}d {hours}h {minutes}m"


def make_svg(lines: list[str], dark: bool = True) -> str:
    """Build the full SVG string."""

    # ── palette ───────────────────────────────────────────────────────────────
    if dark:
        bg        = "#0d1117"
        card_bg   = "#0d1117"   # same as outer bg — ASCII chars float on dark
        panel_bg  = "#161b22"
        titlebar  = "#21262d"
        ascii_clr = "#c9d1d9"
        name_clr  = "#e6edf3"
        handle_c  = "#58a6ff"
        prompt_c  = "#7dcfff"
        cmd_c     = "#9ece6a"
        arg_c     = "#c0caf5"
        kw_c      = "#bb9af7"   # export, const (purple)
        fn_c      = "#7aa2f7"   # LeDucAnh (blue)
        type_c    = "#e0af68"   # Developer type (yellow/gold)
        prop_c    = "#7dcfff"   # object keys (cyan)
        val_c     = "#9ece6a"   # strings (green)
        sep_c     = "#89ddff"   # operators: =, :, () => ({
        punct_c   = "#c0caf5"   # braces, brackets, commas
        comment_c = "#565f89"   # comments
        contact_c = "#73daca"
        cursor_c  = "#7dcfff"
        title_c   = "#565f89"
        red       = "#ff5f57"
        yellow    = "#febc2e"
        green_tl  = "#28c840"
    else:
        bg        = "#f0f2f5"
        card_bg   = "#e1e4e8"
        panel_bg  = "#ffffff"
        titlebar  = "#f6f8fa"
        ascii_clr = "#24292e"
        name_clr  = "#24292e"
        handle_c  = "#0366d6"
        prompt_c  = "#0366d6"
        cmd_c     = "#22863a"
        arg_c     = "#24292e"
        kw_c      = "#d73a49"   # export, const (red)
        fn_c      = "#6f42c1"   # LeDucAnh (purple)
        type_c    = "#6f42c1"   # Developer type (purple)
        prop_c    = "#005cc5"   # object keys (blue)
        val_c     = "#22863a"   # strings (green)
        sep_c     = "#d73a49"   # operators
        punct_c   = "#24292e"   # punctuation
        comment_c = "#6a737d"   # comments
        contact_c = "#0366d6"
        cursor_c  = "#0366d6"
        title_c   = "#8b949e"
        red       = "#ff5f57"
        yellow    = "#febc2e"
        green_tl  = "#28c840"

    # ── layout constants ──────────────────────────────────────────────────────
    W, H        = 1000, 580
    MARGIN      = 14
    LEFT_W      = 420           # wider ASCII panel for more columns
    LEFT_H      = H - MARGIN*2
    RIGHT_X     = MARGIN + LEFT_W + 10
    RIGHT_W     = W - RIGHT_X - MARGIN
    RIGHT_H     = LEFT_H

    TITLEBAR_H  = 34
    PAD         = 8             # tighter padding so art can breathe

    ASCII_FONT  = 8.2           # smaller font → more cols fit → more detail
    CHAR_W      = ASCII_FONT * 0.605
    LINE_H      = 12.5          # tighter line height for denser art

    CODE_FONT   = 12.0          # code panel font size
    CODE_LINE_H = 18.0          # code line height

    # ── ASCII art: stretch to fill left panel ─────────────────────────────────
    usable_w  = LEFT_W - 2 * PAD
    usable_h  = LEFT_H - 2 * PAD - 42   # reserve bottom 42px for name/handle

    # Strip leading/trailing blank rows first
    first = next((i for i, l in enumerate(lines) if l.strip()), 0)
    last  = len(lines) - 1 - next((i for i, l in enumerate(reversed(lines)) if l.strip()), 0)
    lines_trimmed = lines[first : last + 1]

    if lines_trimmed:
        char_count = len(lines_trimmed[0])
        row_count  = len(lines_trimmed)
        CHAR_W = usable_w / char_count
        ls     = CHAR_W - ASCII_FONT * 0.606
        LINE_H = usable_h / row_count    # stretch rows to fill height
    else:
        ls = 0

    ascii_x  = MARGIN + PAD
    ascii_y0 = MARGIN + PAD + LINE_H   # first baseline

    ascii_rows_svg = []
    for i, ln in enumerate(lines_trimmed):
        y = ascii_y0 + i * LINE_H
        safe = (ln
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))
        ascii_rows_svg.append(
            f'  <text x="{ascii_x:.1f}" y="{y:.1f}" '
            f'font-size="{ASCII_FONT}" fill="{ascii_clr}" '
            f'letter-spacing="{ls:.3f}" xml:space="preserve">{safe}</text>'
        )

    # Name + handle pinned just below ASCII art
    name_y   = ascii_y0 + len(lines_trimmed) * LINE_H + 8
    handle_y = name_y + 17

    # ── code panel content (TypeScript) ───────────────────────────────────────
    cx  = RIGHT_X + 16
    cy0 = MARGIN + TITLEBAR_H + 14 + CODE_LINE_H   # first code line y

    def ln(offset: float) -> int:
        return cy0 + int(offset * CODE_LINE_H)

    def tspan(fill: str, text: str) -> str:
        safe = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    .replace('"', "&quot;"))
        return f'<tspan fill="{fill}">{safe}</tspan>'

    uptime_str = get_uptime(BIRTH_DATE)

    code_lines = [
        # export const LeDucAnh: Developer = () => ({
        f'<text x="{cx}" y="{ln(0)}" font-size="{CODE_FONT}">'
        + tspan(kw_c, "export ") + tspan(kw_c, "const ") + tspan(fn_c, "LeDucAnh")
        + tspan(punct_c, ": ") + tspan(type_c, "Developer ")
        + tspan(sep_c, "= ") + tspan(punct_c, "() ") + tspan(sep_c, "=> ") + tspan(punct_c, "({")
        + "</text>",

        # username
        f'<text x="{cx+16}" y="{ln(1)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "username") + tspan(punct_c, ": ") + tspan(val_c, '"ldanh270"') + tspan(punct_c, ",")
        + "</text>",

        # fullName
        f'<text x="{cx+16}" y="{ln(2)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "fullName") + tspan(punct_c, ": ") + tspan(val_c, '"Le Duc Anh"') + tspan(punct_c, ",")
        + "</text>",

        # dateOfBirth
        f'<text x="{cx+16}" y="{ln(3)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "dateOfBirth") + tspan(punct_c, ": ") + tspan(val_c, '"27/02/2005"') + tspan(punct_c, ",")
        + "</text>",

        # location
        f'<text x="{cx+16}" y="{ln(4)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "location") + tspan(punct_c, ": ") + tspan(val_c, '"Da Nang, Viet Nam"') + tspan(punct_c, ",")
        + "</text>",

        # company
        f'<text x="{cx+16}" y="{ln(5)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "company") + tspan(punct_c, ": ") + tspan(val_c, '"Outfiz - Ohtez"') + tspan(punct_c, ",")
        + "</text>",

        # title
        f'<text x="{cx+16}" y="{ln(6)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "title") + tspan(punct_c, ": ") + tspan(val_c, '"Full Stack Software Engineer"') + tspan(punct_c, ",")
        + "</text>",

        # education: {
        f'<text x="{cx+16}" y="{ln(7)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "education") + tspan(punct_c, ": {")
        + "</text>",

        #   highSchool
        f'<text x="{cx+32}" y="{ln(8)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "highSchool") + tspan(punct_c, ": ") + tspan(val_c, '"Hoang Hoa Tham high school"') + tspan(punct_c, ",")
        + "</text>",

        #   university
        f'<text x="{cx+32}" y="{ln(9)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "university") + tspan(punct_c, ": ") + tspan(val_c, '"FPT University Da Nang"') + tspan(punct_c, ",")
        + "</text>",

        # },
        f'<text x="{cx+16}" y="{ln(10)}" font-size="{CODE_FONT}" fill="{punct_c}">}},</text>',

        # major
        f'<text x="{cx+16}" y="{ln(11)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "major") + tspan(punct_c, ": ") + tspan(val_c, '"Software Engineering"') + tspan(punct_c, ",")
        + "</text>",

        # specialties: [
        f'<text x="{cx+16}" y="{ln(12)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "specialties") + tspan(punct_c, ": [")
        + "</text>",

        #   "Web Development", "Competitive Programming",
        f'<text x="{cx+32}" y="{ln(13)}" font-size="{CODE_FONT}">'
        + tspan(val_c, '"Web Development"') + tspan(punct_c, ", ")
        + tspan(val_c, '"Competitive Programming"') + tspan(punct_c, ",")
        + "</text>",

        #   "CI/CD", "AI Integration",
        f'<text x="{cx+32}" y="{ln(14)}" font-size="{CODE_FONT}">'
        + tspan(val_c, '"CI/CD"') + tspan(punct_c, ", ")
        + tspan(val_c, '"AI Integration"') + tspan(punct_c, ",")
        + "</text>",

        #   "Blockchain", "Embedded - Arduino"
        f'<text x="{cx+32}" y="{ln(15)}" font-size="{CODE_FONT}">'
        + tspan(val_c, '"Blockchain"') + tspan(punct_c, ", ")
        + tspan(val_c, '"Embedded - Arduino"')
        + "</text>",

        # ],
        f'<text x="{cx+16}" y="{ln(16)}" font-size="{CODE_FONT}" fill="{punct_c}">],</text>',

        # socials: {
        f'<text x="{cx+16}" y="{ln(17)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "socials") + tspan(punct_c, ": {")
        + "</text>",

        #   website
        f'<text x="{cx+32}" y="{ln(18)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "website") + tspan(punct_c, ": ") + tspan(val_c, '"https://ldadev.vercel.app/"') + tspan(punct_c, ",")
        + "</text>",

        #   github
        f'<text x="{cx+32}" y="{ln(19)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "github") + tspan(punct_c, ": ") + tspan(val_c, '"github.com/ldanh270"') + tspan(punct_c, ",")
        + "</text>",

        #   linkedin
        f'<text x="{cx+32}" y="{ln(20)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "linkedin") + tspan(punct_c, ": ") + tspan(val_c, '"in/ldanh270"') + tspan(punct_c, ",")
        + "</text>",

        #   telegram
        f'<text x="{cx+32}" y="{ln(21)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "telegram") + tspan(punct_c, ": ") + tspan(val_c, '"t.me/ldanh270"') + tspan(punct_c, ",")
        + "</text>",

        #   facebook
        f'<text x="{cx+32}" y="{ln(22)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "facebook") + tspan(punct_c, ": ") + tspan(val_c, '"facebook.com/ldanh270"') + tspan(punct_c, ",")
        + "</text>",

        #   email
        f'<text x="{cx+32}" y="{ln(23)}" font-size="{CODE_FONT}">'
        + tspan(prop_c, "email") + tspan(punct_c, ": ") + tspan(val_c, '"ducanhle.dn@gmail.com"') + tspan(punct_c, ",")
        + "</text>",

        # },
        f'<text x="{cx+16}" y="{ln(24)}" font-size="{CODE_FONT}" fill="{punct_c}">}},</text>',

        # });
        f'<text x="{cx}" y="{ln(25)}" font-size="{CODE_FONT}" fill="{punct_c}">}});</text>',
    ]

    cursor_y = ln(26.5)

    # ── assemble SVG ─────────────────────────────────────────────────────────
    mode_label = "dark" if dark else "light"
    border_style = "" if dark else f'stroke="#e1e4e8" stroke-width="1"'

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
  width="{W}" height="{H}" viewBox="0 0 {W} {H}"
  font-family="'Cascadia Code','Fira Code','Consolas',monospace">

  <!-- outer card -->
  <rect width="{W}" height="{H}" rx="16" fill="{bg}"/>

  <!-- ── LEFT: ASCII art panel ── -->
  <rect x="{MARGIN}" y="{MARGIN}" width="{LEFT_W}" height="{LEFT_H}"
        rx="12" fill="{card_bg}"/>

  <!-- ASCII art rows -->
{"".join(chr(10) + l for l in ascii_rows_svg)}

  <!-- name -->
  <text x="{MARGIN + LEFT_W//2}" y="{name_y}"
        text-anchor="middle" font-size="15" font-weight="700"
        fill="{name_clr}" letter-spacing="0.4">Lê Đức Anh</text>
  <text x="{MARGIN + LEFT_W//2}" y="{handle_y}"
        text-anchor="middle" font-size="11"
        fill="{handle_c}" letter-spacing="0.3">@ldanh270</text>

  <!-- ── RIGHT: code terminal panel ── -->
  <rect x="{RIGHT_X}" y="{MARGIN}" width="{RIGHT_W}" height="{RIGHT_H}"
        rx="12" fill="{panel_bg}" {border_style}/>

  <!-- title bar -->
  <rect x="{RIGHT_X}" y="{MARGIN}" width="{RIGHT_W}" height="{TITLEBAR_H}"
        rx="12" fill="{titlebar}"/>
  <rect x="{RIGHT_X}" y="{MARGIN + TITLEBAR_H - 8}" width="{RIGHT_W}" height="10"
        fill="{titlebar}"/>

  <!-- macOS traffic lights -->
  <circle cx="{RIGHT_X + 22}" cy="{MARGIN + TITLEBAR_H//2}" r="6" fill="{red}"/>
  <circle cx="{RIGHT_X + 40}" cy="{MARGIN + TITLEBAR_H//2}" r="6" fill="{yellow}"/>
  <circle cx="{RIGHT_X + 58}" cy="{MARGIN + TITLEBAR_H//2}" r="6" fill="{green_tl}"/>

  <!-- title -->
  <text x="{RIGHT_X + RIGHT_W//2}" y="{MARGIN + TITLEBAR_H//2 + 5}"
        text-anchor="middle" font-size="12" fill="{title_c}" letter-spacing="0.4">
    profile.ts — ldanh270</text>

  <!-- code lines -->
{"".join(chr(10) + '  ' + l for l in code_lines)}

  <!-- blinking cursor -->
  <rect x="{cx}" y="{cursor_y - 13}" width="8" height="15" rx="1" fill="{cursor_c}">
    <animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite"/>
  </rect>

</svg>"""

    return svg


if __name__ == "__main__":
    IMG = "ref/image.jpg"

    print("Generating ASCII art (dark)…")
    lines_dark  = img_to_ascii(IMG, cols=70, rows=40, light=False)

    print("Generating ASCII art (light)…")
    lines_light = img_to_ascii(IMG, cols=70, rows=40, light=True)

    print("Writing dark_mode.svg…")
    with open("dark_mode.svg", "w", encoding="utf-8") as f:
        f.write(make_svg(lines_dark,  dark=True))

    print("Writing light_mode.svg…")
    with open("light_mode.svg", "w", encoding="utf-8") as f:
        f.write(make_svg(lines_light, dark=False))

    print("Done! Preview a few lines of ASCII:")
    for l in lines_dark[5:10]:
        print(repr(l))
