# subjects: môn học
# tạo ra một cái chương trình để thêm môn học
# môn toán, môn văn, môn tiếng anh,..
import json
import os # operating system: hệ thống

folder = "du_lieu"
filename = "mon_hoc.json"
fullpath = f"{folder}/{filename}" # du_lieu/mon_hoc.json


# 1. kiểm tra thư mục du_lieu đã tồn tại hay chưa ?
#       -> tạo thư mục nếu chưa có
#       -> ghi dữ liệu vào file
# print(f"du_lieu tồn tại hay chưa ?: {os.path.exists(folder)}")

if not os.path.exists(folder): # not false = true
    os.mkdir(folder)
    print("Tạo thư mục du_lieu")

# print(f"du_lieu tồn tại hay chưa ?: {os.path.exists(folder)}")

# 1. đọc được dữ liệu đã có
# 2. ghi dữ liệu mới vào sau dữ liệu đã có
# 3. lưu
du_lieu_truoc_do = None

try:
    # đọc dữ liệu cũ
    with open(fullpath, "r", encoding="utf-8") as file:
        # print("truoc khi doc file")
        du_lieu_truoc_do = json.load(file)
        # print(du_lieu_truoc_do)
        # print("sau khi doc file")
except FileNotFoundError:
    # lỗi (ko có file) -> tạo file mới, dữ liệu = []
    with open(fullpath, "w") as file:
        print("tạo mot file moi")
        du_lieu_truoc_do = []
        json.dump(du_lieu_truoc_do, file)

# ghi dữ liệu vào file
def ghi_du_lieu():
    with open(fullpath, "w", encoding="utf-8") as file:
        subject = {
            "mon_hoc": "mon toan",
        }
        du_lieu_truoc_do.append(subject)
        json.dump(du_lieu_truoc_do, file, ensure_ascii=False, indent=4)

ghi_du_lieu()

# xóa dữ liệu
def xoa_du_lieu():
    with open(fullpath, "w", encoding="utf-8") as file:
        # du_lieu_truoc_do
        # json.dump(du_lieu_truoc_do, file, indent=4)
        print(du_lieu_truoc_do)

        vi_tri_mon_van = None

        for vi_tri in range(0, len(du_lieu_truoc_do)):
            # print(f"vi_tri: {vi_tri} - {du_lieu_truoc_do[vi_tri]['mon_hoc']}")

            if du_lieu_truoc_do[vi_tri]["mon_hoc"] == "tiếng anh":
                vi_tri_mon_van = vi_tri

            # print("====")
        print(f"vi_tri_mon_van: {vi_tri_mon_van}")

        print(f"du lieu tai vi tri {vi_tri_mon_van} : {du_lieu_truoc_do[vi_tri_mon_van]}")

        du_lieu_truoc_do.remove(du_lieu_truoc_do[vi_tri_mon_van])
        json.dump(du_lieu_truoc_do, file, ensure_ascii=False, indent=2) # ghi dữ liệu vào file
        # encoding = "utf-8":
        # ensure_ascii=False: hỗ trợ ghi tiếng việt

        # mặc định là nó chỉ hỗ trợ ghi tiếng anh
        # indent = 4

# về tạo một cái chức năng để thêm và xóa môn học, lớp, từ vựng