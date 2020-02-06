import random
import pygame
import numpy as np

# constants
gold_count = 2
map_len = 4
factor = 100

# color
white = (255, 255, 255)
grey = (112, 128, 144)
black = (0, 0, 0)

# images
img_gold = pygame.image.load('img/gold.png')
img_bomb = pygame.image.load('img/bomb.png')
img_robot = pygame.image.load('img/robot.png')


class Entity(object):
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((map_len * factor, map_len * factor))
        self.img_background = self.init_screen()
        # init objects
        self.bomb = Bomb(self.screen)
        self.robot = Robot(self.bomb.pos, self.screen)
        self.golds = Golds(self.robot.pos, self.bomb.pos, self.screen)

    def init_screen(self):
        pygame.display.set_caption("Robot Simulator - Step : 0")
        self.screen.fill(white)
        for k in range(factor, map_len * factor, factor):
            pygame.draw.line(self.screen, grey, (k, 0), (k, map_len * factor))
            pygame.draw.line(self.screen, grey, (0, k), (map_len * factor, k))
        pygame.display.flip()
        pygame.image.save(self.screen, "img/screen.png")
        return pygame.image.load('img/screen.png')

    def kill(self):
        if self.robot.pos == self.bomb.pos:
            return True

    def earn(self):
        if self.golds.exist[self.robot.pos[0]][self.robot.pos[1]]:
            self.golds.exist[self.robot.pos[0]][self.robot.pos[1]] = False
            self.golds.remain -= 1

    def message_display(self, text):
        # display message in the center
        font = pygame.font.SysFont('Calibri.ttf', 30)
        text_surface = font.render(text, True, black)
        text_surf, text_rect = text_surface, text_surface.get_rect()
        text_rect.center = (factor * map_len / 2, factor * map_len / 2)
        self.screen.blit(text_surf, text_rect)
        pygame.display.flip()

    def play(self):
        step = 1
        pygame.display.set_caption("Robot Simulator - Step : %d" % step)
        gameExit = False

        while not gameExit and self.golds.remain >= 0:
            self.clock.tick(10)

            # check if the simulation is to be terminated
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            # check end of game
            if self.golds.remain == 0:
                print("Happy ending! Robot won")
                self.message_display("Happy ending! Robot won")
                gameExit = True
                continue

            # check bomb collision
            if self.kill():
                print("Game Over! Bomb killed the Robot")
                self.message_display("Game Over! Bomb killed the Robot")
                gameExit = True
                continue

            # display step number
            pygame.display.set_caption("Robot Simulator - Step : %d" % step)
            self.screen.blit(self.img_background, (0, 0))
            self.golds.display()

            if step % 3 == 0:
                self.robot.display()
                self.bomb.move(self.golds.exist)
            else:
                self.robot.move(self.bomb.pos)
                self.earn()
                self.bomb.display()
            pygame.display.flip()

            # increment step
            step += 1
            pygame.time.wait(150)

        pygame.display.flip()
        pygame.time.wait(20000)
        pygame.quit()

class Bomb(object):
    def __init__(self, screen):
        self.pos = [random.randrange(map_len), random.randrange(map_len)]
        self.img = img_bomb
        self.step_choice = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        self.screen = screen
        self.display()

    def display(self):
        self.screen.blit(self.img, (self.pos[0] * factor, self.pos[1] * factor))

    def check_neighbour(self, gold_exist):
        # check if bomb is surrounded by gold
        neighbour_count = 0
        for i in range(len(self.step_choice)):
            new = [self.pos[0] + self.step_choice[i][0], self.pos[1] + self.step_choice[i][1]]
            if 0 <= new[0] < map_len and 0 <= new[1] < map_len:
                neighbour_count += 1
                if gold_exist[new[0]][new[1]]:
                    neighbour_count -= 1

        if neighbour_count == 0:
            return False
        else:
            return True

    def move(self, gold_exist):
        if not self.check_neighbour(gold_exist):
            self.display()
            return
        move = self.step_choice[random.randrange(len(self.step_choice))]
        new = [self.pos[0] + move[0], self.pos[1] + move[1]]
        while new[0] >= map_len or new[0] < 0 or new[1] >= map_len or new[1] < 0 or gold_exist[new[0]][new[1]]:
            move = self.step_choice[random.randrange(len(self.step_choice))]
            new = [self.pos[0] + move[0], self.pos[1] + move[1]]
        self.pos = new
        self.display()

class Robot(object):
    def __init__(self, bomb_pos, screen):
        self.pos = [random.randrange(map_len), random.randrange(map_len)]
        while self.pos == bomb_pos:
            self.pos = [random.randrange(map_len), random.randrange(map_len)]
        self.img = img_robot
        self.step_choice = [[-1, 0],[-1,1],[-1,-1],[0, -1], [0, 1],[1, 0],[1,1],[1,-1]]
        self.screen = screen
        self.display()

    def display(self):
        self.screen.blit(self.img, (self.pos[0] * factor, self.pos[1] * factor))

    def move(self, bomb_pos):
        move = self.step_choice[random.randrange(len(self.step_choice))]
        new = [self.pos[0] + move[0], self.pos[1] + move[1]]
        while not (0 <= new[0] < map_len) or not (0 <= new[1] < map_len) or new == bomb_pos:
            move = self.step_choice[random.randrange(len(self.step_choice))]
            new = [self.pos[0] + move[0], self.pos[1] + move[1]]
        self.pos = new
        self.display()


class Golds(object):
    def __init__(self, robot_pos, bomb_pos, screen):
        self.exist = np.full((map_len, map_len), False)
        self.remain = gold_count
        self.img = img_gold
        self.add(robot_pos, bomb_pos)
        self.screen = screen
        self.display()

    def add(self, robot_pos, bomb_pos):
        count = 0
        while count < gold_count:
            new_gold = [random.randrange(map_len), random.randrange(map_len)]
            # add gold if position not occupied by other gold
            while self.exist[new_gold[0]][new_gold[1]] or new_gold == robot_pos or new_gold == bomb_pos:
                new_gold = [random.randrange(map_len), random.randrange(map_len)]
            self.exist[new_gold[0]][new_gold[1]] = True
            count += 1

    def display(self):
        for i in range(map_len):
            for j in range(map_len):
                if self.exist[i][j]:
                    self.screen.blit(self.img, [i * factor, j * factor])


def main():
    game = Entity()
    game.play()

if __name__ == "__main__":
    main()






