import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox, QFileDialog, QCheckBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt
import folium
import io

# メインウィンドウの設定
class CarNavigationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cool Car Navi")
        self.setGeometry(100, 100, 1200, 800)

        # メインレイアウト
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # サイドメニューの作成
        self.create_side_menu()

        # Webビュー（Leaflet地図を表示）
        self.map_view = QWebEngineView()
        self.load_map()
        self.main_layout.addWidget(self.map_view)

    def create_side_menu(self):
        self.side_menu = QWidget()
        self.side_menu_layout = QVBoxLayout(self.side_menu)

        # 経路切り替えドロップダウンリスト
        self.route_select_label = QLabel("Select Route")
        self.route_select_combo = QComboBox()
        self.route_select_combo.addItems(["Route 1", "Route 2", "Route 3"])
        self.route_select_combo.currentIndexChanged.connect(self.change_route)

        # ファイル読み込みボタン
        self.load_file_btn = QPushButton("Load Route File")
        self.load_file_btn.clicked.connect(self.load_route_file)

        # 開発者モードチェックボックス
        self.dev_mode_checkbox = QCheckBox("Developer Mode")
        self.dev_mode_checkbox.stateChanged.connect(self.toggle_dev_mode)

        # サイドメニューのレイアウトに要素を追加
        self.side_menu_layout.addWidget(self.route_select_label)
        self.side_menu_layout.addWidget(self.route_select_combo)
        self.side_menu_layout.addWidget(self.load_file_btn)
        self.side_menu_layout.addStretch()
        self.side_menu_layout.addWidget(self.dev_mode_checkbox)

        # サイドメニューをメインレイアウトに追加
        self.main_layout.addWidget(self.side_menu)

    def load_map(self):
        # folium 地図の作成と読み込み
        m = folium.Map(location=[35.170915, 136.881537], zoom_start=12)  # 名古屋駅付近を初期位置に設定
        data = io.BytesIO()
        m.save(data, close_file=False)

        # QWebEngineView に地図を表示
        self.map_view.setHtml(data.getvalue().decode())

    def change_route(self, index):
        # 経路変更のロジック（仮）
        print(f"Route changed to: {self.route_select_combo.currentText()}")

    def load_route_file(self):
        # ファイル選択ダイアログを表示し、選択されたファイルを読み込む
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Route File", "", "GPX Files (*.gpx);;JSON Files (*.json)")
        if file_name:
            print(f"Loaded route file: {file_name}")
            # ファイル読み込みと経路表示の実装はここに追加

    def toggle_dev_mode(self, state):
        # 開発者モードのトグル切り替え
        if state == Qt.Checked:
            print("Developer Mode Enabled")
        else:
            print("Developer Mode Disabled")

    def get_device_location(self, gps_inputmode=""):
        if gps_inputmode == "external":
            return self.get_external_gps()  # 外部デバイスから取得（未実装）
        elif gps_inputmode == "ocr":
            return self.get_ocr_coordinates()  # 画面OCRから取得（未実装）
        else:
            return [35.6804, 139.7690]  # デフォルト位置


# アプリケーションの開始
app = QApplication(sys.argv)
window = CarNavigationApp()
window.show()
sys.exit(app.exec())
