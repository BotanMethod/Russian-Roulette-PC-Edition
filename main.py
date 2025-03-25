import random
import os
import time
import pygame
import sys
import wave
import struct
from pygame import mixer
from tkinter import messagebox
from tkinter import Tk

# Initialize Pygame
pygame.init()
mixer.init()

# Function to shutdown computer
def shutdown_computer():
    """Shuts down the computer with a warning"""
    try:
        # Stop music before shutdown
        mixer.music.stop()
        
        # Create hidden Tkinter window for messagebox
        root = Tk()
        root.withdraw()
        
        # Show warning
        messagebox.showwarning(
            "Goodbye!",
            "You closed the game. Computer will shutdown in 10 seconds!\n"
            "Press Ctrl+C in terminal to cancel."
        )
        root.destroy()
        
        # Wait before shutdown
        time.sleep(10)
        
        # Shutdown command
        if os.name == 'nt':
            os.system('shutdown /s /t 1')
        else:
            os.system('shutdown -h now')
            
    except Exception as e:
        print(f"Shutdown error: {e}")

# Function to create dummy WAV file
def create_dummy_wav(filename):
    """Creates a silent WAV file"""
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)  # mono
        f.setsampwidth(2)  # 2 bytes per sample
        f.setframerate(44100)  # sample rate
        f.setnframes(44100)  # 1 second of silence
        # Write silent samples
        frames = []
        for i in range(44100):
            frames.append(struct.pack('<h', 0))
        f.writeframes(b''.join(frames))

# Create source folder if doesn't exist
if not os.path.exists('source'):
    os.makedirs('source')
    # Create dummy sound files
    create_dummy_wav('source/shot.wav')
    create_dummy_wav('source/click.wav')
    create_dummy_wav('source/reload.wav')
    # Create empty music files
    open('source/menu_music.mp3', 'a').close()
    open('source/game_music.mp3', 'a').close()

# Window dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Russian Roulette: PC Edition")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)

# Fonts
font_large = pygame.font.SysFont('Arial', 48)
font_medium = pygame.font.SysFont('Arial', 36)
font_small = pygame.font.SysFont('Arial', 24)

# Sound loading with error handling
def load_sound(filename):
    try:
        return mixer.Sound(filename)
    except:
        print(f"Failed to load sound: {filename}")
        return mixer.Sound(buffer=bytearray(100))

def load_music(filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            mixer.music.load(filename)
            return True
        except:
            print(f"Failed to load music: {filename}")
    return False

# Load sounds
shot_sound = load_sound('source/shot.wav')
click_sound = load_sound('source/click.wav')
reload_sound = load_sound('source/reload.wav')

# Music paths
menu_music = 'source/menu_music.mp3'
game_music = 'source/game_music.mp3'

class GameState:
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    WIN = 3

class Revolver:
    def __init__(self, chambers=6):
        self.chambers = chambers
        self.reset()
        
    def reset(self):
        self.bullet_pos = random.randint(0, self.chambers-1)
        self.current_pos = 0
        self.shots_fired = 0
        
    def spin(self):
        self.current_pos = random.randint(0, self.chambers-1)
        self.shots_fired = 0
        reload_sound.play()
        
    def shoot(self):
        self.shots_fired += 1
        if self.current_pos == self.bullet_pos:
            self.bullet_pos = -1
            shot_sound.play()
            return True
        else:
            click_sound.play()
            return False
        
    def next_chamber(self):
        self.current_pos = (self.current_pos + 1) % self.chambers
        
    def get_chamber_status(self, chamber):
        if chamber == self.current_pos:
            return "current"
        elif chamber == self.bullet_pos and self.bullet_pos != -1:
            return "bullet"
        else:
            return "empty"

def play_music(track, volume=0.5):
    """Play music with looping"""
    if load_music(track):
        try:
            mixer.music.set_volume(volume)
            mixer.music.play(loops=-1)
        except:
            print(f"Failed to play music: {track}")

def draw_revolver(revolver):
    radius = 200
    center_x, center_y = WIDTH // 2, HEIGHT // 2 - 50
    
    pygame.draw.circle(screen, GRAY, (center_x, center_y), radius, 5)
    
    for i in range(revolver.chambers):
        angle = 2 * 3.14159 * i / revolver.chambers
        x = center_x + (radius - 30) * -pygame.math.Vector2(1, 0).rotate(i * 360/revolver.chambers).x
        y = center_y + (radius - 30) * pygame.math.Vector2(1, 0).rotate(i * 360/revolver.chambers).y
        
        status = revolver.get_chamber_status(i)
        
        if status == "current":
            color = RED
        elif status == "bullet":
            color = BLACK
        else:
            color = WHITE
            
        pygame.draw.circle(screen, color, (int(x), int(y)), 20)
        
        if status == "current":
            pygame.draw.circle(screen, RED, (int(x), int(y)), 25, 3)

def draw_button(text, x, y, width, height, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
        if click[0] == 1 and action is not None:
            return action()
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))
    
    text_surf = font_medium.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=(x + width/2, y + height/2))
    screen.blit(text_surf, text_rect)
    
    return False

def show_message(text):
    root = Tk()
    root.withdraw()
    messagebox.showinfo("Russian Roulette", text)
    root.destroy()

def main():
    # Game initialization
    revolver = Revolver()
    game_state = GameState.MENU
    rounds = 0
    
    # Start with menu music
    play_music(menu_music)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Shutdown when window closed
                shutdown_computer()
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    current_vol = mixer.music.get_volume()
                    mixer.music.set_volume(min(current_vol + 0.1, 1.0))
                elif event.key == pygame.K_MINUS:
                    current_vol = mixer.music.get_volume()
                    mixer.music.set_volume(max(current_vol - 0.1, 0.0))
                elif event.key == pygame.K_ESCAPE:
                    # ESC also triggers shutdown
                    shutdown_computer()
                    running = False
        
        # Render based on game state
        if game_state == GameState.MENU:
            title_text = font_large.render("RUSSIAN ROULETTE", True, RED)
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
            
            subtitle_text = font_medium.render("PC Edition", True, WHITE)
            screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, 160))
            
            warning_text = font_small.render("Closing the game will shutdown your PC!", True, RED)
            screen.blit(warning_text, (WIDTH//2 - warning_text.get_width()//2, 220))
            
            start_clicked = draw_button("Start Game", 300, 350, 200, 50, GREEN, BLUE)
            if start_clicked:
                game_state = GameState.PLAYING
                play_music(game_music)
                
        elif game_state == GameState.PLAYING:
            draw_revolver(revolver)
            
            rounds_text = font_small.render(f"Round: {rounds + 1}", True, WHITE)
            screen.blit(rounds_text, (20, 20))
            
            volume_text = font_small.render("Volume: +/-", True, WHITE)
            screen.blit(volume_text, (WIDTH - volume_text.get_width() - 20, 20))
            
            shoot_clicked = draw_button("Shoot", 150, 500, 200, 50, WHITE, GREEN, lambda: revolver.shoot())
            spin_clicked = draw_button("Spin", 450, 500, 200, 50, WHITE, GREEN, revolver.spin)
            
            if shoot_clicked:
                if revolver.shoot():
                    game_state = GameState.GAME_OVER
                else:
                    revolver.next_chamber()
                    rounds += 1
                    
            if spin_clicked:
                rounds += 1
            
            if revolver.bullet_pos == -1:
                game_state = GameState.WIN
                
        elif game_state == GameState.GAME_OVER:
            result_text = font_large.render("YOU LOST!", True, RED)
            screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 250))
            
            pygame.display.flip()
            shutdown_computer()
            running = False
            
        elif game_state == GameState.WIN:
            result_text = font_large.render("YOU WON!", True, GREEN)
            screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 250))
            
            restart_clicked = draw_button("Back to Menu", 300, 350, 200, 50, WHITE, GREEN)
            if restart_clicked:
                game_state = GameState.MENU
                revolver.reset()
                rounds = 0
                play_music(menu_music)
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    response = messagebox.askyesno(
        "Warning!",
        "This game will shutdown your PC if you lose or close it!\n"
        "Are you sure you want to continue?",
        icon='warning'
    )
    root.destroy()
    
    if response:
        main()