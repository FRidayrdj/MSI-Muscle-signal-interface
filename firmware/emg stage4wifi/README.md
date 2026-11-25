# emgstage4wifi — Wi-Fi streaming version

Same sampling and filter chain as `emg stage3`, but streams over Wi-Fi (UDP, port 5005) instead of USB serial.

Packet format: 8-byte header (`<2sBBI`: magic `EM`, channel count, samples per channel, sequence number) followed by int16 samples (millivolts × 10), 50 samples per channel per packet. The sequence number lets the laptop count lost packets.

Before flashing, set `WIFI_SSID` and `WIFI_PASS` at the top of the sketch (2.4 GHz network or phone hotspot). Written for N channels: for a second channel set `NUM_CH = 2` and `ADC_PINS = {34, 35}`.
