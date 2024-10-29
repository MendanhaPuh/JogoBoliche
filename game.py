import sys
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QOpenGLWidget, QStatusBar
from PyQt5.QtGui import QFont
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image

# Variáveis globais para controlar a posição da bola
ball_position = [0.0, -0.8, 0.0]  # Inicialmente no centro, perto da base da pista
ball_direction = [0.0, 1.0]  # Direção do movimento da bola
ball_speed = 0.02  # Velocidade da bola

# Raio da bola e dos pinos
ball_radius = 0.05
pin_radius = 0.02

# Variáveis globais para a posição dos pinos
pin_positions = [
    [-0.1, 0.9, 0.0], [0.0, 0.9, 0.0], [0.1, 0.9, 0.0],  # Primeira linha
    [-0.05, 0.8, 0.0], [0.05, 0.8, 0.0],  # Segunda linha
    [0.0, 0.7, 0.0]  # Pino central
]

# Variável para a pontuação
score = 0

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    gluOrtho2D(-1.0, 1.0, -1.0, 1.0)

def draw_ball():
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(ball_position[0], ball_position[1], ball_position[2])
    glutSolidSphere(ball_radius, 50, 50)
    glPopMatrix()

def draw_pins():
    glColor3f(1.0, 1.0, 1.0)
    for position in pin_positions:
        glPushMatrix()
        glTranslatef(position[0], position[1], position[2])
        glutSolidCylinder(pin_radius, 0.1, 20, 20)
        glPopMatrix()

def check_collision():
    global pin_positions, score
    new_pin_positions = []
    
    for position in pin_positions:
        distance = math.sqrt(
            (ball_position[0] - position[0]) ** 2 + 
            (ball_position[1] - position[1]) ** 2
        )
        if distance < (ball_radius + pin_radius):
            print(f"Colisão detectada com o pino em {position}!")
            score += 1
        else:
            new_pin_positions.append(position)
    
    pin_positions = new_pin_positions

def draw_score():
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(-0.9, 0.9)
    for char in f'Score: {score}':
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char)) # type: ignore


def draw():
    glClear(GL_COLOR_BUFFER_BIT)
    
    # Desenhar pista de boliche
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_QUADS)
    glVertex2f(-0.5, -1.0)
    glVertex2f(0.5, -1.0)
    glVertex2f(0.5, 1.0)
    glVertex2f(-0.5, 1.0)
    glEnd()
    
    draw_ball()
    draw_pins()
    draw_score()
    
    glFlush()

def move_ball(value):
    global ball_position, ball_direction
    
    # Mover a bola na direção atual
    ball_position[0] += ball_direction[0] * ball_speed
    ball_position[1] += ball_direction[1] * ball_speed
    
    # Verificar colisões com os pinos
    check_collision()
    
    # Verificar colisões com as bordas da pista
    if ball_position[0] - ball_radius < -0.5 or ball_position[0] + ball_radius > 0.5:
        ball_direction[0] *= -1
    if ball_position[1] + ball_radius > 1.0:
        ball_direction[1] *= -1
    
    # Verificar se a bola saiu da pista (parte inferior)
    if ball_position[1] - ball_radius < -1.0:
        reset_game()
    
    glutPostRedisplay()
    glutTimerFunc(16, move_ball, 0)

def reset_game():
    global ball_position, ball_direction, pin_positions, score
    ball_position = [0.0, -0.8, 0.0]
    ball_direction = [0.0, 1.0]
    pin_positions = [
        [-0.1, 0.9, 0.0], [0.0, 0.9, 0.0], [0.1, 0.9, 0.0],  # Primeira linha
        [-0.05, 0.8, 0.0], [0.05, 0.8, 0.0],  # Segunda linha
        [0.0, 0.7, 0.0]  # Pino central
    ]
    score = 0

def main():
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(500, 500)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Jogo de Boliche")
    init()
    glutDisplayFunc(draw)
    glutTimerFunc(16, move_ball, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
