import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("whisper_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

print("==== بدء اختبار تثبيت نموذج Whisper ====")
print("يرجى الانتظار بينما نتحقق من المكتبات المطلوبة...")

# Check Python version
print(f"إصدار Python: {sys.version}")

# Check dependencies
dependencies = [
    "whisper", 
    "torch", 
    "numpy", 
    "moviepy",
    "pydub",
    "ffmpeg"
]

for dep in dependencies:
    try:
        if dep == "ffmpeg":
            # Check if ffmpeg is installed
            import subprocess
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ تم العثور على {dep} - {result.stdout.splitlines()[0]}")
            else:
                print(f"✗ لم يتم العثور على {dep} - يرجى تثبيته")
        else:
            # Try to import the module
            module = __import__(dep)
            version = getattr(module, "__version__", "unknown version")
            print(f"✓ تم العثور على {dep} - {version}")
    except ImportError:
        print(f"✗ لم يتم العثور على {dep} - يرجى تثبيته باستخدام: pip install {dep}")
    except Exception as e:
        print(f"✗ حدثت مشكلة عند التحقق من {dep}: {str(e)}")

print("\n==== محاولة تحميل نموذج Whisper ====")

try:
    import whisper
    import torch
    
    # Check CUDA availability
    cuda_available = torch.cuda.is_available()
    device = "cuda" if cuda_available else "cpu"
    print(f"CUDA متاح: {cuda_available}")
    print(f"سيتم استخدام: {device}")
    
    # Try to load Whisper model
    print("جاري تحميل نموذج Whisper (tiny)...")
    whisper_model = whisper.load_model("tiny", device=device)
    print("✓ تم تحميل نموذج Whisper بنجاح!")
    
    # Test transcription with a simple test
    print("\n==== إجراء اختبار بسيط للتعرف على الكلام ====")
    test_audio = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_audio.mp3")
    
    if os.path.exists(test_audio):
        print(f"اختبار التعرف على الكلام باستخدام: {test_audio}")
        result = whisper_model.transcribe(test_audio)
        print(f"✓ نتيجة التعرف: {result['text'][:100]}...")
    else:
        print("ملف الصوت الاختباري غير موجود. يمكنك إضافة ملف صوت بالاسم 'test_audio.mp3' لاختبار النموذج")
    
except Exception as e:
    print(f"✗ فشل تحميل نموذج Whisper: {str(e)}")
    print("\nاقتراحات للإصلاح:")
    print("1. تأكد من تثبيت جميع المكتبات المطلوبة: pip install openai-whisper torch numpy")
    print("2. تأكد من تثبيت FFmpeg: https://ffmpeg.org/download.html")
    print("3. إذا كنت تستخدم بطاقة رسومات، تأكد من تثبيت برامج تشغيل CUDA المناسبة")
    print("4. قد تحتاج إلى إعادة تشغيل جهاز الكمبيوتر بعد تثبيت المكتبات")

print("\n==== اكتمل اختبار Whisper ====")
input("اضغط Enter للخروج...")
