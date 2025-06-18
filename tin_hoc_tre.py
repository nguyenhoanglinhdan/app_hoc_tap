import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk

import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import os
from pydub import AudioSegment
from fuzzywuzzy import fuzz

from gtts import gTTS
import pygame.mixer

import json
from datetime import datetime

# Day la mot thay doi
class PronunciationApp:
    def __init__(self, master):
        self.master = master
        master.title("Ứng dụng Luyện Phát âm Tiếng Anh - Elsa Style")
        # THAY ĐỔI TẠI ĐÂY: Tăng chiều cao của cửa sổ
        master.geometry("900x900") # Tăng từ 780 lên 900
        master.resizable(False, False)
        master.config(bg='#e6f2ff')  # Màu nền cho cửa sổ chính

        pygame.mixer.init()

        # --- Cấu hình Style (Phong cách) cho Tkinter ---
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Bảng màu lấy cảm hứng từ Elsa Speak (Định nghĩa là thuộc tính của lớp)
        self.color_primary = '#4CAF50'  # Xanh lá cây (Record)
        self.color_secondary = '#6A1B9A'  # Tím đậm (nút chính, tiêu đề)
        self.color_accent_blue = '#2196F3'  # Xanh dương (một số nút, highlight)
        self.color_accent_pink = '#E91E63'  # Hồng (có thể dùng cho phản hồi tiêu cực)
        self.color_neutral_bg = '#f0f2f5'  # Nền cho các khung
        self.color_neutral_light = '#ffffff'  # Nền cho các ô input, text
        self.color_text_dark = '#333333'  # Chữ tối
        self.color_text_light = '#ffffff'  # Chữ sáng
        self.color_border = '#bbdefb'  # Màu viền nhẹ nhàng

        # Font chữ (Định nghĩa là thuộc tính của lớp)
        self.font_header = ('Arial', 24, 'bold')
        self.font_instruction_text = ('Arial', 18, 'bold')
        self.font_section_title = ('Arial', 14, 'bold')
        self.font_body = ('Arial', 12)
        self.font_input = ('Arial', 13)
        self.font_button = ('Arial', 12, 'bold')
        self.font_feedback = ('Arial', 15) # Font cho kết quả phản hồi

        # Cấu hình chung cho các widget
        self.style.configure('TLabel', font=self.font_body, background='#e6f2ff', foreground=self.color_text_dark)
        self.style.configure('TButton', font=self.font_button, padding=(15, 10), borderwidth=0, focusthickness=0,
                             focuscolor='none', relief='flat')
        self.style.configure('TCombobox', font=self.font_input, fieldbackground=self.color_neutral_light,
                             background='#e6f2ff', bordercolor=self.color_border, arrowcolor=self.color_secondary)
        self.style.configure('TFrame', background='#e6f2ff')
        self.style.configure('TLabelframe', font=self.font_section_title, background=self.color_neutral_bg,
                             foreground=self.color_text_dark, borderwidth=1, relief='flat',
                             bordercolor=self.color_border, highlightbackground=self.color_border)
        self.style.configure('TLabelframe.Label', background=self.color_neutral_bg, foreground=self.color_secondary,
                             font=self.font_section_title)

        # Cấu hình màu sắc riêng cho các nút
        self.style.map('Green.TButton',
                       background=[('!disabled', self.color_primary), ('active', '#388E3C')],
                       foreground=[('!disabled', self.color_text_light), ('disabled', '#cccccc')])
        self.style.map('Red.TButton',
                       background=[('!disabled', self.color_accent_pink), ('active', '#C2185B')],
                       foreground=[('!disabled', self.color_text_light), ('disabled', '#cccccc')])
        self.style.map('Orange.TButton',
                       background=[('!disabled', self.color_accent_blue), ('active', '#1976D2')],
                       foreground=[('!disabled', self.color_text_light), ('disabled', '#cccccc')])
        self.style.map('Blue.TButton',
                       background=[('!disabled', self.color_secondary), ('active', '#4527A0')],
                       foreground=[('!disabled', self.color_text_light), ('disabled', '#cccccc')])

        # Style cho nhãn kết quả phản hồi (sẽ không dùng style này trực tiếp trên tk.Message)
        # self.style.configure('Result.TLabel', font=self.font_feedback, wraplength=780, justify='center', foreground=self.color_text_dark)


        # --- Các biến trạng thái và dữ liệu (không đổi) ---
        self.is_recording = False
        self.audio_frames = []
        self.samplerate = 44100
        self.channels = 1
        self.audio_filename = "user_pronunciation.wav"
        self.standard_audio_filename = "standard_pronunciation.mp3"
        self.history_file = "pronunciation_history.json"
        self.sentences_file = "sentences.json"

        self.sample_sentences = self.load_sample_sentences()

        self.reference_text = tk.StringVar()
        if self.sample_sentences:
            self.reference_text.set(self.sample_sentences[0])
        else:
            self.reference_text.set("Welcome! Please add sentences to 'sentences.json' to begin.")
            messagebox.showwarning("Cảnh báo",
                                   "Không tìm thấy câu mẫu hoặc tệp 'sentences.json' rỗng. Vui lòng thêm câu vào tệp.")

        # --- Tạo các thành phần GUI với Grid Layout ---
        main_frame = ttk.Frame(master, padding="25 25 25 25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        # Các hàng cần co giãn để lấp đầy không gian mới
        main_frame.grid_rowconfigure(0, weight=0)
        main_frame.grid_rowconfigure(1, weight=0)
        main_frame.grid_rowconfigure(2, weight=0)
        main_frame.grid_rowconfigure(3, weight=0)
        main_frame.grid_rowconfigure(4, weight=1) # Hàng kết quả, cho phép co giãn nhiều hơn
        main_frame.grid_rowconfigure(5, weight=0)

        ttk.Label(main_frame, text="Ứng dụng Luyện Phát âm Tiếng Anh", font=self.font_header,
                  foreground=self.color_secondary, background='#e6f2ff').grid(row=0, column=0, pady=(0, 10),
                                                                              sticky="nsew")

        self.label_instruction = ttk.Label(main_frame, text="Nhấn 'Ghi Âm' để bắt đầu luyện tập!",
                                           font=self.font_instruction_text, foreground=self.color_text_dark,
                                           background='#e6f2ff')
        self.label_instruction.grid(row=1, column=0, pady=(0, 20), sticky="nsew")

        self.frame_text_management = ttk.Labelframe(main_frame, text="Chọn hoặc Tùy chỉnh Văn bản Luyện Tập",
                                                    padding="15 15 15 15")
        self.frame_text_management.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")
        self.frame_text_management.grid_columnconfigure(0, weight=1)

        ttk.Label(self.frame_text_management, text="Chọn câu mẫu từ danh sách có sẵn:").grid(row=0, column=0,
                                                                                             pady=(0, 5), sticky="w")
        self.selected_sentence_var = tk.StringVar()
        if self.sample_sentences:
            self.selected_sentence_var.set(self.sample_sentences[0])
        else:
            self.selected_sentence_var.set("No sentences available")
        self.sentence_combobox = ttk.Combobox(self.frame_text_management,
                                              textvariable=self.selected_sentence_var,
                                              values=self.sample_sentences,
                                              width=80)
        self.sentence_combobox.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        self.sentence_combobox.bind("<<ComboboxSelected>>", self.on_sentence_selected)

        ttk.Label(self.frame_text_management, text="Hoặc nhập/chỉnh sửa văn bản của riêng bạn:").grid(row=2, column=0,
                                                                                                      pady=(5, 5),
                                                                                                      sticky="w")
        self.text_editor = scrolledtext.ScrolledText(self.frame_text_management, wrap=tk.WORD, height=4,
                                                     font=self.font_input, relief='solid', borderwidth=1,
                                                     highlightbackground=self.color_border,
                                                     highlightcolor=self.color_border, bg=self.color_neutral_light,
                                                     fg=self.color_text_dark)
        self.text_editor.insert(tk.END, self.reference_text.get())
        self.text_editor.grid(row=3, column=0, pady=(0, 5), sticky="nsew")
        self.frame_text_management.grid_rowconfigure(3, weight=1)

        self.btn_update_text = ttk.Button(self.frame_text_management, text="Cập nhật Văn bản từ ô trên",
                                          command=self.update_reference_text_from_editor, style='Blue.TButton')
        self.btn_update_text.grid(row=4, column=0, pady=(5, 0), sticky="e")

        control_frame = ttk.Frame(main_frame, padding="15 0 15 15")
        control_frame.grid(row=3, column=0, pady=20)
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)

        self.btn_record = ttk.Button(control_frame, text="Ghi Âm", command=self.start_recording, style='Green.TButton')
        self.btn_record.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.btn_stop = ttk.Button(control_frame, text="Dừng Ghi Âm", command=self.stop_recording, state=tk.DISABLED,
                                   style='Red.TButton')
        self.btn_stop.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.btn_play_standard = ttk.Button(control_frame, text="Phát Âm Chuẩn", command=self.play_standard_audio,
                                            style='Orange.TButton')
        self.btn_play_standard.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        self.label_feedback = ttk.Label(main_frame, text="KẾT QUẢ PHÂN TÍCH:", font=self.font_section_title,
                                        foreground=self.color_secondary, background='#e6f2f5')
        self.label_feedback.grid(row=4, column=0, pady=(15, 5), sticky="n")

        self.result_text_var = tk.StringVar()
        self.result_text_var.set("Chưa có kết quả phân tích.")
        self.result_display = tk.Message(main_frame, textvariable=self.result_text_var,
                                         font=self.font_feedback,
                                         bg='#e6f2ff',
                                         fg=self.color_text_dark,
                                         width=780,
                                         justify=tk.CENTER)
        self.result_display.grid(row=4, column=0, pady=(40, 10), sticky="nsew")

        self.btn_show_history = ttk.Button(main_frame, text="Xem Lịch Sử Luyện Tập", command=self.show_history_window,
                                           style='Blue.TButton')
        self.btn_show_history.grid(row=5, column=0, pady=(10, 0), sticky="s")

    # Các hàm chức năng (không đổi)
    def load_sample_sentences(self):
        if not os.path.exists(self.sentences_file):
            messagebox.showwarning("Cảnh báo",
                                   f"Không tìm thấy tệp '{self.sentences_file}'. Vui lòng tạo tệp này với định dạng JSON (danh sách chuỗi).")
            return []
        try:
            with open(self.sentences_file, 'r', encoding='utf-8') as f:
                sentences = json.load(f)
                if not isinstance(sentences, list) or not all(isinstance(s, str) for s in sentences):
                    messagebox.showerror("Lỗi tệp câu mẫu",
                                         "Định dạng tệp 'sentences.json' không hợp lệ. Phải là một danh sách các chuỗi.")
                    return []
                return sentences
        except json.JSONDecodeError:
            messagebox.showerror("Lỗi tệp câu mẫu", "Lỗi đọc tệp 'sentences.json'. Đảm bảo nó là JSON hợp lệ.")
            return []
        except Exception as e:
            messagebox.showerror("Lỗi tệp câu mẫu", f"Đã xảy ra lỗi khi tải câu mẫu: {e}")
            return []

    def on_sentence_selected(self, event):
        selected_text = self.selected_sentence_var.get()
        self.reference_text.set(selected_text)
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert(tk.END, selected_text)
        messagebox.showinfo("Cập nhật", "Văn bản luyện tập đã được chọn từ danh sách!")

    def update_reference_text_from_editor(self):
        new_text = self.text_editor.get("1.0", tk.END).strip()
        if new_text:
            self.reference_text.set(new_text)
            self.selected_sentence_var.set(new_text)
            messagebox.showinfo("Cập nhật", "Văn bản luyện tập đã được cập nhật từ trình soạn thảo!")
        else:
            messagebox.showwarning("Cảnh báo", "Văn bản luyện tập không được để trống!")
            self.text_editor.insert(tk.END, self.reference_text.get())

    def start_recording(self):
        if self.is_recording:
            return

        self.is_recording = True
        self.audio_frames = []

        self.btn_record.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.label_instruction.config(
            text=f"ĐANG GHI ÂM... Vui lòng đọc to và rõ ràng: \"{self.reference_text.get()}\"",
            font=self.font_instruction_text)
        self.result_text_var.set("...")
        self.master.update_idletasks() # Đảm bảo cập nhật ngay lập tức

        self.stream = sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=self.audio_callback)
        self.stream.start()

        messagebox.showinfo("Thông báo", "Bắt đầu ghi âm. Hãy nói vào microphone của bạn!")

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        if self.is_recording:
            self.audio_frames.append(indata.copy())

    def stop_recording(self):
        if not self.is_recording:
            return

        self.is_recording = False
        self.stream.stop()
        self.stream.close()

        self.btn_record.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.label_instruction.config(text="Ghi âm hoàn tất. Đang xử lý...", font=self.font_instruction_text)
        self.master.update_idletasks() # Đảm bảo cập nhật ngay lập tức

        messagebox.showinfo("Thông báo", "Ghi âm đã dừng. Đang phân tích phát âm của bạn...")

        if self.audio_frames:
            import numpy as np
            full_audio_data = np.concatenate(self.audio_frames, axis=0)
            sf.write(self.audio_filename, full_audio_data, self.samplerate)
            self.analyze_pronunciation()
        else:
            self.result_text_var.set("Không có âm thanh nào được ghi.")
            messagebox.showwarning("Cảnh báo", "Không có âm thanh nào được ghi. Vui lòng thử lại.")
            self.label_instruction.config(text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!", font=self.font_instruction_text)
        self.master.update_idletasks() # Cập nhật lại trạng thái cuối cùng


    def play_standard_audio(self):
        current_text = self.reference_text.get()
        if not current_text:
            messagebox.showwarning("Cảnh báo", "Không có văn bản nào để phát âm!")
            return

        try:
            self.label_instruction.config(text="Đang phát âm chuẩn... Vui lòng chờ.", font=self.font_instruction_text)
            self.master.update_idletasks()

            tts = gTTS(text=current_text, lang='en', slow=False)
            tts.save(self.standard_audio_filename)

            pygame.mixer.music.load(self.standard_audio_filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                self.master.update()

            messagebox.showinfo("Phát Âm Chuẩn", "Đã phát âm chuẩn xong.")
            self.label_instruction.config(text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!", font=self.font_instruction_text)

        except Exception as e:
            messagebox.showerror("Lỗi phát âm",
                                 f"Không thể phát âm chuẩn: {e}\nĐảm bảo bạn có kết nối internet và thư viện 'gTTS', 'pygame' đã cài đặt đúng cách.")
            self.label_instruction.config(text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!", font=self.font_instruction_text)
        finally:
            if os.path.exists(self.standard_audio_filename):
                os.remove(self.standard_audio_filename)

    def analyze_pronunciation(self):
        self.result_text_var.set("Đang phân tích phát âm của bạn... Vui lòng chờ.")
        self.master.update_idletasks() # Cập nhật giao diện ngay lập tức

        if not os.path.exists(self.audio_filename):
            self.result_text_var.set("Lỗi: Không tìm thấy tệp ghi âm để phân tích.")
            messagebox.showerror("Lỗi", "Không tìm thấy tệp ghi âm. Vui lòng ghi âm trước.")
            self.label_instruction.config(text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!", font=self.font_instruction_text)
            self.master.update_idletasks() # Cập nhật ngay lập tức
            return

        recognizer = sr.Recognizer()

        temp_audio_file = "temp_converted_audio.wav"
        try:
            audio = AudioSegment.from_wav(self.audio_filename)
            audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
            audio.export(temp_audio_file, format="wav")
        except Exception as e:
            self.result_text_var.set(f"Lỗi xử lý tệp âm thanh: {e}.\nVui lòng kiểm tra cài đặt FFmpeg.")
            messagebox.showerror("Lỗi xử lý âm thanh",
                                 f"Không thể xử lý tệp âm thanh: {e}\nBạn đã cài đặt và cấu hình FFmpeg đúng cách chưa?")
            self.label_instruction.config(text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!", font=self.font_instruction_text)
            self.master.update_idletasks() # Cập nhật ngay lập tức
            return

        try:
            with sr.AudioFile(temp_audio_file) as source:
                audio_data = recognizer.record(source)

            current_reference_text = self.reference_text.get()
            user_spoken_text = recognizer.recognize_google(audio_data, language="en-US")

            ratio = fuzz.ratio(current_reference_text.lower(), user_spoken_text.lower())
            partial_ratio = fuzz.partial_ratio(current_reference_text.lower(), user_spoken_text.lower())

            feedback = ""
            color_feedback = self.color_text_dark
            if ratio >= 90:
                feedback = "Tuyệt vời! Phát âm của bạn rất chính xác."
                color_feedback = self.color_primary
            elif ratio >= 70:
                feedback = "Tốt! Phát âm của bạn khá rõ ràng."
                color_feedback = '#FFC107'
            elif ratio >= 50:
                feedback = "Cần cải thiện. Hãy cố gắng luyện tập thêm."
                color_feedback = '#fd7e14'
            else:
                feedback = "Cần rất nhiều luyện tập. Đừng nản lòng!"
                color_feedback = self.color_accent_pink

            result_message = (f"Bạn đã nói:\n\"{user_spoken_text}\"\n\n"
                              f"Văn bản chuẩn:\n\"{current_reference_text}\"\n\n"
                              f"Độ chính xác tương đối: {ratio}%\n"
                              f"Độ chính xác một phần: {partial_ratio}%\n\n"
                              f"Phản hồi: {feedback}")

            self.result_text_var.set(result_message)
            # Cập nhật foreground cho tk.Message
            self.result_display.config(fg=color_feedback)
            self.master.update_idletasks() # Đảm bảo cập nhật hiển thị

            self.save_history({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "reference_text": current_reference_text,
                "user_spoken_text": user_spoken_text,
                "accuracy_ratio": ratio,
                "accuracy_partial_ratio": partial_ratio,
                "feedback": feedback
            })

        except sr.UnknownValueError:
            self.result_text_var.set(
                "Kết quả: KHÔNG THỂ NHẬN DẠNG GIỌNG NÓI của bạn.\nVui lòng nói rõ hơn hoặc thử lại. (UnknownValueError)")
            self.result_display.config(fg=self.color_accent_pink) # Cập nhật foreground
        except sr.RequestError as e:
            self.result_text_var.set(
                f"Kết quả: LỖI KẾT NỐI đến dịch vụ nhận dạng giọng nói;\nKiểm tra internet của bạn. (RequestError: {e})")
            self.result_display.config(fg=self.color_accent_pink) # Cập nhật foreground
        except Exception as e:
            self.result_text_var.set(f"Kết quả: ĐÃ XẢY RA LỖI không mong muốn:\n{e}")
            self.result_display.config(fg=self.color_accent_pink) # Cập nhật foreground
        finally:
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
            self.label_instruction.config(text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!", font=self.font_instruction_text)
            self.master.update_idletasks() # Cập nhật trạng thái cuối cùng

    def load_history(self):
        if not os.path.exists(self.history_file):
            return []
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showwarning("Lỗi lịch sử", "Không thể đọc tệp lịch sử. Tệp có thể bị hỏng.")
            return []
        except Exception as e:
            messagebox.showerror("Lỗi lịch sử", f"Đã xảy ra lỗi khi tải lịch sử: {e}")
            return []

    def save_history(self, entry):
        history = self.load_history()
        history.append(entry)
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Lỗi lưu lịch sử", f"Không thể lưu lịch sử: {e}")

    def show_history_window(self):
        history_window = tk.Toplevel(self.master)
        history_window.title("Lịch Sử Luyện Tập")
        history_window.geometry("850x650")
        history_window.transient(self.master)
        history_window.grab_set()
        history_window.focus_set()
        history_window.config(bg='#e6f2ff')

        history_label = ttk.Label(history_window, text="LỊCH SỬ CÁC PHIÊN LUYỆN TẬP", font=self.font_instruction_text,
                                  foreground=self.color_secondary, background='#e6f2ff')
        history_label.pack(pady=15)

        history_text_area = scrolledtext.ScrolledText(history_window, wrap=tk.WORD, width=95, height=28,
                                                      font=self.font_body, relief='solid', borderwidth=1,
                                                      highlightbackground=self.color_border,
                                                      highlightcolor=self.color_border, bg=self.color_neutral_light,
                                                      fg=self.color_text_dark)
        history_text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        history_data = self.load_history()
        if not history_data:
            history_text_area.insert(tk.END, "Chưa có dữ liệu lịch sử nào.")
        else:
            for i, entry in enumerate(history_data):
                history_text_area.insert(tk.END, f"--- PHIÊN {i + 1} ({entry.get('timestamp', 'N/A')}) ---\n", 'header')
                history_text_area.insert(tk.END, f"Văn bản chuẩn: {entry.get('reference_text', 'N/A')}\n")
                history_text_area.insert(tk.END, f"Bạn đã nói: {entry.get('user_spoken_text', 'N/A')}\n")
                history_text_area.insert(tk.END, f"Độ chính xác: {entry.get('accuracy_ratio', 'N/A')}%\n")
                history_text_area.insert(tk.END,
                                         f"Độ chính xác một phần: {entry.get('accuracy_partial_ratio', 'N/A')}%\n")
                history_text_area.insert(tk.END, f"Phản hồi: {entry.get('feedback', 'N/A')}\n")
                history_text_area.insert(tk.END, "---------------------------------------------------\n\n")

        history_text_area.tag_configure('header', font=('Arial', 11, 'bold'), foreground=self.color_secondary)
        history_text_area.config(state=tk.DISABLED)

        history_window.protocol("WM_DELETE_WINDOW", lambda: self.on_history_window_close(history_window))

    def on_history_window_close(self, history_window):
        history_window.destroy()
        self.master.grab_release()


# --- Khởi chạy ứng dụng ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PronunciationApp(root)
    root.mainloop()