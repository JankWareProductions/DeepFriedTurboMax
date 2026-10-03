import pygame as pg, sys, random, math
pg.init(); pg.mixer.init(22050, -16, 1, 512)

W, H, CLOCK = 800, 450, pg.time.Clock()
SCREEN = pg.display.set_mode((W, H))
pg.display.set_caption("DEEP FRIED TURBO MAX")

BG, PLAT, SPK, PLR, WHT, UI, ALT = (255,0,255), (0,255,0), (255,255,0), (0,255,255), (255,255,255), (0,0,0), (255,0,0)
deaths, current_level, camera_x, show_spikes, crash_state, crash_timer, flash_timer = 0, 1, 0, False, False, 0, 0
px, py, pw, ph, p_vx, p_vy, p_speed, gravity, jump_pow, grounded, j_count, j_held = 60, 200, 25, 25, 0, 0, 5.2, 0.45, -10.5, False, 0, False
last_switch, inverted, lag_queue, blocks, player_history, game_state, reporting_state, report_timer, report_msg = pg.time.get_ticks(), False, [], [], [], 'TITLE', False, 0, ""

move_l_pressed, move_r_pressed = False, False

def sf_snd(f, d, t="square"):
    b = bytearray()
    for i in range(int(22050 * (d / 1000.0))):
        v = 16383 if math.sin(2 * math.pi * f * (i / 22050)) >= 0 else -16384 if t == "square" else random.randint(-32768, 32767)
        b.extend(v.to_bytes(2, 'little', signed=True))
    return pg.mixer.Sound(buffer=bytes(b))

def play_bgm(dc):
    t = max(40, 150 - (dc * 10)); buf = bytearray()
    for n in [98.0, 139.2, 221.7, 92.5, 311.1, 49.3]:
        for i in range(int(22050 * (t / 1000.0))):
            v = 15000 if math.sin(2 * math.pi * (n + random.uniform(-15, 15)) * (i / 22050)) >= 0 else -15000
            v = random.randint(-30000, 30000) if random.random() < 0.15 else v
            buf.extend(v.to_bytes(2, 'little', signed=True))
    try: pg.mixer.Channel(0).play(pg.mixer.Sound(buffer=bytes(buf)), loops=-1)
    except: pass

try: s_jmp, s_dth, s_swp = sf_snd(261, 150), sf_snd(70, 500, "noise"), sf_snd(880, 250)
except:
    class Dummy:
        def play(self): pass
    s_jmp = s_dth = s_swp = Dummy()
def build_level(lvl):
    global blocks, show_spikes, px, py, p_vx, p_vy, j_count, last_switch, inverted, player_history, lag_queue, move_l_pressed, move_r_pressed, j_held
    show_spikes, px, py, p_vx, p_vy, j_count, inverted, move_l_pressed, move_r_pressed, j_held = False, 60, 200, 0, 0, 0, False, False, False, False
    player_history.clear(); lag_queue.clear()
    for _ in range(10): lag_queue.append({"l": False, "r": False, "j": False})
    pg.event.pump(); last_switch = pg.time.get_ticks(); play_bgm(deaths)
    if lvl == 1: blocks = [{"x": 0, "y": 340, "w": 250, "h": 60, "m": "floor"}, {"x": 340, "y": 290, "w": 110, "h": 20, "m": "crumble", "t": 0}, {"x": 560, "y": 230, "w": 100, "h": 20, "m": "floor"}, {"x": 740, "y": 230, "w": 120, "h": 20, "m": "troll_fall"}, {"x": 960, "y": 300, "w": 150, "h": 20, "m": "floor"}, {"x": 1200, "y": 240, "w": 100, "h": 20, "m": "crumble", "t": 0}, {"x": 1400, "y": 180, "w": 100, "h": 20, "m": "troll_spike"}, {"x": 1650, "y": 220, "w": 120, "h": 20, "m": "floor"}, {"x": 1880, "y": 260, "w": 100, "h": 20, "m": "crumble", "t": 0}, {"x": 2120, "y": 200, "w": 90, "h": 20, "m": "win"}]
    elif lvl == 2: blocks = [{"x": 0, "y": 340, "w": 200, "h": 60, "m": "floor"}, {"x": 280, "y": 270, "w": 90, "h": 20, "m": "troll_spike"}, {"x": 460, "y": 220, "w": 120, "h": 20, "m": "floor"}, {"x": 680, "y": 280, "w": 100, "h": 20, "m": "crumble", "t": 0}, {"x": 900, "y": 210, "w": 80, "m": "troll_fall"}, {"x": 1100, "y": 160, "w": 130, "h": 20, "m": "floor"}, {"x": 1350, "y": 220, "w": 100, "h": 20, "m": "troll_spike"}, {"x": 1580, "y": 280, "w": 120, "h": 20, "m": "crumble", "t": 0}, {"x": 1820, "y": 210, "w": 110, "h": 20, "m": "floor"}, {"x": 2040, "y": 160, "w": 90, "h": 20, "m": "troll_fall"}, {"x": 2260, "y": 210, "w": 120, "h": 20, "m": "troll_spike"}, {"x": 2500, "y": 160, "w": 90, "h": 20, "m": "win"}]
    else: blocks = [{"x": 0, "y": 340, "w": 150, "h": 60, "m": "floor"}, {"x": 220, "y": 290, "w": 80, "h": 20, "m": "crumble", "t": 0}, {"x": 380, "y": 230, "w": 80, "h": 20, "m": "troll_spike"}, {"x": 540, "y": 180, "w": 80, "h": 20, "m": "troll_fall"}, {"x": 700, "y": 230, "w": 100, "h": 20, "m": "crumble", "t": 0}, {"x": 880, "y": 280, "w": 120, "h": 20, "m": "troll_spike"}, {"x": 1080, "y": 220, "w": 80, "h": 20, "m": "floor"}, {"x": 1260, "y": 170, "w": 80, "h": 20, "m": "troll_fall"}, {"x": 1440, "y": 220, "w": 100, "h": 20, "m": "crumble", "t": 0}, {"x": 1640, "y": 270, "w": 90, "h": 20, "m": "troll_spike"}, {"x": 2400, "y": 270, "w": 100, "h": 20, "m": "troll_spike"}, {"x": 2600, "y": 200, "w": 80, "h": 20, "m": "win"}]

fnt, b_fnt, huge_fnt = pg.font.SysFont("impact", 18), pg.font.SysFont("comic sans ms", 24, bold=True), pg.font.SysFont("impact", 48); build_level(current_level)

while True:
    now = pg.time.get_ticks()
    if game_state == 'TITLE':
        for e in pg.event.get():
            if e.type == pg.QUIT: pg.quit(); sys.exit()
            if e.type == pg.KEYDOWN or e.type == pg.MOUSEBUTTONDOWN: game_state = 'PLAYING'; build_level(1)
        SCREEN.fill(BG if now % 200 < 100 else ALT); SCREEN.blit(huge_fnt.render("DEEP FRIED TURBO MAX", True, PLR), (W // 2 - 200, H // 3)); SCREEN.blit(b_fnt.render("PRESS ANY KEY TO START THE RECKONING", True, SPK), (W // 2 - 250, H // 2 + 30)); SCREEN.blit(fnt.render("F1 IN-GAME TO FILE COMPLAINT", True, WHT), (W // 2 - 120, H - 40)); pg.display.flip(); CLOCK.tick(60); continue
    if crash_state:
        if now - crash_timer > 3000: crash_state, current_level, deaths = False, 1, 0; build_level(1)
        SCREEN.fill((255, 0, 0)); SCREEN.blit(b_fnt.render("SYSTEM FAILURE!!! Save data fried.", True, (255, 255, 0)), (40, 150)); pg.display.flip()
        for e in pg.event.get(): (pg.quit(), sys.exit()) if e.type == pg.QUIT else None
        CLOCK.tick(60); continue
    if reporting_state:
        if now - report_timer > 2500: reporting_state = False; deaths += 1; build_level(current_level); continue
        SCREEN.fill(ALT); SCREEN.blit(b_fnt.render("!!! PROCESSING BUG REPORT MODULE !!!", True, SPK), (40, 140)); SCREEN.blit(fnt.render(f"LOGGED ERROR: '{report_msg}'", True, WHT), (40, 190)); SCREEN.blit(fnt.render("RESOLUTION: User error. Deleting level footprints...", True, UI), (40, 230)); pg.display.flip()
        for e in pg.event.get(): (pg.quit(), sys.exit()) if e.type == pg.QUIT else None
        CLOCK.tick(60); continue
    if now - last_switch >= 10000:
        last_switch = now; inverted = not inverted if random.random() < 0.5 else inverted; pg.mixer.Channel(1).play(s_swp) if inverted else None; flash_timer = 15 if inverted else flash_timer

    jump_this_frame = False
    for e in pg.event.get():
        if e.type == pg.QUIT: pg.quit(); sys.exit()
        if e.type == pg.KEYDOWN:
            if e.key == pg.K_F1: print("\n"+"="*40+"\nBUG REPORTING SYSTEM\n"+"="*40); i = input("Specify issue: ").strip(); report_msg = i if i else "Complaining."; reporting_state = True; report_timer = pg.time.get_ticks(); pg.mixer.Channel(1).play(s_dth)
            if e.key in [pg.K_LEFT, pg.K_a]: move_l_pressed = True
            if e.key in [pg.K_RIGHT, pg.K_d]: move_r_pressed = True
            if e.key in [pg.K_SPACE, pg.K_UP, pg.K_w]: jump_this_frame = True
        if e.type == pg.KEYUP:
            if e.key in [pg.K_LEFT, pg.K_a]: move_l_pressed = False
            if e.key in [pg.K_RIGHT, pg.K_d]: move_r_pressed = False

    if reporting_state: continue

    wl, wr = move_l_pressed, move_r_pressed
    if inverted: wl, wr = wr, wl

    lag_queue.append({"l": wl, "r": wr, "j": jump_this_frame}); inp = lag_queue.pop(0) if len(lag_queue) > 8 else {"l": False, "r": False, "j": False}
    p_vx = p_speed if inp["r"] else (-p_speed if inp["l"] else 0); p_vy += gravity; px, py = px + p_vx, py + p_vy
    
    if inp["j"]:
        if grounded:
            p_vy = jump_pow; grounded = False; j_count = 1; j_held = True; pg.mixer.Channel(1).play(s_jmp)
        elif j_count < 2 and not j_held:
            p_vy = jump_pow; j_count += 1; j_held = True; pg.mixer.Channel(1).play(s_jmp)
        else:
            j_held = True
    else:
        j_held = False

    if px < 0: px = 0
    if py > H: pg.mixer.Channel(1).play(s_dth); deaths += 1; build_level(current_level); continue
    camera_x = max(0, px - 250); grounded, pr = False, pg.Rect(px, py, pw, ph); player_history.append((px, py)); player_history.pop(0) if len(player_history) > 10 else None
    for b in blocks:
        if b["w"] <= 0: continue
        br = pg.Rect(b["x"], b["y"], b["w"], b["h"])
        if b["m"] == "troll_spike" and abs(px - b["x"]) < 180: show_spikes = True
        if b["m"] == "crumble" and b["t"] > 0: b["t"] += 1; b["w"] = 0 if b["t"] > 25 else b["w"]; continue
        if pr.colliderect(br):
            if b["m"] == "troll_fall": b["w"] = 0; continue
            if b["m"] == "crumble" and b["t"] == 0: b["t"] = 1
            if b["m"] == "troll_spike" and p_vy > 0: show_spikes = True; pg.mixer.Channel(1).play(s_dth); deaths += 1; build_level(current_level); break
            if b["m"] == "win":
                if current_level < 3: current_level += 1; build_level(current_level)
                else: pg.mixer.Channel(1).play(s_dth); crash_state, crash_timer = True, pg.time.get_ticks()
                break
            if p_vy > 0 and (py + ph - p_vy) <= b["y"] + 8: py, p_vy, grounded, j_count, pr.y = b["y"] - ph, 0, True, 0, b["y"] - ph
    sx, sy = random.randint(-5, 5), random.randint(-5, 5)
    if flash_timer > 0: flash_timer -= 1; SCREEN.fill(WHT if flash_timer % 2 == 0 else ALT)
    else: SCREEN.fill(BG)
    for idx, (tx, ty) in enumerate(player_history): pg.draw.rect(SCREEN, (255,255,0) if idx%2==0 else (255,0,0), pg.Rect(tx-camera_x+sx, ty+sy, pw, ph))
    for b in blocks:
        if b["w"] <= 0: continue
        rx, by_s = b["x"] - camera_x + sx, b["y"] + sy; c = (0,0,255) if b["m"] == "win" else (SPK if (b["m"] == "troll_spike" and show_spikes) else ((255,255,255) if (b["m"] == "crumble" and b["t"] > 0) else PLAT))
        pg.draw.rect(SCREEN, c, pg.Rect(rx, by_s, b["w"], b["h"]))
        if b["m"] == "troll_spike" and show_spikes: [pg.draw.polygon(SCREEN, ALT, [(rx+i, by_s), (rx+i+6, by_s-12), (rx+i+12, by_s)]) for i in range(0, b["w"], 12)]
        if b["m"] == "win": SCREEN.blit(fnt.render("!!! WIN !!!", True, WHT), (rx + 5, by_s + 2))
    pg.draw.rect(SCREEN, PLR, pg.Rect(px - camera_x + sx, py + sy, pw, ph)); SCREEN.blit(fnt.render(f"FAILURES: {deaths}", True, UI), (20, 20)); SCREEN.blit(fnt.render(f"ROULETTE SWAP: {max(0, 10 - int((now - last_switch) / 1000))}s", True, UI), (20, 45))
    if inverted: SCREEN.blit(b_fnt.render("!!! CONTROL CRITICAL FAILURE !!!", True, ALT), (220, 15))
    else: SCREEN.blit(fnt.render("STATUS MODULE RUNNING NORMAL...", True, UI), (480, 20))
    pg.display.flip(); CLOCK.tick(60)
