@echo off
echo ==== تثبيت مكتبات برنامج استخراج النص من الفيديو ====
echo تأكد من أن بيئة Python الافتراضية نشطة (venv)

call venv\Scripts\activate.bat

echo تحديث pip...
python -m pip install --upgrade pip

echo تثبيت المكتبات الأساسية...
pip install flask pysrt yt-dlp moviepy pytube pydub

echo تثبيت مكتبات التعرف على الكلام...
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
pip install openai-whisper==20231117

echo تثبيت مكتبات إضافية...
pip install numpy tqdm ffmpeg-python

echo ==== اكتمل التثبيت ====
echo يرجى تشغيل test_whisper.py للتحقق من تثبيت مكتبة Whisper بشكل صحيح

python test_whisper.py

pause
