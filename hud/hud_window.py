import os
import sys
import math
import psutil
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame


class ArcReactorWidget(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(110, 110)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rotation_angle = 0
        self.pulse_phase = 0
        self.core_color = QColor(0, 240, 255)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._animate_frame)
        self.anim_timer.start(16)

    def set_theme_color(self, color: QColor):
        self.core_color = color

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def _animate_frame(self):
        self.rotation_angle = (self.rotation_angle + 1.2) % 360
        self.pulse_phase = (self.pulse_phase + 0.08) % (2 * math.pi)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        # 1. Outer Diffuse Energy Halo
        glow_intensity = int(140 + 70 * math.sin(self.pulse_phase))
        halo_color = QColor(self.core_color.red(), self.core_color.green(), self.core_color.blue(), int(glow_intensity * 0.25))
        painter.setBrush(QBrush(halo_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(cx - 50), int(cy - 50), 100, 100)

        # 2. Outer Containment Ring
        ring_pen = QPen(QColor(self.core_color.red(), self.core_color.green(), self.core_color.blue(), 120), 1.5)
        painter.setPen(ring_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(int(cx - 44), int(cy - 44), 88, 88)

        # 3. Rotating Induction Coils (8 segments)
        num_coils = 8
        coil_radius = 35
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.rotation_angle)

        coil_pen = QPen(QColor(self.core_color.red(), self.core_color.green(), self.core_color.blue(), 220), 3)
        painter.setPen(coil_pen)

        for i in range(num_coils):
            angle = i * (360 / num_coils)
            rad = math.radians(angle)
            x1 = coil_radius * math.cos(rad)
            y1 = coil_radius * math.sin(rad)
            x2 = (coil_radius + 6) * math.cos(rad)
            y2 = (coil_radius + 6) * math.sin(rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        painter.restore()

        # 4. Secondary Counter-Rotating Segment Ring
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-self.rotation_angle * 1.5)
        segment_pen = QPen(QColor(self.core_color.red(), self.core_color.green(), self.core_color.blue(), 180), 1.5, Qt.PenStyle.DashLine)
        painter.setPen(segment_pen)
        painter.drawEllipse(-26, -26, 52, 52)
        painter.restore()

        # 5. Inner Core Ring
        core_pen = QPen(QColor(self.core_color.red(), self.core_color.green(), self.core_color.blue(), 240), 2)
        painter.setPen(core_pen)
        painter.drawEllipse(int(cx - 16), int(cy - 16), 32, 32)

        # 6. Central High-Intensity Plasma Node
        core_alpha = int(180 + 75 * math.sin(self.pulse_phase))
        core_glow = QColor(220, 245, 255, core_alpha)
        painter.setBrush(QBrush(core_glow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(cx - 8), int(cy - 8), 16, 16)


class JarvisHUD(QWidget):
    reactor_triggered = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(440, 210)
        self.old_pos = QPoint()

        self._build_ui()
        self._load_css()
        self._start_telemetry_loop()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setObjectName("MainFrame")
        frame_layout = QHBoxLayout(self.frame)
        frame_layout.setContentsMargins(20, 16, 20, 16)

        info_layout = QVBoxLayout()

        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()

        self.title_lbl = QLabel("MARK-II")
        self.title_lbl.setObjectName("TitleLabel")
        self.sub_lbl = QLabel("AUTONOMOUS DESKTOP CORE")
        self.sub_lbl.setObjectName("SubtitleLabel")

        title_box.addWidget(self.title_lbl)
        title_box.addWidget(self.sub_lbl)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        self.state_badge = QLabel("SYSTEM IDLE")
        self.state_badge.setObjectName("StateBadge")
        header_layout.addWidget(self.state_badge)

        info_layout.addLayout(header_layout)
        info_layout.addSpacing(10)

        self.audio_lbl = QLabel('"Press Alt+Space to talk, Alt+V for vision"')
        self.audio_lbl.setObjectName("AudioPrompt")
        info_layout.addWidget(self.audio_lbl)

        info_layout.addSpacing(10)

        self.telemetry_lbl = QLabel("CPU: --%   RAM: --%   BAT: --%")
        self.telemetry_lbl.setObjectName("TelemetryLabel")
        info_layout.addWidget(self.telemetry_lbl)

        frame_layout.addLayout(info_layout, stretch=3)

        self.reactor = ArcReactorWidget()
        self.reactor.clicked.connect(self.reactor_triggered.emit)
        frame_layout.addWidget(self.reactor, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(self.frame)

    def _load_css(self):
        css_path = os.path.join(os.path.dirname(__file__), "style.css")
        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def _start_telemetry_loop(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_telemetry)
        self.timer.start(1500)
        self._refresh_telemetry()

    def _refresh_telemetry(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        bat = psutil.sensors_battery()
        bat_str = f"{bat.percent}%" if bat else "AC"
        self.telemetry_lbl.setText(f"CPU: {cpu}%   RAM: {ram}%   BAT: {bat_str}")

    def set_agent_state(self, state: str, prompt_text: str = None):
        self.state_badge.setText(state.upper())

        if "VISION" in state.upper():
            color = QColor(179, 136, 255)
            self.reactor.set_theme_color(color)
            self.state_badge.setStyleSheet(
                "color: #b388ff; border-color: #b388ff; background-color: rgba(179, 136, 255, 0.15);"
            )
        elif "LISTEN" in state.upper():
            color = QColor(0, 255, 136)
            self.reactor.set_theme_color(color)
            self.state_badge.setStyleSheet(
                "color: #00ff88; border-color: #00ff88; background-color: rgba(0, 255, 136, 0.1);"
            )
        elif "PROC" in state.upper() or "THINK" in state.upper():
            color = QColor(255, 170, 0)
            self.reactor.set_theme_color(color)
            self.state_badge.setStyleSheet(
                "color: #ffaa00; border-color: #ffaa00; background-color: rgba(255, 170, 0, 0.1);"
            )
        else:
            color = QColor(0, 240, 255)
            self.reactor.set_theme_color(color)
            self.state_badge.setStyleSheet(
                "color: #00f0ff; border-color: #00f0ff; background-color: rgba(0, 240, 255, 0.1);"
            )

        if prompt_text:
            self.audio_lbl.setText(f'"{prompt_text}"')

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if not self.old_pos.isNull():
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = QPoint()