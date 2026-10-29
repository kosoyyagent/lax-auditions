# Generates a 33-point .cube LUT: "warm storybook" grade
# soft golden light, gentle contrast, rich non-neon color, no crushed blacks / clipped highlights
SIZE = 33

def clamp(x): return min(1.0, max(0.0, x))

def smoothstep(a, b, x):
    t = clamp((x - a) / (b - a))
    return t * t * (3 - 2 * t)

def grade(r, g, b):
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b

    # 1) gentle S-contrast around pivot 0.45 (strength 0.13), blended with original
    def s_curve(x):
        s = smoothstep(0.0, 1.0, (x - 0.45) * 1.45 + 0.45)
        return x + (s - x) * 0.32  # mild blend => gentle contrast
    r, g, b = s_curve(r), s_curve(g), s_curve(b)

    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b

    # 2) golden warmth: strongest in mids/highs, slight warm lift in shadows
    warm = smoothstep(0.10, 0.70, luma)          # 0 in deep shadows -> 1 in highs
    shad = 1.0 - smoothstep(0.0, 0.35, luma)     # shadow zone
    r += 0.075 * warm + 0.018 * shad
    g += 0.038 * warm + 0.008 * shad
    b -= 0.085 * warm
    b += 0.010 * shad                            # shadows stay slightly warm, not blue

    # 3) mild highlight shoulder (keeps detail, no hard clip)
    def shoulder(x):
        if x <= 0.86: return x
        t = (x - 0.86) / 0.14
        return 0.86 + 0.14 * (t / (1.0 + 0.55 * t))
    r, g, b = shoulder(r), shoulder(g), shoulder(b)

    # 4) tiny black lift (storybook softness, no crush)
    def blacklift(x): return 0.018 + x * (1.0 - 0.018)
    r, g, b = blacklift(r), blacklift(g), blacklift(b)

    # 5) saturation control: keep rich but non-neon — slight desat only where very saturated
    luma2 = 0.2126 * r + 0.7152 * g + 0.0722 * b
    mx, mn = max(r, g, b), min(r, g, b)
    sat = (mx - mn) / (mx + 1e-6)
    desat = 0.25 * smoothstep(0.55, 0.95, sat)   # only tame the most saturated
    boost = 0.06 * (1.0 - smoothstep(0.0, 0.5, sat))  # lift muted tones a touch
    f = 1.0 - desat + boost
    r = luma2 + (r - luma2) * f
    g = luma2 + (g - luma2) * f
    b = luma2 + (b - luma2) * f

    return clamp(r), clamp(g), clamp(b)

with open("look.cube", "w") as f:
    f.write('TITLE "Warm Storybook (Kognai audition)"\n')
    f.write("LUT_3D_SIZE %d\n" % SIZE)
    f.write("DOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n")
    for bi in range(SIZE):
        for gi in range(SIZE):
            for ri in range(SIZE):
                r, g, b = grade(ri / (SIZE - 1), gi / (SIZE - 1), bi / (SIZE - 1))
                f.write("%.6f %.6f %.6f\n" % (r, g, b))
print("done")
