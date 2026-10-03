import numpy as np, subprocess, os
from scipy.signal import butter, lfilter, fftconvolve

SR = 44100
OUT = "./audio"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

def lp(x, f, o=2): b, a = butter(o, f / (SR / 2), "low"); return lfilter(b, a, x)
def hp(x, f, o=2): b, a = butter(o, f / (SR / 2), "high"); return lfilter(b, a, x)
def bp(x, lo, hi, o=2): b, a = butter(o, [lo / (SR / 2), hi / (SR / 2)], "band"); return lfilter(b, a, x)

def reverb(x, secs=2.5, decay=3.0, wet=0.35):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-decay * np.linspace(0, secs, n))
    ir = lp(ir, 3500)
    y = fftconvolve(x, ir)[: len(x)]
    y /= np.max(np.abs(y)) + 1e-9
    return (1 - wet) * x / (np.max(np.abs(x)) + 1e-9) + wet * y

def loopify(x, fade=2.0):
    """Crossfade tail into head so the file loops seamlessly."""
    n = int(fade * SR)
    head, tail, body = x[:n], x[-n:], x[n:-n]
    w = np.linspace(0, 1, n)
    return np.concatenate([tail * (1 - w) + head * w, body])

def norm(x, peak=0.8): return x / (np.max(np.abs(x)) + 1e-9) * peak

def stereo(x, spread_ms=11):
    d = int(spread_ms / 1000 * SR)
    r = np.concatenate([x[-d:], x[:-d]])
    return np.stack([x, 0.85 * x + 0.15 * r], 1)

def write(name, x, loop=True):
    if loop: x = loopify(x)
    x = norm(x)
    if x.ndim == 1: x = stereo(x)
    raw = (x * 32767).astype("<i2").tobytes()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2",
                    "-i", "-", "-c:a", "libvorbis", "-q:a", "5", f"{OUT}/{name}.ogg"], input=raw, check=True)

def t(secs): return np.arange(int(secs * SR)) / SR

# 1. Fluorescent hum: mains hum + harmonics, ballast buzz, occasional flicker stutter, room tone
def hum():
    T = t(64); x = np.zeros_like(T)
    for k, a in [(1, 1.0), (2, .55), (3, .35), (4, .2), (6, .12), (8, .08), (12, .05)]:
        x += a * np.sin(2 * np.pi * 60 * k * T + rng.uniform(0, 6))
    buzz = np.sign(np.sin(2 * np.pi * 120 * T)) * 0.12
    x += lp(buzz, 2500)
    x *= 1 + 0.04 * np.sin(2 * np.pi * 0.13 * T)          # slow swell
    env = np.ones_like(T)                                     # flickers
    for s in rng.uniform(3, 60, 6):
        i = int(s * SR); L = int(rng.uniform(.15, .6) * SR)
        stut = (np.sin(2 * np.pi * rng.uniform(9, 17) * np.arange(L) / SR) > 0).astype(float)
        env[i:i + L] = 0.25 + 0.75 * stut
    x *= lp(env, 400)
    room = lp(rng.standard_normal(len(T)), 600) * 0.6
    return lp(x, 4000) + room

# 2. Undercroft: low rumble, irregular drips with long reverb, far pipe groans
def drip():
    T = t(64)
    x = lp(rng.standard_normal(len(T)), 120) * 2.0
    for s in rng.uniform(0, 62, 38):
        i = int(s * SR); L = int(.12 * SR); f = rng.uniform(900, 1900)
        tt = np.arange(L) / SR
        x[i:i + L] += 0.5 * np.sin(2 * np.pi * (f + 1800 * tt) * tt) * np.exp(-tt * 45)
    for s in rng.uniform(5, 55, 3):
        i = int(s * SR); L = int(3.5 * SR); tt = np.arange(L) / SR
        f = 55 + 8 * np.sin(2 * np.pi * .4 * tt)
        g = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 3.5) * 0.5
        x[i:i + L] += g + 0.3 * np.sign(g) * 0.2
    return reverb(x, 3.5, 1.6, .55)

# 3. Distant celebration: detuned music-box waltz heard through walls
def party():
    T = t(64); x = np.zeros_like(T)
    notes = [0, 4, 7, 12, 7, 4, 2, 5, 9, 14, 9, 5, -1, 2, 7, 11, 7, 2, 0, 4, 7, 12, 16, 12]
    beat = 0.5; i = 0; pos = 0.0
    while pos < 62:
        n = notes[i % len(notes)]; f = 523.25 * 2 ** ((n + rng.uniform(-.25, .25)) / 12) * (1 - .03 * (pos / 64))
        L = int(1.4 * SR); s = int(pos * SR); tt = np.arange(L) / SR
        tone = (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * f * 2.01 * tt)) * np.exp(-tt * 4)
        e = min(len(x), s + L); x[s:e] += tone[: e - s] * .4
        pos += beat * (1 + rng.uniform(-.06, .09)); i += 1
    crowd = bp(rng.standard_normal(len(T)), 250, 900) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * .05 * T)))
    x = lp(x, 1400) + crowd * .35
    return reverb(x, 4, 1.4, .6)

# 4. Threshold: deep beating drone, slow paper rustle / clock tick
def drone():
    T = t(64)
    x = sum(np.sin(2 * np.pi * f * T) * a for f, a in [(41.2, 1), (41.9, .9), (82.4, .5), (123.6, .25), (61.7, .3)])
    x *= 1 + .3 * np.sin(2 * np.pi * .07 * T)
    tick = np.zeros_like(T)
    for k in range(64):
        i = int(k * SR + (.03 if k % 2 else 0) * SR); L = 600
        tick[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / 60) * .6
    x = x + hp(tick, 2000) + lp(rng.standard_normal(len(T)), 300) * .3
    return reverb(x, 5, 1.0, .45)

# Stingers (non-looping)
def footsteps():
    T = t(9); x = np.zeros_like(T)
    for k in range(9):
        i = int((0.8 + k * .78 + rng.uniform(-.03, .03)) * SR); L = int(.25 * SR); tt = np.arange(L) / SR
        thud = lp(rng.standard_normal(L), 300) * np.exp(-tt * 30) * (0.3 + .7 * k / 8)
        x[i:i + L] += thud
    return reverb(x, 3, 2, .6)

def howl():
    T = t(6)
    f = 180 + 420 * np.sin(np.pi * np.clip(T / 4.5, 0, 1)) ** 2 + 15 * np.sin(2 * np.pi * 6 * T)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + .5 * np.sin(2.02 * ph) + .3 * np.sin(3.1 * ph)) * np.sin(np.pi * np.clip(T / 5, 0, 1))
    x = np.tanh(x * 2.5) + bp(rng.standard_normal(len(T)), 600, 2400) * .4 * np.sin(np.pi * np.clip(T / 5, 0, 1))
    return reverb(x, 4, 1.4, .65)

def blackout():
    T = t(5)
    x = sum(np.sin(2 * np.pi * 60 * k * T) / k for k in range(1, 8))
    env = np.clip(1 - T / .9, 0, 1) ** 2
    pop = np.zeros_like(T); L = 2500; pop[int(.9 * SR):int(.9 * SR) + L] = rng.standard_normal(L) * np.exp(-np.arange(L) / 300) * 2
    return reverb(x * env + pop, 3, 1.2, .5)

def doorbell():  # a cheerful party chime, slightly wrong
    T = t(5); x = np.zeros_like(T)
    for k, n in enumerate([12, 7, 4, 1]):
        f = 523.25 * 2 ** (n / 12); s = int(k * .45 * SR); tt = T[: len(T) - s]
        x[s:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 2.2)
    return reverb(x, 3, 1.5, .5)

for name, fn, loop in [("ambience-waiting-halls-hum", hum, True), ("ambience-undercroft-drip", drip, True),
                       ("ambience-celebration-distant", party, True), ("ambience-threshold-drone", drone, True),
                       ("sting-footsteps", footsteps, False), ("sting-hollow-howl", howl, False),
                       ("sting-lights-die", blackout, False), ("sting-party-chime", doorbell, False)]:
    write(name, fn(), loop); print("wrote", name)
