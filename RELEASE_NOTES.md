**Beta — unofficial 32-bit Android build of sm64coopdx 1.5.1**

- For 32-bit ARM (armeabi-v7a), Android 7.0+, OpenGL ES 3.0.
- No ROM included: bring your own.
- Tested on one device only (Redmi 9A, Android 10). Please report your device in an issue.
- Multiplayer verified against the official 1.5.1 client (CoopNet and direct connection).
- Known limits: update checker disabled; performance varies by device.

Verify the download with the `.sha256` file


**Beta 2 — unofficial 32-bit Android build of sm64coopdx 1.5.1**

What's new
- **Rendering performance:** faster vertex upload (persistent buffer). On a Redmi 9A (PowerVR GE8320) the same scene went from ~36 to ~58 FPS, and water levels no longer stay capped at 30 FPS.
- **Touch joystick:** the touch area now matches the drawn joystick (no more pressing exactly at its center).
- **Draw distance:** new installs default to 3x (was Infinite). If you are updating, your saved setting is kept; change it in Options → Display → Draw Distance.
- CoopNet fix from beta 1 stays (32-bit clients can join public lobbies).

If you see graphical glitches (flicker, broken geometry): create an empty file named `legacy_upload.txt` in the game folder (`/storage/emulated/0/com.maniscat2.sm64coopdx32bits/`), restart the game, and tell us your device model and GPU.

Verify the download with the `.sha256` file. Still tested on a limited set of devices.

