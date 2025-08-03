# giới thiệu hàm class
class Person:
    def __init__(self, ten, tuoi):
        self.ten = ten
        self.tuoi = tuoi

    def lay_thong_tin_tuoi(self):
        return self.tuoi

if __name__ == "__main__" :
    linh_dan = Person( ten = 'Linh Dan',tuoi = 12)
    print(linh_dan.lay_thong_tin_tuoi())
