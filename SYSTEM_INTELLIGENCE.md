# System Intelligence Report
**Generated:** 2026-02-02 22:41:31 PST
**Last Updated:** 2026-02-05 02:50:00 PST
**Host:** sabertooth
**User:** fasahov

## 1. Executive Summary
This system is a robust legacy workstation built on the **Intel X58** platform. It runs **Debian 13 (Trixie)** with a **GNOME** desktop. The primary shell is **Bash**. The system is currently configured for general-purpose computing and media streaming, with a developing toolchain for software engineering.

## 2. Hardware Architecture
*   **Motherboard:** ASUS SABERTOOTH X58 (Socket LGA1366)
    *   *Chipset:* Intel X58 (Northbridge) + ICH10R (Southbridge)
    *   *BIOS/Sensors:* Winbond W83667HG Super IO
*   **Processor (CPU):** Intel Core i7 950
    *   *Cores/Threads:* 4 Cores / 8 Threads
    *   *Clock:* 3.07 GHz Base
*   **Memory (RAM):** 12 GB DDR3
    *   *Configuration:* 3x 4GB modules (Triple Channel)
    *   *Speed:* 1066 MT/s
    *   *Slots Used:* DIMM0, DIMM2, DIMM4
*   **Graphics (GPU):** NVIDIA GeForce GTX 580
    *   *Architecture:* Fermi
    *   *Driver:* `nouveau` (Open Source)
    *   *VRAM:* 1.5 GB GDDR5
    *   *Ports:* 2x DVI-I, 1x Mini-HDMI
*   **Peripherals:**
    *   Xbox Wireless Adapter (USB)
    *   Realtek RTL88x2bu AC1200 WiFi Adapter (USB) [Driver: `88x2bu` Community]
    *   Standard USB Keyboard & Mouse

## 3. Software Environment
*   **Operating System:** Debian 13 (trixie)
*   **Kernel:** Linux 6.12.63+deb13-amd64
*   **Desktop Environment:** GNOME 48.7 (Wayland)
*   **Shell:** Zsh 5.9 (Default) | Bash 5.2.32 (Alternative)
*   **Package Managers:**
    *   **APT:** System-wide packages.
    *   **pipx:** User-space Python applications.
    *   **npm:** Global JavaScript tools.
    *   **pip:** Python package manager (for user libraries).
*   **Key Installed Tools:**
    *   **Dev:** `gcc` 14.2.0, `make` 4.4.1, `git` 2.47.3, `python3` 3.13.5, `node` 20.19.2, `perl` 5.40.1, `google-genai` (SDK), `python-is-python3`.
    *   **Shell Env:** `zsh`, `oh-my-zsh`, `powerlevel10k` (Theme).
    *   **Utils:** `gemini-cli` (npm), `catt` (pipx), `speedtest-cli` (pipx), `mkchromecast` (apt), `rclone` (apt), `fastfetch` (apt), `qbittorrent` (apt), `iso2god` (manual).
    *   **Services:** Home Assistant (Podman container), `minidlna` (DLNA/UPnP Media Server), `rclone-drive` (Google Drive Mount Service).
    *   **Startup:** `gemini-cli` (Auto-launch in GNOME Terminal Fullscreen).
    *   **Extensions:** GNOME "Cast to TV" (Installed, potentially version-incompatible with GNOME 48).
    *   **System:** `htop`, `btop`, `curl`, `wget`, `brave-browser`, `GNOME Terminal`.
    *   **Firmware:** Comprehensive non-free firmware suite installed.
    *   **Localization:** Optimized for English (US) and Russian. Excess language packs and Japanese input methods (Mozc) purged.

## 4. Network Topology
*   **Gateway / Router:** 192.168.0.1
*   **Primary Interface:** `wlx0013eff2047b` (Realtek RTL88x2bu WiFi)
    *   *Connection:* "SR7" @ 5.2 GHz (Signal: -31 dBm, Link: 867 Mb/s)
    *   *IP Address:* 192.168.0.108 (IPv4)
    *   *Driver:* `rtl88x2bu` (Community/Morrownr v5.13.1) - Power Mgmt: OFF
*   **Secondary Interface:** `wlx6245b508e8ff` (MediaTek)
    *   *Status:* DISABLED (Administratively down to prevent interference)
*   **Infrastructure:**
    *   `192.168.0.6`: TP-Link RE315 WiFi Extender (Bridging multiple devices)
    *   *Anomaly:* Extender blocks mDNS/Multicast discovery packets; devices on extender are visible via direct IP (Unicast) but hidden from mobile app discovery.
    *   `192.168.0.4`: Philips Hue Bridge
*   **Media Devices (Google Cast):**
    *   `192.168.0.102`: Family Room speaker (Google Home Max)
    *   `192.168.0.25`: G Home (Google Nest Hub)
    *   `192.168.0.18`: G Mini (Nest Mini) [via Extender]
    *   `192.168.0.44`: G mini 4 (Home Mini) [via Extender]
    *   `192.168.0.21`: Chromecast (Video)
*   **Mobile/IoT:**
    *   Pixel 7, Galaxy S20 FE, Xiaomi Device, ESP8266/32 Smart Plugs.
*   **Performance Profile:**
    *   *Download:* ~136 Mbit/s
    *   *Upload:* ~174 Mbit/s
    *   *Ping:* ~21 ms
*   **Secondary Interface:** `enp7s1` (Ethernet)
    *   *Status:* DOWN
*   **Listening Services:**
    *   TCP 631 (CUPS) [Localhost only]
    *   UDP 5353 (mDNS)

## 5. Storage Map
*   **Drive A (/dev/sda):** Intel SSDSA2M160 (160 GB) - [HEALTHY]
    *   *Usage:* Legacy Windows Installation (Mounted at `/mnt/windows`)
    *   *Filesystem:* NTFS
*   **Drive B (/dev/sdb):** WDC WD1002FAEX (1 TB) - [HEALTHY]
    *   *Usage:* Primary System Drive (Linux)
    *   *Strategy:* Split `/` (OS) and `/home` (Data)
    *   `/` (Root): 50 GB [ext4] (25% Used)
    *   `/home`: 869.5 GB [ext4] (1% Used)
    *   `swap`: 12 GB
*   **Drive C (/dev/sdc):** WDC WD1002FAEX (1 TB) - [HEALTHY]
    *   *Usage:* Data Storage (Mounted at `/mnt/storage`)
    *   *Filesystem:* NTFS
*   **Removable Storage:**
    *   `/dev/sdd1`: 7.5 GB USB (DIESEL) - [Mounted at /media/fasahov/NOOK]

## 6. AI Agent Guidelines
*   **User Context:** Supplementing/Migrating from ChromeOS. Prefer Google-friendly or Chromium-compatible solutions when possible.
*   **Privileges:** User `fasahov` has password-less `sudo` access.
*   **Conventions:** Prefer `pipx` for Python tools. Do not assume Docker is available (Podman is active).
*   **Memory:** Consult `.gemini/GEMINI.md` for the active agent memory and specific project contexts.

## 7. Terrain Map (Key Directories)
```text
/home/fasahov/
├── Desktop/
├── Documents/
├── Downloads/
├── GoogleDrive/        # [Cloud] Mounted Business Files via Rclone
├── Music/
├── Pictures/
├── Public/
├── Templates/
├── Videos/
├── .config/            # User configs (Brave, Kitty, htop, etc.)
├── .local/bin/         # User binaries (pipx apps: catt, speedtest)
└── SYSTEM_INTELLIGENCE.md

/mnt/
├── windows/            # [Drive B] Windows 10 System Partition
└── storage/            # [Drive C] Extra Data Storage
```
