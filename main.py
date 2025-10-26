
import pygame
import random
import os
import time
import neat
import pickle
#import visualize
#import pickle
pygame.font.init()  # init font

WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())

gen = 0

class Bird:
    """
    Bird class representing the flappy bird
    """
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        """
        make the bird jump
        :return: None
        """
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        """
        make the bird move
        :return: None
        """
        self.tick_count += 1

        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement

        # terminal velocity
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        """
        draw the bird
        :param win: pygame window or surface
        :return: None
        """
        self.img_count += 1

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2


        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)


class Pipe():
    """
    represents a pipe object
    """
    GAP = 160
    VEL = 5

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
    """
    Represents the moving floor of the game
    """
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        move floor so it looks like its scrolling
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :param gen: current generation
    :param pipe_ind: index of closest pipe
    :return: None
    """
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        # draw bird
        bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def eval_genomes(genomes, config): 
    """
    runs the simulation of the current population of
    birds and sets their fitness based on the distance they
    reach in the game.
    """
    global WIN, gen
    win = WIN
    gen += 1

    nets = []
    birds = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0 # de "fitness" (een mate van hoe goed/slim elk vogeltje is) wordt op 0 gesteld.
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0
    best_score = 0  # stelt de beste score op 0 voor de huidige generatie    
    best_bird = None # Omdat er nog geen spel is gespeeld, is er nog geen beste vogel bepaald.

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(100)

        # per gebeurtenis wordt er een bepaald event geactiveerd.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1 # Als de vogel de eerste pijp voorbij is gevolgen, dan wordt de tweede pijp als eerstvolgende gezien.

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.4 # Dit geeft het vogeltje een beloning wannneer het blijft leven (en dus niet crashed).
            bird.move()

            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump() # Dit is de NEAT, die zegt of het vogeltje moet springen of niet.

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()

            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1 # Dit geeft het vogeltje een straf wannneer het crashed/tegen de pijp aan botst. De             NEAT leert zo de botsingen te voorkomen. Het vogeltje zal daarna dus ook verwijderd worden uit de generatie.
                    nets.pop(birds.index(bird)) 
                    ge.pop(birds.index(bird)) 
                    birds.pop(birds.index(bird)) # Deze drie regels verwijderen het vogeltje, die tegen de pijp is gebotst. Daarbij wordt ook          het netwerk en de genomene (genetische informatie) verwijderd.)

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe) # Hier wordt de pijp verwijderd als hij buiten het scherm is.

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True # Er wordt een nieuwe pijp toegevoegd als de laatste pijp weg is.

        if add_pipe:
            score += 1 # Omdat het vogeltje de pijp voorbij is gevlogen, verhoogd de score met 1.

            for genome in ge:
                genome.fitness += 5 # Wanneer het vogeltje door de pijp vliegt, zonder te crashen, krijgt het een beloning. De NEAT leert zo            dat dit goed gedrag is en zal doorgaan met dit vogeltje in de volgende generatie.  

            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)


        # kijk of de huidige score hoger is dan de beste score
        if score > best_score:
            best_score = score
            best_bird = ge[0]

        # Alle registraties van de vogel worden verwijderd als deze de grond/bovenkant van het scherm raakt.
        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

        if best_score >= 100:
            print("Beste vogel heeft 100 punten gehaald. Training van de vogels stopt...")
            break # Hier wordt de training gestopt als de beste vogel 100 punten heeft gehaald.

    if best_bird:
        print("Bewaar de beste vogel in een pickle-bestand...")
        with open("best_bird.pkl", "wb") as f :
            pickle.dump(best_bird, f) # De beste vogel (die dus meer dan 100 punten heeft gehaald) wordt opgeslagen in een pickle-bestand.  
        
def play_with_best_bird(path, config):
    """
    Deze functie laadt het beste netwerk uit een pickle-bestand en speelt het Flappy Bird spel met dat netwerk.
    :param path: pad naar het pickle-bestand met het beste netwerk
    :param config: NEAT-configuratie
    """
    # Laad het beste netwerk uit de pickle
    with open(path, "rb") as f:
        winner = pickle.load(f)

    # Maak een netwerk voor het beste genetische netwerk, deze gebruikt de inputs van de vogel uit het beste netwerk.
    net = neat.nn.FeedForwardNetwork.create(winner, config)

    # Nu wordt het spel opnnieuw opgesteld, maar dan met het beste netwerk.
    win = WIN
    bird = Bird(230, 350)
    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    # Hoofd-game loop
    run = True
    while run:
        clock.tick(100)

        # per gebeurtenis wordt er weer een bepaald event geactiveerd.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        # Vind de index van de dichtstbijzijnde pijp
        pipe_ind = 0
        if len(pipes) > 1 and bird.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1

        # Laat de vogel bewegen
        bird.move()

        # Verkrijg de output van het neurale netwerk (beslissing om te springen of niet)
        output = net.activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

        # Als de output groter is dan 0.5, laat de vogel springen
        if output[0] > 0.5:
            bird.jump()

        base.move()

        # De instellingen voor de pijpen worden hier nog een keer genoteerd.
        rem = []
        add_pipe = False 
        for pipe in pipes:
            pipe.move()

            # Controleer op botsingen tussen de vogel en de pijp
            if pipe.collide(bird, win):
                run = False
                pygame.quit()
                quit()
                break

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        # Als de vogel de grond raakt of de bovenkant van het scherm verlaat, eindig het spel
        if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
            run = False

        # Teken het spelvenster
        draw_window(win, [bird], pipes, base, score, 0, pipe_ind)

def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    # Laadt de configuratie voor NEAT (config file)
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config) # Maakt een populatie aan.

    p.add_reporter(neat.StdOutReporter(True)) # Een reporter is toegevoegd, die de status van de lopende (vliegendende*) populatie weergeeft.
    stats = neat.StatisticsReporter() 
    p.add_reporter(stats) # Deze reporter kan de statestieken (in de regel hierboven aangemaakt) van de populatie weergeven.
    p.add_reporter(neat.Checkpointer(5)) # Elke 5 generaties wordt de populatie opgeslagen, zodat het niet verloren kan gaan.

    winner = p.run(eval_genomes, 50) # 50 generaties lang leert de NEAT het spel.

    print('\nBest genome:\n{!s}'.format(winner))  # Geeft de volledige informatie van het beste vogeltje weer.

    # Bewaar de winnaar in een pickle .pkl bestand
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)

    # Speel het eindspel met het beste netwerk
    play_with_best_bird("winner.pkl", config)

    # Roep de functie aan om NEAT te draaien en zo het beste netwerk te verkrijgen.
    if __name__ == '__main__':
    # Bepaal het pad naar het configuratiebestand
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')

    # Roep de functie aan om het spel te starten met de opgegeven configuratie
    run(config_path)

    # Dit kunnen we als het goed is weglaten, want de alerbeste vogel wordt al gebruikt.
    play_with_best_bird("best_bird.pkl", config)
    
    # Sluit Pygame netjes af na afloop
    pygame.quit()
