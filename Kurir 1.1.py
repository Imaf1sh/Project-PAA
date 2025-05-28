import pygame
import random
import sys
from collections import deque
import math

pygame.init()

# Ukuran layar
WIDTH, HEIGHT = 800, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kurir Antar Barang")

# Load gambar
map_image = pygame.image.load("map.jpg").convert()
courier_image = pygame.image.load("kurir.png")
courier_image = pygame.transform.scale(courier_image, (40, 40))

# Warna & font
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (90, 90, 90)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
font = pygame.font.SysFont("Arial", 24)

# Tombol
btn_tujuan = pygame.Rect(20, 20, 160, 40)
btn_mulai = pygame.Rect(200, 20, 100, 40)
btn_stop = pygame.Rect(320, 20, 120, 40)

# Pickup point
pickup_point = (100, 700)

# Titik tujuan berdasarkan warna kuning pada map (disesuaikan dari koordinat yang benar-benar kuning)
yellow_targets = [
    (775, 811), (737, 147), (185, 140), (571, 818), (74, 259),
    (312, 147), (512, 620), (650, 240), (240, 760), (120, 370)
]

# Fungsi cek jalan (jalan bisa abu-abu gelap atau kuning)
def is_road(x, y):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        pixel = map_image.get_at((x, y))[:3]
        return pixel == (90, 90, 90) or pixel == (255, 255, 0)
    return False

# BFS untuk cari jalur
def find_path(start, goal):
    if not is_road(start[0], start[1]):
        return []
    queue = deque()
    queue.append((start, [start]))
    visited = set()
    visited.add(start)

    while queue:
        (x, y), path = queue.popleft()
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in visited and is_road(nx, ny):
                visited.add((nx, ny))
                if abs(nx - goal[0]) < 5 and abs(ny - goal[1]) < 5:
                    return path + [(nx, ny)]
                queue.append(((nx, ny), path + [(nx, ny)]))
    return []

# Posisi awal
start_pos = (90, 710)
courier_pos = list(start_pos)
courier_angle = 0

# Status
pickup_done = False
destination = None
path = []
path_index = 0
delivering = False
arrived = False
tujuan_ditentukan = False
notif_text = ""
notif_timer = 0

clock = pygame.time.Clock()
running = True
while running:
    screen.blit(map_image, (0, 0))

    # Tombol
    pygame.draw.rect(screen, GRAY, btn_tujuan)
    screen.blit(font.render("Tentukan Tujuan", True, BLACK), (btn_tujuan.x + 5, btn_tujuan.y + 7))

    pygame.draw.rect(screen, GRAY if not tujuan_ditentukan else GREEN, btn_mulai)
    screen.blit(font.render("Mulai", True, BLACK), (btn_mulai.x + 20, btn_mulai.y + 7))

    if arrived:
        pygame.draw.rect(screen, GREEN, btn_stop)
        screen.blit(font.render("Berhenti", True, BLACK), (btn_stop.x + 10, btn_stop.y + 7))

    # Gambar titik tujuan dan pickup
    if tujuan_ditentukan:
        pygame.draw.circle(screen, RED, pickup_point, 10)
        pygame.draw.circle(screen, YELLOW, destination, 10)
        screen.blit(font.render("Pickup", True, BLACK), (pickup_point[0] + 10, pickup_point[1]))
        screen.blit(font.render("Tujuan", True, BLACK), (destination[0] + 10, destination[1]))

    # Tampilkan notifikasi jika ada
    if notif_text:
        notif_surface = font.render(notif_text, True, RED)
        screen.blit(notif_surface, (20, HEIGHT - 40))
        notif_timer -= 1
        if notif_timer <= 0:
            notif_text = ""

    # Rotasi kurir
    rotated_courier = pygame.transform.rotate(courier_image, -courier_angle)
    rect = rotated_courier.get_rect(center=(courier_pos[0], courier_pos[1]))
    screen.blit(rotated_courier, rect.topleft)

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
                path = []
                path_index = 0
                delivering = False
                arrived = False
                print("📍 Pickup dan tujuan ditentukan.")

            elif btn_mulai.collidepoint(mouse_pos) and tujuan_ditentukan:
                path = find_path(tuple(courier_pos), pickup_point)
                if not path:
                    delivering = False
                    notif_text = "❌ Tidak ditemukan jalur ke pickup."
                    notif_timer = 180  # tampilkan notifikasi selama 3 detik (180 frame @60fps)
                    print(notif_text)
                else:
                    path_index = 0
                    delivering = True
                    pickup_done = False
                    arrived = False

            elif btn_stop.collidepoint(mouse_pos) and arrived:
                delivering = False
                arrived = False
                tujuan_ditentukan = False
                courier_pos = list(start_pos)
                path = []
                print("🔄 Kurir direset.")

    # Gerak kurir
    if delivering and path_index < len(path):
        target_pos = path[path_index]
        dx = target_pos[0] - courier_pos[0]
        dy = target_pos[1] - courier_pos[1]
        distance = math.hypot(dx, dy)
        if distance > 0:
            move_x = dx / distance * 2  # kecepatan
            move_y = dy / distance * 2
            courier_pos[0] += move_x
            courier_pos[1] += move_y

            # Rotasi kurir sesuai arah gerak
            courier_angle = math.degrees(math.atan2(-move_y, move_x))

            if distance < 2:
                path_index += 1

        elif distance <= 2:
            path_index += 1

        if path_index >= len(path):
            if not pickup_done:
                pickup_done = True
                path = find_path(pickup_point, destination)
                path_index = 0
                print("📦 Paket dijemput. Menuju tujuan...")
            else:
                arrived = True
                delivering = False
                print("🏁 Paket berhasil dikirim!")

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
