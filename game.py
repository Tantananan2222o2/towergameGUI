import pygame
import random
from sys import exit
from constants import DISC_FLOAT_SPEED,DISC_FLOAT_HEIGHT,IMAGE_PATH,DISC_MOVE_SPEED,SCREEN_WIDTH,SLIDE_BUTTON_IMAGE,X_BUTTON_IMAGE,RIGHT_SLIDE, HELP_IMAGES,SCREEN_HEIGHT,LEFT_SLIDE, GROUND_Y, PEG_POSITIONS, DISC_IMAGE, UNDO_BUTTON_IMAGE,RESTART_BUTTON,MENU_BUTTON, PLAY_BUTTON_IMAGE,MEMBERS_BUTTON_IMAGE, RULES_BUTTON_IMAGE, WARNING_COLOR, WARNING_FONT_SIZE, WARNING_POSITION, SOLVE_BUTTON_IMAGE, base_width, base_height
from disc import Disc
from peg import Peg


class Game:
    def __init__(self):

   
        self.min_moves = 2 ** len(DISC_IMAGE) - 1 
        self.game_outcome = None 

        self.fade_alpha = 255 
        self.fading_out = False 

        self.game_over_fade = False
        self.game_over_fade_alpha = 0


        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tower of Hanoi')
        self.clock = pygame.time.Clock()
        pygame.mixer.music.load("assets/bg_music.mp3")  
        pygame.mixer.music.set_volume(0.0) 
        pygame.mixer.music.play(-1) 
        self.bg = pygame.transform.scale(pygame.image.load("assets/toh_bg.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT))

      
        cc_raw = pygame.image.load("assets/cc.png").convert_alpha()
        self.cc_logo = pygame.transform.scale(cc_raw, (base_width, base_height))

        hci_raw = pygame.image.load("assets/hci.png").convert_alpha()
        self.hci_logo = pygame.transform.scale(hci_raw, (base_width, base_height))

        self.cc_rect = self.cc_logo.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        self.hci_rect = self.hci_logo.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))

        
        self.logo_scale = 1.0  
        self.scale_speed = 0.006  
        self.min_scale = 0.95 
        self.max_scale = 1.1  
        self.scale_direction = 1  
       
        self.cloud_images = [pygame.transform.scale(pygame.image.load(path), (200, 150)) for path in IMAGE_PATH]
     
        self.clouds = []
        for image in self.cloud_images:
            x = random.randint(-SCREEN_WIDTH, 0) 
            y = random.randint(300,400)
            speed = random.uniform(0.01, 0.5)  
            self.clouds.append({"image": image, "x": x, "y": y, "speed": speed})

        
        self.pegs = [Peg(x, 500, "assets/peg.png") for x in PEG_POSITIONS]
        self.discs = []
        self.held_disc = None
        self.game_started = False
        self.warning_message = ""
        self.move_history = []
        
        self.play_button = pygame.transform.scale(pygame.image.load(PLAY_BUTTON_IMAGE), (100, 100))
        self.play_button_rect = self.play_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 300))
        self.play_button_clicked = False

        self.rules_button = pygame.transform.scale(pygame.image.load(RULES_BUTTON_IMAGE), (70, 70))
        self.rules_button_rect = self.rules_button.get_rect(center=(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 300))
        self.show_rules = False

        self.members_button = pygame.transform.scale(pygame.image.load(MEMBERS_BUTTON_IMAGE), (80, 70))
        self.members_button_rect = self.members_button.get_rect(center=(SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT // 2 + 300))
        self.show_members = False
        
        self.undo_button = pygame.transform.scale(pygame.image.load(UNDO_BUTTON_IMAGE), (80,70))
        self.undo_button_rect = self.undo_button.get_rect(topleft=(SCREEN_WIDTH - 90, 20))
        self.undo_button_clicked = False
        
        self.solve_button = pygame.transform.scale(pygame.image.load(SOLVE_BUTTON_IMAGE), (80,70))
        self.solve_button_rect = self.solve_button.get_rect(topleft=(SCREEN_WIDTH - 90, 120))
        self.solve_button_clicked = False

        self.restart_button = pygame.transform.scale(pygame.image.load(RESTART_BUTTON), (80,70))
        self.restart_button_rect = self.restart_button.get_rect(topleft=(SCREEN_WIDTH - 90, 220))
        self.restart_button_clicked = False


   
        self.menu_button = pygame.transform.scale(pygame.image.load(MENU_BUTTON), (80,70))
        self.menu_button_rect = self.menu_button.get_rect(topleft=(20, 700))
        self.menu_button_clicked = False


        self.slide_button = pygame.transform.scale(pygame.image.load(SLIDE_BUTTON_IMAGE), (80,80))
        self.slide_button_rect = self.slide_button.get_rect(topleft=(SCREEN_WIDTH - 90, 320))  
        
        self.x_button = pygame.transform.scale(pygame.image.load(X_BUTTON_IMAGE), (20, 20))
        self.x_button_rect = self.x_button.get_rect(topright=(SCREEN_WIDTH - 150, 100))       
        self.x_button = pygame.transform.scale(pygame.image.load(X_BUTTON_IMAGE), (20, 20))
        self.overlay_x_rect = self.x_button.get_rect(topright=(SCREEN_WIDTH - 300, 200))
        
        self.next_slide_button_clicked = False
        self.prev_slide_button_clicked = False
        self.next_slide_button = pygame.transform.scale(pygame.image.load(RIGHT_SLIDE), (40,40))
        self.next_slide_button_rect = self.next_slide_button.get_rect(bottomright=(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100))  
        self.prev_slide_button = pygame.transform.scale(pygame.image.load(LEFT_SLIDE), (40,40))
        self.prev_slide_button_rect = self.prev_slide_button.get_rect(bottomright=(SCREEN_WIDTH - 1000, SCREEN_HEIGHT - 100))  
        
        self.help_images = [pygame.transform.scale(pygame.image.load(path), (int(SCREEN_WIDTH * 0.8), int(SCREEN_HEIGHT * 0.8))) for path in HELP_IMAGES] 
        
        self.show_slides = False  
        self.current_slide = 0   


        
        self.initialize_discs()
        self.solution_moves = []
        self.current_move = 0
        self.solving = False
        self.last_move_time = 0
        self.move_delay = 1000

        self.moving_disc = None
        self.move_state = None  # 'lifting', 'moving', 'dropping'
        self.move_target_x = None
        self.move_float_y = None



    def reset_game(self):

        self.game_outcome = None
        self.discs.clear()
        for peg in self.pegs:
             peg.discs.clear()
        self.initialize_discs()
        self.move_history.clear()
        self.warning_message = ""

        self.game_over_fade = False
        self.game_over_fade_alpha = 0
        self.held_disc = None

    def initialize_discs(self):
        for i, (size, image_path) in enumerate(DISC_IMAGE.items()):
            disc = Disc(size, image_path, PEG_POSITIONS[0], GROUND_Y, i)
            self.discs.append(disc)
            self.pegs[0].add_disc(disc)

    def draw_warning(self):
        if self.warning_message:
            font = pygame.font.Font(None, WARNING_FONT_SIZE)
            text = font.render(self.warning_message, True, WARNING_COLOR)
            self.screen.blit(text, WARNING_POSITION)

    def is_valid_move(self, disc, target_peg):
        if not target_peg.discs:
            return True
        top_disc = target_peg.get_top_disc()
        return disc.size < top_disc.size

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if self.show_slides:
      
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.x_button_rect.collidepoint(event.pos):
                        self.show_slides = False
                    elif self.next_slide_button_rect.collidepoint(event.pos):
                        self.current_slide = (self.current_slide + 1) % len(self.help_images) 
                        self.next_slide_button_clicked = True
                    elif self.prev_slide_button_rect.collidepoint(event.pos):
                        self.prev_slide_button_clicked = True
                        self.current_slide = (self.current_slide - 1) % len(self.help_images)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.next_slide_button_clicked = False 
                    self.prev_slide_button_clicked = False
            else:
               
                if not self.game_started: 
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.play_button_rect.collidepoint(event.pos):
                            self.play_button_clicked = True
                            self.fading_out = True
                        elif self.rules_button_rect.collidepoint(event.pos):
                            self.rules_button_clicked = True
                            if not self.show_rules:
                                self.show_rules = True
                                self.show_members = False
                        elif self.members_button_rect.collidepoint(event.pos):
                            if not self.show_members:
                                self.show_members = True
                                self.show_rules = False
                        if (self.show_rules or self.show_members) and self.overlay_x_rect.collidepoint(event.pos):
                            self.show_rules = False
                            self.show_members = False

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if self.play_button_clicked and self.play_button_rect.collidepoint(event.pos):
                            self.game_started = True 
                        self.play_button_clicked = False
                        self.members_button_clicked = False
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.menu_button_rect.collidepoint(event.pos):
                            self.reset_game()
                            self.game_started = False 
                            self.fading_out = False
                            self.fade_alpha = 255
                            self.game_over_fade = False
                            self.game_over_fade_alpha = 0
                        elif self.restart_button_rect.collidepoint(event.pos):
                            self.restart_button_clicked = True

                            if all(len(peg.discs) == 0 for peg in self.pegs[:-1] ):
                                self.solving= False
                                self.reset_game()
                            if not self.solving:
                                self.reset_game()
                            else:
                                self.warning_message = "Any kind of action that cause the disc to move is not allowed during the solving process"
                            continue
      
                        elif self.undo_button_rect.collidepoint(event.pos):
                            if self.solving:
                                self.warning_message = "Any kind of action that cause the disc to move is not allowed during the solving process"
                            self.undo_button_clicked = True
                            self.undo_move()
                        elif self.solve_button_rect.collidepoint(event.pos):  
                            self.solve_button_clicked = True
                            self.start_solving()
                        elif self.slide_button_rect.collidepoint(event.pos):
                            self.show_slides = True
                            self.current_slide = 0 
                        elif not self.solving and not self.game_outcome:
                            for peg in self.pegs:
                                top_disc = peg.get_top_disc()
                                if top_disc:
                                    disc_rect = top_disc.image.get_rect(topleft=tuple(top_disc.pos))
                                    if disc_rect.collidepoint(event.pos):
                                        top_disc.dragging = True
                                        self.held_disc = top_disc
                                        peg.remove_disc(top_disc)
                                        break
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.undo_button_clicked = False
                        self.solve_button_clicked = False  
                        self.restart_button_clicked = False
                        if self.held_disc:
                            closest_peg = min(self.pegs, key=lambda p: abs(p.x - self.held_disc.pos[0]))
                            self.held_disc.pos[0] = closest_peg.x - self.held_disc.image.get_width() // 2 + 19
                            if self.is_valid_move(self.held_disc, closest_peg):
                                self.move_history.append((self.held_disc, closest_peg, self.held_disc.peg_x, self.held_disc.pos.copy()))
                                self.held_disc.peg_x = closest_peg.x
                                stack_height = len(closest_peg.discs)
                                self.held_disc.target_y = GROUND_Y - (stack_height * 15)
                                closest_peg.add_disc(self.held_disc)
                                self.held_disc.dragging = False
                                self.held_disc.falling = True
                                self.warning_message = ""
                            else:
                                original_peg = next(peg for peg in self.pegs if peg.x == self.held_disc.peg_x)
                                original_peg.add_disc(self.held_disc)
                                self.warning_message = "Invalid move! A larger disc cannot be placed on a smaller one."
                            self.held_disc = None
                    elif event.type == pygame.MOUSEMOTION and self.held_disc:
                        self.held_disc.pos[0], self.held_disc.pos[1] = event.pos
 

    def start_solving(self):

        if all(len(peg.discs) == 0 for peg in self.pegs[1:]):
            self.solution_moves = []
            self.generate_solution()
            self.current_move = 0
            self.solving = True
            self.last_move_time = pygame.time.get_ticks()

        
        else:
            self.warning_message = "Put them on their initial place first"

      

    def generate_solution(self):
        self.algorithm(len(self.discs), 0, 2, 1)

    def algorithm(self, n, source, target, auxiliary):
        if n > 0:
            self.algorithm(n - 1, source, auxiliary, target)
            self.solution_moves.append((source, target))
            self.algorithm(n - 1, auxiliary, target, source)

    def execute_next_move(self):
        current_time = pygame.time.get_ticks()
    
        if self.moving_disc:

            if self.move_state == 'lifting':
                if self.moving_disc.pos[1] > self.move_float_y:
                    self.moving_disc.pos[1] -= DISC_FLOAT_SPEED
                else:
                    self.moving_disc.pos[1] = self.move_float_y
                    self.move_state = 'moving'
                
            elif self.move_state == 'moving':
                dx = self.move_target_x - self.moving_disc.pos[0]
                if abs(dx) > DISC_MOVE_SPEED:
                    self.moving_disc.pos[0] += DISC_MOVE_SPEED if dx > 0 else -DISC_MOVE_SPEED
                else:
                    self.moving_disc.pos[0] = self.move_target_x
                    self.move_state = 'dropping'
                
            elif self.move_state == 'dropping':
                if self.moving_disc.pos[1] < self.moving_disc.target_y:
                    self.moving_disc.pos[1] += DISC_FLOAT_SPEED
                else:
                    self.moving_disc.pos[1] = self.moving_disc.target_y
                    self.moving_disc = None
                    self.move_state = None
                    self.current_move += 1
                    self.last_move_time = current_time
    
        elif self.current_move < len(self.solution_moves) and current_time - self.last_move_time >= self.move_delay:
            source_peg_index, target_peg_index = self.solution_moves[self.current_move]
            source_peg = self.pegs[source_peg_index]
            target_peg = self.pegs[target_peg_index]

            disc = source_peg.get_top_disc()
            if disc:
                source_peg.remove_disc(disc)
                disc.peg_x = target_peg.x
            
                stack_height = len(target_peg.discs)
                disc.target_y = GROUND_Y - (stack_height * 15)
                self.move_float_y = GROUND_Y - DISC_FLOAT_HEIGHT  
                self.move_target_x = target_peg.x - disc.image.get_width() // 2 + 19
            
                self.moving_disc = disc
                self.move_state = 'lifting'
            
                target_peg.add_disc(disc) 

    def undo_move(self):
        if self.move_history:
            disc, target_peg, original_peg_x, _ = self.move_history.pop()
            target_peg.remove_disc(disc)
            original_peg = next(peg for peg in self.pegs if peg.x == original_peg_x)
            original_peg.add_disc(disc)
            stack_height = len(original_peg.discs) - 1
            disc.pos[0] = original_peg.x - disc.image.get_width() // 2 + 19
            disc.pos[1] = GROUND_Y - (stack_height * 15)
            disc.peg_x = original_peg_x
            disc.falling = False

    def draw_metallic(self):
        if self.warning_message: 
            font = pygame.font.Font(None, WARNING_FONT_SIZE)
            text = font.render(self.warning_message, True, WARNING_COLOR)
            self.screen.blit(text, WARNING_POSITION)

    def update(self):
        if self.game_started and not self.show_slides: 
            if self.solving:
                self.execute_next_move()

              
            for peg in self.pegs:
                for disc in peg.discs:
                    if disc.falling:
                        if disc.pos[1] < disc.target_y:
                            disc.pos[1] += 10
                        else:
                            disc.pos[1] = disc.target_y
                            disc.falling = False
            if len(self.pegs[2].discs) == len(self.discs):
                if len(self.move_history) <= self.min_moves:
                    self.game_outcome = 'win'
                else:
                    self.game_outcome = 'lose'
            if self.game_outcome and not self.game_over_fade:
                self.game_over_fade = True
            if self.game_over_fade and self.game_over_fade_alpha < 200:
                self.game_over_fade_alpha += 2
   
        self.logo_scale += self.scale_speed 
        if self.logo_scale >= self.max_scale or self.logo_scale <= self.min_scale:
            self.scale_speed = -self.scale_speed
        cc_current_scale = self.logo_scale
        hci_current_scale = (self.max_scale + self.min_scale) - self.logo_scale
        cc_width = int(self.cc_logo.get_width() * cc_current_scale)
        cc_height = int(self.cc_logo.get_height() * cc_current_scale)
        self.scaled_cc = pygame.transform.scale(self.cc_logo, (cc_width, cc_height))
        hci_width = int(self.hci_logo.get_width() * hci_current_scale)
        hci_height = int(self.hci_logo.get_height() * hci_current_scale)
        self.scaled_hci = pygame.transform.scale(self.hci_logo, (hci_width, hci_height))
        self.cc_rect = self.scaled_cc.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 150))
        self.hci_rect = self.scaled_hci.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))

    def draw_overlay(self, content_list, title):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)) 
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 40)
        title_surface = font.render(title, True, (255, 215, 0))  
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        self.screen.blit(title_surface, title_rect)

        line_height = 45
        start_y = SCREEN_HEIGHT // 2 - 100

        for i, text in enumerate(content_list):
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * line_height))
            self.screen.blit(text_surface, text_rect)

    def fade_out_effect(self):
        if self.fading_out:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)  
            self.screen.blit(fade_surface, (0, 0))

            if self.fade_alpha > 0:
                self.fade_alpha -= 5 
            else:
                self.fading_out = False
                self.game_started = True 

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.fade_out_effect()

        for cloud in self.clouds:
            cloud["x"] += cloud["speed"]
            if cloud["x"] > SCREEN_WIDTH:
                cloud["x"] = random.randint(-SCREEN_WIDTH, 0)
                cloud["y"] = random.randint(300, 400)
                cloud["speed"] = random.uniform(0.05, 0.5)
            self.screen.blit(cloud["image"], (cloud["x"], cloud["y"]))

        if not self.game_started: 
            mouse_pos = pygame.mouse.get_pos()
            self.screen.blit(self.scaled_cc, self.cc_rect.topleft)
            self.screen.blit(self.scaled_hci, self.hci_rect.topleft)
            if self.play_button_rect.collidepoint(mouse_pos):
                scaled_play = pygame.transform.scale(self.play_button, (110, 110))
                self.screen.blit(scaled_play, self.play_button_rect.topleft)
            else:
                self.screen.blit(self.play_button, self.play_button_rect.topleft)
            if self.rules_button_rect.collidepoint(mouse_pos):
                scaled_rules = pygame.transform.scale(self.rules_button, (77, 77))
                self.screen.blit(scaled_rules, self.rules_button_rect.topleft)
            else:
                self.screen.blit(self.rules_button, self.rules_button_rect.topleft)
            if self.members_button_rect.collidepoint(mouse_pos):
                scaled_members = pygame.transform.scale(self.members_button, (88, 77)) 
                self.screen.blit(scaled_members, self.members_button_rect.topleft)
            else:
                self.screen.blit(self.members_button, self.members_button_rect.topleft)
            if self.show_rules:
                self.draw_overlay([
                    "How to Play:",
                    "- Move all discs to the last peg in descending order",
                    "- Larger discs cannot be placed above the smaller ones",
                    "- Use UNDO to revert moves",
                    "- Click SOLVE to see optimal solution",
                    "- Minimum moves required: 2^n - 1"
                ], "Game Rules")
            if self.show_members:
                self.draw_overlay([
                                   "Kreah Miracle Jumanoy",
                                   "Mark Ahron Yandog",
                                   "Ahrvie Gyle Garcia",
                                   "Adonis Manabeng",
                                   "Miceil  Placencia",
                                   "Tristhan Rodimo",
                                   "Noriel Felipe Jr.",
                                   "Andrei Canoza"], "The Project was Designed by:")
            if self.show_rules or self.show_members:
                if self.overlay_x_rect.collidepoint(mouse_pos):
                    scaled_x = pygame.transform.scale(self.x_button, (24, 24))
                    adjusted_rect = scaled_x.get_rect(topright=(SCREEN_WIDTH - 300, 200))
                    self.screen.blit(scaled_x, adjusted_rect.topleft)
                else:
                    self.screen.blit(self.x_button, self.overlay_x_rect.topleft)

        else:
            mouse_pos = pygame.mouse.get_pos()
            for peg in self.pegs:
                peg.draw(self.screen)
            if self.held_disc:
                self.held_disc.draw(self.screen)
            
            if self.undo_button_clicked:
                scaled_undo = pygame.transform.scale(self.undo_button, (99, 99 * 4 // 5))
                self.screen.blit(scaled_undo, self.undo_button_rect.topleft)
            else:
                self.screen.blit(self.undo_button, self.undo_button_rect.topleft)
            if self.solve_button_clicked:
                scaled_solve = pygame.transform.scale(self.solve_button, (99, 99 * 4 // 5))
                self.screen.blit(scaled_solve, self.solve_button_rect.topleft)
            else:
                self.screen.blit(self.solve_button, self.solve_button_rect.topleft)
            

            if not self.show_slides:
                if self.slide_button_rect.collidepoint(mouse_pos):
                    scaled_slide = pygame.transform.scale(self.slide_button, (99, 99 * 4 // 5))
                    self.screen.blit(scaled_slide, self.slide_button_rect.topleft)
                else:
                    self.screen.blit(self.slide_button, self.slide_button_rect.topleft)

            if self.show_slides:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))  
                self.screen.blit(overlay, (0, 0))
                current_image = self.help_images[self.current_slide]
                image_rect = current_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(current_image, image_rect)
               

                if not self.x_button_rect.collidepoint(mouse_pos):
                  
                    self.screen.blit(self.x_button, self.x_button_rect)
                else:
                    scaled_button = pygame.transform.scale(self.x_button, (24, 24))  
                    self.screen.blit(scaled_button, self.x_button_rect.topleft)

        
                if self.next_slide_button_clicked:
                    scaled_next = pygame.transform.scale(self.next_slide_button, (35,35)) 
                    self.screen.blit(scaled_next, self.next_slide_button_rect.topleft)
                elif self.next_slide_button_rect.collidepoint(mouse_pos):
                    scaled_next = pygame.transform.scale(self.next_slide_button, (45,45)) 
                    self.screen.blit(scaled_next, self.next_slide_button_rect.topleft)
                else:
                    self.screen.blit(self.next_slide_button, self.next_slide_button_rect.topleft)

      
                if self.prev_slide_button_clicked:
                    scaled_prev = pygame.transform.scale(self.prev_slide_button, (35,35)) 
                    self.screen.blit(scaled_prev, self.prev_slide_button_rect.topleft)
                elif self.prev_slide_button_rect.collidepoint(mouse_pos):
                    scaled_prev = pygame.transform.scale(self.prev_slide_button, (45,45)) 
                    self.screen.blit(scaled_prev, self.prev_slide_button_rect.topleft)
                else:
                    self.screen.blit(self.prev_slide_button, self.prev_slide_button_rect.topleft)


        
            font = pygame.font.Font(None, 36)
            moves_text = font.render(f"Moves: {len(self.move_history)} / {self.min_moves}", True, (255, 255, 255))
            self.screen.blit(moves_text, (10, 10))

            if self.game_over_fade and self.game_outcome:
                fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(self.game_over_fade_alpha)
                self.screen.blit(fade_surface, (0, 0))

            if self.game_outcome:
                outcome_font = pygame.font.Font(None, 74)
                color = (0, 255, 0) if self.game_outcome == 'win' else (255, 0, 0)
                text = "You Win!" if self.game_outcome == 'win' else "You Lose!"
                text_surface = outcome_font.render(text, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
                self.screen.blit(text_surface, text_rect)

            if self.menu_button_rect.collidepoint(mouse_pos):
                scaled_menu = pygame.transform.scale(self.menu_button, (99, 99 * 4 // 5))
                self.screen.blit(scaled_menu, self.menu_button_rect.topleft)
            else:
                self.screen.blit(self.menu_button, self.menu_button_rect.topleft)

            if self.restart_button_rect.collidepoint(mouse_pos) and self.restart_button_clicked :
                scaled_restart = pygame.transform.scale(self.restart_button, (99, 99 * 4 // 5))
                self.screen.blit(scaled_restart, self.restart_button_rect.topleft)
            else:
                self.screen.blit(self.restart_button, self.restart_button_rect.topleft)
        self.draw_metallic()
        pygame.display.update()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

    