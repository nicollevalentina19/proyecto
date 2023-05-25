import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.uic import loadUi


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('ventanaprincipal.ui', self)

        self.botoninicio.clicked.connect(self.mostrar_ventana_secundaria)
        self.ventana_secundaria = None
        self.botoninicio.setGeometry(350, 550, 200, 60)
        self.label_2.setStyleSheet("font: 12pt \"Arial Rounded MT Bold\";")
        self.label_2.setGeometry(180, 500, 1000, 25)
        self.label_2.setText("DETECCIÓN DE MEDICAMENTOS POR COLORES")
        self.label.setGeometry(340, 150, 300, 300)

    def mostrar_ventana_secundaria(self):
        if self.ventana_secundaria is None:
            self.ventana_secundaria = VentanaSecundaria()
            self.ventana_secundaria.mostrarImagenSignal.connect(self.mostrar_imagen_ventana_secundaria)
            self.ventana_secundaria.closed.connect(self.cerrar_programa)
        self.ventana_secundaria.show()
        self.hide()

    def mostrar_imagen_ventana_secundaria(self, pixmap):
        self.ventana_secundaria.mostrar_imagen(pixmap)

    def mostrar_imagen(self, pixmap):
        self.label.setPixmap(pixmap)

    def cerrar_programa(self):
        self.close()

    def closeEvent(self, event):
        if self.ventana_secundaria is not None:
            self.ventana_secundaria.detener_camara()
            self.ventana_secundaria.close()
        event.accept()


class VentanaSecundaria(QMainWindow):
    mostrarImagenSignal = pyqtSignal(QPixmap)
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        loadUi('segunda.ui', self)

        self.label_4.setGeometry(650, 10, 300, 50)
        self.usarcamara.clicked.connect(self.abrir_camara)
        self.video_capture = None
        self.subirimagen.clicked.connect(self.subir_imagen)
        self.visualizador.setAlignment(Qt.AlignCenter)
        self.amoxicilina.clicked.connect(self.detectar_amoxicilina)
        self.buscapina.clicked.connect(self.detectar_buscapina_fem)
        self.image_path = None

    def abrir_camara(self):
        self.detener_camara()  # Detener la cámara si ya se estaba utilizando
        self.video_capture = cv2.VideoCapture(0)
        self.showing_camera = True

        while self.showing_camera and self.video_capture.isOpened():
            ret, frame = self.video_capture.read()

            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = QImage(
                    frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888
                )

                image = image.scaled(self.visualizador.width(), self.visualizador.height(), Qt.KeepAspectRatio)

                pixmap = QPixmap.fromImage(image)

                self.visualizador.setPixmap(pixmap)
                self.visualizador.repaint()

                QApplication.processEvents()
            else:
                break

        self.video_capture.release()

    def detener_camara(self):
        self.showing_camera = False
        if self.video_capture is not None and self.video_capture.isOpened():
            self.video_capture.release()

    def subir_imagen(self):
        self.detener_camara()  # Detener la cámara si se estaba utilizando
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Seleccionar Imagen", "", "Archivos de Imagen (*.png *.jpg)")
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            self.mostrarImagenSignal.emit(pixmap)

    def mostrar_imagen(self, pixmap):
        self.visualizador.setPixmap(pixmap.scaled(self.visualizador.size(), aspectRatioMode=Qt.KeepAspectRatio))


    def detectar_amoxicilina(self):
        if self.image_path is not None:
            image = cv2.imread(self.image_path)
            color_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Detectar los colores azul y amarillo
            lower_blue = np.array([100, 100, 0])
            upper_blue = np.array([255, 255, 100])
            lower_yellow = np.array([0, 100, 100])
            upper_yellow = np.array([100, 255, 255])

            blue_mask = cv2.inRange(color_image, lower_blue, upper_blue)
            yellow_mask = cv2.inRange(color_image, lower_yellow, upper_yellow)

            # Encontrar los contornos de los objetos detectados
            contours, _ = cv2.findContours(blue_mask + yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Dibujar rectángulos alrededor de los contornos detectados
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Mostrar imagen con rectángulos
            cv2.imshow("Imagen con rectángulos", color_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            # Mostrar mensaje si se detecta el color amarillo y azul simultáneamente
            if np.any(blue_mask) and np.any(yellow_mask):
                QMessageBox.information(self, "Amoxicilina detectada", "Se ha detectado Amoxicilina.")

    def detectar_buscapina_fem(self):
        if self.image_path is None:
            QMessageBox.warning(self, "Error", "No se ha seleccionado ninguna imagen.")
            return
        image2 = cv2.imread(self.image_path)
        color_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)

        # Cargar la imagen
        original_image = cv2.imread(self.image_path)

        # Convertir la imagen a espacio de color HSV
        hsv_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)

        # Definir los rangos de color para el rosa claro
        lower_pink = np.array([140, 50, 50])
        upper_pink = np.array([180, 255, 255])

        # Aplicar una máscara para obtener solo los píxeles en el rango de color deseado
        mask = cv2.inRange(hsv_image, lower_pink, upper_pink)

        # Encontrar los contornos de los objetos detectados
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Encerrar los objetos detectados en rectángulos
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(color_image2, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Imagen con rectángulos", color_image2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def closeEvent(self, event):
        self.detener_camara()
        self.closed.emit()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana_principal = VentanaPrincipal()
    ventana_principal.show()
    sys.exit(app.exec_())
