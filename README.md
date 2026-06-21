# Jackit-Respawn

[![Python](https://img.shields.io/badge/Python-100%25-blue)](https://github.com/Ant-RWFS/Jackit-Respawn/search?l=python)
[![Version](https://img.shields.io/badge/version-1.2.2-brightgreen)](https://github.com/Ant-RWFS/Jackit-Respawn/releases/tag/release-v1.2.2)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

**Jackit-Respawn** is a graphical tool for configuring radio parameters and testing nRF‑series wireless devices (e.g., mice, keyboards). It provides an intuitive GUI that eliminates the need to manually edit configuration files.

## ✨ Features

- **Complete radio driver configuration** – adjust all RF parameters directly from the UI.
- **Hot‑plugin loading** – dynamically load plugins (HID fingerprints & RF ) without restarting the application.
- **Enhanced UI/UX** – improved layout and user experience.
- **Fully cross‑platform** – packaged for Windows, Linux (including Kali), and macOS.
- **Ready to run** – download, extract, and launch – no additional setup required.

## 📦 Installation & Usage

### System Requirements

- **Windows** 10 / 11 – no extra dependencies.
- **Linux** (tested on Kali) – requires **zenity** (for graphical dialogs) and **mpv** (for audio/video playback support).  
- **macOS** – no extra dependencies (mpv is bundled if needed).

### Quick Start

1. **Download the latest release**  
   Get the packaged archive from the [Releases page](https://github.com/Ant-RWFS/Jackit-Respawn/releases).

2. **Extract the archive**  
   Unzip the downloaded file to any folder of your choice.

3. **Run the application**  
   - On Windows:
     1. Double‑click `Jackit Respawn.exe`
   - On Linux:
     1. Install zenity & mpv:
      ```bash
      #Kali
      sudo apt update
      sudo apt install zenity mpv -y
    2. Make the executable file executable if necessary.
    3. Double-click the `Jackit Respawn` executable file.
   - On macOS:
     1. Double-click `Jackit Respawn.app`.

4. **Connect your device**  
   Plug in an nRF Research Firmware device and start testing.

## 🔌 Plugin Interface

Jackit-Respawn supports runtime plugin loading – you can add new device drivers or extend functionality by simply placing a Python .py file into the designated Plugin/ folder. The application automatically detects and loads the plugin without requiring a restart.

### What can plugins do?

Add support for new hardware – e.g., devices used for HID fingerprint spoofing or RF attack devices tools.
Customize radio parameter handling – define your own logic for reading/writing registers, calibrating frequencies, or implementing proprietary protocols.

### Plugin Structure

- `Plugin/Device/` – Device drivers (current driver is based on the [nrf-research-firmware](https://github.com/BastilleResearch/nrf-research-firmware)).  
- `Plugin/HID/` – HID fingerprint plugins for attack workflows.

### How to Write a Plugin and Use It?

1. Choose the appropriate folder (`Device/` or `HID/`) based on your plugin type.  
2. Check the existing files in that folder – they serve as fully working examples.  
3. Create a new `.py` file and implement **all the same class functions** as the example plugins, and declare any required **ID values** (e.g., device ID, vendor ID).  
4. Launch `Jackit Respawn`, navigate to the **Config Panel**, select the **Plugin** option, and register your `.py` file(s) as plugins.

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## 📬 Contact

- Author: [@Ant-RWFS](https://github.com/Ant-RWFS)
- Project URL: [https://github.com/Ant-RWFS/Jackit-Respawn](https://github.com/Ant-RWFS/Jackit-Respawn)
