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
import time
import tempfile

import json
from datetime import datetime


# --- LỚP CHO TRANG LUYỆN PHÁT ÂM ---
class PronunciationPage:
    def __init__(self, master_frame, controller):
        self.master_frame = master_frame
        self.controller = controller

        self.is_recording = False
        self.audio_frames = []
        self.samplerate = 44100
        self.channels = 1
        self.audio_filename = "../user_pronunciation.wav"
        self.history_file = "../pronunciation_history.json"
        self.sentences_file = "../sentences.json"

        self.sample_sentences = self.load_sample_sentences()

        self.reference_text = tk.StringVar()
        if self.sample_sentences:
            self.reference_text.set(self.sample_sentences[0])
        else:
            self.reference_text.set("Welcome! Please add sentences to 'sentences.json' to begin.")
            messagebox.showwarning("Cảnh báo",
                                   "Không tìm thấy câu mẫu hoặc tệp 'sentences.json' rỗng. Vui lòng thêm câu vào tệp.")

        # --- Tạo các thành phần GUI với Grid Layout bên trong master_frame ---
        page_frame = ttk.Frame(master_frame, padding="25 25 25 25")
        page_frame.grid_columnconfigure(0, weight=1)
        # Các hàng được cấu hình để kiểm soát vị trí chính xác
        page_frame.grid_rowconfigure(0, weight=0)  # Hàng cho nút quay lại
        page_frame.grid_rowconfigure(1, weight=0)  # Hàng cho tiêu đề trang
        page_frame.grid_rowconfigure(2, weight=0)  # Hàng cho label_instruction
        page_frame.grid_rowconfigure(3, weight=0)  # Hàng cho frame_text_management
        page_frame.grid_rowconfigure(4, weight=0)  # Hàng cho control_frame (nút ghi âm/dừng/phát)
        page_frame.grid_rowconfigure(5, weight=0)  # Hàng cho label_feedback
        page_frame.grid_rowconfigure(6, weight=1)  # Hàng kết quả (result_display), cho phép co giãn nhiều hơn
        page_frame.grid_rowconfigure(7, weight=0)  # Hàng cho nút xem lịch sử

        # THAY ĐỔI TẠI ĐÂY: Đặt nút quay lại ở hàng riêng (row=0) và căn theo Northwest
        self.btn_back_to_home = ttk.Button(page_frame, text="< Quay lại Trang Chủ",
                                           command=lambda: self.controller.show_frame("StartPage"),
                                           style='Blue.TButton')
        self.btn_back_to_home.grid(row=0, column=0, pady=(0, 10), sticky="nw", padx=10)  # row=0, column=0, sticky="nw"

        # THAY ĐỔI TẠI ĐÂY: Đặt tiêu đề trang ở hàng riêng (row=1) và căn giữa
        ttk.Label(page_frame, text="Luyện Phát Âm Tiếng Anh", font=self.controller.font_header,
                  foreground=self.controller.color_secondary, background='#e6f2ff').grid(row=1, column=0, pady=(0, 10),
                                                                                         sticky="nsew")  # row=1

        # Dịch chuyển các thành phần xuống các hàng tương ứng
        self.label_instruction = ttk.Label(page_frame, text="Nhấn 'Ghi Âm' để bắt đầu luyện tập!",
                                           font=self.controller.font_instruction_text,
                                           foreground=self.controller.color_text_dark,
                                           background='#e6f2ff')
        self.label_instruction.grid(row=2, column=0, pady=(0, 20), sticky="nsew")  # row=2

        self.frame_text_management = ttk.Labelframe(page_frame, text="Chọn hoặc Tùy chỉnh Văn bản Luyện Tập",
                                                    padding="15 15 15 15")
        self.frame_text_management.grid(row=3, column=0, pady=10, padx=10, sticky="nsew")  # row=3
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
                                                     font=self.controller.font_input, relief='solid', borderwidth=1,
                                                     highlightbackground=self.controller.color_border,
                                                     highlightcolor=self.controller.color_border,
                                                     bg=self.controller.color_neutral_light,
                                                     fg=self.controller.color_text_dark)
        self.text_editor.insert(tk.END, self.reference_text.get())
        self.text_editor.grid(row=3, column=0, pady=(0, 5), sticky="nsew")
        self.frame_text_management.grid_rowconfigure(3, weight=1)

        self.btn_update_text = ttk.Button(self.frame_text_management, text="Cập nhật Văn bản từ ô trên",
                                          command=self.update_reference_text_from_editor, style='Blue.TButton')
        self.btn_update_text.grid(row=4, column=0, pady=(5, 0), sticky="e")

        control_frame = ttk.Frame(page_frame, padding="15 0 15 15")
        control_frame.grid(row=4, column=0, pady=20)  # row=4
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

        self.label_feedback = ttk.Label(page_frame, text="KẾT QUẢ PHÂN TÍCH:", font=self.controller.font_section_title,
                                        foreground=self.controller.color_secondary, background='#e6f2f5')
        self.label_feedback.grid(row=5, column=0, pady=(15, 5), sticky="n")  # row=5

        self.result_text_var = tk.StringVar()
        self.result_text_var.set("Chưa có kết quả phân tích.")
        self.result_display = tk.Message(page_frame, textvariable=self.result_text_var,
                                         font=self.controller.font_feedback,
                                         bg='#e6f2ff',
                                         fg=self.controller.color_text_dark,
                                         width=780,
                                         justify=tk.CENTER)
        self.result_display.grid(row=6, column=0, pady=(40, 10), sticky="nsew")  # row=6

        self.btn_show_history = ttk.Button(page_frame, text="Xem Lịch Sử Luyện Tập", command=self.show_history_window,
                                           style='Blue.TButton')
        self.btn_show_history.grid(row=7, column=0, pady=(10, 0), sticky="s")  # row=7

        self.page_frame = page_frame  # Giữ tham chiếu đến frame của trang này để có thể ẩn/hiện

    # --- Các hàm chức năng của PronunciationPage ---
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
            font=self.controller.font_instruction_text)
        self.result_text_var.set("...")
        self.controller.update_idletasks()

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
        self.label_instruction.config(text="Ghi âm hoàn tất. Đang xử lý...", font=self.controller.font_instruction_text)
        self.controller.update_idletasks()

        messagebox.showinfo("Thông báo", "Ghi âm đã dừng. Đang phân tích phát âm của bạn...")

        if self.audio_frames:
            import numpy as np
            full_audio_data = np.concatenate(self.audio_frames, axis=0)
            sf.write(self.audio_filename, full_audio_data, self.samplerate)
            self.analyze_pronunciation()
        else:
            self.result_text_var.set("Không có âm thanh nào được ghi.")
            messagebox.showwarning("Cảnh báo", "Không có âm thanh nào được ghi. Vui lòng thử lại.")
            self.label_instruction.config(text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!",
                                          font=self.controller.font_instruction_text)
        self.controller.update_idletasks()

    def play_standard_audio(self):
        current_text = self.reference_text.get()
        if not current_text:
            messagebox.showwarning("Cảnh báo", "Không có văn bản nào để phát âm!")
            return

        temp_mp3_path = None
        try:
            self.label_instruction.config(text="Đang phát âm chuẩn... Vui lòng chờ.",
                                          font=self.controller.font_instruction_text)
            self.controller.update_idletasks()

            tts = gTTS(text=current_text, lang='en', slow=False)

            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3_file:
                tts.write_to_fp(temp_mp3_file)
                temp_mp3_path = temp_mp3_file.name

            time.sleep(0.1)

            pygame.mixer.music.load(temp_mp3_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                self.controller.update()
                time.sleep(0.01)

            messagebox.showinfo("Phát Âm Chuẩn", "Đã phát âm chuẩn xong.")
            self.label_instruction.config(text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!",
                                          font=self.controller.font_instruction_text)

        except Exception as e:
            messagebox.showerror("Lỗi Phát Âm Chuẩn",
                                 f"Không thể tạo/phát âm thanh cho câu này. Vui lòng kiểm tra:\n1. Kết nối Internet của bạn.\n2. Câu văn có quá dài hoặc phức tạp.\n3. Tệp âm thanh không bị khóa bởi chương trình khác.\n\nLỗi chi tiết: {e}")
            self.label_instruction.config(text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!",
                                          font=self.controller.font_instruction_text)
        finally:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            if temp_mp3_path is not None and os.path.exists(temp_mp3_path):
                try:
                    os.remove(temp_mp3_path)
                except OSError as e:
                    print(f"Cảnh báo: Không thể xóa tệp tạm thời {temp_mp3_path}: {e}")
                    messagebox.showwarning("Cảnh báo", f"Không thể xóa tệp tạm thời: {e}\nVui lòng xóa thủ công sau.")

    def analyze_pronunciation(self):
        self.result_text_var.set("Đang phân tích phát âm của bạn... Vui lòng chờ.")
        self.controller.update_idletasks()

        if not os.path.exists(self.audio_filename):
            self.result_text_var.set("Lỗi: Không tìm thấy tệp ghi âm để phân tích.")
            messagebox.showerror("Lỗi", "Không tìm thấy tệp ghi âm. Vui lòng ghi âm trước.")
            self.label_instruction.config(text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!",
                                          font=self.controller.font_instruction_text)
            self.controller.update_idletasks()
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
            self.label_instruction.config(text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!",
                                          font=self.controller.font_instruction_text)
            self.controller.update_idletasks()
            return

        try:
            with sr.AudioFile(temp_audio_file) as source:
                audio_data = recognizer.record(source)

            current_reference_text = self.reference_text.get()
            user_spoken_text = recognizer.recognize_google(audio_data, language="en-US")

            ratio = fuzz.ratio(current_reference_text.lower(), user_spoken_text.lower())
            partial_ratio = fuzz.partial_ratio(current_reference_text.lower(), user_spoken_text.lower())

            feedback = ""
            color_feedback = self.controller.color_text_dark
            if ratio >= 90:
                feedback = "Tuyệt vời! Phát âm của bạn rất chính xác."
                color_feedback = self.controller.color_primary
            elif ratio >= 70:
                feedback = "Tốt! Phát âm của bạn khá rõ ràng."
                color_feedback = '#FFC107'
            elif ratio >= 50:
                feedback = "Cần cải thiện. Hãy cố gắng luyện tập thêm."
                color_feedback = '#fd7e14'
            else:
                feedback = "Cần rất nhiều luyện tập. Đừng nản lòng!"
                color_feedback = self.controller.color_accent_pink

            result_message = (f"Bạn đã nói:\n\"{user_spoken_text}\"\n\n"
                              f"Văn bản chuẩn:\n\"{current_reference_text}\"\n\n"
                              f"Độ chính xác tương đối: {ratio}%\n"
                              f"Độ chính xác một phần: {partial_ratio}%\n\n"
                              f"Phản hồi: {feedback}")

            self.result_text_var.set(result_message)
            self.result_display.config(fg=color_feedback)
            self.controller.update_idletasks()

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
                "Kết quả: KHÔNG THỂ NHẬN DẠNG GIỌC NÓI của bạn.\nVui lòng nói rõ hơn hoặc thử lại. (UnknownValueError)")
            self.result_display.config(fg=self.controller.color_accent_pink)
        except sr.RequestError as e:
            self.result_text_var.set(
                f"Kết quả: LỖI KẾT NỐI đến dịch vụ nhận dạng giọng nói;\nKiểm tra internet của bạn. (RequestError: {e})")
            self.result_display.config(fg=self.controller.color_accent_pink)
        except Exception as e:
            self.result_text_var.set(f"Kết quả: ĐÃ XẢY RA LỖI không mong muốn:\n{e}")
            self.result_display.config(fg=self.controller.color_accent_pink)
        finally:
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
            self.label_instruction.config(text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!",
                                          font=self.controller.font_instruction_text)
            self.controller.update_idletasks()

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
        history_window = tk.Toplevel(self.controller)
        history_window.title("Lịch Sử Luyện Tập")
        history_window.geometry("850x650")
        history_window.transient(self.controller)
        history_window.grab_set()
        history_window.focus_set()
        history_window.config(bg='#e6f2ff')

        history_label = ttk.Label(history_window, text="LỊCH SỬ CÁC PHIÊN LUYỆN TẬP",
                                  font=self.controller.font_instruction_text,
                                  foreground=self.controller.color_secondary, background='#e6f2f5')
        history_label.pack(pady=15)

        history_text_area = scrolledtext.ScrolledText(history_window, wrap=tk.WORD, width=95, height=28,
                                                      font=self.controller.font_body, relief='solid', borderwidth=1,
                                                      highlightbackground=self.controller.color_border,
                                                      highlightcolor=self.controller.color_border,
                                                      bg=self.controller.color_neutral_light,
                                                      fg=self.controller.color_text_dark)
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

        history_text_area.tag_configure('header', font=('Arial', 11, 'bold'),
                                        foreground=self.controller.color_secondary)
        history_text_area.config(state=tk.DISABLED)

        history_window.protocol("WM_DELETE_WINDOW", lambda: self.on_history_window_close(history_window))

    def on_history_window_close(self, history_window):
        history_window.destroy()
        self.controller.grab_release()


# --- LỚP CHO TRANG CHỦ (Mới) ---
class StartPage:
    def __init__(self, master_frame, controller):
        self.master_frame = master_frame
        self.controller = controller

        page_frame = ttk.Frame(master_frame, padding="50 50 50 50")
        page_frame.grid_columnconfigure(0, weight=1)
        page_frame.grid_columnconfigure(1, weight=1)
        page_frame.grid_rowconfigure(0, weight=0)
        page_frame.grid_rowconfigure(1, weight=1)

        # Tiêu đề "HELLO"
        ttk.Label(page_frame, text="HELLO!", font=self.controller.font_header,
                  foreground=self.controller.color_secondary, background='#e6f2f5').grid(row=0, column=0, columnspan=2,
                                                                                         pady=(0, 50), sticky="nsew")

        # Khung chứa chức năng "Học từ vựng" (bên trái)
        vocab_frame = ttk.Labelframe(page_frame, text="HỌC TỪ VỰNG", padding="20 20 20 20")
        vocab_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        vocab_frame.grid_columnconfigure(0, weight=1)
        vocab_frame.grid_rowconfigure(0, weight=1)

        ttk.Label(vocab_frame, text="Chức năng học từ vựng sẽ được phát triển tại đây.", font=self.controller.font_body,
                  wraplength=200).grid(row=0, column=0, sticky="nsew")
        # THAY ĐỔI TẠI ĐÂY: Nút "Bắt đầu Học Từ Vựng" sẽ chuyển sang VocabularyPage
        ttk.Button(vocab_frame, text="Bắt đầu Học Từ Vựng",
                   command=lambda: self.controller.show_frame("VocabularyPage"), style='Orange.TButton').grid(row=1,
                                                                                                              column=0,
                                                                                                              pady=10,
                                                                                                              sticky="s")

        # Khung chứa chức năng "Luyện phát âm" (bên phải)
        pronunciation_frame = ttk.Labelframe(page_frame, text="LUYỆN PHÁT ÂM TIẾNG ANH", padding="20 20 20 20")
        pronunciation_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        pronunciation_frame.grid_columnconfigure(0, weight=1)
        pronunciation_frame.grid_rowconfigure(0, weight=1)

        ttk.Label(pronunciation_frame, text="Cải thiện kỹ năng phát âm của bạn với các bài tập tương tác.",
                  font=self.controller.font_body, wraplength=250).grid(row=0, column=0, sticky="nsew")
        ttk.Button(pronunciation_frame, text="Bắt đầu Luyện Phát Âm",
                   command=lambda: self.controller.show_frame("PronunciationPage"), style='Green.TButton').grid(row=1,
                                                                                                                column=0,
                                                                                                                pady=10,
                                                                                                                sticky="s")

        self.page_frame = page_frame  # Giữ tham chiếu đến frame của trang này


# --- LỚP CHO TRANG HỌC TỪ VỰNG (MỚI) ---
class VocabularyPage:
    def __init__(self, master_frame, controller):
        self.master_frame = master_frame
        self.controller = controller

        self.vocabulary_file = "../vocabulary.json"
        self.vocabulary_list = self.load_vocabulary()
        self.current_word_index = 0

        self.word_var = tk.StringVar()
        self.meaning_var = tk.StringVar()

        # --- Tạo GUI cho VocabularyPage ---
        page_frame = ttk.Frame(master_frame, padding="25 25 25 25")
        page_frame.grid_columnconfigure(0, weight=1)
        page_frame.grid_rowconfigure(0, weight=0)  # Nút quay lại
        page_frame.grid_rowconfigure(1, weight=0)  # Tiêu đề trang
        page_frame.grid_rowconfigure(2, weight=1)  # Hiển thị từ và nghĩa (co giãn)
        page_frame.grid_rowconfigure(3, weight=0)  # Nút điều khiển từ

        # Nút quay lại trang chủ
        ttk.Button(page_frame, text="< Quay lại Trang Chủ", command=lambda: self.controller.show_frame("StartPage"),
                   style='Blue.TButton').grid(row=0, column=0, pady=(0, 10), sticky="nw", padx=10)

        # Tiêu đề trang học từ vựng
        ttk.Label(page_frame, text="HỌC TỪ VỰNG", font=self.controller.font_header,
                  foreground=self.controller.color_secondary, background='#e6f2f5').grid(row=1, column=0, pady=(0, 20),
                                                                                         sticky="nsew")

        # Khung hiển thị từ và nghĩa
        display_frame = ttk.Labelframe(page_frame, text="Từ Vựng Hiện Tại", padding="20 20 20 20")
        display_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        display_frame.grid_columnconfigure(0, weight=1)
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_rowconfigure(1, weight=1)
        display_frame.grid_rowconfigure(2, weight=0)  # Nút phát âm

        ttk.Label(display_frame, textvariable=self.word_var, font=self.controller.font_instruction_text,
                  foreground=self.controller.color_text_dark).grid(row=0, column=0, pady=10, sticky="nsew")
        ttk.Label(display_frame, textvariable=self.meaning_var, font=self.controller.font_body,
                  foreground=self.controller.color_secondary).grid(row=1, column=0, pady=10, sticky="nsew")

        ttk.Button(display_frame, text="Nghe Phát Âm", command=self.play_word_audio, style='Orange.TButton').grid(row=2,
                                                                                                                  column=0,
                                                                                                                  pady=10,
                                                                                                                  sticky="s")

        # Khung nút điều khiển từ (Previous/Next)
        nav_frame = ttk.Frame(page_frame, padding="15 0 15 15")
        nav_frame.grid(row=3, column=0, pady=20)
        nav_frame.grid_columnconfigure(0, weight=1)
        nav_frame.grid_columnconfigure(1, weight=1)

        ttk.Button(nav_frame, text="< Từ Trước", command=self.show_previous_word, style='Blue.TButton').grid(row=0,
                                                                                                             column=0,
                                                                                                             padx=10,
                                                                                                             sticky="ew")
        ttk.Button(nav_frame, text="Từ Tiếp >", command=self.show_next_word, style='Blue.TButton').grid(row=0, column=1,
                                                                                                        padx=10,
                                                                                                        sticky="ew")

        self.page_frame = page_frame  # Giữ tham chiếu đến frame của trang này

        self.display_current_word()  # Hiển thị từ đầu tiên khi khởi tạo

    # --- Các hàm chức năng của VocabularyPage ---
    def load_vocabulary(self):
        if not os.path.exists(self.vocabulary_file):
            messagebox.showwarning("Cảnh báo",
                                   f"Không tìm thấy tệp '{self.vocabulary_file}'. Vui lòng tạo tệp này với định dạng JSON (danh sách đối tượng từ/nghĩa).")
            return []
        try:
            with open(self.vocabulary_file, 'r', encoding='utf-8') as f:
                vocab = json.load(f)
                # Kiểm tra định dạng: phải là list, mỗi phần tử là dict có 'word' và 'meaning'
                if not isinstance(vocab, list) or not all(
                        isinstance(item, dict) and 'word' in item and 'meaning' in item for item in vocab):
                    messagebox.showerror("Lỗi tệp từ vựng",
                                         "Định dạng tệp 'vocabulary.json' không hợp lệ. Phải là danh sách các đối tượng {'word': '...', 'meaning': '...'}.")
                    return []
                return vocab
        except json.JSONDecodeError:
            messagebox.showerror("Lỗi tệp từ vựng", "Lỗi đọc tệp 'vocabulary.json'. Đảm bảo nó là JSON hợp lệ.")
            return []
        except Exception as e:
            messagebox.showerror("Lỗi tệp từ vựng", f"Đã xảy ra lỗi khi tải từ vựng: {e}")
            return []

    def display_current_word(self):
        if not self.vocabulary_list:
            self.word_var.set("Chưa có từ vựng.")
            self.meaning_var.set("Vui lòng thêm từ vào 'vocabulary.json'.")
            return

        if self.current_word_index < 0:
            self.current_word_index = len(self.vocabulary_list) - 1  # Về cuối danh sách
        elif self.current_word_index >= len(self.vocabulary_list):
            self.current_word_index = 0  # Quay về đầu danh sách

        current_item = self.vocabulary_list[self.current_word_index]
        self.word_var.set(current_item.get("word", "N/A"))
        self.meaning_var.set(current_item.get("meaning", "N/A"))

    def show_next_word(self):
        self.current_word_index += 1
        self.display_current_word()

    def show_previous_word(self):
        self.current_word_index -= 1
        self.display_current_word()

    def play_word_audio(self):
        word_to_play = self.word_var.get()
        if not word_to_play or word_to_play == "Chưa có từ vựng.":
            messagebox.showwarning("Cảnh báo", "Không có từ nào để phát âm!")
            return

        temp_mp3_path = None
        try:
            self.controller.update_idletasks()  # Cập nhật GUI

            tts = gTTS(text=word_to_play, lang='en', slow=False)

            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3_file:
                tts.write_to_fp(temp_mp3_file)
                temp_mp3_path = temp_mp3_file.name

            time.sleep(0.1)

            pygame.mixer.music.load(temp_mp3_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                self.controller.update()
                time.sleep(0.01)

        except Exception as e:
            messagebox.showerror("Lỗi Phát Âm Từ",
                                 f"Không thể phát âm từ này. Vui lòng kiểm tra:\n1. Kết nối Internet.\n2. Từ không quá phức tạp.\n\nLỗi chi tiết: {e}")
        finally:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            if temp_mp3_path is not None and os.path.exists(temp_mp3_path):
                try:
                    os.remove(temp_mp3_path)
                except OSError as e:
                    print(f"Cảnh báo: Không thể xóa tệp tạm thời {temp_mp3_path}: {e}")
                    messagebox.showwarning("Cảnh báo", f"Không thể xóa tệp tạm thời: {e}\nVui lòng xóa thủ công sau.")


# --- LỚP CHO TRANG CHỦ ---
class StartPage:
    def __init__(self, master_frame, controller):
        self.master_frame = master_frame
        self.controller = controller

        page_frame = ttk.Frame(master_frame, padding="50 50 50 50")
        page_frame.grid_columnconfigure(0, weight=1)
        page_frame.grid_columnconfigure(1, weight=1)
        page_frame.grid_rowconfigure(0, weight=0)
        page_frame.grid_rowconfigure(1, weight=1)

        # Tiêu đề "HELLO"
        ttk.Label(page_frame, text="HELLO!", font=self.controller.font_header,
                  foreground=self.controller.color_secondary, background='#e6f2f5').grid(row=0, column=0, columnspan=2,
                                                                                         pady=(0, 50), sticky="nsew")

        # Khung chứa chức năng "Học từ vựng" (bên trái)
        vocab_frame = ttk.Labelframe(page_frame, text="HỌC TỪ VỰNG", padding="20 20 20 20")
        vocab_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        vocab_frame.grid_columnconfigure(0, weight=1)
        vocab_frame.grid_rowconfigure(0, weight=1)

        ttk.Label(vocab_frame, text="Mở rộng vốn từ vựng của bạn với các bài học tương tác.",
                  font=self.controller.font_body, wraplength=200).grid(row=0, column=0, sticky="nsew")
        # THAY ĐỔI TẠI ĐÂY: Nút "Bắt đầu Học Từ Vựng" sẽ chuyển sang VocabularyPage
        ttk.Button(vocab_frame, text="Bắt đầu Học Từ Vựng",
                   command=lambda: self.controller.show_frame("VocabularyPage"), style='Orange.TButton').grid(row=1,
                                                                                                              column=0,
                                                                                                              pady=10,
                                                                                                              sticky="s")

        # Khung chứa chức năng "Luyện phát âm" (bên phải)
        pronunciation_frame = ttk.Labelframe(page_frame, text="LUYỆN PHÁT ÂM TIẾNG ANH", padding="20 20 20 20")
        pronunciation_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        pronunciation_frame.grid_columnconfigure(0, weight=1)
        pronunciation_frame.grid_rowconfigure(0, weight=1)

        ttk.Label(pronunciation_frame, text="Cải thiện kỹ năng phát âm của bạn với các bài tập tương tác.",
                  font=self.controller.font_body, wraplength=250).grid(row=0, column=0, sticky="nsew")
        ttk.Button(pronunciation_frame, text="Bắt đầu Luyện Phát Âm",
                   command=lambda: self.controller.show_frame("PronunciationPage"), style='Green.TButton').grid(row=1,
                                                                                                                column=0,
                                                                                                                pady=10,
                                                                                                                sticky="s")

        self.page_frame = page_frame  # Giữ tham chiếu đến frame của trang này


# --- LỚP ỨNG DỤNG CHÍNH (Quản lý các trang) ---
class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Ứng dụng Học Tiếng Anh")
        self.geometry("900x900")
        self.resizable(False, False)
        self.config(bg='#e6f2ff')

        pygame.mixer.init()

        # --- Cấu hình Style (Phong cách) cho Tkinter ---
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.color_primary = '#4CAF50'
        self.color_secondary = '#6A1B9A'
        self.color_accent_blue = '#2196F3'
        self.color_accent_pink = '#E91E63'
        self.color_neutral_bg = '#f0f2f5'
        self.color_neutral_light = '#ffffff'
        self.color_text_dark = '#333333'
        self.color_text_light = '#ffffff'
        self.color_border = '#bbdefb'

        self.font_header = ('Arial', 24, 'bold')
        self.font_instruction_text = ('Arial', 18, 'bold')
        self.font_section_title = ('Arial', 14, 'bold')
        self.font_body = ('Arial', 12)
        self.font_input = ('Arial', 13)
        self.font_button = ('Arial', 12, 'bold')
        self.font_feedback = ('Arial', 15)

        # Cấu hình chung cho các widget (dùng self.style)
        self.style.configure('TLabel', font=self.font_body, background='#e6f2f5', foreground=self.color_text_dark)
        self.style.configure('TButton', font=self.font_button, padding=(15, 10), borderwidth=0, focusthickness=0,
                             focuscolor='none', relief='flat')
        self.style.configure('TCombobox', font=self.font_input, fieldbackground=self.color_neutral_light,
                             background='#e6f2f5', bordercolor=self.color_border, arrowcolor=self.color_secondary)
        self.style.configure('TFrame', background='#e6f2f5')
        self.style.configure('TLabelframe', font=self.font_section_title, background=self.color_neutral_bg,
                             foreground=self.color_text_dark, borderwidth=1, relief='flat',
                             bordercolor=self.color_border, highlightbackground=self.color_border)
        self.style.configure('TLabelframe.Label', background=self.color_neutral_bg, foreground=self.color_secondary,
                             font=self.font_section_title)

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

        self.style.configure('Result.TLabel', font=self.font_feedback, wraplength=780, justify='center',
                             foreground=self.color_text_dark)

        # --- Khung chứa các trang ---
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Thêm VocabularyPage vào danh sách các trang
        for F in (StartPage, PronunciationPage, VocabularyPage):
            page_name = F.__name__
            frame = F(container, self)
            self.frames[page_name] = frame
            frame.page_frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.page_frame.tkraise()


# --- Khởi chạy ứng dụng ---
if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()