import tkinter as tk
from tkinter import ttk
import random

window = tk.Tk()
window.title("Gửi chú Hiếu đẹp zai")
window.geometry("500x400")
window.resizable(False, False)


FONT_TITLE = ("Arial", 24, "bold")
FONT_NORMAL = ("Arial", 14)

def tao_nen_sao(canvas, so_luong_sao):
    width = int(canvas.cget("width"))
    height = int(canvas.cget("height"))
    canvas.config(bg="#0A0A2A")

    for _ in range(so_luong_sao):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 3)
        color = random.choice(["#FFFFFF", "#F0F0F0", "#FFFFE0"])
        canvas.create_oval(x - size, y - size, x + size, y + size, fill=color, outline="")


        if random.random() < 0.1:
            x_star = random.randint(0, width)
            y_star = random.randint(0, height)
            size_star = random.randint(3, 5)

            points = [x_star, y_star - size_star * 2, x_star + size_star, y_star + size_star, x_star - size_star,
                      y_star + size_star]
            color_special = random.choice(["#FFFFCC", "#FAF0E6"])
            canvas.create_polygon(points, fill=color_special, outline="")

frame_hien_tai = None

def hien_thi_man_hinh(man_hinh_func):
    global frame_hien_tai
    if frame_hien_tai:
        frame_hien_tai.destroy()

    canvas = tk.Canvas(window, width=500, height=400)
    tao_nen_sao(canvas, 200)

    frame = man_hinh_func(canvas)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    canvas.pack(fill="both", expand=True)
    frame_hien_tai = canvas

def tao_man_hinh_1(canvas):
    frame = tk.Frame(canvas, bg="#0A0A2A")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    label_chao = tk.Label(frame, text="Cháu chào chú!", font=FONT_TITLE, fg="#FFFFFF", bg="#0A0A2A")
    label_chao.pack(pady=(20, 10))

    label_mo_dau = tk.Label(frame, text="Chắc là hôm qua chú đã nhận được món quà\n nhỏ xíu của cháu :)", font=FONT_NORMAL, fg="#FFFFFF",
                            bg="#0A0A2A")
    label_mo_dau.pack(pady=(0, 15))

    nut_tiep_tuc = ttk.Button(frame, text="Hẹ hẹ hẹ :)", command=lambda: hien_thi_man_hinh(tao_man_hinh_2))
    nut_tiep_tuc.pack(pady=20)

    return frame


def tao_man_hinh_2(canvas):
    frame = tk.Frame(canvas, bg="#0A0A2A")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    label_bi_mat_1 = tk.Label(frame, text="Cháu có điều chưa nói về món quà nhỏ xíu cháu tặng chú đấy", font=FONT_TITLE, fg="#FFFFFF",
                              bg="#0A0A2A", wraplength=400, justify='center')
    label_bi_mat_1.pack(pady=(30, 15))


    nut_kham_pha = ttk.Button(frame, text="Hì hì", command=lambda: hien_thi_man_hinh(tao_man_hinh_3))
    nut_kham_pha.pack(pady=20)

    return frame


def tao_man_hinh_3(canvas):
    frame = tk.Frame(canvas, bg="#0A0A2A")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    noi_dung = """
Thật ra món quà chính,
là 1000 ngôi sao cháu gấp đầy ở trong hộp quà í :)

Ở trường cháu, gấp được 1000 ngôi sao
là sẽ nhận được một điều ước.

Nhưng cháu muốn tặng điều ước này cho chú 
hơn là cháu tự ước.

Cháu tặng chú điều ước này,
chú nhớ ước đấy nhó!
"""

    label_noi_dung = tk.Label(frame, text=noi_dung, font=FONT_NORMAL, fg="#FFFFFF", bg="#0A0A2A",
                              justify='center', wraplength=450)
    label_noi_dung.pack(pady=(0, 20))

    nut_hoan_thanh = ttk.Button(frame, text="Bai bai chú", command=window.destroy)
    nut_hoan_thanh.pack(pady=20)

    return frame


hien_thi_man_hinh(tao_man_hinh_1)
window.mainloop()