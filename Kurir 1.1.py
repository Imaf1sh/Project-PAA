import pygame
import random
import sys
from collections import deque

pygame.init()

# Ukuran dan layar
WIDTH, HEIGHT = 768, 768
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
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
font = pygame.font.SysFont("Arial", 24)

# Tombol
btn_tujuan = pygame.Rect(20, 20, 160, 40)
btn_mulai = pygame.Rect(200, 20, 100, 40)
btn_stop = pygame.Rect(320, 20, 120, 40)

# Posisi rumah-rumah (titik kuning di map)
houses = [
    (80, 50), (250, 50), (430, 50), (600, 50),
    (100, 220), (300, 220), (520, 220),
    (90, 420), (300, 420), (520, 420),
    (80, 610), (250, 610), (430, 610), (600, 610),
]

# Fungsi cek apakah piksel adalah jalan (toleransi warna)
def is_road(x, y):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        r, g, b = map_image.get_at((x, y))[:3]
        return abs(r - DARK_GRAY[0]) < 20 and abs(g - DARK_GRAY[1]) < 20 and abs(b - DARK_GRAY[2]) < 20
    return False

# Fungsi BFS mencari jalur
def find_path(start, goal):
    print(f"🔍 Mencari jalur dari {start} ke {goal}...")
    if not is_road(start[0], start[1]):
        print("❌ Titik awal bukan jalan!")
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
                    print("✅ Jalur ditemukan!")
                    return path + [(nx, ny)]

                queue.append(((nx, ny), path + [(nx, ny)]))

    print("❌ Tidak ditemukan jalur!")
    return []

# Titik awal kurir di kiri atas (misalnya jalan di pojok kiri atas)
start_pos = (70, 70)
courier_pos = list(start_pos)

# Status
destination = None
path = []
path_index = 0
delivering = False
arrived = False
tujuan_ditentukan = False

# Loop utama
clock = pygame.time.Clock()
running = True
while running:
    screen.blit(map_image, (0, 0))

    # Gambar tombol
    pygame.draw.rect(screen, GRAY, btn_tujuan)
    screen.blit(font.render("Tentukan Tujuan", True, BLACK), (btn_tujuan.x + 5, btn_tujuan.y + 7))

    pygame.draw.rect(screen, GRAY if not tujuan_ditentukan else GREEN, btn_mulai)
    screen.blit(font.render("Mulai", True, BLACK), (btn_mulai.x + 20, btn_mulai.y + 7))

    if arrived:
        pygame.draw.rect(screen, GREEN, btn_stop)
        screen.blit(font.render("Berhenti", True, BLACK), (btn_stop.x + 10, btn_stop.y + 7))

    # Gambar tujuan
    if destination:
        pygame.draw.circle(screen, RED, destination, 10)
        screen.blit(font.render("Tujuan", True, BLACK), (destination[0] + 15, destination[1]))

    # Gambar kurir
    screen.blit(courier_image, courier_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if btn_tujuan.collidepoint(mouse_pos):
                destination = random.choice(houses)
                tujuan_ditentukan = True
                courier_pos = list(start_pos)
                path = []
                path_index = 0
                delivering = False
                arrived = False
                print("📍 Tujuan ditentukan:", destination)

            elif btn_mulai.collidepoint(mouse_pos) and tujuan_ditentukan:
                path = find_path(start_pos, destination)
                path_index = 0
                courier_pos = list(start_pos)
                delivering = True if path else False
                arrived = False
                if not path:
                    print("⚠️ Tidak bisa menemukan jalur ke rumah tujuan!")

            elif btn_stop.collidepoint(mouse_pos) and arrived:
                delivering = False
                arrived = False
                tujuan_ditentukan = False
                destination = None
                courier_pos = list(start_pos)
                path = []
                print("🔄 Kurir direset ke awal.")

    # Gerakkan kurir
    if delivering and path_index < len(path):
        courier_pos = list(path[path_index])
        path_index += 1
        if path_index == len(path):
            arrived = True
            delivering = False
            print("🏁 Kurir sampai ke tujuan!")

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
