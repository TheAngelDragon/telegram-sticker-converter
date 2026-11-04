# telegram-sticker-converter

Converts videos into telegram webm stickers



You must download ffmpeg and put it in /ffmepg/ folder.



Build:

Run

```

pyinstaller --onefile --windowed --name "Telegram Sticker Converter" --add-binary "ffmpeg\\ffmpeg.exe;ffmpeg" --add-binary "ffmpeg\\ffprobe.exe;ffmpeg" sticker\_converter.py

```

