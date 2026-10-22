# SM64 Coop Deluxe — Android 32-bit (ARMv7) · Unofficial port

> **Unofficial community port.** Not affiliated with or endorsed by the sm64coopdx team or by Nintendo.
> This repository and its releases contain **no ROM and no Nintendo assets**. You must provide your own legally obtained Super Mario 64 (US) ROM.

## What is this?
A build of sm64coopdx 1.5.1 for 32-bit ARM Android devices (`armeabi-v7a`), based on the Android branch of
[ManIsCat2/sm64coopdx](https://github.com/ManIsCat2/sm64coopdx). It exists for devices whose Android system
is 32-bit only (many low-end phones are, even with a 64-bit CPU).

## Requirements
- Android 7.0+ (API 24), 32-bit ARM. If your device supports 64-bit apps, use the official build instead.
- OpenGL ES 3.0
- Your own ROM: In your internal storage, locate the folder **com.maniscat2.sm64coopdx32bits/user** and place your legal copy of the game there, naming it baserom.us

## Install
1. Download the APK from **Releases** and check it against the `.sha256` file.
2. Allow installing apps from unknown sources.
3. Install and open the app. You must grant storage permissions to the application and place your copy of the game (you can launch the game for the first time to generate the folder).

## Multiplayer
Tested against the official 1.5.1 client over CoopNet and direct connection. Versions must match.

## Known limitations
- Tested on few devices (Redmi 9A, Android 10, PowerVR GE8320): typically 45–60 FPS, with a short dip when entering a world.
- The built-in update checker is disabled.
- This is a beta: expect bugs.

## Troubleshooting
- **Graphical glitches (flicker, broken geometry):** create an empty `legacy_upload.txt` in the game folder and restart. Please report your device and GPU in an issue.
- **Game closes:** attach `crash_native.txt` from the game folder when opening an issue.

## Reporting bugs
Open an issue with your device model, Android version and what happened. If the game closes, attach
`crash_native.txt` from the game folder (`/storage/emulated/0/com.maniscat2.sm64coopdx32bits/`).

## What differs from upstream
32-bit build configuration and libraries; sound data converted to 32-bit layout (`tools/convert_sound_32.py`);
8-byte alignment in the memory pools; CoopNet wire-format fix (`hash` field is now 64-bit on all platforms);
native crash log; update checker removed.

## Credits and licenses
- sm64coopdx — coop-deluxe and contributors · Android fork — ManIsCat2 · original Android port — VDavid003
- Libraries: SDL2, Lua, libjuice, miniaudio, CoopNet (AGPL-3.0).
- The corresponding source code for each release is this repository at the release tag.

---

# Versión en español
**Port comunitario no oficial.** Sin relación con el equipo de sm64coopdx ni con Nintendo. No incluye ROM ni
recursos de Nintendo: necesitas tu propia ROM de Super Mario 64 (US) obtenida legalmente.

Es una compilación de sm64coopdx 1.5.1 para Android de 32 bits (`armeabi-v7a`). Requiere Android 7.0+ y OpenGL ES 3.0.
Instalación: descarga el APK de **Releases**, verifica la suma SHA-256 e instálalo permitiendo orígenes desconocidos.
Si el juego se cierra, adjunta `crash_native.txt` al abrir un issue. El archivo se encuentra en **com.maniscat2.sm64coopdx32bits/crash_native.txt**
