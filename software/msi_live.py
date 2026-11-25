import argparse
import datetime
import os
import socket
import struct
import threading
import time

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

FS = 2000                              
HEADER = struct.Struct("<2sBBI")       
ENV_WINDOW = int(0.1 * FS)             


TONE_HZ = 100.0                        


def tone_rms(x, f0=TONE_HZ, search=3.0):
    """RMS of the sine component near f0 (searches f0 +/- search Hz), via a Hann-windowed FFT.

    Unlike plain RMS, this ignores broadband noise, so it can measure tiny tone
    residuals (e.g. the common-mode output in a CMRR test) far below the noise floor.
    """
    n = len(x)
    if n < FS // 2:
        return 0.0
    w = np.hanning(n)
    nfft = 1 << int(np.ceil(np.log2(4 * n)))          
    spec = np.abs(np.fft.rfft((x - x.mean()) * w, nfft))
    freqs = np.fft.rfftfreq(nfft, 1.0 / FS)
    band = (freqs > f0 - search) & (freqs < f0 + search)
    peak = spec[band].max()
    amp = 2.0 * peak / w.sum()                         
    return float(amp / np.sqrt(2.0))


class Receiver(threading.Thread):
    """Background thread: receives UDP packets and queues the samples."""

    def __init__(self, port):
        super().__init__(daemon=True)
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", port))
        self.sock.settimeout(0.5)
        self.lock = threading.Lock()
        self.pending = []
        self.esp_ip = None
        self.last_seq = None
        self.packets = 0
        self.lost = 0
        self.last_hello = 0.0

    def run(self):
        while True:

            now = time.time()
            if self.esp_ip and now - self.last_hello > 2.0:
                try:
                    self.sock.sendto(b"hi", (self.esp_ip, self.port))
                except OSError:
                    pass
                self.last_hello = now
            try:
                data, addr = self.sock.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:            
                continue
            if len(data) < HEADER.size:
                continue
            magic, nch, count, seq = HEADER.unpack_from(data, 0)
            n = nch * count
            if magic != b"EM" or nch == 0 or len(data) < HEADER.size + 2 * n:
                continue
            samples = np.frombuffer(data, dtype="<i2", count=n, offset=HEADER.size)
            samples = samples.astype(np.float32).reshape(count, nch) / 10.0   # back to mV
            if addr[0] != self.esp_ip:
                self.esp_ip = addr[0]
                self.last_hello = 0.0
            with self.lock:
                if self.last_seq is not None:
                    gap = (seq - self.last_seq - 1) & 0xFFFFFFFF
                    if gap < 10000:    
                        self.lost += gap
                self.last_seq = seq
                self.packets += 1
                self.pending.append(samples)

    def drain(self):
        with self.lock:
            chunks, self.pending = self.pending, []
        return chunks


class Window(QtWidgets.QWidget):
    def __init__(self, rx, window_s):
        super().__init__()
        self.rx = rx
        self.N = int(window_s * FS)
        self.t = np.arange(-self.N, 0) / FS
        self.buf = None
        self.curves, self.env_curves = [], []
        self.rec_file, self.rec_name, self.sample_idx = None, "", 0
        self.rate, self.rate_count, self.rate_t = 0.0, 0, time.time()

        self.setWindowTitle("MSI live EMG")
        self.resize(1100, 700)
        layout = QtWidgets.QVBoxLayout(self)
        top = QtWidgets.QHBoxLayout()
        self.status = QtWidgets.QLabel(f"Waiting for ESP32 data on UDP port {rx.port}...")
        self.rec_btn = QtWidgets.QPushButton("Start recording")
        self.rec_btn.clicked.connect(self.toggle_rec)
        top.addWidget(self.status, 1)
        top.addWidget(self.rec_btn)
        layout.addLayout(top)


        self.filled = 0                
        self.meas_t = 0.0
        self.last_meas = []
        meas = QtWidgets.QHBoxLayout()
        self.meas_label = QtWidgets.QLabel("Measure: waiting for data...")
        f = self.meas_label.font()
        f.setPointSize(f.pointSize() + 3)
        f.setBold(True)
        self.meas_label.setFont(f)
        self.log_name = QtWidgets.QLineEdit()
        self.log_name.setPlaceholderText("label, e.g. AD623 gain a50=1.005V")
        self.log_name.setFixedWidth(300)
        self.log_btn = QtWidgets.QPushButton("Log reading")
        self.log_btn.clicked.connect(self.log_reading)
        meas.addWidget(self.meas_label, 1)
        meas.addWidget(self.log_name)
        meas.addWidget(self.log_btn)
        layout.addLayout(meas)

        self.glw = pg.GraphicsLayoutWidget()
        layout.addWidget(self.glw)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(33)           

    def setup_plots(self, nch):
        self.glw.clear()
        self.curves, self.env_curves = [], []
        self.buf = np.zeros((self.N, nch), dtype=np.float32)
        for i in range(nch):
            p = self.glw.addPlot(row=i, col=0, title=f"Channel {i + 1}")
            p.setLabel("left", "mV")
            p.setLabel("bottom", "time", "s")
            p.setYRange(-1700, 1700)
            p.showGrid(x=True, y=True, alpha=0.3)
            p.setDownsampling(auto=True, mode="peak")
            p.setClipToView(True)
            p.addLegend()
            self.curves.append(p.plot(pen=pg.mkPen((60, 130, 220), width=1), name="filtered"))
            self.env_curves.append(p.plot(pen=pg.mkPen((230, 120, 30), width=2),
                                          name="envelope (RMS 100 ms)"))

    def update_plot(self):
        chunks = self.rx.drain()
        if chunks:
            data = np.concatenate(chunks, axis=0)
            if self.buf is None or self.buf.shape[1] != data.shape[1]:
                self.setup_plots(data.shape[1])
            m = len(data)
            if m >= self.N:
                self.buf[:] = data[-self.N:]
            else:
                self.buf[:-m] = self.buf[m:]
                self.buf[-m:] = data
            if self.rec_file:
                idx = np.arange(self.sample_idx, self.sample_idx + m)
                np.savetxt(self.rec_file, np.column_stack([idx, data]), delimiter=",",
                           fmt=["%d"] + ["%.1f"] * data.shape[1])
            self.sample_idx += m
            self.rate_count += m
            self.filled = min(self.N, self.filled + m)

        if self.buf is not None:
            k = np.ones(ENV_WINDOW, dtype=np.float32) / ENV_WINDOW
            for i, (c, e) in enumerate(zip(self.curves, self.env_curves)):
                x = self.buf[:, i]
                c.setData(self.t, x)
                e.setData(self.t, np.sqrt(np.convolve(x * x, k, mode="same")))

        now = time.time()
        if self.buf is not None and self.filled >= FS and now - self.meas_t >= 0.5:
            self.meas_t = now
            self.update_measure()
        if now - self.rate_t >= 1.0:
            self.rate = self.rate_count / (now - self.rate_t)
            self.rate_count, self.rate_t = 0, now
        if self.rx.esp_ip:
            total = self.rx.packets + self.rx.lost
            loss = 100.0 * self.rx.lost / total if total else 0.0
            nch = self.buf.shape[1] if self.buf is not None else 0
            rec = f"   |   RECORDING to {self.rec_name}" if self.rec_file else ""
            self.status.setText(
                f"ESP32 {self.rx.esp_ip}   |   {nch} channel(s)   |   "
                f"{self.rate:.0f} samples/s   |   packets lost: {self.rx.lost} ({loss:.1f}%){rec}")

    def update_measure(self):
        """RMS over the last 1 s and over the whole window, plus peak-to-peak (1 s)."""
        parts, self.last_meas = [], []
        for i in range(self.buf.shape[1]):
            x1 = self.buf[-FS:, i]
            xw = self.buf[-self.filled:, i]
            rms1 = float(np.sqrt(np.mean(x1 * x1)))
            rmsw = float(np.sqrt(np.mean(xw * xw)))
            pp = float(x1.max() - x1.min())
            tone = tone_rms(xw)
            self.last_meas.append((rms1, rmsw, pp, tone))
            parts.append(f"Ch{i + 1}: RMS 1 s = {rms1:.1f} mV   "
                         f"RMS {self.filled / FS:.0f} s = {rmsw:.1f} mV   p-p = {pp:.0f} mV   "
                         f"100 Hz tone = {tone:.3f} mV")
        self.meas_label.setText("     |     ".join(parts))

    def log_reading(self):
        """Append the current readings to measurements.csv with the typed label."""
        if not self.last_meas:
            return
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        label = self.log_name.text().replace(",", ";").strip() or "(no label)"
        rows = [f"{stamp},{label},{i + 1},{rms1:.2f},{rmsw:.2f},{self.filled / FS:.1f},{pp:.1f},{tone:.4f}"
                for i, (rms1, rmsw, pp, tone) in enumerate(self.last_meas)]

        for r in rows:
            print("LOG:", r)

        here = os.path.dirname(os.path.abspath(__file__))
        saved = None
        for name in ("measurements_v3.csv", "measurements_v3_backup.csv"):
            path = os.path.join(here, name)
            try:
                new = not os.path.exists(path)
                with open(path, "a") as fh:
                    if new:
                        fh.write("time,label,channel,rms_1s_mV,rms_window_mV,window_s,pp_1s_mV,tone100_rms_mV\n")
                    fh.write("\n".join(rows) + "\n")
                saved = name
                break
            except PermissionError:
                continue
        if saved is None:
            self.log_btn.setText("File locked! (see console)")
        elif saved != "measurements_v3.csv":
            self.log_btn.setText("Saved to backup ✓")
        else:
            self.log_btn.setText("Logged ✓")
        QtCore.QTimer.singleShot(1500, lambda: self.log_btn.setText("Log reading"))

    def toggle_rec(self):
        if self.rec_file:
            self.rec_file.close()
            self.rec_file = None
            self.rec_btn.setText("Start recording")
            return
        if self.buf is None:
            return
        os.makedirs("recordings", exist_ok=True)
        self.rec_name = datetime.datetime.now().strftime("recordings/emg_%Y%m%d_%H%M%S.csv")
        self.rec_file = open(self.rec_name, "w")
        self.rec_file.write("sample," + ",".join(f"ch{i + 1}" for i in range(self.buf.shape[1])) + "\n")
        self.sample_idx = 0
        self.rec_btn.setText("Stop recording")

    def closeEvent(self, ev):
        if self.rec_file:
            self.rec_file.close()
        super().closeEvent(ev)


def main():
    ap = argparse.ArgumentParser(description="MSI live EMG plot")
    ap.add_argument("--port", type=int, default=5005)
    ap.add_argument("--window", type=float, default=5.0, help="seconds shown on screen")
    args = ap.parse_args()

    app = pg.mkQApp("MSI live EMG")
    rx = Receiver(args.port)
    rx.start()
    w = Window(rx, args.window)
    w.show()
    pg.exec()


if __name__ == "__main__":
    main()
