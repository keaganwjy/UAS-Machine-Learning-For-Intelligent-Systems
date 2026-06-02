import pygame
import sys
import cv2
import mediapipe as mp
import numpy as np
import traceback
import random
import threading 
from queue import Queue 

# ==========================================
# WORKER AI THREAD (Berjalan di latar belakang)
# ==========================================
hand_coords_queue = Queue(maxsize=1) 
running = True 

def ai_hand_tracking_thread(queue):
    global running
    print("LOG: Jalur AI Latar Belakang Dinyalakan...")
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("LOG ERROR: Gagal membuka kamera di jalur AI.")
        running = False
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    
    print("LOG: Jalur AI MediaPipe SIAP MENDETEKSI TANGAN.")
    
    while running:
        ret, frame = cap.read()
        if not ret: continue
        
        frame = cv2.flip(frame, 1)
        small_frame = cv2.resize(frame, (160, 120))
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        mp_image = np.ascontiguousarray(rgb_small)
        
        results = hands.process(mp_image)
        
        x_norm, shooting = None, False
        if results.multi_hand_landmarks:
            for lm in results.multi_hand_landmarks:
                x_norm = lm.landmark[0].x 
                if lm.landmark[8].y < lm.landmark[6].y: 
                    shooting = True
        
        if queue.full():
            try: queue.get_nowait() 
            except: pass
        queue.put((frame, x_norm, shooting)) 

    cap.release()
    hands.close()
    print("LOG: Jalur AI Dimatikan.")

# ==========================================
# INISIALISASI DASAR (MAIN THREAD)
# ==========================================
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Vision Control (Ultimate Edition)")

# Daftar Warna 
BLACK, WHITE, GREEN, RED = (0, 0, 0), (255, 255, 255), (0, 255, 0), (255, 0, 0)
GRAY, YELLOW = (150, 150, 150), (255, 255, 0)
CYAN, MAGENTA, ORANGE = (0, 255, 255), (255, 0, 255), (255, 165, 0)

font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 72)
clock = pygame.time.Clock()

game_state = "MENU"
score, lives, level = 0, 3, 1
player_x, player_y = WIDTH // 2, HEIGHT - 50
bullets, aliens = [], []
last_shot_time = 0 
alien_speed_x = 1.5 

frame_surface = pygame.Surface((160, 120))
frame_surface.fill(GRAY)

# ==========================================
# GENERATOR PIXEL ART SPRITES
# ==========================================
def create_sprite(art, color, scale):
    width = len(art[0]) * scale
    height = len(art) * scale
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y, row in enumerate(art):
        for x, char in enumerate(row):
            if char == '#':
                pygame.draw.rect(surface, color, (x * scale, y * scale, scale, scale))
    return surface

alien_art = ["  #     #  ","   #   #   ","  #######  "," ## ### ## ","###########","# ####### #","# #     # #","   ## ##   "]
player_art = ["     #     ","    ###    ","    ###    ","   #####   "," ######### ","###########","###########","###     ###"]
boss_art = ["   #######   ","  #########  "," ### ### ### ","#############"," ##  # #  ## ","  #       #  "]

player_img = create_sprite(player_art, WHITE, 4)
boss_img = create_sprite(boss_art, YELLOW, 5)
alien_colors = [RED, CYAN, MAGENTA, ORANGE]
alien_imgs = [create_sprite(alien_art, color, 3) for color in alien_colors]

# Variabel Boss (Diubah jadi Immortal & Punya Sistem 'Rage')
boss_active = True
boss_rect = pygame.Rect(WIDTH//2, 30, boss_img.get_width(), boss_img.get_height())
boss_rage = 0
boss_speed = 3
boss_bullets, boss_shoot_timer = [], 0

def reset_boss(lvl):
    global boss_active, boss_rage, boss_rect, boss_speed, boss_bullets
    boss_active = True
    boss_rage = 0 # Tingkat kemarahan bos di-reset tiap naik level
    boss_rect.centerx = WIDTH // 2
    boss_speed = 3 + (lvl * 0.5)
    boss_bullets.clear()

def create_aliens(lvl):
    aliens.clear()
    for row in range(4):
        img = alien_imgs[row % len(alien_imgs)]
        for col in range(10):
            rect = pygame.Rect(50 + col * 60, 130 + row * 40, img.get_width(), img.get_height())
            aliens.append({'rect': rect, 'img': img})
            
    calculated_speed = 1.5 + (lvl * 0.3)
    return min(calculated_speed, 4.5) 

def reset_game():
    global score, lives, level, bullets, alien_speed_x
    score, lives, level = 0, 3, 1
    bullets.clear()
    alien_speed_x = create_aliens(level)
    reset_boss(level)

def draw_text(text, font_type, color, x, y, center=False):
    surface = font_type.render(text, True, color)
    rect = surface.get_rect()
    if center: rect.center = (x, y)
    else: rect.topleft = (x, y)
    screen.blit(surface, rect)

def draw_button(text, x, y, w, h, color):
    pygame.draw.rect(screen, color, (x, y, w, h))
    draw_text(text, font, BLACK, x + w//2, y + h//2, center=True)
    return pygame.Rect(x, y, w, h)

# ==========================================
# JALANKAN JALUR AI (THREAD) SEBELUM LOOP UTAMA
# ==========================================
ai_thread = threading.Thread(target=ai_hand_tracking_thread, args=(hand_coords_queue,), daemon=True)
ai_thread.start()

# ==========================================
# MAIN LOOP (JALUR UTAMA / HANYA RENDER)
# ==========================================
try:
    while running:
        # A. BACA DATA AI DARI ANTRIAN
        hand_frame, hand_x, hand_shooting = None, None, False
        
        if not hand_coords_queue.empty():
            try: hand_frame, hand_x, hand_shooting = hand_coords_queue.get_nowait()
            except: pass 

        if hand_frame is not None:
            small_frame = cv2.resize(hand_frame, (160, 120))
            rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            py_frame = np.swapaxes(rgb_small, 0, 1).copy()
            frame_surface = pygame.surfarray.make_surface(py_frame)

        if game_state == "PLAYING" and hand_x is not None:
            player_x = int(hand_x * WIDTH)
            if hand_shooting:
                now = pygame.time.get_ticks()
                if now - last_shot_time > 500:
                    bullets.append(pygame.Rect(player_x - 2, player_y - 15, 5, 15))
                    last_shot_time = now

        player_rect = pygame.Rect(player_x - player_img.get_width()//2, player_y, player_img.get_width(), player_img.get_height())

        # B. EVENT & INPUT MOUSE/KEYBOARD
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p and game_state == "PLAYING": game_state = "PAUSED"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p and game_state == "PAUSED": game_state = "PLAYING"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "MENU":
                    if btn_start.collidepoint(mouse_pos): 
                        draw_text("MEMUAT AI... SABAR BRO!", font, YELLOW, WIDTH//2, 450, center=True)
                        pygame.display.flip()
                        reset_game()
                        game_state = "PLAYING"
                    if btn_exit.collidepoint(mouse_pos): running = False
                elif game_state == "GAME_OVER":
                    if btn_menu.collidepoint(mouse_pos): game_state = "MENU"
                    if btn_restart.collidepoint(mouse_pos): reset_game(); game_state = "PLAYING"

        # C. LOGIKA GAME & RENDER
        screen.fill(BLACK)
        if game_state == "MENU":
            draw_text("SPACE INVADERS", title_font, GREEN, WIDTH//2, 200, center=True)
            btn_start = draw_button("MULAI GAME", 300, 300, 200, 50, WHITE)
            btn_exit = draw_button("KELUAR", 300, 370, 200, 50, GRAY)
            
        elif game_state == "PLAYING":
            # 1. LOGIKA PASUKAN ALIEN
            edge_hit = False
            for a in aliens:
                if a['rect'].right + alien_speed_x >= WIDTH or a['rect'].left + alien_speed_x <= 0:
                    edge_hit = True
                    break 

            if edge_hit:
                alien_speed_x *= -1
                for a in aliens: 
                    a['rect'].y += 20 
            else:
                for a in aliens: 
                    a['rect'].x += alien_speed_x

            # 2. LOGIKA BOSS (Immortal & Makin Marah Kalau Ditembak)
            if boss_active:
                boss_rect.x += boss_speed
                if boss_rect.right >= WIDTH or boss_rect.left <= 0: boss_speed *= -1
                
                now = pygame.time.get_ticks()
                # Makin level tinggi & makin sering ditembak (Rage), makin cepat nembak!
                boss_shoot_delay = max(250, 1500 - (level * 100) - (boss_rage * 50)) 
                
                if now - boss_shoot_timer > boss_shoot_delay: 
                    if random.choice([True, True, False]): 
                        boss_bullets.append(pygame.Rect(boss_rect.centerx - 3, boss_rect.bottom, 6, 20))
                    boss_shoot_timer = now
            
            # 3. Tabrakan Peluru Kita
            for b in bullets[:]:
                b.y -= 10
                hit = False
                
                # Cek kena Boss
                if boss_active and b.colliderect(boss_rect):
                    bullets.remove(b)
                    score += 20 # Dapat poin terus kalau rajin nembak boss
                    boss_rage += 1 # Boss makin marah!
                    
                    # Boss bergerak makin cepat saat marah (Maksimal speed dibatasi 15)
                    if boss_speed > 0:
                        boss_speed = min(boss_speed + 0.5, 15)
                    else:
                        boss_speed = max(boss_speed - 0.5, -15)
                        
                    hit = True
                
                if not hit:
                    for a in aliens[:]:
                        if b.colliderect(a['rect']): 
                            bullets.remove(b)
                            aliens.remove(a)
                            score += 10
                            break
                if not hit and b.y < 0: bullets.remove(b)
            
            # 4. Tabrakan Peluru Boss
            for bb in boss_bullets[:]:
                bb.y += 8
                if bb.y > HEIGHT: boss_bullets.remove(bb)
                elif bb.colliderect(player_rect): 
                    lives -= 1; boss_bullets.clear(); bullets.clear()
                    if lives <= 0: game_state = "GAME_OVER"
                    else: player_x = WIDTH // 2
                    break 
            
            # 5. PINDAH LEVEL (Sekarang HANYA perlu membunuh semua alien kecil)
            if len(aliens) == 0: 
                level += 1
                alien_speed_x = create_aliens(level)
                reset_boss(level)
            
            # 6. Tabrakan Alien vs Kita
            for a in aliens:
                if a['rect'].colliderect(player_rect) or a['rect'].bottom >= HEIGHT:
                    lives -= 1; bullets.clear()
                    if lives <= 0: game_state = "GAME_OVER"
                    else: player_x = WIDTH // 2

            # MENGGAMBAR SPRITE
            screen.blit(player_img, player_rect.topleft)
            for a in aliens: screen.blit(a['img'], a['rect'].topleft)
            for b in bullets: pygame.draw.rect(screen, YELLOW, b)
            for bb in boss_bullets: pygame.draw.rect(screen, MAGENTA, bb)
            if boss_active:
                screen.blit(boss_img, boss_rect.topleft)
                # HP Bar dihapus karena Boss sekarang Abadi!
            
            draw_text(f"Skor: {score} | Level: {level} | Nyawa: {lives}", font, WHITE, 10, 10)
            screen.blit(frame_surface, (WIDTH - 170, 10))
            
        elif game_state == "PAUSED": draw_text("PAUSED", title_font, YELLOW, WIDTH//2, HEIGHT//2, center=True)
        elif game_state == "GAME_OVER":
            draw_text("GAME OVER", title_font, RED, WIDTH//2, 200, center=True)
            btn_menu = draw_button("MENU", 200, 350, 180, 50, GRAY)
            btn_restart = draw_button("ULANG", 420, 350, 180, 50, GREEN)

        pygame.display.flip()
        clock.tick(60)

except BaseException as e: 
    print("\n=== PROGRAM DIHENTIKAN ===")
finally:
    running = False 
    pygame.quit()
    sys.exit()