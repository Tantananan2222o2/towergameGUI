import pygame
import random
from sys import exit
from constants import IMAGE_PATH,SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_Y, PEG_POSITIONS, DISC_IMAGE, UNDO_BUTTON_IMAGE,RESTART_BUTTON, PLAY_BUTTON_IMAGE,MEMBERS_BUTTON_IMAGE, RULES_BUTTON_IMAGE, WARNING_COLOR, WARNING_FONT_SIZE, WARNING_POSITION, SOLVE_BUTTON_IMAGE, base_width, base_height
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
        pygame.mixer.music.set_volume(0.1) 
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
        self.rules_button_clicked = False
        self.show_rules = False

        self.members_button = pygame.transform.scale(pygame.image.load(MEMBERS_BUTTON_IMAGE), (80, 70))
        self.members_button_rect = self.members_button.get_rect(center=(SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT // 2 + 300))
        self.members_button_clicked = False
        self.show_members = False
        
        self.undo_button = pygame.transform.scale(pygame.image.load(UNDO_BUTTON_IMAGE), (90, 90 * 4 // 5))
        self.undo_button_rect = self.undo_button.get_rect(topleft=(SCREEN_WIDTH - 90, 20))
        self.undo_button_clicked = False
        
        self.solve_button = pygame.transform.scale(pygame.image.load(SOLVE_BUTTON_IMAGE), (90, 90 * 4 // 5))
        self.solve_button_rect = self.solve_button.get_rect(topleft=(SCREEN_WIDTH - 90, 120))
        self.solve_button_clicked = False

        self.restart_button = pygame.transform.scale(pygame.image.load(RESTART_BUTTON), (90, 90 * 4 // 5))
        self.restart_button_rect = self.restart_button.get_rect(topleft=(SCREEN_WIDTH - 90, 220))
        self.restart_button_clicked = False
        
        self.initialize_discs()
        self.solution_moves = []
        self.current_move = 0
        self.solving = False
        self.last_move_time = 0
        self.move_delay = 1000

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

            if not self.game_started:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_button_rect.collidepoint(event.pos):
                        self.play_button_clicked = True
                        self.fading_out = True
                    elif self.rules_button_rect.collidepoint(event.pos):
                        self.rules_button_clicked = True
                        self.show_rules = not self.show_rules
                    elif self.members_button_rect.collidepoint(event.pos):
                        self.members_button_clicked = True
                        self.show_members = not self.show_members
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.play_button_clicked and self.play_button_rect.collidepoint(event.pos):
                        self.game_started = True  
                    self.play_button_clicked = False
                    self.rules_button_clicked = False
                    self.members_button_clicked = False

            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.restart_button_rect.collidepoint(event.pos):
                        self.restart_button_clicked = True
                        if not self.solving:
                            self.reset_game()
                        else:
                            self.warning_message = "Cannot reset during solving!"
                        continue

                    if self.game_outcome:
                        continue
                    if self.undo_button_rect.collidepoint(event.pos):
                        self.undo_button_clicked = True
                        self.undo_move()
                    elif self.solve_button_rect.collidepoint(event.pos):
                        self.solve_button_clicked = True
                        self.start_solving()

                    elif self.restart_button_rect.collidepoint(event.pos):
                        if not self.solving:
                            self.restart_button_clicked = True
                            self.reset_game()
                        else:
                            self.warning_message = "Cannot reset during solving!"

                    elif not self.solving:
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

                if event.type == pygame.MOUSEMOTION and self.held_disc:
                    self.held_disc.pos[0], self.held_disc.pos[1] = event.pos

                elif event.type == pygame.MOUSEBUTTONUP and self.held_disc:
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
        if self.current_move < len(self.solution_moves):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_move_time >= self.move_delay:
                source_peg_index, target_peg_index = self.solution_moves[self.current_move]
                source_peg = self.pegs[source_peg_index]
                target_peg = self.pegs[target_peg_index]

                disc = source_peg.get_top_disc()
                if disc:
                    source_peg.remove_disc(disc)
                    target_peg.add_disc(disc)
                    disc.peg_x = target_peg.x
                    stack_height = len(target_peg.discs) - 1
                    disc.pos[0] = target_peg.x - disc.image.get_width() // 2 + 19
                    disc.pos[1] = GROUND_Y - (stack_height * 15)
                    self.current_move += 1
                    self.last_move_time = current_time
        else:
            self.solving = False 

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

    def update(self):

        if self.game_started:
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
            else:
                self.game_outcome = None

           
            if self.game_over_fade and self.game_over_fade_alpha < 200:  
                self.game_over_fade_alpha += 2 
        else:

            self.logo_scale += self.scale_direction * self.scale_speed

            if self.logo_scale >= self.max_scale or self.logo_scale <= self.min_scale:
                self.scale_direction *= -1

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
        """Create a fade-out effect when starting the game."""
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
        """Draw everything on the screen."""
        self.screen.blit(self.bg, (0, 0))
        self.fade_out_effect() 

    

        for cloud in self.clouds:       
            cloud["x"] += cloud["speed"]
    
            if cloud["x"] > SCREEN_WIDTH:
                cloud["x"] = random.randint(-SCREEN_WIDTH, 0)
                cloud["y"] = random.randint(300,400)

       
            self.screen.blit(cloud["image"], (cloud["x"], cloud["y"]))
            cloud["speed"] = random.uniform(0.01, 0.5)
        

        if not self.game_started:

            mouse_pos = pygame.mouse.get_pos()
            self.screen.blit(self.scaled_cc, self.cc_rect.topleft)
            self.screen.blit(self.scaled_hci, self.hci_rect.topleft)
            
            if self.play_button_rect.collidepoint(mouse_pos):
                scaled_play = pygame.transform.scale(self.play_button, (110, 110))
                scaled_play_rect = scaled_play.get_rect(center=self.play_button_rect.center)
                self.screen.blit(scaled_play, scaled_play_rect.topleft)
            else:
                self.screen.blit(self.play_button, self.play_button_rect.topleft)
        
         
            if self.rules_button_rect.collidepoint(mouse_pos):
                scaled_rules = pygame.transform.scale(self.rules_button, (77, 77))
                scaled_rules_rect = scaled_rules.get_rect(center=self.rules_button_rect.center)
                self.screen.blit(scaled_rules, scaled_rules_rect.topleft)
            else:
                self.screen.blit(self.rules_button, self.rules_button_rect.topleft)
        
  
            if self.members_button_rect.collidepoint(mouse_pos):
                scaled_members = pygame.transform.scale(self.members_button, (88, 77))
                scaled_members_rect = scaled_members.get_rect(center=self.members_button_rect.center)
                self.screen.blit(scaled_members, scaled_members_rect.topleft)
            else:
                self.screen.blit(self.members_button, self.members_button_rect.topleft)

            if self.show_rules:
                self.draw_overlay([
                    "How to Play:",
                    "- Move all discs to the last peg in ascending order",
                    "- Larger discs cannot be placed above the smaller ones",
                    "- Use UNDO to revert moves",
                    "- Click SOLVE to see optimal solution",
                    "- Minimum moves required: 2^n -1",
                    "Click RULES to close this window"
                ], "Game Rules")

            if self.show_members:
                self.draw_overlay([
                    "ME"
                ], "This projesct was designed by:")
           
        else:
            for peg in self.pegs:
                peg.draw(self.screen)
            if self.held_disc:
                self.held_disc.draw(self.screen)

         
            if self.game_over_fade and self.game_outcome:
                fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(self.game_over_fade_alpha)
                self.screen.blit(fade_surface, (0, 0))

            if self.undo_button_clicked:
                scaled_undo_button = pygame.transform.scale(self.undo_button, (85, 85 * 4 // 5))
                self.screen.blit(scaled_undo_button, self.undo_button_rect.topleft)
            else:
                self.screen.blit(self.undo_button, self.undo_button_rect.topleft)

            if self.restart_button_clicked:
                scaled_nextlevel_button = pygame.transform.scale(self.restart_button, (85, 85 * 4 // 5))
                self.screen.blit(scaled_nextlevel_button, self.restart_button_rect.topleft)
            else:
                self.screen.blit(self.restart_button, self.restart_button_rect.topleft)


            if self.solve_button_clicked:
                scaled_solve_button = pygame.transform.scale(self.solve_button, (85, 85 * 4 // 5))
                self.screen.blit(scaled_solve_button, self.solve_button_rect.topleft)
            else:
                self.screen.blit(self.solve_button, self.solve_button_rect.topleft)

            self.draw_warning()

            font = pygame.font.Font(None, 36)
            moves_text = font.render(
                f"Moves: {len(self.move_history)}/{self.min_moves}", 
                True, (255, 255, 255)
            )
            self.screen.blit(moves_text, (10, 10))

            if self.game_outcome:
                outcome_font = pygame.font.Font(None, 74)
                color = (0, 255, 0) if self.game_outcome == 'win' else (255, 0, 0)
                text = "You Win!" if self.game_outcome == 'win' else "You Lose!"
                text_surface = outcome_font.render(text, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2-100))
                self.screen.blit(text_surface, text_rect)

        pygame.display.update()

    def run(self):
        """Run the game loop."""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

    