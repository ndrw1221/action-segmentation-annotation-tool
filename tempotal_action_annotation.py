import sys
import os
import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSlider,
    QLineEdit,
    QDialog,
    QListWidget,
    QGroupBox,
    QMenu,
    QAction,
)


class VideoPlayerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_frame = 0
        self.is_playing = False
        self.frames = []
        self.fps = 30
        self.actions = {}
        self.video_name = ""

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Temporal action annotatation tool")
        self.setGeometry(450, 200, 1000, 700)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        font_14 = QFont()
        font_14.setPointSize(14)

        self.video = QLabel(self)
        self.action = QListWidget()
        self.action.itemSelectionChanged.connect(self.update_button_state)

        self.delete_action_button = QPushButton("Delete", self)
        self.delete_action_button.setEnabled(False)
        self.delete_action_button.clicked.connect(self.delete_action)

        self.slider = QSlider(1, self)
        self.slider.valueChanged.connect(self.onSliderChange)

        self.load_button = QPushButton("Load Video", self)
        self.load_button.clicked.connect(self.loadVideo)

        self.play_button = QPushButton("Play", self)
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.playVideo)

        self.forward_button = QPushButton("Forward", self)
        self.forward_button.setEnabled(False)
        self.forward_button.clicked.connect(self.forwardFrame)

        self.backward_button = QPushButton("Backward", self)
        self.backward_button.setEnabled(False)
        self.backward_button.clicked.connect(self.backwardFrame)

        self.frame_label = QLabel("Frame: 0", self)

        self.add_action_button = QPushButton("Add Action", self)
        # self.add_action_button.setEnabled(False)
        self.add_action_button.clicked.connect(self.addTemporalAction)

        self.action_start_button = QPushButton("Action Start", self)
        self.action_start_button.setEnabled(False)
        self.action_start_button.clicked.connect(self.temporalActionStart)

        self.action_end_button = QPushButton("Action End", self)
        self.action_end_button.setEnabled(False)
        self.action_end_button.clicked.connect(self.temporalActionEnd)

        self.output_annotation_button = QPushButton("Output Annotation", self)
        self.output_annotation_button.setEnabled(False)
        self.output_annotation_button.clicked.connect(self.outputAnnotation)

        group_box = QGroupBox("Actions")
        group_box.setFont(font_14)

        group_box_layout = QVBoxLayout()
        group_box_layout.addWidget(self.action)
        group_box_layout.addWidget(self.delete_action_button)
        group_box.setLayout(group_box_layout)

        self.hbox_vid = QHBoxLayout()
        self.hbox_vid.addStretch(1)
        self.hbox_vid.addWidget(self.video)
        self.hbox_vid.addStretch(1)
        self.hbox_vid.addWidget(group_box)
        self.hbox_vid.addStretch(1)

        self.hbox_1 = QHBoxLayout()
        self.hbox_1.addWidget(self.load_button)
        self.hbox_1.addWidget(self.play_button)
        self.hbox_1.addWidget(self.backward_button)
        self.hbox_1.addWidget(self.forward_button)

        self.hbox_2 = QHBoxLayout()
        self.hbox_2.addWidget(self.add_action_button)
        self.hbox_2.addWidget(self.action_start_button)
        self.hbox_2.addWidget(self.action_end_button)
        self.hbox_2.addWidget(self.output_annotation_button)

        self.vbox = QVBoxLayout()
        self.vbox.addStretch(1)
        self.vbox.addLayout(self.hbox_vid)
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.frame_label)
        self.vbox.addWidget(self.slider)
        self.vbox.addLayout(self.hbox_1)
        self.vbox.addLayout(self.hbox_2)

        central_widget.setLayout(self.vbox)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)

    def update_button_state(self, mode=None):
        if mode == "init":
            self.play_button.setEnabled(True)
            self.forward_button.setEnabled(True)
            self.backward_button.setEnabled(True)
            self.add_action_button.setEnabled(True)
            self.slider.setRange(0, len(self.frames))
            self.slider.setValue(0)

        item_selected = self.action.selectedItems()
        if item_selected:
            self.action_start_button.setEnabled(True)
            self.action_end_button.setEnabled(True)
            self.delete_action_button.setEnabled(True)

    def loadVideo(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.flv);;All Files (*)",
            options=options,
        )

        if file_path:
            video_capture = cv2.VideoCapture(file_path)
            self.frames = []
            self.video_name = os.path.basename(file_path)

            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break
                self.frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            frame = self.frames[0]
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(
                frame.data, width, height, bytes_per_line, QImage.Format_RGB888
            )
            pixmap = QPixmap.fromImage(q_img)
            self.video.setPixmap(pixmap)

            self.update_button_state("init")

    def playVideo(self):
        if self.current_frame == len(self.frames) - 1:
            self.current_frame = 0

        if not self.is_playing:
            self.is_playing = True
            self.timer.start(round(1000 / self.fps))
            self.play_button.setText("Pause")

        else:
            self.stopVideo()

    def stopVideo(self):
        if self.is_playing:
            self.is_playing = False
            self.timer.stop()
            self.play_button.setText("Play")

    def forwardFrame(self):
        if not self.is_playing:
            self.current_frame += 1
            if self.current_frame > len(self.frames) - 1:
                self.current_frame = len(self.frames) - 1
            self.updateFrame()

    def backwardFrame(self):
        if not self.is_playing:
            self.current_frame -= 1
            if self.current_frame < 0:
                self.current_frame = 0
            self.updateFrame()

    def onSliderChange(self):
        if not self.is_playing:
            self.current_frame = self.slider.value()
            self.updateFrame()

            if self.slider.value() < len(self.frames) - 1:
                self.play_button.setText("Play")

    def updateFrame(self):
        if not self.current_frame < len(self.frames) - 1:
            self.stopVideo()
            self.play_button.setText("Restart")

        else:
            if self.is_playing:
                self.current_frame += 1

            frame = self.frames[self.current_frame]
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(
                frame.data, width, height, bytes_per_line, QImage.Format_RGB888
            )
            pixmap = QPixmap.fromImage(q_img)
            self.video.setPixmap(pixmap)
            self.frame_label.setText(f"Frame: {self.current_frame}")
            self.slider.setValue(self.current_frame)

    def addTemporalAction(self):
        dialog = ActionNameInputDialog()
        result = dialog.exec_()

        if result == QDialog.Accepted:
            action_name = dialog.action_input.text()
            if action_name:
                print(f"Added action {action_name}")
                self.actions[action_name] = [None, None]
                self.action.addItem(action_name)
                self.output_annotation_button.setEnabled(True)

    def temporalActionStart(self):
        action = self.action.currentItem().text()
        if action:
            self.actions[action][0] = self.current_frame
            print(self.actions)

    def temporalActionEnd(self):
        action = self.action.currentItem().text()
        if action:
            self.actions[action][1] = self.current_frame
            print(self.actions)

    def outputAnnotation(self):
        file_name, file_extension = os.path.splitext(self.video_name)
        print(file_name)

        with open(f"./{self.video_name}.txt", "w") as file:
            for action in self.actions:
                file.write(f"{action} \n")

        print("f{self.video_name}.txt created successfully.")

    def delete_action(self):
        selected_action = self.action.currentItem()
        row = self.action.row(selected_action)
        self.action.takeItem(row)


class ActionNameInputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(" ")

        font = QFont()
        font.setPointSize(16)

        self.action_input = QLineEdit()
        self.action_input.setPlaceholderText("Enter action name")
        self.action_input.setFont(font)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)

        Vlayout = QVBoxLayout()
        Vlayout.addWidget(self.action_input)
        Vlayout.addWidget(ok_button)

        self.setLayout(Vlayout)


def main():
    app = QApplication(sys.argv)
    window = VideoPlayerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
