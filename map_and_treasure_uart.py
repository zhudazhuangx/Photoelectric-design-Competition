import sensor, image, time, pyb, utime,ucollections, gc,json, lcd
from ucollections import deque
from pyb import UART
if_once = 1
led = pyb.LED(3)
led.off()
flag = 1
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE) # or GRAYSCALE...
sensor.set_framesize(sensor.VGA) # or QQVGA...
sensor.skip_frames(time = 2000)
clock = time.clock()
sensor.set_windowing((400,400))
#img = image.Image('./5.jpg',[copy_to_fb=True])
sensor.set_auto_whitebal(False)
lcd.init() # Initialize the lcd screen.
uart = UART(3,9600)   #定义串口3变量
uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters
w = sensor.width()
h = sensor.height()
gc.enable()

def map():
    img = sensor.snapshot()
    lcd.display(sensor.snapshot()) # Take a picture and display the image.
    B = 0
    C = 0
    D = 0
    E = 0
    F = 0
    item = 0
    out = 0
    FH = 0
    int_list = []
    points = [[]]
    # 设置起点终点 左下角（0,9） 右上角（9，0）
    begin_point = [0, 9]
    end_point = [9, 0]
    res_path = []
    # 透视变换前的坐标，程序自动识别获取
    p1 = [0, 0]
    p2 = [0, 0]
    p3 = [0, 0]
    p4 = [0, 0]
    dis1 = 1000000
    dis2 = 1000000
    dis3 = 1000000
    dis4 = 1000000


    # 下上右左
    bx = 60
    by = 60
    dx = 31
    dy = 31
    pos_x = [int(bx + dx * i) for i in range(10)]
    pos_y = [int(by + dy * i) for i in range(10)]

    res_p = [[0, 0] for i in range(9)]
    res_p_visited = [0 for i in range(9)]
    res_p[8] = [end_point[0], end_point[1]]
    res_p_visited[8] = 1
    blobs = img.find_blobs([(0, 70)], merge=False, invert = 0, area_threshold = 30)
    if blobs:
        for blob in blobs:

            area = blob.pixels()
            left = blob.x()
            top = blob.y()
            width = blob.w()
            height = blob.h()

            if area > 20/4 and area / (width * height) >= 0.7 and width <= 22/2 and height <= 22/2 and width/height < 1.3 and height/width < 1.3:
                img.draw_rectangle(blob.rect(), color=254)
                x = round(left + width / 2)
                y = round(top + height / 2)
                points.append([x, y])
                if pow(x, 2) + pow(y, 2) < dis1:
                    dis1 = pow(x, 2) + pow(y, 2)
                    p1 = [x, y]
                if pow(x - w + 1, 2) + pow(y, 2) < dis2:
                    dis2 = pow(x - w + 1, 2) + pow(y, 2)
                    p2 = [x, y]

                if pow(x, 2) + pow(y - h + 1, 2) < dis3:
                    dis3 = pow(x, 2) + pow(y - h + 1, 2)
                    p3 = [x, y]

                if pow(x - w + 1, 2) + pow(y - h + 1, 2) < dis4:
                    dis4 = pow(x - w + 1, 2) + pow(y - h + 1, 2)
                    p4 = [x, y]
    if len(points) != 13:
        print("res_point error!")
        return 0
    if abs(abs(p1[0]-p3[0])-abs(abs(p1[0]-p3[0]))) >10 or abs(abs(p1[1]-p3[1])-abs(abs(p1[1]-p3[1])))>10:
        print("4_points error!")
        return 0
    img.draw_circle(p1[0], p1[1], 22, color=(255,255,255))
    img.draw_circle(p2[0], p2[1], 22,color=(255,255,255))
    img.draw_circle(p3[0], p3[1], 22, color=(255,255,255))
    img.draw_circle(p4[0], p4[1], 22, color=(255,255,255))

    TARGET_POINTS = [(p1[0],   p1[1]),   # (x, y) CHANGE ME!
                     (p2[0], p2[1]),   # (x, y) CHANGE ME!
                     (p4[0],   p4[1]), # (x, y) CHANGE ME!
                     (p3[0], p3[1])] # (x, y) CHANGE ME!
    img = sensor.snapshot().rotation_corr(corners = TARGET_POINTS)
    for i in range(10):
        for j in range(10):
            img.draw_circle(round(bx + dx * i), round(by + dy * j), 7, color = (255, 255, 255))

    #while True:
        #sensor.skip_frames(time = 2000)
    _i = 0
    del blobs
    gc.collect()
    blobs = img.find_blobs([(0, 80)], merge=False, invert = 0, area_threshold = 30)
    if blobs:
        for blob in blobs:

            area = blob.pixels()
            left = blob.x()
            top = blob.y()
            width = blob.w()
            height = blob.h()

            if area > 30 and area / (width * height) >= 0.6 and width <= 20 and height <= 20 and width/height < 1.3 and height/width < 1.3:
                #img.draw_rectangle(blob.rect(), color=254)
                x = round(left + width / 2)
                y = round(top + height / 2)
                res_p[_i][0] = x
                res_p[_i][1] = y
                if _i >= 8:
                    return 0
                _i = _i + 1
    del blobs
    gc.collect()
    if _i != 8:
        print(_i)
        return 0
    for i in range(8):
        img.draw_cross(round(res_p[i][0]), round(res_p[i][1]), 7, color = (255, 255, 255))
        res_p[i][0] = round((res_p[i][0]-bx)/dx)
        res_p[i][1] = round((res_p[i][1]-by)/dy)
        #print(res_p[i][0], res_p[i][1])
        #data=bytearray([0x2C,res_p[i][0],res_p[i][1],0x5B])
        #uart.write(data)
        if res_p[i][0] >= 10 or res_p[i][0] <= -1 or res_p[i][1] >=10 or res_p[i][1]<=-1:
            return 0
    print(res_p, len(res_p))
    for E in range(8):
      print(res_p[E][0], res_p[E][1])
      data=bytearray([0x2C,res_p[E][0],res_p[E][1],0x5B])
      uart.write(data)
    print("succeed!!")

    return 1

def treatuer():
    img = sensor.snapshot()
    blue=0;red=0;
    for blob11 in img.find_blobs(red_thresholds, pixels_threshold=20, area_threshold=20,merge=True):
        left_roi = [blob11.x(), blob11.y(), blob11.x()+blob11.w(), blob11.y()+blob11.h()]
        for blob12 in img.find_blobs(green_thresholds,roi=left_roi, pixels_threshold=10, area_threshold=10,merge=True):
            img.draw_rectangle(blob11.rect())
            img.draw_string(blob11.x(),blob11.y(), "true red")
            print("true red")
            red=1
            data=bytearray([0x3C,red,blue,0x6B])
            uart.write(data)
            return

        for blob12 in img.find_blobs(yellow_thresholds,roi=left_roi, pixels_threshold=10, area_threshold=10,merge=True):
            img.draw_rectangle(blob11.rect())
            print("false red")
            img.draw_string(blob11.x(),blob11.y(), "false red")
            red=0
            data=bytearray([0x3C,red,blue,0x6B])
            uart.write(data)
            return

        #img.draw_rectangle(blob.rect())
        #img.draw_cross(blob.cx(), blob.cy())
        #print(blob.code())

    for blob21 in img.find_blobs(blue_thresholds, pixels_threshold=20, area_threshold=20,merge=True):
        left_roi = [blob21.x(), blob21.y(), blob21.x()+blob21.w(), blob21.y()+blob21.h()]
        for blob22 in img.find_blobs(yellow_thresholds,roi=left_roi, pixels_threshold=10, area_threshold=10,merge=True):
            img.draw_rectangle(blob21.rect())
            print("true blue")
            img.draw_string(blob21.x(),blob21.y(), "true blue")
            blue=1
            data=bytearray([0x3C,red,blue,0x6B])
            uart.write(data)
            return


        for blob22 in img.find_blobs(green_thresholds,roi=left_roi, pixels_threshold=10, area_threshold=10,merge=True):
            img.draw_rectangle(blob21.rect())
            print("false blue")
            img.draw_string(blob21.x(),blob21.y(), "false blue")
            blue=0
            data=bytearray([0x3C,red,blue,0x6B])
            uart.write(data)
            return

        #img.draw_rectangle(blob.rect())
        #img.draw_cross(blob.cx(), blob.cy())
        #print(blob.code())


if if_once:
    while True:
        if map() == 1:
            while True:
                led.on()
                sensor.set_pixformat(sensor.RGB565)
                sensor.set_framesize(sensor.QVGA)
                sensor.skip_frames(10)
                red_thresholds = [(28,34,36,47,19,38)]
                green_thresholds = [(37,44,-38,-26,15,30)]
                yellow_thresholds = [(79, 84, -26, -14, 48, 62)]
                blue_thresholds = [(48, 56, -19, -5, -31, -15)]
                while True:
                    treatuer()
                   # if(uart.any()>0):
                   # uart.write(0x3B,blue,red,0x2C)
    #utime.sleep(1)
else:
    while True:
         map()
