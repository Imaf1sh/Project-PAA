import pygame
import random
import sys
import math
from collections import deque

pygame.init()

# Ukuran layar default
WIDTH, HEIGHT = 800, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Courier")

# Warna & font
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (90, 90, 90)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
font = pygame.font.SysFont("Arial", 24)

# Tombol
btn_tujuan = pygame.Rect(20, 20, 160, 40)
btn_mulai = pygame.Rect(200, 20, 100, 40)
btn_stop = pygame.Rect(320, 20, 120, 40)
btn_load = pygame.Rect(460, 20, 120, 40)
btn_acak = pygame.Rect(600, 20, 160, 40)

# Load kurir images berdasarkan arah
courier_images = {
    "right": pygame.image.load("assets/kurir0.png"),
    "down": pygame.image.load("assets/kurir1.png"),
    "left": pygame.image.load("assets/kurir2.png"),
    "up": pygame.image.load("assets/kurir3.png"),
}
for key in courier_images:
    courier_images[key] = pygame.transform.scale(courier_images[key], (40, 40))

DIRECTION_VEC = {
    "right": (1, 0),
    "down": (0, 1),
    "left": (-1, 0),
    "up": (0, -1),
}
DIR_ORDER = ["right", "down", "left", "up"]

# Load map
def load_map():
    global map_image
    map_image = pygame.image.load("assets/map.png").convert()

load_map()

# Fungsi cek apakah pixel adalah jalan
def is_road(x, y):
    if 0 <= x < map_image.get_width() and 0 <= y < map_image.get_height():
        pixel = map_image.get_at((x, y))[:3]
        r, g, b = pixel
        return 90 <= r <= 150 and 90 <= g <= 150 and 90 <= b <= 150
    return False

# Titik pickup dan tujuan
pickup_point = (100, 700)
yellow_targets = [
    (775, 811), (737, 147), (185, 140), (571, 818), (74, 259),
    (312, 147), (512, 620), (650, 240), (240, 760), (120, 370)
]

# Pathfinding dengan arah
def find_path_with_direction(start, start_dir, goal):
    queue = deque()
    visited = set()
    queue.append((start, start_dir, []))
    visited.add((start, start_dir))

    while queue:
        (x, y), direction, path = queue.popleft()

        if abs(x - goal[0]) < 5 and abs(y - goal[1]) < 5:
            return path

        # Coba jalan lurus
        dx, dy = DIRECTION_VEC[direction]
        nx, ny = x + dx * 10, y + dy * 10
        if is_road(int(nx), int(ny)) and ((int(nx), int(ny)), direction) not in visited:
            visited.add(((int(nx), int(ny)), direction))
            queue.append(((int(nx), int(ny)), direction, path + [((int(nx), int(ny)), direction)]))

        # Coba belok kiri/kanan
        curr_idx = DIR_ORDER.index(direction)
        for turn in [-1, 1]:
            new_dir = DIR_ORDER[(curr_idx + turn) % 4]
            if ((x, y), new_dir) not in visited:
                visited.add(((x, y), new_dir))
                queue.append(((x, y), new_dir, path + [((x, y), new_dir)]))

    return []

# Status kurir
start_pos = (90, 710)
courier_pos = list(start_pos)
courier_dir = "right"
courier_path = []
path_index = 0

destination = None
pickup_done = False
delivering = False
arrived = False
notif_text = ""
notif_timer = 0
tujuan_ditentukan = False

clock = pygame.time.Clock()
running = True

# Fungsi acak posisi
def randomize_positions():
    global destination, courier_pos, courier_dir, courier_path
    destination = random.choice(yellow_targets)
    courier_pos[0] = random.randint(50, 700)
    courier_pos[1] = random.randint(600, 800)
    courier_dir = random.choice(DIR_ORDER)
    courier_path = []
    print("🔀 Posisi kurir dan tujuan diacak.")

while running:
    screen.fill(WHITE)  
    screen.blit(map_image, (0, 80))  


    # Tombol
    pygame.draw.rect(screen, GRAY, btn_tujuan)
    screen.blit(font.render("Tentukan Tujuan", True, BLACK), (btn_tujuan.x + 5, btn_tujuan.y + 7))

    pygame.draw.rect(screen, GRAY if not tujuan_ditentukan else (0, 200, 0), btn_mulai)
    screen.blit(font.render("Mulai", True, BLACK), (btn_mulai.x + 20, btn_mulai.y + 7))

    pygame.draw.rect(screen, GRAY, btn_stop)
    screen.blit(font.render("Berhenti", True, BLACK), (btn_stop.x + 10, btn_stop.y + 7))

    pygame.draw.rect(screen, GRAY, btn_load)
    screen.blit(font.render("Load Peta", True, BLACK), (btn_load.x + 5, btn_load.y + 7))

    pygame.draw.rect(screen, GRAY, btn_acak)
    screen.blit(font.render("Acak Kurir & Tujuan", True, BLACK), (btn_acak.x + 5, btn_acak.y + 7))

    # Pickup & tujuan
    if tujuan_ditentukan:
        pygame.draw.circle(screen, RED, pickup_point, 10)
        pygame.draw.circle(screen, YELLOW, destination, 10)

    # Notifikasi
    if notif_text:
        notif_surface = font.render(notif_text, True, RED)
        screen.blit(notif_surface, (20, HEIGHT - 40))
        notif_timer -= 1
        if notif_timer <= 0:
            notif_text = ""

    # Gambar kurir
    img = courier_images[courier_dir]
    rect = img.get_rect(center=(courier_pos[0], courier_pos[1]))
    screen.blit(img, rect.topleft)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if btn_tujuan.collidepoint(mouse_pos):
                destination = random.choice(yellow_targets)
                tujuan_ditentukan = True
                pickup_done = False
                courier_pos = list(start_pos)
                courier_dir = "right"
                print("📍 Pickup dan tujuan ditentukan.")

            elif btn_mulai.collidepoint(mouse_pos) and tujuan_ditentukan:
                courier_path = find_path_with_direction(tuple(courier_pos), courier_dir, pickup_point)
                path_index = 0
                delivering = True
                print("🚚 Kurir mulai bergerak.")

            elif btn_stop.collidepoint(mouse_pos):
                delivering = False
                arrived = False
                tujuan_ditentukan = False
                courier_pos = list(start_pos)
                courier_path = []
                print("⏹️ Kurir dihentikan.")

            elif btn_load.collidepoint(mouse_pos):
                load_map()
                print("🗺️ Peta dimuat ulang.")

            elif btn_acak.collidepoint(mouse_pos):
                randomize_positions()

    # Gerakan kurir mengikuti path
    if delivering and path_index < len(courier_path):
        next_pos, next_dir = courier_path[path_index]
        courier_dir = next_dir
        dx = next_pos[0] - courier_pos[0]
        dy = next_pos[1] - courier_pos[1]
        dist = math.hypot(dx, dy)
        if dist > 1:
            courier_pos[0] += dx / dist * 2
            courier_pos[1] += dy / dist * 2
        else:
            path_index += 1

        if path_index >= len(courier_path):
            if not pickup_done:
                pickup_done = True
                courier_path = find_path_with_direction(pickup_point, courier_dir, destination)
                path_index = 0
                print("📦 Pickup selesai. Menuju tujuan...")
            else:
                delivering = False
                arrived = True
                print("🎉 Paket berhasil dikirim!")

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
