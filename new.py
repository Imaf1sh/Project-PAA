import sys
import random
import heapq
from PIL import Image
from tkinter import Tk, filedialog

try:
    import pygame
except ModuleNotFoundError:
    print("Error: Modul 'pygame' tidak ditemukan. Silakan instal dengan menjalankan 'pip install pygame' terlebih dahulu.")
    sys.exit()

pygame.init()

DIRECTIONS = ['up', 'right', 'down', 'left']
DIR_VECTORS = {
    'up': (0, -1),
    'right': (1, 0),
    'down': (0, 1),
    'left': (-1, 0)
}

MAX_WINDOW_WIDTH = 1280
MAX_WINDOW_HEIGHT = 800
UI_HEIGHT = 60
TILE_SIZE = 20

kurir = {
    'x': 0,
    'y': 0,
    'direction': 'right'
}

jalan_matrix = []
path_result = []
path_index = 0
moving = False
paket_diambil = False
goal = (0, 0)

screen = None
font = None
start_button = pygame.Rect(10, 10, 100, 30)
reset_button = pygame.Rect(120, 10, 180, 30)
load_button = pygame.Rect(320, 10, 120, 30)
stop_button = pygame.Rect(450, 10, 100, 30)


def load_map(path):
    global jalan_matrix, TILE_SIZE
    img = Image.open(path).convert('RGB')
    width, height = img.size
    jalan_matrix = [[False for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            if 90 <= r <= 150 and 90 <= g <= 150 and 90 <= b <= 150:
                jalan_matrix[y][x] = True

    TILE_SIZE = 1  # Satu piksel per tile untuk menyesuaikan ukuran gambar asli
    return width, height


def random_pos():
    h = len(jalan_matrix)
    w = len(jalan_matrix[0])
    while True:
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        if jalan_matrix[y][x]:
            return x, y


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal):
    open_set = []
    heapq.heappush(open_set, (0, (start['x'], start['y'])))
    came_from = {}
    g_score = {(start['x'], start['y']): 0}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dir in DIR_VECTORS.values():
            neighbor = (current[0] + dir[0], current[1] + dir[1])
            if 0 <= neighbor[1] < len(jalan_matrix) and 0 <= neighbor[0] < len(jalan_matrix[0]) and jalan_matrix[neighbor[1]][neighbor[0]]:
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    priority = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (priority, neighbor))
                    came_from[neighbor] = current
    return []


def draw():
    mouse_pos = pygame.mouse.get_pos()
    def get_color(button, base_color, hover_color):
        return hover_color if button.collidepoint(mouse_pos) else base_color
    screen.fill((30, 30, 30))
    for y in range(len(jalan_matrix)):
        for x in range(len(jalan_matrix[0])):
            color = (120, 120, 120) if jalan_matrix[y][x] else (50, 50, 50)
            pygame.draw.rect(screen, color, (x, y + UI_HEIGHT, 1, 1))

    for px, py in path_result:
        pygame.draw.rect(screen, (0, 255, 255), (px, py + UI_HEIGHT, 1, 1))

    flag_color = (255, 255, 0) if not paket_diambil else (255, 0, 0)
    pygame.draw.rect(screen, flag_color, (goal[0], goal[1] + UI_HEIGHT, 1, 1))
    pygame.draw.polygon(screen, (0, 255, 0), get_kurir_shape())

    pygame.draw.rect(screen, get_color(start_button, (70, 130, 180), (100, 160, 210)), start_button)
    pygame.draw.rect(screen, get_color(reset_button, (100, 180, 100), (140, 220, 140)), reset_button)
    pygame.draw.rect(screen, get_color(load_button, (180, 100, 100), (220, 140, 140)), load_button)
    pygame.draw.rect(screen, get_color(stop_button, (180, 50, 50), (220, 80, 80)), stop_button)
    screen.blit(font.render("Start", True, (255, 255, 255)), (start_button.x + 20, start_button.y + 5))
    screen.blit(font.render("Acak Kurir & Tujuan", True, (0, 0, 0)), (reset_button.x + 5, reset_button.y + 5))
    screen.blit(font.render("Load Peta", True, (255, 255, 255)), (load_button.x + 10, load_button.y + 5))
    screen.blit(font.render("Stop", True, (255, 255, 255)), (stop_button.x + 25, stop_button.y + 5))

    pygame.display.flip()


def get_kurir_shape():
    cx = kurir['x']
    cy = kurir['y'] + UI_HEIGHT
    size = 5
    dir = kurir['direction']
    if dir == 'up':
        return [(cx, cy - size), (cx - size, cy + size), (cx + size, cy + size)]
    elif dir == 'down':
        return [(cx, cy + size), (cx - size, cy - size), (cx + size, cy - size)]
    elif dir == 'left':
        return [(cx - size, cy), (cx + size, cy - size), (cx + size, cy + size)]
    elif dir == 'right':
        return [(cx + size, cy), (cx - size, cy - size), (cx - size, cy + size)]


def is_facing_target():
    dx = goal[0] - kurir['x']
    dy = goal[1] - kurir['y']
    if dx == 1 and kurir['direction'] == 'right': return True
    if dx == -1 and kurir['direction'] == 'left': return True
    if dy == 1 and kurir['direction'] == 'down': return True
    if dy == -1 and kurir['direction'] == 'up': return True
    return False

Tk().withdraw()
map_path = filedialog.askopenfilename(title="Pilih Gambar Peta", filetypes=[("Image files", "*.png *.jpg *.bmp")])
if not map_path:
    print("Tidak ada file yang dipilih.")
    sys.exit()

width, height = load_map(map_path)
window_width = width
window_height = height + UI_HEIGHT
screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
font = pygame.font.SysFont(None, 24)
kurir['x'], kurir['y'] = random_pos()
goal = random_pos()

running = True
clock = pygame.time.Clock()
while running:
    draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                path_result = astar(kurir, goal)
                path_index = 0
                moving = True if path_result else False
            elif reset_button.collidepoint(event.pos):
                kurir['x'], kurir['y'] = random_pos()
                goal = random_pos()
                path_result = []
                moving = False
                paket_diambil = False
            elif load_button.collidepoint(event.pos):
                map_path = filedialog.askopenfilename(title="Pilih Gambar Peta", filetypes=[("Image files", "*.png *.jpg *.bmp")])
                if map_path:
                    width, height = load_map(map_path)
                    window_width = width
                    window_height = height + UI_HEIGHT
                    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
                    kurir['x'], kurir['y'] = random_pos()
                    goal = random_pos()
                    path_result.clear()
                    moving = False
                    paket_diambil = False
                    print("[INFO] Peta dimuat ulang.")
            elif stop_button.collidepoint(event.pos):
                moving = False
                path_result.clear()
                print("[INFO] Pergerakan kurir dihentikan.")

    if moving and path_index < len(path_result):
        next_x, next_y = path_result[path_index]
        dx = next_x - kurir['x']
        dy = next_y - kurir['y']
        for dir_name, (vx, vy) in DIR_VECTORS.items():
            if (vx, vy) == (dx, dy):
                kurir['direction'] = dir_name
                break
        kurir['x'], kurir['y'] = next_x, next_y
        path_index += 1
    elif moving and path_index >= len(path_result):
        moving = False
        if is_facing_target():
            if not paket_diambil:
                paket_diambil = True
                goal = random_pos()
                print("[INFO] Paket diambil. Menuju ke tujuan baru.")
            else:
                paket_diambil = False
                print("[INFO] Paket dikirim.")
        else:
            print("[WARNING] Kurir belum menghadap ke arah bendera. Tidak bisa ambil/antar paket.")

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        idx = (DIRECTIONS.index(kurir['direction']) - 1) % 4
        kurir['direction'] = DIRECTIONS[idx]
    if keys[pygame.K_RIGHT]:
        idx = (DIRECTIONS.index(kurir['direction']) + 1) % 4
        kurir['direction'] = DIRECTIONS[idx]
    if keys[pygame.K_UP]:
        dx, dy = DIR_VECTORS[kurir['direction']]
        nx, ny = kurir['x'] + dx, kurir['y'] + dy
        if 0 <= ny < len(jalan_matrix) and 0 <= nx < len(jalan_matrix[0]) and jalan_matrix[ny][nx]:
            kurir['x'], kurir['y'] = nx, ny

    clock.tick(5)

pygame.quit()
sys.exit()
