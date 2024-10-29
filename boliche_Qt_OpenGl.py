import sys
import math
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QOpenGLWidget, QStatusBar
from PyQt5.QtGui import QFont
from OpenGL.GL import *
from OpenGL.GLU import *


class BowlingGame(QOpenGLWidget):    
    
    # ==== Construtor
    def __init__(self, score_label, progress_bar):
        super().__init__()


        # Variáveis globais: bola e pinos
        self.ball_position = [-0.43, -1.0, 0.0]  # Inicialmente no centro, perto da base da pista
        self.ball_speed = 0.0  # Inicialmente a bola não se move
        self.rotation_angle = 360.0
        self.rotation_speed = 10.0
        self.ball_direction = [0.0, 0.0]  # Direção inicial (x, y) para controle da direção da bola
        self.force = 0.0  # Força de lançamento da bola
        self.first_pin_height = 1.8 # Altura do primeiro pino, usada para calcular a altura dos demais
        self.ball_radius = 0.05 # Raio da bola e dos pinos
        self.pin_radius = 0.03
        self.score_label = score_label
        self.progress_bar = progress_bar
        self.progress_bar.setValue(int(self.force * 100))
        # Inicialização dos pinos com rotação, estado de queda e cor
        self.pin_positions = [
            {"position": [-0.1, self.first_pin_height+0.91, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
            {"position": [0.0, self.first_pin_height+0.91, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
            {"position": [0.1, self.first_pin_height+0.91, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
            {"position": [-0.05, self.first_pin_height+0.4, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#2ª
            {"position": [0.05, self.first_pin_height+0.4, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#2ª
            {"position": [0.0, self.first_pin_height+0.3, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#1ª
            {"position": [-0.15, self.first_pin_height+1.4, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [-0.05, self.first_pin_height+1.4, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [0.05, self.first_pin_height+1.4, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [0.15, self.first_pin_height+1.4, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)}#4ª
        ]
        
        self.setWindowTitle("Boliche com PyQt")
        #self.setFixedSize(800, 600)
        
        self.setFocusPolicy(Qt.StrongFocus)  # Garante que o widget receberá o foco
        self.setFocus()  # Dá o foco para o widget

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 800 / 600, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0.0, -2.0, 1.0,  # Posição da câmera
                  0.0, 0.0, 0.0,  # Ponto de visão
                  0.0, 1.0, 0.0)  # Vetor "para cima"
        #Texture area
        self.floor_texture = self.load_texture('textures/piso4.png')
        self.ball_texture = self.load_texture('textures/Marble016.png')
        self.pin_texture = self.load_texture('textures/pino2.png')

    def load_texture(self, path):
        texture_surface = pygame.image.load(path)
        texture_surface = pygame.transform.flip(texture_surface, False, True)  # Flip the texture vertically
        texture_data = pygame.image.tostring(texture_surface, "RGBA", True)

        # Generate texture ID
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Upload the texture to OpenGL
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture_surface.get_width(), texture_surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        
        return texture_id

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT)

        # Atualizar a posição da bola com base na velocidade e direção
        if self.ball_speed > 0:
            self.ball_position[1] += self.ball_speed * self.ball_direction[1]
            
            # Impedir que a bola saia da tela ou ultrapasse os pinos
            if self.ball_position[1] > 6.0:
                #self.ball_position[1] = 3.0
                #self.ball_speed = 0.0  # Parar a bola quando atingir o final da pista
                self.reset_ball_position()


        self.draw_pist()
        self.draw_ball()
        self.draw_pins()
        self.move_ball()
        self.loopBall()
        self.remove_pins()
        self.update()
        glFlush()

    def remove_pins(self):
        # Filtra os pinos que não caíram
        self.pin_positions = [pin for pin in self.pin_positions if pin["rotation"] < 90.0]

    def move_ball(self):
        #self.ball_position[1] += self.ball_speed * self.ball_direction[1]
        #self.ball_position[0] += self.ball_speed * self.ball_direction[0]
        #self.check_collision()
        
        if self.ball_position[1] <= 5.5 and self.ball_position[1] != 1.0:
            
            if(self.ball_speed > 0):
                self.rotation_angle +=self.rotation_speed
            
            
            self.ball_position[1] += self.ball_speed * self.ball_direction[1]
            self.ball_position[0] += self.ball_speed * self.ball_direction[0]
            self.check_collision()
            print(self.ball_position, self.ball_direction, sep="|")

        else:
            # Atualize a rotação com base na velocidade da bola
            
            
            self.ball_position[1] += self.ball_speed * self.ball_direction[1]
            self.ball_position[0] += self.ball_speed * self.ball_direction[0]
        

    def check_collision(self):
        for pin in self.pin_positions:
            position = pin["position"]
            distance = math.sqrt(
                (self.ball_position[0] - position[0]) ** 2 + 
                (self.ball_position[1] - position[1]) ** 2
            )
            if distance < (self.ball_radius + self.pin_radius) and not pin["falling"]:
                print(f"Colisão detectada com o pino em {position}!")
                pin["falling"] = True

    def draw_pist(self):
        # Desenhar a pista
        glEnable(GL_TEXTURE_2D)  # Enable textures
        glBindTexture(GL_TEXTURE_2D, self.floor_texture)  # Bind the floor texture

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-1.0, -1.1, -0.5)  # Bottom left vertex
        
        glTexCoord2f(1.0, 0.0)
        glVertex3f(1.0, -1.1, -0.5)  # Bottom right vertex
        
        glTexCoord2f(1.0, 1.0)
        glVertex3f(1.0, 3.0, 0.5)  # Top right vertex
        
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-1.0, 3.0, 0.5)  # Top left vertex
        glEnd()

        glDisable(GL_TEXTURE_2D)  # Disable textures
    
    def draw_sphere(self, radius, slices, stacks):
        glEnable(GL_TEXTURE_2D)  # Enable textures
        glBindTexture(GL_TEXTURE_2D, self.ball_texture)  # Bind the ball texture
        
        for i in range(slices):
            lat0 = math.pi * (-0.5 + float(i) / slices)
            z0 = math.sin(lat0)
            zr0 = math.cos(lat0)
            lat1 = math.pi * (-0.5 + float(i + 1) / slices)
            z1 = math.sin(lat1)
            zr1 = math.cos(lat1)
            
            glBegin(GL_QUAD_STRIP)
            for j in range(stacks + 1):
                lng = 2 * math.pi * float(j) / stacks
                x = math.cos(lng)
                y = math.sin(lng)
                
                # Apply texture coordinates
                glTexCoord2f(float(j) / stacks, float(i) / slices)
                glVertex3f(x * zr0 * radius, y * zr0 * radius, z0 * radius)
                
                glTexCoord2f(float(j) / stacks, float(i + 1) / slices)
                glVertex3f(x * zr1 * radius, y * zr1 * radius, z1 * radius)
            glEnd()
        
        glDisable(GL_TEXTURE_2D)  # Disable textures

    def draw_ball(self):
        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(self.ball_position[0], self.ball_position[1], self.ball_position[2])
        
        # Aplique a rotação
        glRotatef(self.rotation_angle, -1.0, 0.0, 0.0)
        self.draw_sphere(self.ball_radius, 20, 20)
        glPopMatrix()

    def draw_cylinder(self, radius, height, slices):
        glEnable(GL_TEXTURE_2D)  # Enable textures
        glBindTexture(GL_TEXTURE_2D, self.pin_texture)  # Bind the pin texture

        glBegin(GL_QUAD_STRIP)
        for i in range(slices + 1):
            angle = 2 * math.pi * i / slices
            x = math.cos(angle)
            y = math.sin(angle)

            # Apply texture coordinates
            glTexCoord2f(float(i) / slices, 0)  # Bottom texture coordinate
            glVertex3f(x * radius, y * radius, 0.0)

            glTexCoord2f(float(i) / slices, 1)  # Top texture coordinate
            glVertex3f(x * radius, y * radius, height)
        glEnd()

        # Draw the bottom base of the cylinder
        glBegin(GL_POLYGON)
        for i in range(slices):
            angle = 2 * math.pi * i / slices
            x = math.cos(angle)
            y = math.sin(angle)
            glTexCoord2f(x * 0.5 + 0.5, y * 0.5 + 0.5)  # Texture coordinates for bottom
            glVertex3f(x * radius, y * radius, 0.0)
        glEnd()

        # Draw the top base of the cylinder
        glBegin(GL_POLYGON)
        for i in range(slices):
            angle = 2 * math.pi * i / slices
            x = math.cos(angle)
            y = math.sin(angle)
            glTexCoord2f(x * 0.5 + 0.5, y * 0.5 + 0.5)  # Texture coordinates for top
            glVertex3f(x * radius, y * radius, height)
        glEnd()

        glDisable(GL_TEXTURE_2D)  # Disable textures

    def draw_pins(self):
        for pin in self.pin_positions:
            position = pin["position"]
            rotation = pin["rotation"]
            falling = pin["falling"]
            color = pin["color"]

            glColor3f(*color)
            glPushMatrix()
            glTranslatef(position[0], position[1], position[2])

            if falling:
                pin["rotation"] += 5.0
                if pin["rotation"] >= 90.0:
                    pin["falling"] = False
                glRotatef(pin["rotation"], 1.0, 0.0, 0.0)
            else:
                self.draw_cylinder(self.pin_radius, 0.2, 10)
            glPopMatrix()

    def loopBall(self):
        # Verifica se a bola está indo para a direita ou para a esquerda
        if self.ball_direction[0] > 0:  # Movendo para a direita
            if self.ball_position[0] < 0.43:
                self.ball_position[0] += 0.01  # Move para a direita
            else:
                self.ball_direction[0] = -1  # Inverte a direção para a esquerda
        elif self.ball_direction[0] < 0:  # Movendo para a esquerda
            if self.ball_position[0] > -0.43:
                self.ball_position[0] -= 0.01  # Move para a esquerda
            else:
                self.ball_direction[0] = 1  # Inverte a direção para a direita

        # Chame a renderização da bola aqui após atualizar a posição
        self.draw_ball()


    def keyPressEvent(self, event):
        key = event.key()
        #print(f"Evento capturado {key} ASCII_Value")
        if key == Qt.Key_A:
            if not self.ball_speed>0: 
                self.ball_position[0] -= 0.05
                if self.ball_position[0] < -0.45:
                    self.ball_position[0] = -0.45            
        elif key == Qt.Key_D:
            if not self.ball_speed>0:
                print("Tecla D pressionada.")
                self.ball_position[0] += 0.05
                if self.ball_position[0] > 0.45:
                    self.ball_position[0] = 0.45
        elif key == Qt.Key_W:
            self.force = min(self.force + 0.005, 0.05)
            self.update_progress_bar() 
            print(f"Força aumentada para {self.force}")
        elif key == Qt.Key_S:
            self.force = max(self.force - 0.005, 0.001)
            self.update_progress_bar() 
            print(f"Força diminuída para {self.force}")
        elif key == Qt.Key_Space:
            self.ball_direction = [0.0, 3.0] # Direção para frente
            self.ball_speed = self.force / 5.0
            print(f"Lançando com força {self.force}")
        elif key == Qt.Key_Q:
            print(f"Jogo reiniciado, força redefinida: {self.force}")
            self.reset_game()
        elif key == Qt.Key_R:
            print(f"Bola reposicionada, força redefinida: {self.force}")
            self.reset_ball_position()
    
    def update_progress_bar(self):
        max_force = 0.05
        percentage = (self.force / max_force) * 100
        self.progress_bar.setValue(int(percentage))
    
    def reset_ball_position(self):
        self.ball_position = [0.0, -1.0, 0.0]
        self.ball_speed = 0.0
        self.ball_direction = [0.0, 0.0]
        self.force = 0.00
        self.update_progress_bar()
        self.loopBall()

    def reset_game(self):
        self.ball_position = [0.0, -1.0, 0.0]
        self.ball_speed = 0.0
        self.ball_direction = [0.0, 0.0]
        self.force = 0.0
        self.pin_positions = [
            {"position": [-0.1, self.first_pin_height+0.61, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
            {"position": [0.0, self.first_pin_height+0.61, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
            {"position": [0.1, self.first_pin_height+0.61, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
            {"position": [-0.05, self.first_pin_height+0.1, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#2ª
            {"position": [0.05, self.first_pin_height+0.1, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#2ª
            {"position": [0.0, self.first_pin_height, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#1ª
            {"position": [-0.15, self.first_pin_height+1.1, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [-0.05, self.first_pin_height+1.1, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [0.05, self.first_pin_height+1.1, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [0.15, self.first_pin_height+1.1, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)}#4ª
        ]


def main():
    str_instructions = """
[W] Aumenta a força do lançamento
[S] Diminui a força do lançamento
[A] Move a bola para a esquerda
[D] Move a bola para a direita
    """
    app = QApplication(sys.argv)
    window = QMainWindow() # Janela principal da aplicação
    central_widget = QWidget() # Widget central para: Boloche_Core e placar
    layout_vertical = QVBoxLayout() # Vertical Layout para segurar o BolicheCore e placar
    layout_horizontal = QHBoxLayout()
    force_layout = QHBoxLayout()
    
    force_progress_bar = QProgressBar()
    force_progress_bar.setMinimum(0)
    force_progress_bar.setMaximum(100)
    force_progress_bar.setTextVisible(False)
    placar = QLabel("Pontuação: 0 | 24")
    ball_force = QLabel("Força da bola")
    instrucoes_jogo = QLabel(str_instructions)
    font_placar = QFont()
    game = BowlingGame(placar, force_progress_bar)
    font_placar.setPointSize(24)
    placar.setFont(font_placar)
    placar.setAlignment(Qt.AlignCenter)
    placar.setMaximumHeight(28)
    font_placar.setPointSize(13)
    ball_force.setFont(font_placar)
    instrucoes_jogo.setFont(font_placar)
    instrucoes_jogo.setMaximumWidth(280)
    
    

    layout_horizontal.addWidget(instrucoes_jogo)
    layout_vertical.addWidget(placar)
    layout_vertical.addWidget(game)
    force_layout.addWidget(ball_force)
    force_layout.addWidget(force_progress_bar)
    layout_vertical.addLayout(force_layout)
    layout_horizontal.addLayout(layout_vertical)

    central_widget.setLayout(layout_horizontal)
    window.setCentralWidget(central_widget)
    #window.setWindowTitle('Boliche com PyQt e OpenGL')
    #window.show()
    status_bar = QStatusBar()
    status_bar.showMessage("Ernesto, Ernesto, Rafael, Henrique")
    window.setStatusBar(status_bar)
    window.showMaximized()  # Inicia a janela maximizada
    game.update()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
