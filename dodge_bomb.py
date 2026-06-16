import os
import random
import sys
import time
import math
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool] :
    """
    引数：こうかとんRect or 爆弾Rect
    戻り値：横方向・縦方向の判定結果タプル
    （True：画面内／False：画面外）
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right: # 横判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: # 縦判定
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    引数:screen
    戻り値:None
    """
    break_img = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(break_img,(0,0,0),pg.Rect(0,0,WIDTH,HEIGHT))    
    break_img.set_alpha(200)
    fonto = pg.font.Font(None, 100)
    go_txt = fonto.render("Game Over",True,(255, 255, 255))
    break_img.blit(go_txt, [350, HEIGHT/2])
    cry_kk_img = pg.image.load("fig/8.png")
    break_img.blit(cry_kk_img, [WIDTH/2 - 350, HEIGHT/2])
    break_img.blit(cry_kk_img, [WIDTH/2 + 300, HEIGHT/2])
    screen.blit(break_img, (0, 0))  
    pg.display.update()
    time.sleep(5) 


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    引数:なし
    戻り値:タプルbb_imgs, bb_accs
    """
    bb_imgs = [] # 爆弾のサイズ
    bb_accs = [] # 爆弾の加速度
    for r in range(1, 11): 
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r) 
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img) 
        bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
        base_img = pg.image.load("fig/3.png")
        flip_img = pg.transform.flip(base_img,True,False)
        kk_dict = {
            (0,0):base_img,
            (-5,0):base_img,
            (-5,-5):pg.transform.rotozoom(base_img,-45,1.0),
            (0,-5):pg.transform.rotozoom(flip_img,90,1.0),
            (+5,-5):pg.transform.rotozoom(flip_img,45,1.0),
            (+5, 0):flip_img,
            (+5,+5):pg.transform.rotozoom(flip_img,-45,1.0),
            (0,+5):pg.transform.rotozoom(flip_img,-90,1.0),
            (-5,+5):pg.transform.rotozoom(base_img,45,1.0)
            
        }
        return kk_dict
    
def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    dist = math.hypot(dx, dy)
    if dist == 0:
        return current_xy
    if dist < 300:
        return current_xy
    speed = math.sqrt(50) 
    vx = (dx / dist) * speed
    vy = (dy / dist) * speed
    return vx, vy
        

    

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    # こうかとんの初期化
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0,0)]
    # 爆弾の初期化
    bb_img = pg.Surface((20, 20)) 
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10) 
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0,WIDTH)
    bb_rct.centery = random.randint(0,HEIGHT)
    vx, vy = +5, +5
    clock = pg.time.Clock()
    tmr = 0
    
    
    
    bb_imgs, bb_accs = init_bb_imgs()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]  # 横方向の移動
                sum_mv[1] += mv[1]  # 縦方向の移動 
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 移動のキャンセル
        kk_img = kk_imgs.get(tuple(sum_mv), kk_img) # こうかとんの向きの変更
        screen.blit(kk_img, kk_rct)
        idx = min(tmr // 500, 9)
        avx = vx*bb_accs[idx]
        avy = vy*bb_accs[idx]
        bb_img = bb_imgs[idx]
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height
        
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        
        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
