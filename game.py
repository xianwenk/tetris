import math
import random
import sys
from copy import deepcopy
import pygame as pg
import pygame.locals as pl

pg.init()        # 初始化pygame模块

pg.display.set_caption('俄罗斯方块')       # 设置当前窗口标题
fclock = pg.time.Clock()               # 创建一个对象来帮助跟踪时间

FPS = 30    # 每秒的传送帧数
FONT = pg.font.SysFont('simhei', 30)         # 从系统字体创建字体对象
WindowX = 30
WindowY = 25
award = 10  # 奖励倍数
BLOCK_SIZE = 30          # 一个方块的大小
LINE_SPACE = 2
MAIN_X, MAIN_Y = MAIN_WINDOW = [30, 25]
GAME_X, GAME_Y = GAME_WINDOW = [20, MAIN_Y]
NEXT_X = MAIN_X - GAME_X

RED = (255, 0, 0)       # 运用RGB颜色转载，RGB的颜色表示方法
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class BaseBlock:                 # 创建一个类建立基本的方块
    def __init__(self):
        self.turn_times = 0
        self.x_move = 0
        self.y_move = 0
        self.location = []


class IBlock(BaseBlock):            #  定义一个小类，创建I型方块，#在4*4的小网格内，以中间左上角坐下为原点（0,0），7种方块及其各形态4个方块在小网格的相对坐标
                                    # 移动时记录小网络（0,0）点在游戏网格的（x,y)，就知道4个方块在游戏网格中的位置
    def __init__(self):
        super().__init__()
        self.dot = {
            0: [(0, 1), (0, 0), (0, -1), (0, -2)],
            1: [(-1, 0), (0, 0), (1, 0), (2, 0)],
        }


class OBlock(BaseBlock):
    def __init__(self):
        super().__init__()           # 创建o型方块
        self.dot = {
            0: [(0, 0), (1, 0), (1, 1), (0, 1)],
        }


class LBlock(BaseBlock):
    def __init__(self):
        super().__init__()
        self.dot = {
            0: [(0, 0), (0, 1), (0, -1), (-1, 1),(1,1)],           # 创建L型方块
            1: [(0, 0), (-1, 0), (1, 0), (1, 1)],
            2: [(0, 0), (0, 1), (0, -1), (1, -1)],
            3: [(0, 0), (1, 0), (-1, 0), (-1, -1)],
        }


class ULBlock(BaseBlock):
    def __init__(self):                                        # 定义一个小类创建U型方块
        super().__init__()
        self.dot = {
            0: [(0, 0), (0, 1), (0, -1), (1, 1)]
            ,
            1: [(0, 0), (-1, 0), (1, 0), (1, -1)],
            2: [(0, 0), (0, 1), (0, -1), (-1, -1)],
            3: [(0, 0), (1, 0), (-1, 0), (-1, 1)],
        }


class TBlock(BaseBlock):
    def __init__(self):
        super().__init__()
        self.dot = {
            0: [(0, 0), (1, 0), (0, 1), (-1, 0)],
            1: [(0, 0), (1, 0), (0, 1), (0, -1)],
            2: [(0, 0), (1, 0), (0, -1), (-1, 0)],            # 创建T型方块
            3: [(0, 0), (0, -1), (0, 1), (-1, 0)],
        }


class SBlock(BaseBlock):
    def __init__(self, *args, **kwargs):
        super().__init__()                             # 定义一个小类，创建S型方块
        self.dot = {
            0: [(0, 0), (0, 1), (-1, 0), (-1, -1)],
            1: [(0, 0), (1, 0), (0, 1), (-1, 1)],
        }


class ZBlock(BaseBlock):
    def __init__(self):
        super().__init__()
        self.dot = {
            0: [(0, 0), (0, 1), (-1, 0), (-1, -1)],              # 创建Z型方块
            1: [(0, 0), (1, 0), (0, 1), (-1, 1)],
        }


class Game():
    def __init__(self):      # self表示对象本身，谁调用，就表示谁
        self.fps = FPS
        self.screen = pg.display.set_mode([MAIN_X * BLOCK_SIZE, MAIN_Y * BLOCK_SIZE])    # 初始化窗口或屏幕以供显示并设置大小
        self.screen.fill(WHITE)
        self.stop_block = {k: [] for k in range(MAIN_Y)}     # 当k在y轴上循环，当方块在y轴最下方时停止下落；
        self.level_list = ['简单', '一般', '困难', '地狱']    # 设置难度分类
        self.moshi_list = ['单人','双人']
        self.moshi = 1      # 定义初始的单人模式
        self.level = 1      # 定义初始难度等级
        self.score = 0      # 定义初始分数
        self.next_block = self.create_next()     # 调用create_next这个函数生成下一个方块
        self.now_block = None
        self.gaming = False
        self.click_box = []
        self.click_color = RED

    def draw_text(self):
        score_obj = FONT.render('分数: %s' % self.score, True, (0, 0, 0), )   # render(内容，是否抗锯齿，字体颜色，字体背景颜色)
        level_obj = FONT.render('等级: %s' % self.level_list[self.level - 1], True, (0, 0, 0), )
        x, y = self.three.topleft

        self.screen.blit(score_obj, [x + BLOCK_SIZE * 2.5, y + BLOCK_SIZE * 5])   # 在主窗口上建立一个小窗口显示分数
        self.screen.blit(level_obj, [x + BLOCK_SIZE * 1.5, y + BLOCK_SIZE * 7.5])  # 在主窗口上建立一个小窗口显示难度等级

    @property              # 装饰器，让此方法变为私有属性，防止对其修改，可以用调用属性形式来调用方法，后面不需要加（);
    def speed(self):
        # print(round(self.level / 10, 1))
        return round(self.level / 10, 1)         # 定义一个速度函数，用等级除以10，保留一位小数。控制着难度的等级，难度越大，速度越快。

    def start(self):
        if self.gaming:
            if not self.now_block:
                self.change_next()
            self.draw_next_block()
            self.draw_now_block()
            self.draw_stop()
            self.draw_wall()
            self.move()
            remove_line = self.check_full_block()        # 消去的行数调用check.full.block函数；
            if remove_line:                             # 分数等于除去的行数乘上倍数；
                self.score += award * remove_line
            self.draw_text()
        else:
            self.choice_level()

    def level_add(self):
        if self.level + 1 <= len(self.level_list):
            self.level += 1
        else:
            self.level = 1

    def level_pop(self):
        if self.level - 1 >= 1:
            self.level -= 1
        else:
            self.level = len(self.level_list)

    def moshi_add(self):
        if self.moshi + 1 <= len(self.moshi_list):
            self.moshi += 1
        else:
            self.moshi = 1

    def moshi_pop(self):
        if self.moshi - 1 <= len(self.moshi_list):
            self.moshi -= 1
        else:
            self.moshi = len(self.moshi_list)

    def to_gaming(self):
        self.gaming = not self.gaming

    def choice_level(self):
        self.screen.fill(WHITE)
        self.click_box = []
        # self.rect = pg.draw.rect(self.screen, BLACK, (0, 0, MAIN_X*BLOCK_SIZE, MAIN_Y*BLOCK_SIZE), LINE_SPACE)
        surface_image = pg.image.load(r"teris3.jpg")
        self.screen.blit(surface_image, [0,-200])

        font1 = FONT.render('排行榜', True, BLACK)

        self.rect1 = pg.draw.rect(self.screen, BLACK, (MAIN_X * BLOCK_SIZE // 2 - 150 // 2, 80, 150, 60), 10)
        # self.click_box.append([self.rect1, self.show_order])

        self.screen.blit(font1,
                         [self.rect1.centerx - font1.get_width() // 2,
                          self.rect1.centery - font1.get_height() // 2])

        self.rect2 = pg.draw.rect(self.screen, BLACK, (MAIN_X * BLOCK_SIZE // 2 - 150 // 2, 200, 150, 60), 10)

        font2 = FONT.render(self.level_list[self.level - 1], True, (0, 0, 0), )
        self.screen.blit(font2,
                         [self.rect2.centerx - font2.get_width() // 2,
                          self.rect2.centery - font2.get_height() // 2])

        self.rect2_left = pg.draw.circle(self.screen, BLACK,
                                         (MAIN_X * BLOCK_SIZE // 2 - 120, self.rect2.y + self.rect2.height // 2), 15, 5)
        self.click_box.append([self.rect2_left, self.level_pop])

        self.rect2_right = pg.draw.circle(self.screen, BLACK,
                                          (MAIN_X * BLOCK_SIZE // 2 + 120, self.rect2.y + self.rect2.height // 2), 15,
                                          5)
        self.click_box.append([self.rect2_right, self.level_add])

        self.rect3 = pg.draw.rect(self.screen, BLACK, (MAIN_X * BLOCK_SIZE // 2 - 150 // 2, 270, 150, 60), 10)
         # pygame.draw.rect(Surface, color, Rect, width=0): return Rect
         # 在Surface上绘制矩形，第二个参数是线条（或填充）的颜色，第三个参数Rect的形式是((x, y), (width, height))，表示的是所绘制矩形的区域，
        # 其中第一个元组(x, y)表示的是该矩形左上角的坐标，第二个元组 (width, height)表示的是矩形的宽度和高度。width表示线条的粗细，单位为像素；默认值为0，表示填充矩形内部。
        font3 = FONT.render(self.moshi_list[self.moshi - 1], True, (0, 0, 0), )
        self.screen.blit(font3,
                         [self.rect3.centerx - font2.get_width() // 2,
                          self.rect3.centery - font2.get_height() // 2])

        self.rect3_left = pg.draw.circle(self.screen, BLACK,
                                         (MAIN_X * BLOCK_SIZE // 2 - 120, self.rect3.y + self.rect3.height // 2), 15, 5)

        # 画一个圆来选择单人或者多人
        self.click_box.append([self.rect3_left, self.moshi_pop])

        self.rect3_right = pg.draw.circle(self.screen, BLACK,
                                        (MAIN_X * BLOCK_SIZE // 2 + 120, self.rect3.y + self.rect3.height // 2), 15, 5)
        self.click_box.append([self.rect3_right, self.moshi_add])

        font4 = FONT.render('开始游戏', True, BLACK)
        self.rect4 = pg.draw.rect(self.screen, BLACK, (MAIN_X * BLOCK_SIZE // 2 - 200 // 2, 350, 200, 60), 10)
        self.click_box.append([self.rect4, self.to_gaming])
        self.screen.blit(font4,
                         [self.rect4.centerx - font4.get_width() // 2,
                          self.rect4.centery - font4.get_height() // 2])



    def click_check(self, axis):
        if not self.gaming:
            x, y = axis
            for i in self.click_box:                     # 定义一个函数检查点击，鼠标点击某一个框时会变颜色，；
                if i[0].left <= x <= i[0].right:
                    if i[0].top <= y < i[0].bottom:
                        pg.draw.rect(self.screen,RED,i[0],10)
                        i[1]()

    def change_next(self):
        for i in self.next_block.dot[0]:
            self.now_block = self.next_block
            if not self.stop_check(i):     # 当i不在这个函数里循环时就打印game over；
                print('game over')

                self.now_block.location = []
                # break
                self.__init__()
        self.now_block = self.next_block
        self.now_block.location = [list(i) for i in self.next_block.dot[0]]
        self.next_block = self.create_next()

    def now_block_to_stop(self):
        for x, y in self.now_block.location:
            if math.ceil(y) == -1:        # 向上取整，小数部分直接舍去，并向正数部分进1，(如果是负数部分不进1）；
                return
            else:
                y_stop_block = self.stop_block[int(y)]
                # print(5 in y_stop_block)
                if (x + GAME_X // 2) not in y_stop_block:
                    y_stop_block.append(x + GAME_X // 2)
        self.change_next()

    def stop_check(self, axis):
        x, y = axis
        y_stop_block = self.stop_block.get(y)
        if y == int(y):
            if y_stop_block:
                if (x + GAME_X // 2) in y_stop_block:
                    # print(x + GAME_X // 2, y_stop_block, y)
                    return False
            return True
        else:
            y1 = int(y)
            y2 = math.ceil(y)
            check1 = self.stop_check((x, y1))
            check2 = self.stop_check((x, y2))
            if check1 and check2:
                return True
            return False

    def wall_check(self, location):
        wrong = 0
        for x, y in location:
            if x + GAME_X // 2 < 0:
                wrong = 1
            elif x + GAME_X // 2 > 19:        #改变方块左右一定位置，像有一堵无形的墙；
                wrong = -1
        if wrong:
            for i in location:
                i[0] += wrong
            self.wall_check(location)
        return location

    def move_check(self):
        for x, y in self.now_block.location:
            z = round(y + self.speed, 1)       # 定义一个z为y+速度函数。
            if self.stop_check((x, y)):
                pass
            else:
                return False

            if z <= MAIN_Y - 1:  # (0-19)      # 检查到到达底部墙体，方块就不再下落；
                # 到达底部墙体
                pass                          # 用pass关键字来占位；
            else:
                return False
        return True

    def move(self, ):
        if self.move_check():
            for i in self.now_block.location:
                i[1] = round(self.speed + i[1], 1)
            self.now_block.y_move = round(self.speed + self.now_block.y_move, 1)
        else:
            self.now_block_to_stop()

    def change_block(self):
        new_location = []
        dot = self.now_block.dot                                     # 改变方块形状；

        index = self.now_block.turn_times % len(dot.keys())
        for x, y in self.now_block.dot[index]:
            new_location.append([x + self.now_block.x_move, y + self.now_block.y_move])

        return new_location

    def turn(self, direction):

        location_copy = deepcopy(self.now_block.location)
        turn_switch = 0
        if direction == 'LEFT':
            for i in location_copy:
                i[0] -= 1

        elif direction == 'RIGHT':
            for i in location_copy:
                i[0] += 1
        elif direction == 'UP':
            self.now_block.turn_times += 1
            location_copy = self.change_block()

        elif direction == 'left':
            for i in location_copy:
                i[0] -= 1
        elif direction == 'right':
            for i in location_copy:
                i[0] += 1
        elif direction == 'up':
            self.now_block.turn_times += 1
            location_copy = self.change_block()
        # elif direction == 'DOWN':
        #     pass

        location_copy = self.wall_check(location_copy)

        for i in location_copy:
            check_result = self.stop_check(i)

            if not check_result:
                turn_switch += 1

        if turn_switch == 0:
            self.now_block.location = location_copy
            if direction == 'LEFT':
                self.now_block.x_move -= 1
            elif direction == 'RIGHT':
                self.now_block.x_move += 1
            elif direction == 'left':
                self.now_block.x_move -= 1
            elif direction == 'right':
                self.now_block.x_move += 1
            # elif direction == 'UP':

    def draw_now_block(self):
        for x, y in self.now_block.location:
            pg.draw.rect(self.screen, BLUE, (
                (x + GAME_X // 2) * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X // 2) * BLOCK_SIZE, y * BLOCK_SIZE, LINE_SPACE, BLOCK_SIZE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X // 2) * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, LINE_SPACE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X // 2 + 1) * BLOCK_SIZE, y * BLOCK_SIZE, LINE_SPACE, BLOCK_SIZE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X // 2) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE, BLOCK_SIZE, LINE_SPACE), 0)

    def draw_next_block(self):
        self.screen.fill(WHITE)
        for x, y in self.next_block.dot[0]:
            # print(x, y)
            pg.draw.rect(self.screen, RED, (
                (x + GAME_X + NEXT_X // 2) * BLOCK_SIZE, (y + NEXT_X // 2) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X + NEXT_X // 2) * BLOCK_SIZE, (y + NEXT_X // 2) * BLOCK_SIZE, LINE_SPACE, BLOCK_SIZE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X + NEXT_X // 2) * BLOCK_SIZE, (y + NEXT_X // 2) * BLOCK_SIZE, BLOCK_SIZE, LINE_SPACE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X + NEXT_X // 2 + 1) * BLOCK_SIZE, (y + NEXT_X // 2) * BLOCK_SIZE, LINE_SPACE, BLOCK_SIZE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X + NEXT_X // 2) * BLOCK_SIZE, (y + NEXT_X // 2 + 1) * BLOCK_SIZE, BLOCK_SIZE, LINE_SPACE), 0)

    @staticmethod             # 装饰器，装饰的成员函数可以通过类名，方法名来调用；
    def create_next():
        return random.choice([IBlock, OBlock, LBlock, SBlock, ZBlock, TBlock, ULBlock])()
           # 七种方块随机下落的概率是相同的，每次下落的那个方块都是以第一种形式下落；用random.choice函数随机返回数组中的元素随机选取一种方块；
           # 从序列种随机取一个元素（sequence可以是列表，可以是元组，可以是字符串，可以是字典）

    # 画静止方块
    def draw_stop(self):

        for k, v in self.stop_block.items():
            if v:
                for i in v:
                    pg.draw.rect(self.screen, GREEN, (i * BLOCK_SIZE, k * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                    pg.draw.rect(self.screen, BLACK, (i * BLOCK_SIZE, k * BLOCK_SIZE, LINE_SPACE, BLOCK_SIZE), 0)
                    pg.draw.rect(self.screen, BLACK, (i * BLOCK_SIZE, k * BLOCK_SIZE, BLOCK_SIZE, LINE_SPACE), 0)
                    pg.draw.rect(self.screen, BLACK, ((i + 1) * BLOCK_SIZE, k * BLOCK_SIZE, LINE_SPACE, BLOCK_SIZE), 0)
                    pg.draw.rect(self.screen, BLACK, (i * BLOCK_SIZE, (k + 1) * BLOCK_SIZE, BLOCK_SIZE, LINE_SPACE), 0)

    def draw_wall(self):
        pg.draw.rect(self.screen, BLACK, (0, 0, MAIN_X * BLOCK_SIZE, MAIN_Y * BLOCK_SIZE), LINE_SPACE)
        pg.draw.rect(self.screen, BLACK, (0, 0, GAME_X * BLOCK_SIZE, GAME_Y * BLOCK_SIZE), LINE_SPACE)
        pg.draw.rect(self.screen, BLACK, (GAME_X * BLOCK_SIZE, 0, NEXT_X * BLOCK_SIZE, NEXT_X * BLOCK_SIZE), LINE_SPACE)
        self.three = pg.draw.rect(self.screen, BLACK, (GAME_X * BLOCK_SIZE, NEXT_X * BLOCK_SIZE, (MAIN_X - GAME_X) * BLOCK_SIZE,
        (MAIN_Y - NEXT_X) * BLOCK_SIZE),LINE_SPACE)

    def check_full_block(self):
        new_values = []
        block_keys = list(self.stop_block.keys())
        block_values = list(self.stop_block.values())
        remove_line = 0    # 先定义要消的行数为0
        for i in block_values:
            if len(i) < GAME_X:          # i是一个数组，当i的长度小于game_x时
                new_values.append(i)
            else:
                remove_line += 1
        while len(new_values) < len(block_keys):
            new_values.insert(0, [])
        self.stop_block = dict(zip(block_keys, new_values))
        return remove_line




if __name__ == '__main__':
    game = Game()
    while True:
        fclock.tick(game.fps)
        game.start()
        for event in pg.event.get():
            if event.type == pl.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pl.KEYDOWN:
                if game.gaming:
                        if event.key == pl.K_d:  # player1 :d键右移动一格
                            game.turn('right')
                        elif event.key == pl.K_a:  # player1 :a键左移动一格
                            game.turn('left')
                        elif event.key == pl.K_w:  # player1 :w键旋转一次
                            game.turn('up')
                        elif event.key == pl.K_s:  # player1 :s键加速下移
                            game.fps = FPS * 10

                        if event.key == pl.K_LEFT:
                            game.turn('LEFT')
                        elif event.key == pl.K_RIGHT:
                            game.turn('RIGHT')
                        elif event.key == pl.K_UP:
                            game.turn('UP')
                        elif event.key == pl.K_DOWN:
                            game.fps = FPS * 10            # 创建一个时钟，fps在时钟里，tick告诉pygame一秒循环多少次，当按住向下键时，帧率变快，pygame绘图的时间变快，
                            # pygame等待的时间变少，pygame里的每个循环的时间变快，所以控制方块下落速度的那个循环加快，所以按下向下键则下落速度变快。从上往下下落时间是一样的，当
                            # 按下向下键时，帧率变快，方块每次下落的像素加快。

                        elif event.key == pl.K_ESCAPE:
                            sys.exit()
                else:
                    if event.key == pl.K_LEFT:
                        game.level_pop()
                    elif event.key == pl.K_RIGHT:
                        game.level_add()
                    elif event.key == pl.K_SPACE:
                        game.to_gaming()
                    else:
                        print(event.key)

            elif event.type == pl.KEYUP:
                if event.key == pl.K_DOWN or event.key == pl.K_s:
                    game.fps = FPS
            elif event.type == pl.MOUSEBUTTONDOWN:
                axis = pg.mouse.get_pos()
                game.click_check(axis)
        pg.display.update()
