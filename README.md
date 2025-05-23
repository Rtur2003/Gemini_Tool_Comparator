```markdown
# 🚗 Gemini Tool Comparator

An intelligent vehicle comparison web app powered by **Gemini AI**, built with **Python** and **Flask**.  
It allows users to log in, upload vehicle details and images, and compare cars side-by-side using AI-enhanced analysis.

![Demo Preview](static/images/comparator_preview.png)

---

## 🔧 Features

- 🔐 **User Login System** (with optional face recognition)
- 🚘 **Vehicle Database Management** (Add / Update / Delete)
- 📊 **Smart AI-Powered Comparison** via Gemini API
- 🖼️ **Image Upload & Display** for vehicles
- 🌐 **Web Interface** with HTML, CSS, JS
- 💾 Local storage using `.pkl` and SQL file backups

---

## 📁 Project Structure

```

Gemini\_Tool\_Comparator/
│
├── app.py                  # Main Flask application
├── .env                    # Environment variables (e.g. API keys)
├── requirements.txt        # Python package dependencies
├── README.md               # You're reading it!
│
├── users\_db.pkl            # Pickled user login data
├── vehicles\_db.pkl         # Pickled vehicle data
├── SON\_Veritabani.sql      # Backup SQL database
├── Yeni Metin Belgesi.txt  # Notes or temporary text
│
├── faces/                  # Face recognition data (if used)
├── gemini\_cache/           # Cache folder for Gemini outputs
│
├── static/
│   ├── css/                # Custom stylesheets
│   ├── js/                 # JavaScript files
│   ├── images/             # Icons, UI images
│   └── uploads/            # Uploaded vehicle images
│
└── templates/              # HTML templates (Jinja2)

````

---

## ⚙️ Installation & Usage

### 1. Clone the repository

```bash
git clone https://github.com/Rtur2003/Gemini_Tool_Comparator.git
cd Gemini_Tool_Comparator
````

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file with your API keys

```env
OPENAI_API_KEY=your_openai_key_here
SECRET_KEY=your_flask_secret_key
```

### 5. Run the app

```bash
python app.py
```

Then open your browser and visit:
📍 `http://localhost:5000`

---

## 🤖 Gemini AI Usage

This project uses Gemini AI to:

* Analyze and summarize vehicle specifications
* Assist with intelligent recommendations
* Enhance comparison logic with natural language output

---

## 📦 Dependencies

Installable via `requirements.txt`:

```
Flask
openai
pillow
opencv-python
face-recognition
python-dotenv
```

---

## 📌 Notes

* Make sure to replace placeholder keys in `.env`.
* `users_db.pkl` and `vehicles_db.pkl` are used for local storage; replace with a proper DB for production use.
* Images go into `static/uploads/`.

---

## 🛡️ Disclaimer

This is a demo/educational tool. Always verify real-world data from reliable automotive sources before making decisions.

---

## 📬 Contact

Made with ❤️ by [@Rtur2003](https://github.com/Rtur2003)
For issues, suggestions, or contributions, feel free to open an issue or PR on GitHub.

---
