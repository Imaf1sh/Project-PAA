import pygame
import sys
import random
import heapq

pygame.init()
WIDTH, HEIGHT = 1200, 800
GRID_SIZE = 20
ROWS, COLS = HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Kurir - A* Pathfinding")

# Ukuran gambar
GAMBAR_UKURAN = (GRID_SIZE, GRID_SIZE)

# Load gambar
kurir_imgs = {
    "up": pygame.transform.scale(pygame.image.load("kurir mengarah ke atas.png"), GAMBAR_UKURAN),
    "down": pygame.transform.scale(pygame.image.load("kurir mengarah ke bawah.png"), GAMBAR_UKURAN),
    "left": pygame.transform.scale(pygame.image.load("kurir mengarah ke kiri.png"), GAMBAR_UKURAN),
    "right": pygame.transform.scale(pygame.image.load("kurir mengarah ke kanan.png"), GAMBAR_UKURAN)
}
flag_img = pygame.transform.scale(pygame.image.load("Flag.png"), GAMBAR_UKURAN)

# Warna jalan
ROAD_MIN, ROAD_MAX = (90, 90, 90), (150, 150, 150)

# Peta default
map_surface = pygame.Surface((WIDTH, HEIGHT))
map_surface.fill((255, 255, 255))

# Posisi awal
kurir_pos = [0, 0]
kurir_dir = "right"
flag_pos = [30, 30]
path = []
auto_move = False

def is_on_road(x, y):
    try:
        pixel = map_surface.get_at((x, y))[:3]
        return all(ROAD_MIN[i] <= pixel[i] <= ROAD_MAX[i] for i in range(3))
    except:
        return False

def grid_from_map():
    grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLS):
            px, py = x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2
            grid[y][x] = 0 if is_on_road(px, py) else 1
    return grid

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid, start, goal):
    queue = [(0, start)]
    came_from = {}
    cost_so_far = {start: 0}
    while queue:
        _, current = heapq.heappop(queue)
        if current == goal:
            break
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = current[0]+dx, current[1]+dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 0:
                new_cost = cost_so_far[current] + 1
                if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                    cost_so_far[(nx, ny)] = new_cost
                    priority = new_cost + heuristic(goal, (nx, ny))
                    heapq.heappush(queue, (priority, (nx, ny)))
                    came_from[(nx, ny)] = current
    if goal not in came_from: return []
    cur, rev_path = goal, []
    while cur != start:
        rev_path.append(cur)
        cur = came_from[cur]
    rev_path.reverse()
    return rev_path

def draw_scene():
    screen.blit(map_surface, (0, 0))
    screen.blit(flag_img, flag_pos)
    screen.blit(kurir_imgs[kurir_dir], kurir_pos)
    pygame.display.flip()

def update_direction(target):
    dx = target[0] * GRID_SIZE - kurir_pos[0]
    dy = target[1] * GRID_SIZE - kurir_pos[1]
    if abs(dx) > abs(dy):
        return "right" if dx > 0 else "left"
    else:
        return "down" if dy > 0 else "up"

def move_to_grid(grid_pos):
    kurir_pos[0] = grid_pos[0] * GRID_SIZE
    kurir_pos[1] = grid_pos[1] * GRID_SIZE

def acak_posisi():
    while True:
        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)
        if is_on_road(x * GRID_SIZE + 10, y * GRID_SIZE + 10):
            return [x * GRID_SIZE, y * GRID_SIZE]

def load_map(path):
    global map_surface
    try:
        img = pygame.image.load(path)
        map_surface = pygame.transform.scale(img, (WIDTH, HEIGHT))
        print("Peta dimuat.")
    except:
        print("Gagal memuat peta.")

clock = pygame.time.Clock()
print("SPACE = Kurir jalan otomatis (A*)")

while True:
    screen.fill((0,0,0))
    draw_scene()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                auto_move = True
                grid = grid_from_map()
                start = (kurir_pos[0] // GRID_SIZE, kurir_pos[1] // GRID_SIZE)
                goal = (flag_pos[0] // GRID_SIZE, flag_pos[1] // GRID_SIZE)
                path = astar(grid, start, goal)
            elif e.key == pygame.K_r:
                kurir_pos = acak_posisi()
            elif e.key == pygame.K_t:
                flag_pos = acak_posisi()
            elif e.key == pygame.K_l:
                load_map("petaku.png")

    if auto_move and path:
        next_tile = path.pop(0)
        kurir_dir = update_direction(next_tile)
        move_to_grid(next_tile)
        if not path:
            auto_move = False

    clock.tick(10)
