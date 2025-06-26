# Thesis2024.2
# Hướng Dẫn Điều Khiển Drone Bằng Giọng Nói 

Chào mừng bạn đến với dự án điều khiển drone bằng giọng nói sử dụng AirSim và Unreal Engine! Dự án này cho phép bạn dùng các lệnh giọng nói tiếng Việt (như "cất cánh", "hạ cánh", "tiến thẳng") để điều khiển một drone ảo trong môi trường mô phỏng Unreal Engine (UE4). Ứng dụng tích hợp nhận dạng giọng nói qua Google Speech API, xử lý phoneme để nhận diện lệnh chính xác, và giao diện đồ họa (GUI) để theo dõi trạng thái drone.

File này sẽ hướng dẫn bạn từng bước từ cài đặt môi trường đến chạy dự án. Hãy đọc kỹ và làm theo nhé!

## Mục Lục
- [Tính Năng](#tính-năng)
- [Yêu Cầu Cần Thiết](#yêu-cầu-cần-thiết)
- [Cài Đặt](#cài-đặt)
  - [Bước 1: Cài Đặt Unreal Engine 4.27](#bước-1-cài-đặt-unreal-engine-427)
  - [Bước 2: Cài Đặt AirSim](#bước-2-cài-đặt-airsim)
  - [Bước 3: Cài Đặt Python và Các Thư Viện](#bước-3-cài-đặt-python-và-các-thư-viện)
  - [Bước 4: Cài Đặt eSpeak NG](#bước-4-cài-đặt-espeak-ng)
  - [Bước 5: Tải Hình Ảnh Logo (Tùy Chọn)](#bước-5-tải-hình-ảnh-logo-tùy-chọn)
- [Cấu Hình](#cấu-hình)
- [Chạy Ứng Dụng](#chạy-ứng-dụng)
- [Lệnh Giọng Nói](#lệnh-giọng-nói)
- [Khắc Phục Sự Cố](#khắc-phục-sự-cố)
- [Cách Hoạt Động](#cách-hoạt-động)

## Tính Năng
- **Điều Khiển Giọng Nói**: Dùng tiếng Việt để ra lệnh cho drone (ví dụ: "cất cánh", "bay lên 3").
- **Nhận Dạng Chính Xác**: Xử lý phoneme để nhận diện lệnh ngay cả khi phát âm không hoàn hảo.
- **Giao Diện GUI**: Hiển thị lệnh, trạng thái drone (độ cao, tốc độ), và các nút điều khiển (Bắt đầu, Tạm dừng, Dừng khẩn cấp).
- **An Toàn**: Kiểm tra trạng thái drone (trên mặt đất hay đang bay) trước khi thực hiện lệnh, cảnh báo vật cản bên dưới qua cảm biến khoảng cách.
- **Phản Hồi Thời Gian Thực**: Hiển thị thông tin trên GUI và console Unreal Engine.

## Yêu Cầu Cần Thiết
Trước khi bắt đầu, hãy đảm bảo bạn có:
- **Hệ Điều Hành**: Windows 10 hoặc 11 (dự án này được thiết kế cho Windows).
- **Phần Cứng**:
  - Máy tính có ít nhất 8 GB RAM và GPU tốt (khuyến nghị NVIDIA GTX 970 hoặc cao hơn để chạy Unreal Engine mượt mà).
  - Micro hoạt động tốt để nhận giọng nói.
- **Phần Mềm**:
  - Unreal Engine 4.27 (cần thiết cho AirSim).
  - Python 3.8 hoặc 3.9 (không dùng 3.10+ vì có thể gặp lỗi tương thích).
  - eSpeak NG (xử lý phoneme).
- **Kết Nối Internet**: Để tải phần mềm và dùng Google Speech Recognition API.

## Cài Đặt

### Bước 1: Cài Đặt Unreal Engine 4.27
Unreal Engine (UE) là nền tảng mô phỏng chính mà AirSim chạy trên đó. Dưới đây là hướng dẫn chi tiết để cài đặt phiên bản 4.27:

1. **Tải và Cài Đặt Epic Games Launcher**:
   - Truy cập [trang web Epic Games](https://www.epicgames.com/store/download).
   - Nhấn nút **Download Epic Games Launcher** và chạy file cài đặt.
   - Sau khi cài xong, mở Epic Games Launcher và đăng nhập (tạo tài khoản nếu chưa có).

2. **Cài Unreal Engine 4.27**:
   - Trong Epic Games Launcher, chọn tab **Unreal Engine** ở menu bên trái.
   - Nhấn **Library** (Thư viện).
   - Ở góc trên cùng, bạn sẽ thấy nút dấu cộng (+) bên cạnh "Engine Versions". Nhấn vào đó.
   - Chọn phiên bản **4.27** (có thể cần cuộn xuống để tìm), rồi nhấn **Install**.
   - Chọn thư mục cài đặt (khuyến nghị để mặc định, ví dụ: `C:\Program Files\Epic Games\UE_4.27`).
   - Nhấn **Install** và đợi (có thể mất 30 phút đến 1 giờ tùy tốc độ mạng và máy tính).

3. **Cài Đặt Visual Studio 2019 (Yêu cầu để biên dịch AirSim)**:
   - Tải Visual Studio Community 2019 từ [visualstudio.microsoft.com](https://visualstudio.microsoft.com/vs/older-downloads/).
   - Chạy installer và chọn workload **Game Development with C++**.
   - Đảm bảo tích các thành phần sau (ấn "Modify" nếu cần):
     - **MSVC v142 - VS 2019 C++ x64/x86 build tools**.
     - **Windows 10 SDK** (chọn phiên bản mới nhất).
     - **C++ CMake tools for Windows**.
   - Nhấn **Install** và đợi hoàn tất.
   - Sau khi cài xong, khởi động lại máy để đảm bảo mọi thứ hoạt động.

4. **Kiểm Tra Cài Đặt**:
   - Mở Epic Games Launcher, vào Library, nhấp vào Unreal Engine 4.27, chọn **Launch**.
   - Nếu UE4 mở được giao diện chỉnh sửa, cài đặt đã thành công!

### Bước 2: Cài Đặt AirSim
AirSim là plugin mở rộng cho Unreal Engine, cung cấp mô phỏng drone. Đây là cách cài đặt:

1. **Tải Mã Nguồn AirSim**:
   - Mở Command Prompt (nhấn Win + R, gõ `cmd`, Enter) hoặc dùng Git Bash nếu bạn đã cài Git.
   - Chạy lệnh sau để clone repository từ GitHub:
     ```
     git clone https://github.com/Microsoft/AirSim.git
     ```
   - Sau khi tải xong, bạn sẽ có thư mục `AirSim` (ví dụ: `C:\Users\YourName\AirSim`).

2. **Cài Đặt và Biên Dịch AirSim**:
   - Mở Command Prompt, di chuyển vào thư mục AirSim:
     ```
     cd AirSim
     ```
   - Chạy script cài đặt phụ thuộc:
     ```
     .\setup.bat
     ```
     (Chờ 5-15 phút tùy máy để tải các thư viện cần thiết.)
   - Sau khi setup xong, biên dịch AirSim:
     ```
     .\build.bat
     ```
     (Quá trình này có thể mất 10-30 phút, đảm bảo Visual Studio 2019 đã cài).

3. **Tích Hợp AirSim vào Unreal Engine**:
   - **Cách 1: Dùng Môi Trường Mẫu (Khuyến Nghị cho Người Mới)**:
     - Vào thư mục `AirSim\Unreal\Environments\Blocks`.
     - Nhấp đúp file `Blocks.uproject` để mở trong Unreal Engine 4.27.
     - Nếu được hỏi "Build?", chọn **Yes**. Chờ UE biên dịch (mất vài phút).
   - **Cách 2: Tạo Dự Án Mới**:
     - Mở Unreal Engine 4.27 từ Epic Games Launcher.
     - Chọn **New Project > Blank > C++ Project**, đặt tên (ví dụ: `DroneProject`).
     - Sao chép thư mục `AirSim\Unreal\Plugins\AirSim` vào thư mục `Plugins` của dự án mới (tạo thư mục `Plugins` nếu chưa có).
     - Mở file `.uproject` của dự án, chọn **Yes** để build.

4. **Cấu Hình Cảm Biến Khoảng Cách**:
   - Mở File Explorer, vào `%USERPROFILE%\Documents\AirSim` (thường là `C:\Users\YourName\Documents\AirSim`).
   - Nếu chưa có file `settings.json`, tạo mới bằng Notepad và dán đoạn sau:
     ```{
      "SettingsVersion": 1.2,
      "SimMode": "Multirotor",
      "Vehicles": {
        "Drone1": {
          "VehicleType": "SimpleFlight",
          "AutoCreate": true,
          "Sensors": {
            "Distance": {
              "SensorType": 5,
              "Enabled": true,
              "X": 0, "Y": 0, "Z": 0,
              "Yaw": 0, "Pitch": -90, "Roll": 0,
              "MinDistance": 0.2,
              "MaxDistance": 40.0
            }
          }
        }
      }
    } ```
   - Lưu file với encoding UTF-8.

6. **Kiểm Tra AirSim**:
   - Mở dự án UE (Blocks hoặc dự án mới), nhấn nút **Play** trong giao diện UE.
   - Mở Command Prompt, vào `AirSim\PythonClient\multirotor`.
   - Chạy script mẫu:
     ```
     python hello_drone.py
     ```
   - Nếu drone trong UE di chuyển, AirSim đã hoạt động!

### Bước 3: Cài Đặt Python và Các Thư Viện
1. **Cài Python**:
   - Tải Python 3.8 hoặc 3.9 từ [python.org](https://www.python.org/downloads/).
   - Chạy installer, tích chọn **Add Python to PATH**, rồi nhấn **Install Now**.

2. **Tạo Môi Trường Ảo (Khuyến Nghị)**:
   - Mở Command Prompt, chạy:
     ```
     python -m venv drone_env
     .\drone_env\Scripts\activate
     ```
   - Bạn sẽ thấy `(drone_env)` trước dấu nhắc lệnh.

3. **Cài Thư Viện**:
   - Trong môi trường ảo, chạy:
     ```
     pip install airsim speechrecognition phonemizer pillow pybind11 python-Levenshtein
     ```
   - Đợi cài đặt hoàn tất (cần internet).

### Bước 4: Cài Đặt eSpeak NG
eSpeak NG giúp xử lý phoneme để nhận diện lệnh chính xác hơn.

1. **Tải và Cài Đặt**:
   - Vào [GitHub releases của eSpeak NG](https://github.com/espeak-ng/espeak-ng/releases).
   - Tải file `.msi` mới nhất (ví dụ: `espeak-ng-X.X.X.msi`).
   - Chạy file và cài vào đường dẫn mặc định: `C:\Program Files\eSpeak NG`.

2. **Kiểm Tra**:
   - Mở Command Prompt, chạy:
     ```
     "C:\Program Files\eSpeak NG\espeak-ng.exe" --version
     ```
   - Nếu thấy thông tin phiên bản, cài đặt thành công.

### Bước 5: Tải Hình Ảnh Logo (Tùy Chọn)
GUI dùng một logo để hiển thị. Nếu muốn dùng:
1. Tạo thư mục `Google_Web_API` trong cùng thư mục với script Python.
2. Đặt file hình ảnh tên `z6574131043284_d6a8e506d3b09fb82baa8ed727eeb252.jpg` vào đó.
3. Nếu không có, bỏ qua hoặc comment dòng tải logo trong script.

## Cấu Hình
1. **Micro**: Đảm bảo micro được cắm, vào **Settings > Sound** trong Windows để đặt làm thiết bị đầu vào mặc định.
2. **Kết Nối AirSim**: Script dùng `airsim.MultirotorClient()` để kết nối local. Nếu AirSim chạy trên máy khác, chỉnh IP trong script.
3. **Ngôn Ngữ**: Mặc định là `vi-VN`. Thay đổi trong `VoiceListener` nếu cần.

## Chạy Ứng Dụng
1. **Lưu Script**:
   - Sao chép mã nguồn vào file `voice_drone_control.py`.

2. **Khởi Động Unreal Engine**:
   - Mở dự án UE có AirSim, nhấn **Play**.

3. **Chạy Script**:
   - Mở Command Prompt, vào thư mục chứa script:
     ```
     cd path\to\script
     ```
   - Kích hoạt môi trường ảo (nếu dùng):
     ```
     .\drone_env\Scripts\activate
     ```
   - Chạy:
     ```
     python voice_drone_control.py
     ```

4. **Sử Dụng GUI**:
   - GUI mở toàn màn hình (nhấn `Esc` để thoát toàn màn hình).
   - Nhấn **BẮT ĐẦU** để nhận giọng nói.
   - Nói lệnh (xem bảng dưới).
   - **TẠM DỪNG** để dừng nhận giọng, **KẾT THÚC** để thoát.
   - **DỪNG KHẨN CẤP** để dừng drone ngay.

5. **Theo Dõi**:
   - GUI hiển thị lệnh và trạng thái.
   - Console UE4 (ấn `~`) hiển thị độ cao, tốc độ, khoảng cách.

## Lệnh Giọng Nói
Dưới đây là các lệnh hỗ trợ (có thể thêm số, ví dụ: "tiến thẳng 5" là 5 mét):

| Lệnh             | Hành Động            | Ví Dụ               |
|------------------|----------------------|---------------------|
| `cất cánh`       | Cất cánh             | "Cất cánh"          |
| `hạ cánh`        | Hạ cánh              | "Hạ cánh"           |
| `bay lên`        | Tăng độ cao          | "Bay lên 3"         |
| `hạ xuống`       | Giảm độ cao          | "Hạ xuống 2"        |
| `tiến thẳng`     | Di chuyển tới trước  | "Tiến thẳng 5"      |
| `lùi lại`        | Di chuyển lùi        | "Lùi lại 4"         |
| `bay sang trái`  | Di chuyển trái       | "Bay sang trái 3"   |
| `bay sang phải`  | Di chuyển phải       | "Bay sang phải 3"   |
| `quay trái`      | Quay trái (độ)       | "Quay trái 90"      |
| `quay phải`      | Quay phải (độ)       | "Quay phải 45"      |
| `dừng lại`       | Lơ lửng              | "Dừng lại"          |

## Khắc Phục Sự Cố
- **AirSim Không Kết Nối**:
  - Đảm bảo UE đang chạy và nhấn Play.
  - Kiểm tra drone trong môi trường (ấn `F5` để xem).
- **Không Nhận Giọng Nói**:
  - Kiểm tra micro và internet.
  - Giảm tiếng ồn xung quanh.
- **Lỗi eSpeak NG**:
  - Xác minh đường dẫn DLL trong script (`C:\Program Files\eSpeak NG\libespeak-ng.dll`).
- **Drone Không Di Chuyển**:
  - Kiểm tra console UE4 (ấn `~`) để xem lỗi.
  - Đảm bảo `client.armDisarm(True)` được gọi.

## Cách Hoạt Động
- **AirSim**: Điều khiển drone qua API Python.
- **Nhận Dạng Giọng**: Google Speech API chuyển giọng thành văn bản.
- **Phoneme**: eSpeak NG và Levenshtein khớp lệnh chính xác.
- **GUI**: Tkinter hiển thị thông tin và nút điều khiển.
- **An Toàn**: Kiểm tra cảm biến khoảng cách và trạng thái drone.

Chúc bạn thành công và vui vẻ với dự án! Nếu có thắc mắc, hãy thử lại các bước hoặc liên hệ người phát triển. 
