from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty,ListProperty, BoundedNumericProperty, ObjectProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.base import runTouchApp
import random

JUMP_VEL= 8.5

kv_string = '''
<RunDinoGame>:
    canvas.before:
        Color:
            rgba: 0.5, 0.5, 1, 1 
        Rectangle:
            pos: self.pos
            size: self.size
    
    Image:
        id: ground_image
        source: 'imagens/solo.png'
        pos: root.solo_pos[0], root.solo_pos[1] + 270
        size: self.texture_size

    Image:
        id: dino_image
        pos: self.parent.center_x - self.width / 2-400, self.parent.center_y - self.height / 2-100
        
    Button:
        size_hint: None, None
        size: 100, 50
        pos: root.width - self.width - 80, 140
        background_normal: 'imagens/seta2.png'
        on_press: root.on_up_press('up')

    Button:
        size_hint: None, None
        size: 100, 50
        pos: root.width - self.width - 80, 40
        background_normal: 'imagens/seta1.png'
        on_press: root.on_down_press('down')
'''


Builder.load_string(kv_string)

# Configuração da janela
Window.size = (900, 680)

class Jump(Image):
    velocidade_x = NumericProperty(0)

    def move(self):
        self.x -= self.velocidade_x

class Duck(Image):
    velocidade_x = NumericProperty(0)

    def move(self):
        self.x -= self.velocidade_x

    pass

class Cactos(Image):
    velocidade_x = NumericProperty(0)

    def move(self):
        self.x -= self.velocidade_x

class Cloud(Image):
    velocidade_x = NumericProperty(0)

    def move(self):
        self.x -= self.velocidade_x

class Passaro(Image):
    velocidade_x = NumericProperty(0)

    def move(self):
        self.x -= self.velocidade_x

# Classe do Dinossauro
class Dino(Image):
    dino_image_paths = ['imagens/DinoRun1.png', 'imagens/DinoRun2.png']
    jump_image_paths = ['imagens/DinoJump.png']
    duck_image_paths = ['imagens/DinoDuck1.png', 'DinoDuck2.png']
    velocidade_x = 0
    velocidade_y = 0
    dino_index = 0
    step_index = 0
    dino_run = True
    dino_jump = False
    dino_duck = False
    solo_pos = NumericProperty(0)

    def move(self):  # movimentação do solo
        self.pos = Vector(self.velocidade_x, self.velocidade_y) + self.pos

        if self.pos[1] < self.solo_pos:
            self.pos[1] = self.solo_pos
            self.velocidade_y = 0

    def update(self, dt, direction=None):
        
        if self.dino_run:
            self.run(dt)
        elif self.dino_jump:
            self.jump()
        elif self.dino_duck:
            self.duck()
        if direction == 'up' and not self.dino_jump:
            self.dino_run = False
            self.dino_duck = False
            self.dino_jump = True
        elif direction == 'down' and not self.dino_jump:
            self.dino_run = False
            self.dino_duck = True
            self.dino_jump = False
        elif not self.dino_jump and not self.dino_duck:
            self.dino_run = True
            self.dino_duck = False
            self.dino_jump = False
        if self.step_index >= 9:
            self.step_index = 0

    def run(self, dt):
        print("Running animation") 
        self.ids.dino_image.source = self.dino_image_paths[self.dino_index]
        self.dino_index = (self.dino_index + 1) % len(self.dino_image_paths)


    def jump(self, direction):
        self.update(direction)
        if self.y == self.solo_pos:
            jump_image = 'imagens/DinoJump.png'  # ou a imagem desejada
            jump = Jump(source=jump_image)
            jump.velocidade_x = JUMP_VEL
            jump.pos = (self.width / 2, self.solo_pos[1])
            self.add_widget(jump)
            self.y += 100
            self.velocidade_y = JUMP_VEL

    def duck(self):
        if self.y == self.solo_pos:
            duck_image = random.choice(self.duck_image_paths)
            duck = Duck(source=duck_image)
            self.y -= 50
            self.velocidade_y = 0


 
# Classe do Jogo
class RunDinoGame(Widget):

    passaro_image_paths = ['imagens/Bird1.png', 'imagens/Bird2.png']
    cactus_image_paths = ['imagens/LargeCactus1.png', 'imagens/LargeCactus2.png', 'imagens/LargeCactus3.png',
                          'imagens/SmallCactus1.png', 'imagens/SmallCactus2.png', 'imagens/SmallCactus3.png']
    cloud_image_path = 'imagens/Nuvem.png'
    solo_image_path = 'imagens/solo.png'


    passaro = ListProperty([])
    cacti = ListProperty([])
    clouds = ListProperty([])

    dino_index = 0
    solo_speed = 4 #velocidade do solo
    solo_pos = ListProperty([0, 0])


    

    def __init__(self, **kwargs):
        super(RunDinoGame, self).__init__(**kwargs)
        self.solo_pos = [0, 0]
        self.obstacles = []
        self.passaro_index = 0
        self.dino = Dino()
        self.dino.y = self.dino.solo_pos

        Clock.schedule_interval(self.update, 1.0 / 60.0)  
        Clock.schedule_interval(self.update_game, 1.0 / 60.0)      
        Clock.schedule_interval(self.spawn_clouds, 0.5) 
        Clock.schedule_interval(self.spawn_obstacle, 2.0)
        Clock.schedule_interval(self.animate_passaro, 0.2)  
    
    def update(self, dt):
        self.dino.update(dt)

    def spawn_clouds(self, dt):
           if all(cloud.x < 0 for cloud in self.clouds):

               num_clouds = random.randint(1, 4)
               for _ in range(num_clouds):
                   cloud = Cloud(source=self.cloud_image_path)
                   cloud.pos = (random.randint(0, self.width), random.randint(self.height // 2, self.height))
                   cloud.velocidade_x = random.uniform(1, 4)  # Velocidade horizontal aleatória
                   self.clouds.append(cloud)
                   self.add_widget(cloud)
        
    def spawn_obstacle(self, dt):
        obstacle_type = random.choice([self.spawn_cacti, self.spawn_passaro])
        obstacle_type(dt)

    def adjust_obstacle_distance(self, obstacles, dt):
        # Ajusta a distância entre os obstáculos
        min_distance_between_obstacles = 600 
        if len(obstacles) > 1:
            last_obstacle = obstacles[-2]
            if obstacles[-1].x - last_obstacle.x < min_distance_between_obstacles:
                obstacles[-1].x = last_obstacle.x + min_distance_between_obstacles
    
    def spawn_passaro(self, dt):
        passaro = Passaro(source=self.passaro_image_paths[self.passaro_index])
        passaro.velocidade_x = self.solo_speed
        min_distance_between_obstacles = 1300

        last_obstacle = None
        if len(self.passaro) > 0:
            last_obstacle = self.passaro[-1]

        if len(self.cacti) > 0 and (last_obstacle is None or self.cacti[-1].x == last_obstacle.x):
            last_obstacle = self.cacti[-1]

        while last_obstacle is not None and passaro.x - last_obstacle.x < min_distance_between_obstacles:
            passaro.x += 10
        passaro.pos = (self.width + random.randint(50, 150), self.solo_pos[1] + 340)
        self.passaro.append(passaro)
        self.add_widget(passaro)

    def animate_passaro(self, dt):
        # Atualiza o caminho da imagem dos pássaros
        for passaro in self.passaro:
            passaro.source = self.passaro_image_paths[self.passaro_index]

        self.passaro_index = (self.passaro_index + 1) % len(self.passaro_image_paths)
    
    def spawn_cacti(self, dt):
        cactus = Cactos(source=random.choice(self.cactus_image_paths))
        cactus.velocidade_x = self.solo_speed

        min_distance_between_obstacles = 600

        last_obstacle = None
        if len(self.cacti) > 0:
            last_obstacle = self.cacti[-1]

        if len(self.passaro) > 0 and (last_obstacle is None or self.passaro[-1].x > last_obstacle.x):
            last_obstacle = self.passaro[-1]

        while last_obstacle is not None and cactus.x - last_obstacle.x < min_distance_between_obstacles:
            cactus.x += 10

        cactus.pos = (self.width + random.randint(50, 150), self.solo_pos[1] + 270)
        self.cacti.append(cactus)
        self.add_widget(cactus)

        self.adjust_obstacle_distance(self.cacti, dt)    

    def update_game(self, dt):
        self.solo_pos[0] -= self.solo_speed
        if self.solo_pos[0] <= -self.width:
            self.solo_pos[0] = 0

        # Atualiza o dinossauro e a animação apenas se não estiver pulando
        if self.dino.velocidade_y == 0:
            self.dino.move()
            self.dino.run(dt) 

        # Atualiza as nuvens
        for cloud in self.clouds:
            cloud.move()

        # Atualiza os pássaros
        for passaro in self.passaro:
            passaro.move()
            if passaro.x < -passaro.width:
                self.passaro.remove(passaro)
                self.remove_widget(passaro)

        # Atualiza os cactos
        for cactus in self.cacti:
            cactus.move()
            if cactus.x < -cactus.width:
                self.cacti.remove(cactus)
                self.remove_widget(cactus)

        self.adjust_obstacle_distance(self.cacti, dt)
        self.adjust_obstacle_distance(self.passaro, dt)

    def on_up_press(self):
        if self.dino.dino_jump('up'):
            self.dino_jump = True

        

    def on_down_press(self):
        if self.dino.dino_jump('down'):
            self.dino_duck = True



class RunDinoApp(App):
    def build(self):
        game = RunDinoGame()
        return game

if __name__ == '__main__':
    RunDinoApp().run()

 
