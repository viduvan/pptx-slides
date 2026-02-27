# PPTX Slides — AI Presentation Generator

**PPTX Slides** is a powerful tool that helps you create professional PowerPoint presentations quickly by leveraging the power of Google Gemini AI. You can generate slides from existing documents or simply by providing text prompts.

## ✨ Key Features

- 🚀 **Smart Slide Generation:** Create complete presentations from input files or concise ideas.
- 📄 **Multi-format Support:** Upload **Word (.docx)** or **PDF (.pdf)** files for AI to automatically summarize and convert into slides.
- 💬 **Interactive Editing:** Use prompts to ask the AI to edit, add, or remove slides directly on the web interface.
- 🎨 **Modern Interface:** Minimalist, intuitive UI with Dark Mode and glassmorphism effects.
- 🎭 **Theme Options:** Choose from various color themes for your presentation.
- 📥 **Instant Download:** Preview slides and download the `.pptx` file for immediate use.

## 📺 Video Demo

![PPPTX Slides Demo Recording](assets/demo_recording.webp)

## 🛠️ Technology Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **AI Engine:** [Google Gemini AI](https://ai.google.dev/)
- **Frontend:** HTML5, Modern CSS (Vanilla), JavaScript
- **Document Processing:** `python-pptx`, `python-docx`, `PyPDF2`

## 🚀 Installation and Usage

### 1. Environment Setup

Requires Python 3.9 or higher.

```bash
# Clone the project
git clone https://github.com/viduvan/pptx-slides
cd pptx-slides

# Install required libraries
pip install -r requirements.txt
```

### 2. API Key Configuration

Create a `.env` file in the root directory or set an environment variable:

```env
GEMINI_API_KEY=your_google_gemini_api_key
```

### 3. Run the Application

```bash
python run.py
```

Then, open your browser and access: `http://localhost:8000`

## 🤝 Contribution

Any contributions to improve the project are highly appreciated! Please submit an Issue or Pull Request if you have new ideas.

- **Developer:** [ChimSe](https://github.com/viduvan)
- **License:** [MIT License](LICENSE)
- **Completion Date:** February 27, 2026

---

Don't forget to leave a 🌟 if you find this project useful!
