import sys
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QTableWidget,
                             QTableWidgetItem, QLabel, QHeaderView, QMessageBox,
                             QProgressDialog, QAbstractItemView, QStyle)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QIcon
import ctypes
from ultralytics import YOLO

# --- CONFIGURATION ---
CLASSES = ["Indihome", "Indosat", "MyRepublic", "Lintasarta", "CBN"]
MODEL_PATH = "best.pt"

# --- CONFIGURATION PETA BPS ---
MAP_FILE_PATH = "map/Batas_Wilayah_KelurahanDesa_10K_AR.shp"
KECAMATAN_COLUMN = "WADMKC"

# --- TASKBAR ICON ---
myappid = 'provider.detection'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


# --- WORKER THREAD ---
class InferenceWorker(QThread):
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self, model_path, image_paths, start_id, gdf_map):
        super().__init__()
        self.model_path = model_path
        self.image_paths = image_paths
        self.start_id = start_id
        self.gdf_map = gdf_map
        self.is_running = True

    def get_geotagging(self, exif):
        if not exif: return None, None
        geotagging = {}
        for (idx, tag) in TAGS.items():
            if tag == 'GPSInfo':
                if idx not in exif: return None, None
                for (key, val) in GPSTAGS.items():
                    if key in exif[idx]:
                        geotagging[val] = exif[idx][key]
        return geotagging

    def get_decimal_from_dms(self, dms, ref):
        degrees = dms[0]
        minutes = dms[1]
        seconds = dms[2]
        result = degrees + minutes / 60.0 + seconds / 3600.0
        if ref in ['S', 'W']:
            result = -result
        return result

    def get_coordinates(self, file_path):
        try:
            image = Image.open(file_path)
            exif = image._getexif()
            geotags = self.get_geotagging(exif) if exif else None

            if geotags and 'GPSLatitude' in geotags and 'GPSLongitude' in geotags:
                lat = self.get_decimal_from_dms(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])
                lon = self.get_decimal_from_dms(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])
                return round(lon, 6), round(lat, 6)
        except Exception:
            pass
        return 0.0, 0.0

    def get_kecamatan(self, lon, lat):
        if self.gdf_map is None or lon == 0.0: return "Unknown"

        try:
            point = Point(lon, lat)
            matching_area = self.gdf_map[self.gdf_map.contains(point)]

            if not matching_area.empty:
                return matching_area.iloc[0][KECAMATAN_COLUMN]
            else:
                return "Outside Area"
        except Exception:
            return "Error"

    def run(self):
        results_data = []
        try:
            model = YOLO(self.model_path)

            for i, img_path in enumerate(self.image_paths):
                if not self.is_running: break

                filename = os.path.basename(img_path)
                self.progress_signal.emit(i + 1, f"Processing: {filename}")

                results = model(img_path, verbose=False)[0]
                detected_indices = results.boxes.cls.cpu().numpy().astype(int)
                detected_names_lower = [results.names[i].lower() for i in detected_indices]

                lon, lat = self.get_coordinates(img_path)

                # --- LOGIKA KECAMATAN ---
                subdistrict = self.get_kecamatan(lon, lat)

                res_plotted = results.plot()
                current_id = self.start_id + i

                row_data = {
                    "id": current_id,
                    "path": img_path,
                    "name": filename,
                    "lon": lon,
                    "lat": lat,
                    "subdistrict": subdistrict,
                    "result_img": res_plotted
                }

                for cls in CLASSES:
                    row_data[cls] = cls.lower() in detected_names_lower

                results_data.append(row_data)

            self.finished_signal.emit(results_data)

        except Exception as e:
            self.error_signal.emit(str(e))

    def stop(self):
        self.is_running = False


# MAIN APP
class ProviderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Provider Detection Tool")
        self.resize(1300, 800)

        if os.path.exists("logo.ico"):
            self.setWindowIcon(QIcon("logo.ico"))

        self.df_data = []
        self.current_batch_paths = []

        #LOAD PETA BPS
        self.gdf_map = None
        try:
            if os.path.exists(MAP_FILE_PATH):
                self.gdf_map = gpd.read_file(MAP_FILE_PATH)
                if self.gdf_map.crs != "EPSG:4326":
                    self.gdf_map = self.gdf_map.to_crs("EPSG:4326")
            else:
                print(f"Warning: Map file {MAP_FILE_PATH} not found. Subdistrict feature disabled.")
        except Exception as e:
            print(f"Error loading map: {e}")

        # UI Setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top Bar
        btn_layout = QHBoxLayout()
        self.btn_load = QPushButton("1. Load New Images")
        self.btn_load.clicked.connect(self.load_images)
        self.btn_run = QPushButton("2. Run Inference")
        self.btn_run.clicked.connect(self.run_inference)
        self.btn_run.setEnabled(False)
        self.btn_export = QPushButton("3. Export CSV")
        self.btn_export.clicked.connect(self.export_csv)
        self.btn_export.setEnabled(False)
        self.btn_open = QPushButton("Open Full Image")
        self.btn_open.clicked.connect(self.open_full_image)
        self.btn_delete = QPushButton()
        self.btn_delete.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        self.btn_delete.setToolTip("Delete Selected Row")
        self.btn_delete.setFixedSize(30, 20)
        self.btn_delete.clicked.connect(self.delete_selected_rows)
        self.btn_delete.setStyleSheet("background-color: #ffcccc; border: 1px solid #ffcccc; border-radius: 4px;")
        # self.btn_delete.clicked.connect(self.delete_selected_rows)
        # self.btn_delete.setStyleSheet("background-color: #ffcccc; color: red;")

        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_delete)
        main_layout.addLayout(btn_layout)

        # Image Area
        img_layout = QHBoxLayout()
        self.lbl_orig = QLabel("Original Image")
        self.lbl_orig.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_orig.setStyleSheet("border: 1px solid gray; background: #000; color: white;")
        self.lbl_orig.setFixedSize(600, 500)
        self.lbl_orig.setScaledContents(False)
        self.lbl_pred = QLabel("Inference Result")
        self.lbl_pred.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_pred.setStyleSheet("border: 1px solid gray; background: #000; color: white;")
        self.lbl_pred.setFixedSize(600, 500)
        self.lbl_pred.setScaledContents(False)
        img_layout.addWidget(self.lbl_orig)
        img_layout.addWidget(self.lbl_pred)
        main_layout.addLayout(img_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5 + len(CLASSES))
        self.table.setHorizontalHeaderLabels(["ID", "Image Name", "Longitude", "Latitude", "Subdistrict"] + CLASSES)
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellClicked.connect(self.display_image)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 50)
        main_layout.addWidget(self.table)

    def load_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg)")
        if files:
            self.current_batch_paths = files
            self.btn_run.setEnabled(True)
            self.btn_run.setText(f"2. Run Inference ({len(files)} new images)")
            QMessageBox.information(self, "Info", f"Loaded {len(files)} new images.")

    def run_inference(self):
        if not self.current_batch_paths: return

        if self.gdf_map is None:
            QMessageBox.warning(self, "Map Warning", "File BPS not found. Subdistrict will be 'Unknown'.")

        start_id = len(self.df_data)

        self.progress = QProgressDialog("Initializing...", "Cancel", 0, len(self.current_batch_paths), self)
        self.progress.setWindowTitle("Processing Batch")
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.setMinimumDuration(0)
        self.progress.setValue(0)

        # Pass self.gdf_map ke Worker
        self.worker = InferenceWorker(MODEL_PATH, self.current_batch_paths, start_id, self.gdf_map)

        self.worker.progress_signal.connect(self.update_progress_ui)
        self.worker.finished_signal.connect(self.on_inference_complete)
        self.worker.error_signal.connect(self.on_inference_error)
        self.progress.canceled.connect(self.worker.stop)

        self.worker.start()

    def update_progress_ui(self, val, msg):
        self.progress.setValue(val)
        self.progress.setLabelText(msg)

    def on_inference_complete(self, new_data):
        self.df_data.extend(new_data)
        self.current_batch_paths = []
        self.btn_run.setEnabled(False)
        self.btn_run.setText("2. Run Inference")
        self.populate_table()
        self.progress.setValue(self.progress.maximum())
        self.btn_export.setEnabled(True)
        QMessageBox.information(self, "Success", f"Added {len(new_data)} items.")

    def on_inference_error(self, err_msg):
        self.progress.cancel()
        QMessageBox.critical(self, "Error", f"Inference Failed:\n{err_msg}")

    def populate_table(self):
        self.table.setRowCount(len(self.df_data))
        for row, data in enumerate(self.df_data):
            self.table.setItem(row, 0, QTableWidgetItem(str(data['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(data['name']))
            self.table.setItem(row, 2, QTableWidgetItem(str(data['lon'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(data['lat'])))
            self.table.setItem(row, 4, QTableWidgetItem(str(data['subdistrict'])))

            for col_idx, cls in enumerate(CLASSES):
                item = QTableWidgetItem()
                item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                state = Qt.CheckState.Checked if data[cls] else Qt.CheckState.Unchecked
                item.setCheckState(state)
                item.setData(Qt.ItemDataRole.UserRole, data['id'])
                self.table.setItem(row, 5 + col_idx, item)

    def delete_selected_rows(self):
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)
        if not selected_rows: return

        confirm = QMessageBox.question(self, "Confirm Delete",
                                       f"Are you sure you want to delete {len(selected_rows)} rows?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            ids_to_delete = []
            for row in selected_rows:
                id_item = self.table.item(row, 0)
                if id_item: ids_to_delete.append(int(id_item.text()))

            self.df_data = [d for d in self.df_data if d['id'] not in ids_to_delete]

            for new_id, data in enumerate(self.df_data):
                data['id'] = new_id

            self.populate_table()
            if not self.df_data: self.btn_export.setEnabled(False)

    def display_image(self, row, col):
        if row >= len(self.df_data): return
        data = self.df_data[row]
        try:
            pix_orig = QPixmap(data['path'])
            pix_orig_scaled = pix_orig.scaled(self.lbl_orig.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
            self.lbl_orig.setPixmap(pix_orig_scaled)
            img_res = data['result_img']
            height, width, channel = img_res.shape
            bytes_per_line = 3 * width
            q_img = QImage(img_res.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
            pix_res = QPixmap.fromImage(q_img)
            pix_res_scaled = pix_res.scaled(self.lbl_pred.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
            self.lbl_pred.setPixmap(pix_res_scaled)
        except Exception:
            pass

    def open_full_image(self):
        current_row = self.table.currentRow()
        if current_row < 0: return
        if current_row < len(self.df_data):
            img_path = self.df_data[current_row]['path']
            if platform.system() == 'Windows':
                os.startfile(img_path)
            elif platform.system() == 'Darwin':
                subprocess.call(('open', img_path))
            else:
                subprocess.call(('xdg-open', img_path))

    def export_csv(self):
        export_data = []
        for row in range(self.table.rowCount()):
            row_dict = {
                "id": self.table.item(row, 0).text(),
                "image_name": self.table.item(row, 1).text(),
                "longitude": self.table.item(row, 2).text(),
                "latitude": self.table.item(row, 3).text(),
                "subdistrict": self.table.item(row, 4).text(),
            }
            for col_idx, cls in enumerate(CLASSES):
                # Geser index + 5
                item = self.table.item(row, 5 + col_idx)
                is_checked = item.checkState() == Qt.CheckState.Checked
                row_dict[cls] = is_checked
            export_data.append(row_dict)

        df = pd.DataFrame(export_data)
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "detection_results_kecamatan.csv", "CSV (*.csv)")
        if path:
            df.to_csv(path, index=False)
            QMessageBox.information(self, "Success", "Data exported successfully!")


# --- ENTRY POINT ---
import platform
import subprocess

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProviderApp()
    # app.setStyleSheet("""
    #     QMainWindow { background-color: #2b2b2b; }
    #     QLabel { color: #ffffff; font-size: 14px; }
    #     QPushButton {
    #         background-color: #0d6efd;
    #         color: white;
    #         border-radius: 5px;
    #         padding: 8px;
    #         font-weight: bold;
    #     }
    #     QPushButton:hover { background-color: #0b5ed7; }
    #     QPushButton:disabled { background-color: #555; color: #aaa; }
    #     QTableWidget {
    #         background-color: #333;
    #         color: white;
    #         gridline-color: #555;
    #     }
    #     QHeaderView::section {
    #         background-color: #444;
    #         color: white;
    #         padding: 5px;
    #     }
    # """)
    window.show()
    sys.exit(app.exec())