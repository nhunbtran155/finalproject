import pygame #
from pygame import mixer
from pygame.locals import *
import random
import sys 

# Khởi tạo Pygame và âm thanh #
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init() # khởi tạo các module pygame đã nhập, gọi nó là vị trí đầu tiên

# Tải âm thanh
explosion_fx = pygame.mixer.Sound('boom.mp3')
explosion_fx.set_volume(0.335)

explosion2_fx = pygame.mixer.Sound('boom1.mp3')
explosion2_fx.set_volume(0.335)

shot_fx = pygame.mixer.Sound('shot.mp3')
shot_fx.set_volume(0.005)

winning = pygame.mixer.Sound('win.mp3')
winning.set_volume(0.25)

loser = pygame.mixer.Sound('lose.mp3')
loser.set_volume(0.25)

nhac_nen = pygame.mixer.Sound('music.mp3')
nhac_nen.set_volume(0.33)

# Cài đặt chung #
clock = pygame.time.Clock() # giới hạn số khung hình trên giây để đảm các biến tronh đó không chạy quá nhanh or quá chậm tùy loại máy tính khác nhaunhau
fps = 60
screen_width = 736
screen_height = 421
screen = pygame.display.set_mode((screen_width, screen_height)) # tạo mà hình trờ chơi
pygame.display.set_caption('CYBER SHIELD') # đặt tên của sổ game

# Xác định phông chữ
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)
font50 = pygame.font.SysFont('Bold System Font', 40)
font60 = pygame.font.SysFont('Bold System Font', 50)

# Xác định các biến trò chơi #
rows = 5
cols = 5
virus_cooldown = 1000
last_virus_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
score = 0  # Biến lưu điểm số
virus_grid_size = 1  # Kích thước ban đầu của nhóm virus (1x1)
max_virus_grid = 5
game_over = 0

# Xác định màu sắc
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)

# Tải ảnh
icon = pygame.image.load('car1.png')
bg = pygame.image.load('dg1.jpg')
intro_background = pygame.image.load("nen.jpg")
end_background = pygame.image.load("end.jpg")
pygame.display.set_icon(icon)

# Chức năng hiển thị văn bản
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.blit(bg, (0, 0))

# Màn hình chờ 
def intro_screen():
    while True:
        screen.blit(intro_background, (0, 0))
        draw_text("PRESS ANY KEY TO START", font50, yellow, screen_width // 2 - 180, screen_height // 2 + 150)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return

# Màn hình kết thúc #
def game_over_screen(score, result):
    while True:
        # Vẽ background kết thúc
        screen.blit(end_background, (0, 0))
        
        # Hiển thị kết quả
        if result == 'win':
            draw_text("YOU WIN!", font60, yellow, screen_width // 2 - 150, screen_height // 2 - 100)
            winning.play()
        else:
            draw_text("YOU DIED!!!", font40, red, screen_width // 2 - 100, screen_height // 2 - 100)
        # Hiển thị điểm số
        draw_text(f"SCORE: {score}", font30, white, screen_width // 2 - 50, screen_height // 2 - 30)

        # Hiển thị hướng dẫn chơi lại
        draw_text("PRESS '1' TO RESTART", font50, red, screen_width // 2 - 145, screen_height // 2 + 100)
        pygame.display.update()

        # Chờ người chơi nhấn '1'
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return  # Quay lại màn hình chờ

# Spaceship class #
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('car1.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        speed = 5
        cooldown = 300
        game_over = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed
        time_now = pygame.time.get_ticks()
        if key[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= speed
        if key[pygame.K_DOWN] and self.rect.bottom < screen_height:
            self.rect.y += speed
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            shot_fx.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now
        self.mask = pygame.mask.from_surface(self.image)
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 10))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 10))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over

# Bullet class #
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('dan1.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.groupcollide(bullet_group, virus_group, True, True):
            global score
            score += 10  # Tăng điểm khi tiêu diệt virus
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

# Virus class #
class Viruss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('covid' + str(random.randint(1, 4)) + '.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        # Di chuyển sang trái và phải
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 145:
            self.move_direction *= -1
            self.move_counter *= self.move_direction



# Virus Bullet class #
class Virus_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('virus_bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed = 5

    def update(self):
        self.rect.y += 2  
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

# Explosion class #
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(7, 13):
            img = pygame.image.load('ex' + str(num) + '.png')
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        if self.index >= len(self.images) - 1 and self.counter > -explosion_speed:
            self.kill()


# Tạo nhóm sprite #
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
virus_group = pygame.sprite.Group()
virus_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()


# Tạo xe cứu thương 
spaceship = Spaceship(screen_width // 2, screen_height - 50, 3)
spaceship_group.add(spaceship)


def create_virus_group(grid_size): 
    virus_group.empty()  # Xóa nhóm virus cũ
    
    # Tính toán kích thước và khoảng cách của lưới
    virus_width = 30  # Giả định chiều rộng của virus
    virus_height = 30  # Giả định chiều cao của virus
    spacing_x = 40  # Khoảng cách ngang giữa các virus
    spacing_y = 25  # Khoảng cách dọc giữa các virus
    
    total_width = grid_size * (virus_width + spacing_x) - spacing_x
    start_x = (screen_width - total_width) // 2  # Bắt đầu ở giữa màn hình
    
    total_height = grid_size * (virus_height + spacing_y) - spacing_y
    start_y = (screen_height // 3 - total_height // 2)  # 2/3 phần trên của màn hình

    # Tạo lưới virus #
    for row in range(grid_size):
        for col in range(grid_size):
            virus_x = start_x + col * (virus_width + spacing_x)
            virus_y = start_y + row * (virus_height + spacing_y)
            virus = Viruss(virus_x, virus_y)
            virus_group.add(virus)


def virus_shoot(): #
    global last_virus_shot
    time_now = pygame.time.get_ticks()  # Lấy thời gian hiện tại
    if time_now - last_virus_shot > virus_cooldown:  # Kiểm tra cooldown bắn đạn
        if len(virus_group) > 0:  # Kiểm tra xem còn virus không
            attacking_virus = random.choice(virus_group.sprites())  # Chọn 1 virus ngẫu nhiên
            virus_bullet = Virus_Bullets(attacking_virus.rect.centerx, attacking_virus.rect.bottom)
            virus_bullet_group.add(virus_bullet)  # Thêm đạn vào nhóm đạn
            last_virus_shot = time_now



# Vòng lặp chính #
run = True
while run: # để giữ màn hình đứng in, không biến mất tức thì
    intro_screen()
    
    # Reset mọi thứ
    nhac_nen.play(-1)  # Chạy nhạc nền liên tục
    score = 0  # Reset điểm số
    countdown = 3  # Reset thời gian đếm ngược
    spaceship_group.empty()  # Làm trống nhóm sprite
    bullet_group.empty()
    virus_group.empty()
    explosion_group.empty()
    virus_bullet_group.empty()
    
    # Tạo lại đối tượng chính #
    spaceship = Spaceship(screen_width // 2, screen_height - 100, 3)
    spaceship_group.add(spaceship)
    
    # Tạo lại viruses #

    create_virus_group(virus_grid_size)
    game_over = 0

    while game_over == 0:
        clock.tick(fps)
        draw_bg()
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: # thoát khỏi của sổ game trên máy tính
                run = False
                game_over = -1


        if countdown > 0:
            draw_bg()
            draw_text('GET READY!', font40, red, screen_width // 2 - 110, screen_height // 2 - 50)
            draw_text(str(countdown), font40, red, screen_width // 2, screen_height // 2)
            pygame.display.update()
            count_timer = pygame.time.get_ticks()
            if count_timer - last_count > 1000:
                countdown -= 1
                last_count = count_timer
            continue

        


        virus_shoot()
        # Cập nhật và hiển thị các đối tượng
        spaceship_group.update()
        bullet_group.update()
        virus_group.update()
        explosion_group.update()
        virus_bullet_group.update()
        spaceship_group.draw(screen)
        bullet_group.draw(screen)
        virus_group.draw(screen)
        explosion_group.draw(screen)
        virus_bullet_group.draw(screen)

        # Hiển thị điểm 
        draw_text(f"SCORE: {score}", font30, white, 10, 10)
        pygame.display.update() # cập nhật mới game

        # Kiểm tra kết thúc game
        if len(virus_group) == 0:
            game_over = 1
        elif spaceship.health_remaining <= 0:
            game_over = -1


    nhac_nen.stop()
    if game_over == -1:
        loser.play()
        game_over_screen(score, "lose")
        virus_grid_size = 1
        spaceship.health_remaining = 3  # Hồi lại máu
        create_virus_group(virus_grid_size)
        game_over = 0
    else:
        virus_grid_size += 1  # Tăng kích thước lưới virus
        if virus_grid_size > max_virus_grid:  # Nếu đạt kích thước tối đa
            screen.blit(end_background, (0, 0))
            winning.play()
            draw_text("YOU WIN ALL LEVELS!", font40, red, screen_width // 2 - 200, screen_height // 2 - 50)
            draw_text(f"SCORE:{score}", font30, white, screen_width // 2 - 50, screen_height // 2+100)
            pygame.display.update()
            pygame.time.wait(5000)  # Hiển thị thông báo trong 3 giây
            run = False
        else:
            game_over = 0  # Reset trạng thái game
            spaceship.health_remaining = 3  # Hồi lại máu
            create_virus_group(virus_grid_size)  # Tạo virus mới