import airsim
import time
import re
import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import speech_recognition as sr
from phonemizer import phonemize
from Levenshtein import distance
from phonemizer.backend.espeak.wrapper import EspeakWrapper

# Thiết lập thư viện eSpeak NG
EspeakWrapper.set_library(r'C:\Program Files\eSpeak NG\libespeak-ng.dll')

# --- Khởi tạo AirSim ---
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
print("Đã kết nối AirSim!")

# --- Drone Controller ---
current_action = None
current_task = None
flight_started = False  # Đã cất cánh chưa
first_takeoff_attempt = True  # Biến cờ để theo dõi lần thử cất cánh đầu tiên

# Ngưỡng để xác định trên mặt đất
ground_distance_threshold = 0.5  # Khoảng cách đến vật cản dưới < 0.5 mét
velocity_threshold = 0.1  # Vận tốc tổng <= 0.1 m/s để linh hoạt với nhiễu

def stop_current_action():
    global current_task, current_action
    if current_task is not None:
        try:
            current_task.cancel()
        except Exception:
            pass
        client.moveByVelocityAsync(0, 0, 0, 1).join()
        current_task = None
    current_action = None

def is_on_ground():
    # Lấy dữ liệu từ cảm biến khoảng cách
    distance_data = client.getDistanceSensorData(distance_sensor_name="Distance")
    
    # Lấy vận tốc từ trạng thái drone
    vel = client.getMultirotorState().kinematics_estimated.linear_velocity
    velocity_magnitude = (vel.x_val**2 + vel.y_val**2 + vel.z_val**2)**0.5  # Tính vận tốc tổng
    
    # Kiểm tra hai điều kiện:
    # 1. Khoảng cách đến vật cản phía dưới < 0.5 mét (nếu cảm biến có dữ liệu)
    # 2. Vận tốc tổng <= 0.1 m/s
    distance_condition = distance_data.distance < ground_distance_threshold if distance_data.distance > 0 else False
    velocity_condition = velocity_magnitude <= velocity_threshold
    
    # Drone được coi là "trên mặt đất" nếu cả hai điều kiện đều đúng
    on_ground = distance_condition and velocity_condition
    
    return on_ground

def execute_action(action, distance=None):
    global current_action, current_task, flight_started, first_takeoff_attempt

    # Kiểm tra trạng thái trên mặt đất
    on_ground = is_on_ground()

    # Nếu đang ở mặt đất và chưa cất cánh
    if on_ground and not flight_started:
        if action != "cất_cánh":
            # print("🚫 Chưa cất cánh. Lệnh này không được phép.")
            return
    
    # Nếu đã cất cánh rồi và gọi lại lệnh cất cánh
    if flight_started and action == "cất_cánh":
        # print("🚫 Đã cất cánh rồi. Không thể cất cánh lại.")
        return

    # Xử lý cất cánh
    if action == "cất_cánh":
        # Lần cất cánh đầu tiên luôn được phép, bất kể trạng thái
        if first_takeoff_attempt:
            print("✅ Đang cất cánh (lần đầu tiên)...")
            client.takeoffAsync().join()
            flight_started = True
            first_takeoff_attempt = False  # Đánh dấu lần cất cánh đầu tiên đã xảy ra
            display_status_on_ue()
            check_downward_obstacle()  # In khoảng cách lên UE4 sau khi cất cánh
            return
        # Các lần sau kiểm tra trạng thái trên mặt đất
        elif on_ground:
            print("✅ Đang cất cánh...")
            client.takeoffAsync().join()
            flight_started = True
            display_status_on_ue()
            check_downward_obstacle()  # In khoảng cách lên UE4 sau khi cất cánh
            return
        else:
            # print("🚫 Không thể cất cánh, drone không ở trên mặt đất.")
            return

    # Xử lý hạ cánh
    if action == "hạ_cánh" and flight_started:
        print("🛬 Hạ cánh...")
        client.landAsync().join()
        # Kiểm tra trạng thái sau khi hạ cánh
        if is_on_ground():  # Dựa trên logic mới: khoảng cách < 0.5m và vận tốc <= 0.1 m/s
            flight_started = False
            print("✅ Drone đã hạ cánh thành công.")
        else:
            flight_started = True  # Vẫn coi là đang bay nếu không thỏa mãn điều kiện hạ cánh
            print("⚠ Drone chưa hạ cánh hoàn toàn (khoảng cách hoặc vận tốc không đạt yêu cầu).")
        display_status_on_ue()
        check_downward_obstacle()  # In khoảng cách lên UE4 sau khi hạ cánh
        return

    # Các lệnh còn lại chỉ thực khi đang bay
    stop_current_action()

    velocity = 4  # m/s
    if isinstance(distance, tuple):
        value, unit = distance
    else:
        value, unit = distance, None

    if action == "di_chuyển_tới_trước":
        duration = max(1, value / velocity) if value else 999
        current_task = client.moveByVelocityAsync(velocity, 0, 0, duration)
    elif action == "di_chuyển_lùi":
        duration = max(1, value / velocity) if value else 999
        current_task = client.moveByVelocityAsync(-velocity, 0, 0, duration)
    elif action == "di_chuyển_trái":
        duration = max(1, value / velocity) if value else 999
        current_task = client.moveByVelocityAsync(0, -velocity, 0, duration)
    elif action == "di_chuyển_phải":
        duration = max(1, value / velocity) if value else 999
        current_task = client.moveByVelocityAsync(0, velocity, 0, duration)
    elif action == "tăng_độ_cao":
        duration = max(1, value / velocity) if value else 999
        current_task = client.moveByVelocityAsync(0, 0, -velocity, duration)
    elif action == "giảm_độ_cao":
        duration = max(1, value / velocity) if value else 999
        current_task = client.moveByVelocityAsync(0, 0, velocity, duration)
    elif action == "lơ_lửng":
        current_task = client.moveByVelocityAsync(0, 0, 0, 1)
    elif action == "quay_trái":
        if value:
            duration = abs(value) / 30  # tốc độ quay 30 độ/giây
        else:
            duration = 999
        current_task = client.rotateByYawRateAsync(-30, duration)
    elif action == "quay_phải":
        if value:
            duration = abs(value) / 30
        else:
            duration = 999
        current_task = client.rotateByYawRateAsync(30, duration)

    current_action = action
    display_status_on_ue()
    # Đợi hành động hoàn tất (nếu có thời gian xác định) rồi in khoảng cách
    if current_task and distance and isinstance(distance, tuple) and distance[0] is not None:
        current_task.join()  # Đợi lệnh hoàn tất
    check_downward_obstacle()  # In khoảng cách lên UE4 sau khi hành động xong

# --- Voice Recognition ---
class VoiceListener:
    def __init__(self, language='vi-VN'):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.language = language
        self.microphone = sr.Microphone()
        self.background_listener = None

    def start_listening(self, callback):
        def _callback(recognizer, audio):
            try:
                text = recognizer.recognize_google(audio, language=self.language)
                callback(text)
            except sr.UnknownValueError:
                callback("[Không nhận diện được lời nói]")
            except sr.RequestError as e:
                callback(f"[Lỗi kết nối: {e}]")

        with self.microphone as source:
            print("Đang điều chỉnh độ ồn nền...")
            self.recognizer.adjust_for_ambient_noise(source)

        print("Bắt đầu lắng nghe...")
        self.background_listener = self.recognizer.listen_in_background(self.microphone, _callback)

    def stop_listening(self):
        if self.background_listener:
            self.background_listener(wait_for_stop=False)
            print("Đã dừng lắng nghe.")

# --- Xử lý phoneme và lệnh ---
def get_phonemes(text):
    return phonemize(text, language='vi', backend='espeak', strip=True)

commands = {
    "bay lên": {"action": "tăng_độ_cao", "phonemes": get_phonemes("bay lên")},
    "hạ xuống": {"action": "giảm_độ_cao", "phonemes": get_phonemes("hạ xuống")},
    "tiến thẳng": {"action": "di_chuyển_tới_trước", "phonemes": get_phonemes("tiến thẳng")},
    "lùi lại": {"action": "di_chuyển_lùi", "phonemes": get_phonemes("lùi lại")},
    "bay sang trái": {"action": "di_chuyển_trái", "phonemes": get_phonemes("bay sang trái")},
    "bay sang phải": {"action": "di_chuyển_phải", "phonemes": get_phonemes("bay sang phải")},
    "dừng lại": {"action": "lơ_lửng", "phonemes": get_phonemes("dừng lại")},
    "hạ cánh": {"action": "hạ_cánh", "phonemes": get_phonemes("hạ cánh")},
    "quay trái": {"action": "quay_trái", "phonemes": get_phonemes("quay trái")},
    "quay phải": {"action": "quay_phải", "phonemes": get_phonemes("quay phải")},
    "cất cánh": {"action": "cất_cánh", "phonemes": get_phonemes("cất cánh")}
}

# Hàm tách lệnh và thông số từ câu nói
def extract_command_and_value(recognized_text):
    recognized_text = recognized_text.strip().lower()
    value = None

    # Tách phần số bất kể ký tự đơn vị
    match = re.search(r'^(.*?)(\d+|không)\D*$', recognized_text, re.IGNORECASE)
    if match:
        text_part = match.group(1).strip()
        number_str = match.group(2).strip()
        value = 0 if number_str == "không" else int(number_str)
    else:
        text_part = recognized_text
        value = None

    return text_part, value

# Tìm lệnh gần nhất theo phoneme
def find_closest_command(text_part):
    recognized_phonemes = get_phonemes(text_part)
    min_distance = float('inf')
    closest_command = None
    for cmd, data in commands.items():
        dist = distance(recognized_phonemes, data["phonemes"])
        if dist < min_distance:
            min_distance = dist
            closest_command = cmd
    return closest_command

# --- Giao diện điều khiển ---
class VoiceControlGUI:
    def __init__(self, root):
        self.listener = VoiceListener()
        self.root = root
        self.root.title("🛰️ ĐIỀU KHIỂN DRONE BẰNG GIỌNG NÓI 🛰️")
        self.root.attributes('-fullscreen', True)

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height, highlightthickness=0)
        self.canvas.place(x=0, y=0)
        self.draw_gradient_background()

        self.paused = False
        self.exit_requested = False
        self.is_listening_started = False

        logo_size = int(self.screen_width * 0.12)
        font_size_label = int(self.screen_width * 0.03)
        font_size_button = int(self.screen_width * 0.022)
        button_width_chars = 20

        logo_img = Image.open("Google_Web_API/z6574131043284_d6a8e506d3b09fb82baa8ed727eeb252.jpg")
        logo_img = ImageOps.contain(logo_img, (logo_size, logo_size))
        self.logo = ImageTk.PhotoImage(logo_img)
        self.logo_label = tk.Label(self.root, image=self.logo, bg="black")
        self.logo_label.place(x=50, y=50)

        self.label = tk.Label(
            self.root,
            text="🔊 Đang chờ lệnh...",
            font=("Consolas", font_size_label, "bold"),
            fg="#FFB400", bg="black",
            padx=50, pady=40,
            relief="solid",
            bd=2,
            highlightbackground="#FFB400",
            highlightcolor="#FFB400",
            highlightthickness=3
        )
        self.label.place(relx=0.5, rely=0.4, anchor="center")

        self.start_btn = tk.Button(self.root, text="▶ BẮT ĐẦU",
                                   font=("Consolas", font_size_button, "bold"), width=button_width_chars,
                                   bg="#001f1f", fg="#00ffff", activebackground="#003333",
                                   activeforeground="#00ffff", relief="raised", bd=3, highlightthickness=3,
                                   highlightbackground="#00ffff", command=self.start_listening)
        self.start_btn.place(relx=0.25, rely=0.7, anchor="center")

        self.stop_btn = tk.Button(self.root, text="🟥 KẾT THÚC",
                                  font=("Consolas", font_size_button, "bold"), width=button_width_chars,
                                  bg="#1a0d00", fg="#FFB400", activebackground="#330d00",
                                  activeforeground="#FFB400", relief="raised", bd=3, highlightthickness=3,
                                  highlightbackground="#FFB400", command=self.stop_all)
        self.stop_btn.place(relx=0.75, rely=0.7, anchor="center")

        self.emergency_btn = tk.Button(self.root, text="⚠ DỪNG KHẨN CẤP ⚠",
                                       font=("Consolas", font_size_button + 2, "bold"), width=button_width_chars + 4,
                                       bg="#0d0d0d", fg="#ff1a1a", activebackground="#330000",
                                       activeforeground="#ff1a1a", relief="raised", bd=3, highlightthickness=3,
                                       highlightbackground="#ff1a1a", command=self.emergency_stop)
        self.emergency_btn.place(relx=0.5, rely=0.85, anchor="center")

        self.blink_emergency()

    def draw_gradient_background(self):
        for i in range(self.screen_height):
            r = int(10 + (i / self.screen_height) * 10)
            g = int(20 + (i / self.screen_height) * 10)
            b = int(20 + (i / self.screen_height) * 10)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, self.screen_width, i, fill=color)

    def blink_emergency(self):
        current_color = self.emergency_btn.cget("highlightbackground")
        new_color = "#ff1a1a" if current_color == "#0d0d0d" else "#0d0d0d"
        self.emergency_btn.config(highlightbackground=new_color)
        self.root.after(3000, self.blink_emergency)

    def update_command(self, text):
        print("Bạn nói:", text)

        if text and text != "[Không nhận diện được lời nói]" and "[Lỗi" not in text:
            # Tách phần lệnh và giá trị từ câu nói
            command_text, value = extract_command_and_value(text)

            # Tìm lệnh gần đúng nhất dựa trên phoneme
            corrected_command = find_closest_command(command_text)

            if corrected_command:
                action = commands[corrected_command]["action"]

                # Xác định đơn vị dựa trên loại lệnh
                if "quay trái" in corrected_command or "quay phải" in corrected_command:
                    unit = "độ"
                else:
                    unit = "m"

                # Tạo chuỗi hiển thị giá trị nếu có
                distance_display = ""
                if value is not None:
                    if unit == "m":
                        distance_display = f" {value} m"
                    elif unit == "độ":
                        distance_display = f" {value}°"

                # Cập nhật label GUI
                self.label.config(
                    text=f"📡 Lệnh: {corrected_command.upper()}{distance_display}",
                    fg="#00ff00"
                )

                # Gọi hành động nếu cần
                execute_action(action, distance=(value, unit))

            else:
                self.label.config(text="⚠ Không nhận diện được lệnh.", fg="#ff9900")
        else:
            self.label.config(text="❌ Không rõ lời nói.", fg="#ff0000")

    def start_listening(self):
        if self.paused:
            self.listener.start_listening(callback=self.update_command)
            self.label.config(text="🔊 Tiếp tục lắng nghe...", fg="#00ffff")
            self.start_btn.config(text="▶ TIẾP TỤC")
            self.stop_btn.config(text="⏸ TẠM DỪNG")
            self.paused = False
        elif not self.is_listening_started:
            self.listener.start_listening(callback=self.update_command)
            self.label.config(text="🔊 Đang lắng nghe...", fg="#00ffff")
            self.start_btn.config(text="▶ TIẾP TỤC")
            self.stop_btn.config(text="⏸ TẠM DỪNG")
            self.is_listening_started = True
            self.paused = False

    def stop_all(self):
        if not self.is_listening_started:
            # Nếu chưa bắt đầu, ấn KẾT THÚC sẽ thoát luôn
            self.root.destroy()
        elif not self.paused:
            # Nếu đang hoạt động, dừng lại
            self.listener.stop_listening()
            self.label.config(text="⏸ Đã tạm dừng", fg="#FFB400")
            self.paused = True
            self.start_btn.config(text="▶ TIẾP TỤC")
            self.stop_btn.config(text="🟥 KẾT THÚC")
        else:
            # Nếu đang tạm dừng rồi, ấn lần nữa để thoát
            self.root.destroy()

    def emergency_stop(self):
        print("Drone DỪNG KHẨN CẤP ")
        self.update_command("dừng lại")
        self.label.config(text="🛑 KHẨN CẤP: DRONE DỪNG NGAY!", fg="#ff0000")

def display_status_on_ue():
    state = client.getMultirotorState()
    pos = state.kinematics_estimated.position
    vel = state.kinematics_estimated.linear_velocity

    altitude = abs(pos.z_val)
    speed = (vel.x_val**2 + vel.y_val**2 + vel.z_val**2)**0.5

    message = f"Altitude: {altitude:.2f} m | Speed: {speed:.2f} m/s"
    client.simPrintLogMessage("DRONE STATUS", message)

# --- Kiểm tra khoảng cách và in lên màn hình UE4 ---
def check_downward_obstacle(threshold=1.0):
    # Lấy dữ liệu từ cảm biến Distance
    data = client.getDistanceSensorData(distance_sensor_name="Distance")
    
    if data.distance > 0:
        message = f"Distance to object below: {data.distance:.2f} m"
        if data.distance < threshold:
            message += " | WARNING: TOO CLOSE!"
        # In thông báo lên màn hình UE4
        client.simPrintLogMessage("DISTANCE: ", message, severity=2)  # severity=2 cho mức cảnh báo trung bình
    else:
        client.simPrintLogMessage("DISTANCE: ", "No data from Distance sensor.", severity=2)

# --- Main ---
if __name__ == "__main__":
    root = tk.Tk()
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    app = VoiceControlGUI(root)
    root.mainloop()