from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty,ListProperty, BoundedNumericProperty, ObjectProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
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
    ground_pos = ListProperty([0, 0])

    def move(self):
        self.pos = Vector(self.velocity_x, self.velocity_y) + self.pos

        if self.pos[1] < self.ground_pos[1]:
            self.pos[1] = self.ground_pos[1]
            self.velocity_y = 0

    def jump(self):
        print("Jumping...")
        if self.pos[1] == self.ground_pos[1]:
            self.velocity_y = 10  # Ajuste conforme necessário para a altura do pulo
            Clock.schedule_once(self.reset_jump_velocity, 0.2)
    
    def update_jump(self, dt):
        self.move()
            

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
    ground_speed = 4 #velocidade do solo
    dino = ObjectProperty(None)
    ground_pos = ListProperty([0, 0])
    

    def __init__(self, **kwargs):
        super(RunDinoGame, self).__init__(**kwargs)
        self.ground_pos = [0, 0]
        self.obstacles = []
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        Clock.schedule_interval(self.change_dino_image, 0.175)        
        Clock.schedule_interval(self.spawn_clouds, 0.5) #o tempo que as nuvens vão aparecer 
        Clock.schedule_interval(self.spawn_obstacle, 1.5)
        Clock.schedule_interval(self.animate_birds, 0.2)  
        self.ground_pos = [0, 0]  # Adicione esta linha para inicializar a posição do solo

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.current_bird_index = 0
    
    def _on_keyboard_up(self, keyboard, keycode, *args):
        if keycode[1] == 'up':
            self.dino.velocity_y = 0

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None


    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print(f"Key pressed: {keycode}, Dino position: {self.dino.pos}, Ground position: {self.ground_pos}")
        if keycode[1] == 'up' and self.dino.pos[1] == self.ground_pos[1]:
            self.dino.jump()

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
        obstacle_type = random.choice([self.spawn_cacti, self.spawn_birds])
        obstacle_type(dt)

    def adjust_obstacle_distance(self, obstacles, dt):
        # Ajusta a distância entre os obstáculos
        min_distance_between_obstacles = 600  # Ajuste conforme necessário
        if len(obstacles) > 1:
            last_obstacle = obstacles[-2]
            if obstacles[-1].x - last_obstacle.x < min_distance_between_obstacles:
                obstacles[-1].x = last_obstacle.x + min_distance_between_obstacles
    
    def spawn_birds(self, dt):
        bird = Bird(source=self.bird_image_paths[self.current_bird_index])
        bird.velocity_x = self.ground_speed

        # Garante uma distância mínima entre diferentes tipos de obstáculos
        min_distance_between_obstacles = 1300

        last_obstacle = None
        if len(self.birds) > 0:
            last_obstacle = self.birds[-1]

        if len(self.cacti) > 0 and (last_obstacle is None or self.cacti[-1].x == last_obstacle.x):
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
        min_distance_between_obstacles = 600

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
        self.dino.update_jump(dt)
        for cloud in self.clouds:
            cloud.move()
        # Atualiza os pássaros
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

        # Adicione aqui a lógica para garantir a distância entre os obstáculos
        self.adjust_obstacle_distance(self.cacti, dt)
        self.adjust_obstacle_distance(self.birds, dt)

    def change_dino_image(self, dt):
        # Atualiza o caminho da imagem
        self.ids.dino_image.source = self.dino_image_paths[self.current_dino_index]

        # Avança para a próxima imagem na lista
        self.current_dino_index = (self.current_dino_index + 1) % len(self.dino_image_paths)
    def update_jump(self, dt):
        self.dino.update_jump(dt)

# Classe do Aplicativo
class RunDinoApp(App):
    def build(self):
        game = RunDinoGame()
        game.dino = Dino()
        Clock.schedule_interval(game.update_jump, 1.0 / 60.0)  # Chama update_jump a cada quadro
        return game

if __name__ == '__main__':
    RunDinoApp().run()
