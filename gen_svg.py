"""Generate standalone dark and light ASCII portraits for the GitHub profile."""

from PIL import Image, ImageEnhance


# Ordered from dense to sparse. The backtick is inserted separately so this
# source remains easy to embed in tooling while preserving the original set.
CHARS = (
    r'$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^'
    + chr(96)
    + r"\'. "
)


def img_to_ascii(
    path: str,
    cols: int = 70,
    rows: int = 40,
    light: bool = False,
) -> list[str]:
    """Return ASCII lines representing the image."""
    n = len(CHARS) - 1
    img = Image.open(path).convert("RGB")

    # Keep the original tight portrait crop.
    width, height = img.size
    img = img.crop(
        (
            int(width * 0.12),
            int(height * 0.00),
            int(width * 0.88),
            int(height * 0.68),
        )
    )

    # Remove the near-white/grey background before converting to characters.
    rgb_pixels = img.load()
    cropped_width, cropped_height = img.size
    for y in range(cropped_height):
        for x in range(cropped_width):
            red, green, blue = rgb_pixels[x, y]
            luminance = (0.299 * red) + (0.587 * green) + (0.114 * blue)
            saturation = max(red, green, blue) - min(red, green, blue)
            if luminance > 185 and saturation < 30:
                rgb_pixels[x, y] = (255, 255, 255)

    img = img.convert("L")
    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = ImageEnhance.Brightness(img).enhance(1.0)
    img = img.resize((cols, rows), Image.LANCZOS)

    pixels = list(img.getdata())
    lines: list[str] = []
    for row_index in range(rows):
        row = pixels[row_index * cols : (row_index + 1) * cols]
        line_chars: list[str] = []
        for pixel in row:
            normalized = pixel / 255.0
            gamma = normalized**0.45
            line_chars.append(CHARS[int(gamma * n)])
        lines.append("".join(line_chars))

    return lines


def escape_xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def make_svg(lines: list[str], dark: bool = True) -> str:
    """Build an SVG containing only the ASCII portrait and identity."""
    if dark:
        background = "#0d1117"
        card_background = "#0d1117"
        ascii_color = "#c9d1d9"
        name_color = "#e6edf3"
        handle_color = "#58a6ff"
    else:
        background = "#f0f2f5"
        card_background = "#e1e4e8"
        ascii_color = "#24292e"
        name_color = "#24292e"
        handle_color = "#0366d6"

    width, height = 448, 580
    margin = 14
    card_width = 420
    card_height = height - (margin * 2)
    padding = 8
    ascii_font_size = 8.2

    usable_width = card_width - (2 * padding)
    usable_height = card_height - (2 * padding) - 42

    first = next((i for i, line in enumerate(lines) if line.strip()), 0)
    last = len(lines) - 1 - next(
        (i for i, line in enumerate(reversed(lines)) if line.strip()),
        0,
    )
    trimmed_lines = lines[first : last + 1]

    if trimmed_lines:
        character_count = len(trimmed_lines[0])
        row_count = len(trimmed_lines)
        character_width = usable_width / character_count
        letter_spacing = character_width - (ascii_font_size * 0.606)
        line_height = usable_height / row_count
    else:
        letter_spacing = 0
        line_height = 12.5

    ascii_x = margin + padding
    ascii_y = margin + padding + line_height

    rendered_rows: list[str] = []
    for index, line in enumerate(trimmed_lines):
        y = ascii_y + (index * line_height)
        rendered_rows.append(
            f'<text x="{ascii_x:.1f}" y="{y:.1f}" '
            f'font-size="{ascii_font_size}" fill="{ascii_color}" '
            f'letter-spacing="{letter_spacing:.3f}" xml:space="preserve">'
            f"{escape_xml(line)}</text>"
        )

    name_y = ascii_y + (len(trimmed_lines) * line_height) + 8
    handle_y = name_y + 17
    rows_svg = "\n".join(rendered_rows)

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
  width="{width}" height="{height}" viewBox="0 0 {width} {height}"
  role="img" aria-labelledby="title desc"
  font-family="'Cascadia Code','Fira Code','Consolas',monospace">
  <title id="title">ASCII portrait of Lê Đức Anh</title>
  <desc id="desc">A character-based portrait with the handle @ldanh270.</desc>

  <rect width="{width}" height="{height}" rx="16" fill="{background}"/>
  <rect x="{margin}" y="{margin}" width="{card_width}" height="{card_height}"
        rx="12" fill="{card_background}"/>

  {rows_svg}

  <text x="{margin + (card_width // 2)}" y="{name_y}"
        text-anchor="middle" font-size="15" font-weight="700"
        fill="{name_color}" letter-spacing="0.4">Lê Đức Anh</text>
  <text x="{margin + (card_width // 2)}" y="{handle_y}"
        text-anchor="middle" font-size="11"
        fill="{handle_color}" letter-spacing="0.3">@ldanh270</text>
</svg>"""


def make_code_svg(dark: bool = True) -> str:
    """Build a syntax-highlighted TypeScript profile card."""
    if dark:
        colors = {
            "background": "#0d1117",
            "panel": "#161b22",
            "titlebar": "#21262d",
            "border": "#30363d",
            "text": "#c9d1d9",
            "muted": "#6e7681",
            "keyword": "#ff7b72",
            "type": "#d2a8ff",
            "property": "#79c0ff",
            "string": "#a5d6ff",
            "punctuation": "#c9d1d9",
        }
    else:
        colors = {
            "background": "#f0f2f5",
            "panel": "#ffffff",
            "titlebar": "#f6f8fa",
            "border": "#d0d7de",
            "text": "#24292f",
            "muted": "#8c959f",
            "keyword": "#cf222e",
            "type": "#8250df",
            "property": "#0550ae",
            "string": "#0a3069",
            "punctuation": "#24292f",
        }

    width, height = 720, 580
    margin = 14
    panel_width = width - (margin * 2)
    panel_height = height - (margin * 2)
    titlebar_height = 40
    code_x = margin + 64
    code_y = margin + titlebar_height + 27
    font_size = 12.6
    line_height = 18.7

    def token(kind: str, value: str) -> str:
        return f'<tspan fill="{colors[kind]}">{escape_xml(value)}</tspan>'

    code_lines: list[tuple[int, str]] = [
        (
            0,
            token("keyword", "interface ")
            + token("type", "Developer ")
            + token("punctuation", "{"),
        ),
        (
            1,
            token("property", "username")
            + token("punctuation", ": ")
            + token("type", "string")
            + token("punctuation", ";"),
        ),
        (
            1,
            token("property", "fullName")
            + token("punctuation", ": ")
            + token("type", "string")
            + token("punctuation", ";"),
        ),
        (
            1,
            token("property", "title")
            + token("punctuation", ": ")
            + token("type", "string")
            + token("punctuation", ";"),
        ),
        (
            1,
            token("property", "location")
            + token("punctuation", ": ")
            + token("type", "string")
            + token("punctuation", ";"),
        ),
        (
            1,
            token("property", "company")
            + token("punctuation", ": ")
            + token("type", "string")
            + token("punctuation", ";"),
        ),
        (
            1,
            token("property", "education")
            + token("punctuation", ": ")
            + token("type", "string")
            + token("punctuation", ";"),
        ),
        (
            1,
            token("property", "specialties")
            + token("punctuation", ": ")
            + token("keyword", "readonly ")
            + token("type", "string")
            + token("punctuation", "[];"),
        ),
        (0, token("punctuation", "}")),
        (0, ""),
        (
            0,
            token("keyword", "export const ")
            + token("property", "leDucAnh")
            + token("punctuation", ": ")
            + token("type", "Developer ")
            + token("punctuation", "= {"),
        ),
        (
            1,
            token("property", "username")
            + token("punctuation", ": ")
            + token("string", '"ldanh270"')
            + token("punctuation", ","),
        ),
        (
            1,
            token("property", "fullName")
            + token("punctuation", ": ")
            + token("string", '"Lê Đức Anh"')
            + token("punctuation", ","),
        ),
        (
            1,
            token("property", "title")
            + token("punctuation", ": ")
            + token("string", '"Full Stack Software Engineer"')
            + token("punctuation", ","),
        ),
        (
            1,
            token("property", "location")
            + token("punctuation", ": ")
            + token("string", '"Da Nang, Vietnam"')
            + token("punctuation", ","),
        ),
        (
            1,
            token("property", "company")
            + token("punctuation", ": ")
            + token("string", '"Outfiz · Ohtez"')
            + token("punctuation", ","),
        ),
        (
            1,
            token("property", "education")
            + token("punctuation", ": ")
            + token("string", '"FPT University Da Nang"')
            + token("punctuation", ","),
        ),
        (
            1,
            token("property", "specialties") + token("punctuation", ": ["),
        ),
        (2, token("string", '"Web Development"') + token("punctuation", ",")),
        (
            2,
            token("string", '"Competitive Programming"')
            + token("punctuation", ","),
        ),
        (2, token("string", '"CI/CD"') + token("punctuation", ",")),
        (2, token("string", '"AI Integration"') + token("punctuation", ",")),
        (2, token("string", '"Blockchain"') + token("punctuation", ",")),
        (2, token("string", '"Embedded Systems"') + token("punctuation", ",")),
        (1, token("punctuation", "],")),
        (0, token("punctuation", "};")),
    ]

    rendered_lines: list[str] = []
    for line_number, (indent, content) in enumerate(code_lines, start=1):
        y = code_y + ((line_number - 1) * line_height)
        rendered_lines.append(
            f'<text x="{margin + 39}" y="{y:.1f}" text-anchor="end" '
            f'font-size="10.5" fill="{colors["muted"]}">{line_number}</text>'
        )
        if content:
            rendered_lines.append(
                f'<text x="{code_x + (indent * 19)}" y="{y:.1f}" '
                f'font-size="{font_size}" fill="{colors["text"]}" '
                f'xml:space="preserve">{content}</text>'
            )

    code_svg = "\n  ".join(rendered_lines)
    mode = "dark" if dark else "light"

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
  width="{width}" height="{height}" viewBox="0 0 {width} {height}"
  role="img" aria-labelledby="title desc"
  font-family="'Cascadia Code','Fira Code','Consolas',monospace">
  <title id="title">TypeScript profile for Lê Đức Anh</title>
  <desc id="desc">A {mode} TypeScript editor card containing developer profile information.</desc>

  <rect width="{width}" height="{height}" rx="16" fill="{colors["background"]}"/>
  <rect x="{margin}" y="{margin}" width="{panel_width}" height="{panel_height}"
        rx="12" fill="{colors["panel"]}" stroke="{colors["border"]}"/>
  <rect x="{margin}" y="{margin}" width="{panel_width}" height="{titlebar_height}"
        rx="12" fill="{colors["titlebar"]}"/>
  <rect x="{margin}" y="{margin + titlebar_height - 9}" width="{panel_width}" height="10"
        fill="{colors["titlebar"]}"/>

  <circle cx="{margin + 22}" cy="{margin + 20}" r="6" fill="#ff5f57"/>
  <circle cx="{margin + 40}" cy="{margin + 20}" r="6" fill="#febc2e"/>
  <circle cx="{margin + 58}" cy="{margin + 20}" r="6" fill="#28c840"/>
  <text x="{margin + (panel_width / 2):.1f}" y="{margin + 25}"
        text-anchor="middle" font-size="11.5" fill="{colors["muted"]}">
    profile.ts — ldanh270</text>

  <line x1="{margin + 50}" y1="{margin + titlebar_height}"
        x2="{margin + 50}" y2="{margin + panel_height - 12}"
        stroke="{colors["border"]}"/>

  {code_svg}
</svg>"""


if __name__ == "__main__":
    image_path = "ref/image.jpg"

    print("Generating ASCII portrait (dark)...")
    dark_lines = img_to_ascii(image_path, cols=70, rows=40, light=False)

    print("Generating ASCII portrait (light)...")
    light_lines = img_to_ascii(image_path, cols=70, rows=40, light=True)

    print("Writing dark_mode.svg...")
    with open("dark_mode.svg", "w", encoding="utf-8") as output:
        output.write(make_svg(dark_lines, dark=True))

    print("Writing light_mode.svg...")
    with open("light_mode.svg", "w", encoding="utf-8") as output:
        output.write(make_svg(light_lines, dark=False))

    print("Done!")
