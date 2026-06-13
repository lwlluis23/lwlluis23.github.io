"""Gera o icone do app AI Video Studio em PNG (varios tamanhos)."""
from PIL import Image, ImageDraw, ImageFilter

# ---- cores da marca ----
INDIGO = (99, 102, 241)
PURPLE = (168, 85, 247)
CYAN   = (34, 211, 238)

SS = 4                 # supersampling para bordas suaves
SIZE = 1024            # tamanho mestre
W = SIZE * SS


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def grad_color(t):
    """Gradiente de 3 paradas: indigo -> purple -> cyan."""
    if t < 0.5:
        return lerp(INDIGO, PURPLE, t / 0.5)
    return lerp(PURPLE, CYAN, (t - 0.5) / 0.5)


def make_master():
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))

    # ---- fundo com gradiente diagonal ----
    grad = Image.new("RGB", (W, W))
    gpx = grad.load()
    for y in range(W):
        for x in range(W):
            t = (x + y) / (2 * (W - 1))      # diagonal canto-superior-esq -> inferior-dir
            gpx[x, y] = grad_color(t)

    # ---- mascara de quadrado arredondado ----
    mask = Image.new("L", (W, W), 0)
    md = ImageDraw.Draw(mask)
    radius = int(W * 0.235)                  # "squircle" estilo iOS
    md.rounded_rectangle([0, 0, W - 1, W - 1], radius=radius, fill=255)
    img.paste(grad, (0, 0), mask)

    d = ImageDraw.Draw(img)

    # ---- brilho suave no topo ----
    glow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W*0.1, -W*0.35, W*0.9, W*0.35], fill=(255, 255, 255, 38))
    glow = glow.filter(ImageFilter.GaussianBlur(W * 0.06))
    img = Image.alpha_composite(img, Image.composite(glow, Image.new("RGBA",(W,W),(0,0,0,0)), mask))
    d = ImageDraw.Draw(img)

    # ---- triangulo de "play" branco com cantos arredondados ----
    cx, cy = W * 0.50, W * 0.5
    r = W * 0.21
    import math
    pts = []
    for ang in (0, 120, 240):               # triangulo apontando p/ direita (play)
        a = math.radians(ang)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    # sombra do play
    shadow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([(p[0], p[1] + W*0.012) for p in pts], fill=(20, 20, 40, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(W * 0.02))
    img = Image.alpha_composite(img, shadow)
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=(255, 255, 255, 255))

    # ---- "sparkle" de IA (estrela de 4 pontas) no canto sup. direito ----
    sx, sy = W * 0.74, W * 0.27
    s = W * 0.075
    star = [
        (sx, sy - s), (sx + s*0.22, sy - s*0.22), (sx + s, sy),
        (sx + s*0.22, sy + s*0.22), (sx, sy + s),
        (sx - s*0.22, sy + s*0.22), (sx - s, sy),
        (sx - s*0.22, sy - s*0.22),
    ]
    d.polygon(star, fill=(255, 255, 255, 235))
    # sparkle menor
    sx2, sy2 = W * 0.83, W * 0.40
    s2 = W * 0.035
    star2 = [
        (sx2, sy2 - s2), (sx2 + s2*0.22, sy2 - s2*0.22), (sx2 + s2, sy2),
        (sx2 + s2*0.22, sy2 + s2*0.22), (sx2, sy2 + s2),
        (sx2 - s2*0.22, sy2 + s2*0.22), (sx2 - s2, sy2),
        (sx2 - s2*0.22, sy2 - s2*0.22),
    ]
    d.polygon(star2, fill=(255, 255, 255, 200))

    # downscale para o tamanho mestre (antialias)
    return img.resize((SIZE, SIZE), Image.LANCZOS)


def main():
    master = make_master()
    master.save("icon.png")                          # 1024
    for size, name in [(512, "icon-512.png"),
                       (192, "icon-192.png"),
                       (180, "apple-touch-icon.png"),
                       (32,  "favicon.png")]:
        master.resize((size, size), Image.LANCZOS).save(name)
    print("Icones gerados:", "icon.png (1024), 512, 192, 180, 32")


if __name__ == "__main__":
    main()
