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


# gère les différents modes de jeu disponibles

class GameState(Enum):
    playing = 0
    training = 1
    spectating = 2
    continue_training = 3
    race = 4


# variables globales

RESTORE_PATH = "neat-checkpoint-99"
CAPTION = "GAME"
SCREEN_SIZE = (1200, 800)
RADIUS = 100


# classe principale du code

class Game():

    def __init__(self, Gamestate, max_generation=-1,
                 unit_test=False):

        # stock le mode de jeu en cour
        self.GAMESTATE = Gamestate
        # si Blind alors il n'y aura pas d'affichage
        self.BLIND = False
        self.track = Track()
        # retourne True si l'on est entrain de faire un test unitaire
        self.unit_test = unit_test

        if not unit_test:

            # initie pygame
            os.environ["SDL_VIDEO_CENTERED"] = '1'
            pg.init()
            self.screen = pg.display.set_mode(SCREEN_SIZE)
            self.screen_rect = self.screen.get_rect()
            self.clock = pg.time.Clock()
            self.fps = 60.0
            self.keys = pg.key.get_pressed()

            # chaine de if/elif pour faire les initialisations correspondantes
            # au mode de jeu
            if(self.GAMESTATE == GameState.playing):

                # crée un objet joueur
                self.player = Player(170., 200., 50., 20., 1., 100.)
                # ajoute la gestion des entrées du joueur
                self.player.add(Ctl.Player_Controller(self.player))
                # ne donne pas de limite de temps de jeu au joueur
                self.player.max = -1

            elif(self.GAMESTATE == GameState.training):

                # la config stocke des données sur la méthode d'entrainement
                config = neat.Config(neat.DefaultGenome,
                                     neat.DefaultReproduction,
                                     neat.DefaultSpeciesSet,
                                     neat.DefaultStagnation, "./config.txt")

                # crée la population et des outils pour analyser l'entrainement
                population = neat.Population(config)
                population.add_reporter(neat.StdOutReporter(True))
                stats = neat.StatisticsReporter()
                population.add_reporter(stats)
                population.add_reporter(neat.Checkpointer(500))

                winner = population.run(self.run_car, 50)

                # stock le meilleur génome en mémoire
                with open("winner2.pkl", "wb") as f:
                    pickle.dump(winner, f)

                # stock les données sur l'entrainement
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

                # charge l'IA et crée un objet joueur correspondant
                with open("winner.pkl", "rb") as f:
                    genome = pickle.load(f)
                    genomes = [(1, genome)]

                    # si on est en mode course, ajoute un joueur humain
                    if(self.GAMESTATE == GameState.race):
                        self.player = Player(170., 200., 50., 20., 1., 100.)
                        self.player.add(Ctl.Player_Controller(self.player))
                        self.player.max = -1

                    # lance le jeu
                    self.run_car(genomes, neat.Config(neat.DefaultGenome,
                                                      neat.DefaultReproduction,
                                                      neat.DefaultSpeciesSet,
                                                      neat.DefaultStagnation,
                                                      "./config.txt"))
        # code lancé pour le test unitaire
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

    # gère les inputs du joueur
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

    # mise à jour des paramètres
    def Update(self):
        self.player.Update()
        self.track.update(self.player, False)

    # Affiche les objets
    def Draw(self, surface):
        surface.fill(pg.Color("black"))
        self.player.Draw(surface)
        self.track.draw(surface)

    # boucle principale du mode jeu solo, met à jour et affiche les composants
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

    # fonction principales des autres modes de jeu
    def run_car(self, genomes, config):
        nets = []
        cars = []

        # empêche l'IA de faire des demis tours
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

        # initie les IA
        for id, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            g.fitness = 0

            cars.append(Player(170., 200., 50., 20., 1., 100.))
            cars[len(cars)-1].add(Ctl.IA_Controller(cars[len(cars)-1]))
            if(self.GAMESTATE == GameState.spectating or
               self.GAMESTATE == GameState.race):
                cars[len(cars)-1].max = -1

        # boucle principale, met à jour et affiche les composants
        while(True):
            if(self.GAMESTATE == GameState.race):
                self.player.Update()
                self.track.update(self.player, False)
                if not self.player.alive:
                    self = Game(GameState.race)

            # va chercher les outputs du réseau de neuronne et contrôlle l'IA
            # en conséquence
            for index, car in enumerate(cars):
                outputs = nets[index].activate(car.inputs())
                car.Update(outputs)
                self.track.update(car)

            remain_cars = 0

            # calcul le fitness des IA
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

            # si l'affichage est activé, dessine les objets
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
