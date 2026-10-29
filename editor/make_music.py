"""Self-composed ambient track for the 'city waking up' cut.
96 bpm, 35s, warm dawn progression D-G-A feel. Released as CC0."""
import math, struct, wave

SR = 44100
BPM = 96
BEAT = 60.0 / BPM          # 0.625s
BAR = BEAT * 4             # 2.5s
DUR = 35.0
N = int(SR * DUR)

def note(freq, t0, dur, vol, kind='sine', decay=None, buf=None, pan=0.5):
    if buf is None: return
    i0 = int(t0 * SR); i1 = min(N, int((t0 + dur) * SR))
    for i in range(i0, i1):
        t = (i - i0) / SR
        env = math.exp(-t / (decay if decay else dur / 3)) if decay else min(1.0, t / 0.02) * min(1.0, (dur - t) / (dur * 0.5))
        if kind == 'sine': s = math.sin(2 * math.pi * freq * t)
        elif kind == 'tri': s = 2 * abs(2 * (t * freq % 1) - 1) - 1
        else: s = math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)
        l, r = buf[i]
        buf[i] = (l + s * env * vol * (1 - pan), r + s * env * vol * pan)

buf = [(0.0, 0.0)] * N
# progression: Dm - Bb - F - C over 14 bars then resolve; each 2.5s bar
CHORDS = [
    (146.83, 220.0, 293.66),   # D3 A3 D4
    (116.54, 174.61, 233.08),  # Bb2 F3 Bb3
    (174.61, 220.0, 349.23),   # F3 A3 F4
    (130.81, 196.0, 261.63),   # C3 G3 C4
]
# 14 bars: D D Bb Bb F F C C D D Bb Bb F F, then final resolve bars 15-16? (35s=14 bars)
bars = [0,0,1,1,2,2,3,3,0,0,1,1,2,2]
for b, ci in enumerate(bars):
    t0 = b * BAR
    for f in CHORDS[ci]:
        note(f, t0, BAR, 0.06, 'pad', buf=buf, pan=0.5)
        note(f * 2, t0, BAR, 0.02, 'pad', buf=buf, pan=0.5)

# pluck pulse: starts bar 3 (t=5s), every beat
for b in range(2, 14):
    for bt in range(4):
        t0 = b * BAR + bt * BEAT
        f = CHORDS[bars[b]][bt % 3] * 4
        note(f, t0, BEAT, 0.11 if bt == 0 else 0.07, 'sine', decay=BEAT * 0.8, buf=buf, pan=0.3 + 0.4 * (bt % 2))

# bass root each bar from bar 5
for b in range(4, 14):
    note(CHORDS[bars[b]][0] / 2, b * BAR, BAR, 0.10, 'tri', buf=buf)

# arpeggio from bar 9: 8th notes
for b in range(8, 14):
    for st in range(8):
        t0 = b * BAR + st * BEAT / 2
        f = CHORDS[bars[b]][st % 3] * 8
        note(f, t0, BEAT / 2, 0.045, 'sine', decay=BEAT, buf=buf, pan=0.2 + 0.6 * (st % 3) / 2)

# ending resolve: last bar fade + final tonic shimmer
for f in CHORDS[0]:
    note(f, 13 * BAR, 2 * BAR, 0.05, 'pad', buf=buf)

w = wave.open('dawn_theme.wav', 'wb')
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
frames = bytearray()
for l, r in buf:
    l = max(-1, min(1, l)); r = max(-1, min(1, r))
    frames += struct.pack('<hh', int(l * 32767), int(r * 32767))
w.writeframes(bytes(frames)); w.close()
print('wrote dawn_theme.wav', DUR, 's')
