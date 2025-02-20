import os
import pysrt
import google.generativeai as genai
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyBqsEjNqaZVmEsIVQmg-L11jSmR0ao3xB4"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro',
                            generation_config=genai.types.GenerationConfig(
                                temperature=0.3,  # Lower temperature for more precise output
                                top_p=0.8,
                                top_k=40
                            ))

# Available languages
LANGUAGES = {
    'Arabic': 'ar',
    'English': 'en',
    'Turkish': 'tr',
    'French': 'fr',
    'Spanish': 'es',
    'German': 'de',
    'Russian': 'ru',
    'Chinese': 'zh',
    'Japanese': 'ja',
    'Korean': 'ko'
}

class SRTTranslatorApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("SRT Translator")
        self.window.geometry("800x600")
        
        # File selection
        self.file_frame = ctk.CTkFrame(self.window)
        self.file_frame.pack(pady=10, padx=20, fill="x")
        
        self.file_label = ctk.CTkLabel(self.file_frame, text="No file selected")
        self.file_label.pack(side="left", padx=10)
        
        self.select_button = ctk.CTkButton(self.file_frame, text="Select SRT File", command=self.select_file)
        self.select_button.pack(side="right", padx=10)
        
        # Language selection
        self.lang_frame = ctk.CTkFrame(self.window)
        self.lang_frame.pack(pady=10, padx=20, fill="x")
        
        # Source language
        self.source_label = ctk.CTkLabel(self.lang_frame, text="From:")
        self.source_label.pack(side="left", padx=10)
        
        self.source_lang = ctk.CTkComboBox(self.lang_frame, values=list(LANGUAGES.keys()))
        self.source_lang.pack(side="left", padx=10)
        
        # Target language
        self.target_label = ctk.CTkLabel(self.lang_frame, text="To:")
        self.target_label.pack(side="left", padx=10)
        
        self.target_lang = ctk.CTkComboBox(self.lang_frame, values=list(LANGUAGES.keys()))
        self.target_lang.pack(side="left", padx=10)
        
        # Text display frame
        self.text_frame = ctk.CTkFrame(self.window)
        self.text_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Original text
        self.original_label = ctk.CTkLabel(self.text_frame, text="Original Text:")
        self.original_label.pack(pady=5)
        
        self.original_text = ctk.CTkTextbox(self.text_frame, height=200)
        self.original_text.pack(pady=5, padx=10, fill="both", expand=True)
        
        # Translated text
        self.translated_label = ctk.CTkLabel(self.text_frame, text="Translated Text:")
        self.translated_label.pack(pady=5)
        
        self.translated_text = ctk.CTkTextbox(self.text_frame, height=200)
        self.translated_text.pack(pady=5, padx=10, fill="both", expand=True)
        
        # Translate button
        self.translate_button = ctk.CTkButton(self.window, text="Translate", command=self.translate_srt)
        self.translate_button.pack(pady=10)
        
        # Progress
        self.progress_label = ctk.CTkLabel(self.window, text="")
        self.progress_label.pack(pady=5)
        
        self.selected_file = None
        
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("SRT files", "*.srt")])
        if file_path:
            self.selected_file = file_path
            self.file_label.configure(text=os.path.basename(file_path))
            # Load and display original content
            try:
                subs = pysrt.open(file_path)
                original_content = "\n\n".join(sub.text for sub in subs)
                self.original_text.delete("0.0", "end")
                self.original_text.insert("0.0", original_content)
                self.translated_text.delete("0.0", "end")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {str(e)}")
                
    def translate_text(self, text, target_lang):
        try:
            prompt = f"""Please provide a highly accurate and professional translation of the following text to {target_lang}.
Requirements:
- Maintain the exact meaning and context
- Preserve any technical terms accurately
- Keep the same tone and style
- Ensure proper grammar and punctuation
- Maintain any formatting or special characters

Text to translate: {text}

Translation:"""
            
            response = model.generate_content(prompt)
            if hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].content.parts[0].text.strip()
            elif hasattr(response, 'parts') and response.parts:
                return response.parts[0].text.strip()
            else:
                return response.text.strip()
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return text  # Return original text if translation fails
        
    def translate_srt(self):
        if not self.selected_file:
            messagebox.showerror("Error", "Please select an SRT file first")
            return
            
        source = self.source_lang.get()
        target = self.target_lang.get()
        
        if source == target:
            messagebox.showerror("Error", "Source and target languages must be different")
            return
            
        try:
            # Load the SRT file
            subs = pysrt.open(self.selected_file)
            total = len(subs)
            translated_content = []
            
            # Translate each subtitle
            for i, sub in enumerate(subs):
                self.progress_label.configure(text=f"Translating subtitle {i+1}/{total}")
                self.window.update()
                
                # Translate the text
                translated_text = self.translate_text(sub.text, target)
                translated_content.append(translated_text)
                sub.text = translated_text
            
            # Display translated content
            self.translated_text.delete("0.0", "end")
            self.translated_text.insert("0.0", "\n\n".join(translated_content))
            
            # Save the translated file
            output_file = os.path.splitext(self.selected_file)[0] + f"_{LANGUAGES[target]}.srt"
            subs.save(output_file, encoding='utf-8')
            
            self.progress_label.configure(text="Translation completed!")
            messagebox.showinfo("Success", f"Translation completed!\nSaved as: {os.path.basename(output_file)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.progress_label.configure(text="Translation failed!")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = SRTTranslatorApp()
    app.run()
