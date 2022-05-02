import os
import sys
from player import Player
from track import Track
import Controller as Ctl
from enum import Enum
import neat
import pickle
import matplotlib.pyplot as plt
import pygame as pg


class GameState(Enum):
    playing = 0
    training = 1
    spectating = 2
    continue_training = 3
    race = 4


RESTORE_PATH = "neat-checkpoint-99"
CAPTION = "GAME"
SCREEN_SIZE = (1200, 800)
RADIUS = 100


class Game():

    def __init__(self, Gamestate, max_generation=-1,
                 unit_test=False):

        self.GAMESTATE = Gamestate
        self.BLIND = False
        self.track = Track()
        self.generation = 0
        self.max_generation = max_generation
        self.unit_test = unit_test

        if not unit_test:
            os.environ["SDL_VIDEO_CENTERED"] = '1'
            pg.init()
            self.screen = pg.display.set_mode(SCREEN_SIZE)
            self.screen_rect = self.screen.get_rect()
            self.clock = pg.time.Clock()
            self.fps = 60.0
            self.keys = pg.key.get_pressed()

            if(self.GAMESTATE == GameState.playing):
                self.player = Player(170., 200., 50., 20., 1., 100.)
                self.player.add(Ctl.Player_Controller(self.player))
                self.player.max = -1

            elif(self.GAMESTATE == GameState.training):

                config = neat.Config(neat.DefaultGenome,
                                     neat.DefaultReproduction,
                                     neat.DefaultSpeciesSet,
                                     neat.DefaultStagnation, "./config.txt")

                population = neat.Population(config)
                population.add_reporter(neat.StdOutReporter(True))
                stats = neat.StatisticsReporter()
                population.add_reporter(stats)
                population.add_reporter(neat.Checkpointer(500))

                winner = population.run(self.run_car, 50)

                with open("winner2.pkl", "wb") as f:
                    pickle.dump(winner, f)

                with open("stats.pkl", "wb") as f:
                    pickle.dump(stats, f)

                generation = range(len(stats.most_fit_genomes))
                best_fitness = [c.fitness for c in stats.most_fit_genomes]

                plt.plot(generation, best_fitness)
                plt.show()

            elif(self.GAMESTATE == GameState.continue_training):

                population = neat.Checkpointer.restore_checkpoint(RESTORE_PATH)
                population.add_reporter(neat.StdOutReporter(True))
                stats = neat.StatisticsReporter()
                population.add_reporter(stats)
                population.add_reporter(neat.Checkpointer(1000))

                winner = population.run(self.run_car, 1)

                with open("cwinner.pkl", "wb") as f:
                    pickle.dump(winner, f)

                with open("cstats.pkl", "wb") as f:
                    pickle.dump(stats, f)

                generation = range(len(stats.most_fit_genomes))
                best_fitness = [c.fitness for c in stats.most_fit_genomes]

                plt.plot(generation, best_fitness)
                plt.show()

            elif(self.GAMESTATE == GameState.spectating or
                 self.GAMESTATE == GameState.race):
                with open("winner.pkl", "rb") as f:
                    genome = pickle.load(f)
                    genomes = [(1, genome)]
                    if(self.GAMESTATE == GameState.race):
                        self.player = Player(170., 200., 50., 20., 1., 100.)
                        self.player.add(Ctl.Player_Controller(self.player))
                        self.player.max = -1
                    self.run_car(genomes, neat.Config(neat.DefaultGenome,
                                                      neat.DefaultReproduction,
                                                      neat.DefaultSpeciesSet,
                                                      neat.DefaultStagnation,
                                                      "./config.txt"))
        else:
            self.GAMESTATE = GameState.training
            self.BLIND = True
            self.result = -1

            config = neat.Config(neat.DefaultGenome,
                                 neat.DefaultReproduction,
                                 neat.DefaultSpeciesSet,
                                 neat.DefaultStagnation,
                                 "./config.txt")

            population = neat.Population(config)
            population.run(self.run_car, max_generation)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()
                if event.key == pg.K_b:
                    self.BLIND = not self.BLIND
                if (event.key == pg.K_1
                        and not self.GAMESTATE == GameState.training):
                    self = Game(GameState.playing)
                    self.main_loop()
                if (event.key == pg.K_2
                        and not self.GAMESTATE == GameState.training):
                    self = Game(GameState.spectating)
                if (event.key == pg.K_3
                        and not self.GAMESTATE == GameState.training):
                    self = Game(GameState.race)
                if event.key == pg.K_9:
                    self = Game(GameState.training)

    def Update(self):
        self.player.Update()
        self.track.update(self.player)

    def Draw(self, surface):
        surface.fill(pg.Color("black"))
        self.player.Draw(surface)
        self.track.draw(surface)

    def main_loop(self):
        if(self.GAMESTATE == GameState.playing):
            while True:
                self.Update()
                self.event_loop()
                self.Draw(self.screen)
                pg.display.update()
                self.clock.tick(self.fps)
                caption = "{} - FPS: {:.2f}".format(CAPTION,
                                                    self.clock.get_fps())
                pg.display.set_caption(caption)

                if not self.player.alive:
                    break
        self = Game(GameState.playing)
        self.main_loop()

    def run_car(self, genomes, config):
        nets = []
        cars = []

        def player_zone_check(player):
            (x, y) = (player.x, player.y)
            if(x < 200 and x > 100 and y > 100 and y < 200):
                if(player.reward_zone == 0):
                    player.reward_zone = 1
                    return True
                elif(player.reward_zone == 2):
                    player.die()
                    return False
            if(x < 1100 and x > 900 and y > 600 and y < 1200):
                if(player.reward_zone == 1):
                    player.reward_zone = 2
                    return True
                elif(player.reward_zone == 0):
                    player.die()
                    return False
            if(x < 1100 and x > 900 and y > 100 and y < 200):
                if(player.reward_zone == 2):
                    player.reward_zone = 0
                    return True
                elif(player.reward_zone == 1):
                    player.die()
                    return False
            return False

        for id, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            g.fitness = 0

            cars.append(Player(170., 200., 50., 20., 1., 100.))
            cars[len(cars)-1].add(Ctl.IA_Controller(cars[len(cars)-1]))
            if(self.GAMESTATE == GameState.spectating or
               self.GAMESTATE == GameState.race):
                cars[len(cars)-1].max = -1

        self.generation += 1

        while(True):
            if(self.GAMESTATE == GameState.race):
                self.player.Update()
                self.track.update(self.player)
                if not self.player.alive:
                    self = Game(GameState.race)

            for index, car in enumerate(cars):
                outputs = nets[index].activate(car.inputs())
                car.Update(outputs)
                self.track.update(car)

            remain_cars = 0

            for i, car in enumerate(cars):
                if(car.alive):
                    remain_cars += 1
                    genomes[i][1].fitness += car.get_reward()
                    if(player_zone_check(car)):
                        genomes[i][1].fitness += 100.
            if(remain_cars == 0):
                break

            if not self.unit_test:
                self.event_loop()

            if not self.BLIND:
                self.screen.fill(pg.Color("black"))

                if(self.GAMESTATE == GameState.race):
                    self.player.rect.color = pg.Color('green')
                    self.player.Draw(self.screen)

                for car in cars:
                    if car.alive:
                        car.Draw(self.screen)
                self.track.draw(self.screen)
                pg.display.update()
                self.clock.tick(self.fps)
                caption = "{} - FPS: {:.2f}".format(CAPTION,
                                                    self.clock.get_fps())
                pg.display.set_caption(caption)

        if(self.unit_test):
            self.result = max(max([genome[1].fitness for genome in genomes]),
                              self.result)


if __name__ == "__main__":
    run_it = Game(GameState.playing)
    if(run_it.GAMESTATE == GameState.playing):
        run_it.main_loop()
    pg.quit()
    sys.exit()
