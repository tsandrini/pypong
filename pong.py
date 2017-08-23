#!/usr/bin/env python
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import random as r
import sys

class Pong(QMainWindow):
    def __init__(self):
        super(Pong, self).__init__()
        self.board = Board(self)
        self.statusbar = self.statusBar()
        self.board.msg2statusbar[str].connect(self.statusbar.showMessage)
        self.setCentralWidget(self.board)
        self.setWindowTitle('Pong')
        self.resize(600, 400)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        self.board.start()
        self.show()

class Board(QFrame):
    msg2statusbar = pyqtSignal(str)

    def __init__(self, parent):
        super(Board, self).__init__(parent)
        self.balls = []
        self.size = parent.geometry()
        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)
        self.speed = 10
        self.paddle = Paddle(
            pos={'x': 15, 'y': self.size.height() * 0.75 },
            size={'x': 100, 'y': 5},
            speed=5
        )
        self.reset()

    def start(self):
        self.timer.start(self.speed, self)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.msg2statusbar.emit("Points: %d \n Difficulty: %d" % (self.points, self.difficulty))
            self.update()
            self.check_collisions()
            self.paddle.update()
            for ball in self.balls:
                ball.update()

            # So dynamic 8)
            if (self.points % (10 * (2 ** self.difficulty))) == 0 and self.can_inc_diff:
                self.increase_difficulty()
                self.can_inc_diff = False

    def paintEvent(self, event):
        painter = QPainter(self)
        self.paddle.draw(painter)
        for ball in self.balls:
            ball.draw(painter)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Escape, Qt.Key_Q):
            QApplication.exit()
        elif key in (Qt.Key_Left, Qt.Key_H):
            self.paddle.direction = 1
        elif key in (Qt.Key_Right, Qt.Key_L):
            self.paddle.direction = 2

    def keyReleaseEvent(self, event):
        key = event.key()
        self.paddle.direction = 0

    def increase_difficulty(self):
        self.add_ball()
        self.difficulty += 1
        self.paddle.size['x'] += self.size.width() * 0.08
        self.paddle.speed += 1

    def check_collisions(self):
        if (self.paddle.pos['x'] <= 0 and self.paddle.direction == 1) or (self.paddle.pos['x'] + self.paddle.size['x'] >= self.size.width() and self.paddle.direction == 2):
            self.paddle.direction = 0

        for ball in self.balls:
            if ball.pos['x'] <= 0 or ball.pos['x'] >= (self.size.width() - ball.size['x']):
                ball.speed['x'] = -ball.speed['x']

            if ball.pos['y'] <= 0:
                ball.speed['y'] = -ball.speed['y']

            if ((ball.pos['y'] + ball.size['y']) >= self.paddle.pos['y'] and ball.pos['y'] < self.paddle.pos['y']) and ((ball.pos['x'] + ball.size['x']) >= self.paddle.pos['x'] and (ball.pos['x'] - ball.size['x']) <= (self.paddle.pos['x'] + self.paddle.size['x'])):
                ball.speed['y'] = -ball.speed['y']
                self.points += 1
                self.can_inc_diff = True

            if ball.pos['y'] + ball.size['y'] > self.size.height():
                self.reset()

    def add_ball(self):
        self.balls.append(Ball(
            pos={'x': 5, 'y': 50},
            size={'x': 10, 'y': 10},
            speed={'x': 1 + self.difficulty, 'y': 1 + self.difficulty}
        ))

    def reset(self):
        self.can_inc_diff = False
        self.points = 0
        self.difficulty = 1
        self.balls.clear()
        self.add_ball()
        self.paddle.reset()

class Paddle():

    def __init__(self, *args, **kwargs):
        self.pos = self.fallback_pos = kwargs['pos'] if 'pos' in kwargs else {'x': 10, 'y': 10}
        self.size = self.fallback_size = kwargs['size'] if 'size' in kwargs else {'x': 100, 'y': 10}
        self.speed = self.fallback_speed = kwargs['speed'] if 'speed' in kwargs else 5
        self.color = kwargs['color'] if 'color' in kwargs else QColor(r.randrange(0, 255), r.randrange(0, 255), r.randrange(0, 255))
        self.direction = 0

    def update(self):
        if self.direction == 1:
            self.pos['x'] -= self.speed
        elif self.direction == 2:
            self.pos['x'] += self.speed

    def draw(self, painter):
        painter.fillRect(
            self.pos['x'] + 1,
            self.pos['y'] + 1,
            self.size['x'] - 2,
            self.size['y'] - 2,
            self.color
        )

    def reset(self):
        self.pos = self.fallback_pos
        self.speed = self.fallback_speed
        self.direction = 1
        self.size = self.fallback_size
        self.color = QColor(r.randrange(0, 255), r.randrange(0, 255), r.randrange(0, 255))

class Ball():

    def __init__(self, *args, **kwargs):
        self.pos = self.fallback_pos = kwargs['pos'] if 'pos' in kwargs else {'x': 50, 'y': 50}
        self.size = self.fallback_size = kwargs['size'] if 'size' in kwargs else {'x': 10, 'y': 10}
        self.speed = self.fallback_speed = kwargs['speed'] if 'speed' in kwargs else {'x': 3, 'y': 3}
        self.color = self.fallback_color = kwargs['color'] if 'color' in kwargs else QColor(r.randrange(0, 255), r.randrange(0, 255), r.randrange(0, 255))

    def update(self):
        self.pos['x'] += self.speed['x']
        self.pos['y'] += self.speed['y']

    def draw(self, painter):
        painter.fillRect(
            self.pos['x'] + 1,
            self.pos['y'] + 1,
            self.size['x'] - 2,
            self.size['y'] - 2,
            self.color
        )

def main():
    app = QApplication([])
    pong = Pong()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
