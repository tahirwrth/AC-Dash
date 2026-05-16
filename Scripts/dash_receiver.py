import os
import socket
import pygame
import json
import time
import math

# skeleton keys for R36S - adjust or remove as necessary
# fb0 driver assumes R36S
if os.path.exists("/dev/fb0"):
    os.environ["SDL_VIDEODRIVER"] = "fbcon"
    os.environ["SDL_FBDEV"] = "/dev/fb0"
    os.environ["SDL_NOMOUSE"] = "1"
    os.environ["SDL_MOUSEDEV"] = "/dev/null"
    os.environ["SDL_MOUSEDRV"] = "dummy"
    cursor_visible = False
else:
    # fallback - let pygame assume values
    cursor_visible = True

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

pygame.init()
pygame.joystick.init()

# should auto-detect resolution - adjust if incorrect
screen_info = pygame.display.Info()
WIDTH = screen_info.current_w
HEIGHT = screen_info.current_h

W_SCALE = WIDTH / 640.0
H_SCALE = HEIGHT / 480.0
SCALE = H_SCALE  

# initialising R36S gamepad for exit buttons
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
clock = pygame.time.Clock()

# typography - font sizes
font_gear = pygame.font.SysFont(None, int(370 * SCALE))
font_speed = pygame.font.SysFont(None, int(120 * SCALE))
font_delta = pygame.font.SysFont(None, int(55 * SCALE)) 
font_tire = pygame.font.SysFont(None, int(45 * SCALE)) 
font_msg = pygame.font.SysFont(None, int(40 * SCALE))
font_pl = pygame.font.SysFont(None, int(80 * SCALE), bold=True)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5005))
sock.setblocking(False)

# dash state
last_data_time = 0
last_delta = 0.0
delta_history = [] # buffer for delta bar
visual_bar_width = 0.0
last_gear, last_speed = "N", "0"
smoothed_rpm, max_rpm = 0, 7000
t_press, t_temps = [0.0]*4, [0]*4
current_slip, pit_limiter, current_delta = 0, 0, 0.0

def get_temp_color(temp):
    if temp < 75:
        ratio = max(0, (temp - 20) / (75 - 20))
        if ratio < 0.5: return (0, int(200 * (ratio * 2)), 255)
        else: return (0, 255, int(255 * (1 - (ratio - 0.5) * 2)))
    elif temp <= 95: return (0, 255, 0)
    else:
        ratio = min(1.0, (temp - 95) / (115 - 95))
        if ratio < 0.5: return (int(255 * (ratio * 2)), 255, 0)
        else: return (255, int(255 * (1 - (ratio - 0.5) * 2)), 0)

def draw_rpm_arc(surf, center, radius, rpm, max_rpm):
    if max_rpm <= 0: max_rpm = 7000
    pct = min(rpm / max_rpm, 1.0)
    rect = pygame.Rect(center[0]-radius, center[1]-radius, radius*2, radius*2)
    pygame.draw.arc(surf, (35, 35, 35), rect, math.radians(-45), math.radians(225), int(6 * SCALE))
    if pct > 0.01:
        color = (0, 255, 0) if pct < 0.75 else (255, 220, 0)
        if pct >= 0.92:
            pulse = (math.sin(time.time() * 15) + 1) / 2
            color = (int(100 + (pulse * 155)), 0, 0)
        pygame.draw.arc(surf, color, rect, math.radians(220), math.radians(225), int(22 * SCALE))
        if pct > 0.02: pygame.draw.arc(surf, color, rect, math.radians(225 - (pct * 270)), math.radians(222), int(22 * SCALE))

running = True
while running:
    # network loop
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            tele = json.loads(data.decode())
            last_speed, last_gear = str(tele.get("speed", 0)), str(tele.get("gear", "N"))
            raw_rpm, max_rpm = tele.get("rpm", 0), tele.get("max_rpm", 7000)
            t_press, t_temps = tele.get("p", [0.0]*4), tele.get("t", [0]*4)
            current_slip, pit_limiter = tele.get("slip", 0), tele.get("pl", 0)
            new_delta = tele.get("d", 0.0)

            # delta bar
            if last_data_time != 0:
                diff = last_delta - new_delta
                if abs(diff) < 0.2:
                    delta_history.append(diff)
                    if len(delta_history) > 15:
                        delta_history.pop(0)
            
            last_delta = new_delta
            current_delta = new_delta

            smoothed_rpm = (smoothed_rpm * 0.2) + (raw_rpm * 0.8)
            last_data_time = time.time()
        except: break

    # handle R36S buttons for exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 13: # Start: Exit
                running = False
            if event.button == 12: # Select: Launch ES
                os.system("clear > /dev/tty1")
                os.system("systemctl start emulationstation &")
                running = False

    screen.fill((5, 5, 5))

    if time.time() - last_data_time < 2.0:
        # blinking slip indicators
        if current_slip > 1.2 and (pygame.time.get_ticks() // 50) % 2 == 0:
            pygame.draw.rect(screen, (0, 120, 255), (int(20 * W_SCALE), int(100 * H_SCALE), int(15 * W_SCALE), int(280 * H_SCALE)))
            pygame.draw.rect(screen, (0, 120, 255), (WIDTH - int(35 * W_SCALE), int(100 * H_SCALE), int(15 * W_SCALE), int(280 * H_SCALE)))

        # rpm
        arc_center = (WIDTH // 2, int(230 * H_SCALE))
        draw_rpm_arc(screen, arc_center, int(215 * SCALE), smoothed_rpm, max_rpm)

        # gear handling
        gear_surf = font_gear.render(last_gear, True, (255, 255, 255))
        gx, gy = WIDTH // 2 - gear_surf.get_width() // 2, arc_center[1] - gear_surf.get_height() // 2 - int(15 * SCALE)
        screen.blit(gear_surf, (gx, gy))
        if pit_limiter:
            pl_surf = font_pl.render("PL", True, (255, 255, 0))
            screen.blit(pl_surf, (gx - pl_surf.get_width() - int(15 * W_SCALE), arc_center[1] - pl_surf.get_height() // 2))

        # lap delta reading
        delta_color = (0, 255, 0) if current_delta <= 0 else (255, 0, 0)
        delta_surf = font_delta.render(f"{current_delta:+.2f}", True, delta_color)
        screen.blit(delta_surf, (WIDTH // 2 - delta_surf.get_width() // 2, int(310 * H_SCALE)))

        # delta change bar indicator
        bar_h = int(12 * H_SCALE)
        
        # using buffer average for change in delta
        if delta_history:
            avg_diff = sum(delta_history) / len(delta_history)
            target_width = avg_diff * 25000 * W_SCALE
        else:
            target_width = 0

        # linear interpolation to help reduce flicker
        visual_bar_width += (target_width - visual_bar_width) * 0.05
        
        clamped_w = max(-WIDTH // 2, min(WIDTH // 2, visual_bar_width))

        if clamped_w > 1: # gaining
            pygame.draw.rect(screen, (0, 200, 0), (WIDTH // 2, HEIGHT - bar_h, clamped_w, bar_h))
        elif clamped_w < -1: # losing
            pygame.draw.rect(screen, (200, 0, 0), (WIDTH // 2 + clamped_w, HEIGHT - bar_h, abs(clamped_w), bar_h))

        # speed reading
        speed_surf = font_speed.render(last_speed, True, (0, 230, 0) if int(last_speed) > 0 else (120, 120, 120))
        screen.blit(speed_surf, (WIDTH // 2 - speed_surf.get_width() // 2, int(355 * H_SCALE)))
        unit_surf = font_msg.render("MPH", True, (80, 80, 80))
        ux, uy = WIDTH // 2 - unit_surf.get_width() // 2, int(435 * H_SCALE)
        screen.blit(unit_surf, (ux, uy))

        # tyre pressures reading
        positions = [
            (int(25 * W_SCALE), int(25 * H_SCALE)), 
            (WIDTH - int(25 * W_SCALE), int(25 * H_SCALE)), 
            (int(25 * W_SCALE), HEIGHT - int(25 * H_SCALE) - bar_h),
            (WIDTH - int(25 * W_SCALE), HEIGHT - int(25 * H_SCALE) - bar_h)
        ]
        for i, pos in enumerate(positions):
            val_surf = font_tire.render(f"{t_press[i]}", True, get_temp_color(t_temps[i]))
            screen.blit(val_surf, (pos[0] - (val_surf.get_width() if pos[0] > WIDTH // 2 else 0), pos[1] - (val_surf.get_height() if pos[1] > HEIGHT // 2 else 0)))
    else:
        waiting_surf = font_msg.render("READY FOR ASSETTO", True, (40, 40, 40))
        screen.blit(waiting_surf, (WIDTH // 2 - waiting_surf.get_width() // 2, HEIGHT // 2 - waiting_surf.get_height() // 2))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()