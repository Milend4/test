from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty,ListProperty, BoundedNumericProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.core.window import Window
import random


kv_string = '''
<RunDinoGame>:
    canvas.before:
        Color:
            rgba: 0.5, 0.5, 1, 1  # Cor do fundo (azul claro, ajuste conforme necessário)
        Rectangle:
            pos: self.pos
            size: self.size
    
    Image:
        id: ground_image
        source: 'imagens/solo.png'
        pos: root.ground_pos[0], root.ground_pos[1] + 210
        size: self.texture_size

    Image:
        id: dino_image
        source: 'imagens/DinoRun1.png'
        pos: self.parent.center_x - self.width / 2-400, self.parent.center_y - self.height / 2-100

'''

Builder.load_string(kv_string)

# Configuração da janela
Window.size = (800, 600)

class Cactus(Image):
    velocity_x = NumericProperty(0)

    def move(self):
        self.x -= self.velocity_x

class Cloud(Image):
    velocity_x = NumericProperty(0)

    def move(self):
        self.x -= self.velocity_x

class Bird(Image):
    velocity_x = NumericProperty(0)

    def move(self):
        self.x -= self.velocity_x

# Classe do Dinossauro
class Dino(Widget):
    velocity_x = BoundedNumericProperty(0, min=-10, max=10)
    velocity_y = BoundedNumericProperty(0, min=-10, max=10)

    def move(self):
        self.pos = Vector(self.velocity_x, self.velocity_y) + self.pos

        # Limita o movimento do dinossauro à tela
        if self.pos[1] < 0:
            self.pos[1] = 0

    def jump(self):
        self.velocity_y = 4  # Alterado para 4 para subir
        Clock.schedule_once(self.stop_jump, 0.5)  # Agendado para parar o salto após 0.5 segundos

    def stop_jump(self, dt):
        self.velocity_y = 0


# Classe do Jogo
class RunDinoGame(Widget):
    bird_image_paths = ['imagens/Bird1.png', 'imagens/Bird2.png']
    cactus_image_paths = ['imagens/LargeCactus1.png', 'imagens/LargeCactus2.png', 'imagens/LargeCactus3.png',
                          'imagens/SmallCactus1.png', 'imagens/SmallCactus2.png', 'imagens/SmallCactus3.png']

    birds = ListProperty([])
    cacti = ListProperty([])
    cloud_image_path = 'imagens/Nuvem.png'
    clouds = ListProperty([])
    ground_image_path = 'imagens/solo.png'
    dino_image_paths = ['imagens/DinoRun1.png', 'imagens/DinoRun2.png']
    current_dino_index = 0
    ground_speed = 2 #velocidade do solo
    dino = ObjectProperty(None)
    ground_pos = ListProperty([0, 0])

    def __init__(self, **kwargs):
        super(RunDinoGame, self).__init__(**kwargs)
        self.ground_pos = [0, 0]
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        Clock.schedule_interval(self.change_dino_image, 0.175)        
        Clock.schedule_interval(self.spawn_clouds, 0.5) #o tempo que as nuvens vão aparecer 
        Clock.schedule_interval(self.spawn_obstacle, 1.0)
        Clock.schedule_interval(self.animate_birds, 0.2)  

        self.current_bird_index = 0

    def spawn_clouds(self, dt):
           if all(cloud.x < 0 for cloud in self.clouds):

               num_clouds = random.randint(1, 4)
               for _ in range(num_clouds):
                   cloud = Cloud(source=self.cloud_image_path)
                   cloud.pos = (random.randint(0, self.width), random.randint(self.height // 2, self.height))
                   cloud.velocity_x = random.uniform(1, 4)  # Velocidade horizontal aleatória
                   self.clouds.append(cloud)
                   self.add_widget(cloud)
        
    def spawn_obstacle(self, dt):
        # Gera aleatoriamente entre cactos e pássaros
        obstacle_choice = random.choice(['cactus', 'bird'])
        
        if obstacle_choice == 'cactus':
            self.spawn_cacti(dt)
        elif obstacle_choice == 'bird':
            self.spawn_birds(dt)

    def adjust_obstacle_distance(self, obstacles, dt):
        # Ajusta a distância entre os obstáculos
        min_distance_between_obstacles = 400  # Ajuste conforme necessário
        if len(obstacles) > 1:
            last_obstacle = obstacles[-2]
            if obstacles[-1].x - last_obstacle.x < min_distance_between_obstacles:
                obstacles[-1].x = last_obstacle.x + min_distance_between_obstacles
    
    def spawn_birds(self, dt):
        bird = Bird(source=self.bird_image_paths[self.current_bird_index])
        bird.velocity_x = self.ground_speed

        # Garante uma distância mínima entre diferentes tipos de obstáculos
        min_distance_between_obstacles = 500

        last_obstacle = None
        if len(self.birds) > 0:
            last_obstacle = self.birds[-1]

        if len(self.cacti) > 0 and (last_obstacle is None or self.cacti[-1].x > last_obstacle.x):
            last_obstacle = self.cacti[-1]

        while last_obstacle is not None and bird.x - last_obstacle.x < min_distance_between_obstacles:
            bird.x += 10

        bird.pos = (self.width + random.randint(50, 150), self.ground_pos[1] + 310)
        self.birds.append(bird)
        self.add_widget(bird)

    def animate_birds(self, dt):
        # Atualiza o caminho da imagem dos pássaros
        for bird in self.birds:
            bird.source = self.bird_image_paths[self.current_bird_index]

        # Avança para a próxima imagem na lista
        self.current_bird_index = (self.current_bird_index + 1) % len(self.bird_image_paths)
    
    def spawn_cacti(self, dt):
        
        cactus = Cactus(source=random.choice(self.cactus_image_paths))
        cactus.velocity_x = self.ground_speed

        # Garante uma distância mínima entre diferentes tipos de obstáculos
        min_distance_between_obstacles = 400

        last_obstacle = None
        if len(self.cacti) > 0:
            last_obstacle = self.cacti[-1]

        if len(self.birds) > 0 and (last_obstacle is None or self.birds[-1].x > last_obstacle.x):
            last_obstacle = self.birds[-1]

        while last_obstacle is not None and cactus.x - last_obstacle.x < min_distance_between_obstacles:
            cactus.x += 10

        cactus.pos = (self.width + random.randint(50, 150), self.ground_pos[1] + 210)
        self.cacti.append(cactus)
        self.add_widget(cactus)

        self.adjust_obstacle_distance(self.cacti, dt)
    
        

    def on_touch_down(self, touch):
        self.dino.jump()

    def update(self, dt):
        self.ground_pos[0] -= self.ground_speed
        if self.ground_pos[0] <= -self.width:
            self.ground_pos[0] = 0
        self.dino.move()
        for cloud in self.clouds:
            cloud.move()
            if cloud.x > self.width:
                self.clouds.remove(cloud)
                self.remove_widget(cloud)
        for bird in self.birds:
            bird.move()

            # Remove pássaros que saíram da tela
            if bird.x < -bird.width:
                self.birds.remove(bird)
                self.remove_widget(bird)

        # Atualiza os cactos
        for cactus in self.cacti:
            cactus.move()

            # Remove cactos que saíram da tela
            if cactus.x < -cactus.width:
                self.cacti.remove(cactus)
                self.remove_widget(cactus)

    def change_dino_image(self, dt):
        # Atualiza o caminho da imagem
        self.ids.dino_image.source = self.dino_image_paths[self.current_dino_index]

        # Avança para a próxima imagem na lista
        self.current_dino_index = (self.current_dino_index + 1) % len(self.dino_image_paths)

# Classe do Aplicativo
class RunDinoApp(App):
    def build(self):
        game = RunDinoGame()
        game.dino = Dino()
        return game

if __name__ == '__main__':
    RunDinoApp().run()
