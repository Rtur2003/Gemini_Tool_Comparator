# ==============================
# Sistem ve Genel Kütüphaneler
# ==============================
import os  # İşletim sistemi ile etkileşim
import json  # JSON formatında veri işleme
import time  # Zaman ile ilgili işlemler
import base64  # Base64 şifreleme ve çözme işlemleri
import pickle  # Nesneleri serileştirme ve tersine çevirme
import hashlib  # Hashleme işlemleri (örn: parola şifreleme)
import re  # Düzenli ifadeler (regex) kullanımı
import traceback  # Hata izleme ve hata yönetimi
import logging  # Loglama işlemleri
import datetime  # Tarih ve saat işlemleri
import sqlite3  # SQLite veritabanı yönetimi
from decimal import Decimal  # Kesin sayısal işlemler için Decimal sınıfı
from functools import wraps
from venv import logger  # Fonksiyon dekoratörleri için
from flask_caching import Cache

# ==============================
# Veritabanı Bağlantıları
# ==============================
import pyodbc  # Microsoft SQL Server bağlantısı için

# ==============================
# Flask ve Web Tabanlı İşlemler
# ==============================
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from werkzeug.utils import secure_filename  # Flask'ta dosya yükleme işlemleri için

# ==============================
# Görüntü İşleme ve Yapay Zeka
# ==============================
import cv2  # OpenCV kütüphanesi (görüntü işleme)
import numpy as np  # NumPy (sayısal işlemler ve matrisler için)
import face_recognition  # Yüz tanıma işlemleri

# ==============================
# Google AI Modelleri
# ==============================
from google import generativeai as genai  # Google'ın yapay zeka modelleri için
from google.generativeai import GenerativeModel, configure, types  # Generatif AI model işlemleri

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Session için gerekli

# Kullanıcı veritabanı dosyası
DB_FILE = 'users_db.pkl'
# Araç veritabanı dosyası
VEHICLES_DB_FILE = 'vehicles_db.pkl'
# Yüklenen araç resimlerinin kaydedileceği klasör
UPLOAD_FOLDER = 'static/uploads'
# İzin verilen dosya uzantıları
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Upload klasörünü oluştur
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Eğer varsa kullanıcı veritabanını yükle
if os.path.exists(DB_FILE):
    with open(DB_FILE, 'rb') as f:
        users_db = pickle.load(f)
else:
    users_db = {}

# Eğer varsa araç veritabanını yükle
if os.path.exists(VEHICLES_DB_FILE):
    with open(VEHICLES_DB_FILE, 'rb') as f:
        vehicles_db = pickle.load(f)
else:
    vehicles_db = []



def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=ARTHUR\\SQLEXPRESS;'
        'DATABASE=Yazılım;'
        'Trusted_Connection=yes;'
    )
    return conn
# 404 Hataları için özel sayfa
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# 500 Hataları için özel sayfa
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500



# İzin verilen dosya uzantıları
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(image_file):
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    else:
        return None


def save_user_sql(username, email, phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Kullanıcılar (username, email, phone_number) VALUES (?, ?, ?)",
                   (username, email, phone_number))
    conn.commit()
    conn.close()


def save_vehicle_sql(vehicle_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Arabalar (brand, model, year, mileage) VALUES (?, ?, ?, ?)",
                   (vehicle_data['brand'], vehicle_data['model'], vehicle_data['year'], vehicle_data['mileage']))
    conn.commit()
    conn.close()

    """Araç veritabanını kaydet"""
    with open(VEHICLES_DB_FILE, 'wb') as f:
        pickle.dump(vehicles_db, f)


def allowed_file(filename):
    """Dosya uzantısının izin verilen uzantılardan olup olmadığını kontrol et"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')  # Use a proper landing page


@app.route('/register_page')
def register_page():
    return render_template('register.html')


@app.route('/login_page')
def login_page():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login_page'))


# İletişim sayfası için route eklendi
@app.route('/iletisim')
def iletisim_page():
    return render_template('iletisim.html')

@app.route('/onay')
def onaypage():
    return render_template('onay.html')


import os
import logging
from flask import request, jsonify
import google.generativeai as genai

@app.route('/chat', methods=['POST'])
def chat():
    # 1. API Key ve Ortam Kontrolü
    GEMINI_API_KEY_CHAT = os.getenv('GEMINI_API_KEY_CHAT')
    if not GEMINI_API_KEY_CHAT:
        logging.error("GEMINI_API_KEY_CHAT environment variable not set")
        return jsonify({
            'status': 'error',
            'code': 'SERVER_CONFIG_ERROR',
            'message': 'Sunucu yapılandırma hatası. Lütfen yöneticiye bildirin.'
        }), 500

    try:
        # 2. Giriş Validasyonu
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'code': 'INVALID_CONTENT_TYPE',
                'message': 'Geçersiz istek formatı (JSON bekleniyor)'
            }), 400

        user_message = request.json.get('message', '').strip()
        if not user_message:
            return jsonify({
                'status': 'error',
                'code': 'EMPTY_MESSAGE',
                'message': 'Lütfen geçerli bir mesaj girin.'
            }), 400

        if len(user_message) > 1000:
            return jsonify({
                'status': 'error',
                'code': 'MESSAGE_TOO_LONG',
                'message': 'Mesaj çok uzun (maksimum 1000 karakter)'
            }), 400

        # 3. Model Konfigürasyonu
        genai.configure(api_key=GEMINI_API_KEY_CHAT)
        model = genai.GenerativeModel('gemini-1.5-flash')  # Güncel model sürümü

        # 4. Sistem Prompt'u
        system_prompt = """Sen Araç Sat platformunun resmi destek asistanısın. 
Görevin kullanıcılara sadece aşağıdaki konularda yardımcı olmak:

### YETKİ ALANIN:
1. İlan Yönetimi:
   - İlan oluşturma/güncelleme/silme
   - İlan onay süreçleri
   - İlan arama ve filtreleme

2. Hesap İşlemleri:
   - Giriş/çıkış problemleri
   - Şifre sıfırlama
   - Profil düzenleme

3. Ödeme ve Üyelik:
   - Paket yükseltme
   - Fatura bilgileri
   - Ödeme problemleri

4. Platform Kullanımı:
   - Arayüz rehberliği
   - Temel işlevlerin açıklanması

### KURALLAR:
1. **Konu Dışı Soruları** cevaplama:
   - "Bu konuda yardımcı olamam" de
   - "Sadece Araç Sat platformuyla ilgili soruları yanıtlayabilirim" ekle

2. **Format**:
   - En fazla 2 cümle
   - Maddeli listeler kullan (• ile)
   - Emoji kullanma (🚫)

3. **Tarafsız Dil**:
   - Yorum yapma
   - Kişisel görüş belirtme
   - "Bence", "bana göre" gibi ifadeler kullanma

4. **Yönlendirme**:
   - Karmaşık sorunlarda:
   - "Destek ekibine yönlendiriliyorsunuz" de
   - "support@aracsat.com adresine detay yazın" ekle

Örnek soru ve  Yanıtlar:
Hesabıma giriş yapamıyorum, ne yapmalıyım?
Şifrenizi sıfırlamayı deneyin. "Şifremi Unuttum" bağlantısını kullanarak e-posta adresinize sıfırlama bağlantısı gönderebilirsiniz. Sorun devam ederse destek ekibimize ulaşın.

İlanımı yüklerken hata alıyorum, nasıl çözebilirim?
İnternet bağlantınızı kontrol edin. Fotoğrafların boyutunun 5MB'dan küçük ve JPG/PNG formatında olduğundan emin olun. Tarayıcınızı güncelleyin veya farklı bir tarayıcı kullanmayı deneyin. Sorun devam ederse destek ekibimizle iletişime geçin.

İlanım yayına alınmadı, neden?
İlanınız incelemede olabilir (genellikle 24 saat içinde onaylanır) veya eksik/hatalı bilgi içerebilir. Girdiğiniz bilgileri gözden geçirin, özellikle fiyat, konum ve araç özellikleri kısımlarını kontrol edin. Güncelleyerek tekrar deneyebilirsiniz.

İlanımı silemiyorum/düzenleyemiyorum, ne yapmalıyım?
"Hesabım" bölümünden "İlanlarım" sekmesine giderek işlem yapabilirsiniz. İlanınızın durumuna göre (incelemede, yayında, askıda) bazı işlemler kısıtlanmış olabilir. Teknik bir sorun varsa destek ekibimiz yardımcı olabilir.

Web sitesi açılmıyor veya çok yavaş, neden?
Tarayıcınızı yenileyin, önbelleği temizleyin ve internet bağlantınızı kontrol edin. Farklı bir tarayıcı kullanmayı deneyin. Sorun devam ederse kısa süreli bakım çalışması olabilir, sosyal medya hesaplarımızdan güncel bilgilere ulaşabilirsiniz.

Fotoğraf yükleyemiyorum, neden?
Fotoğraf boyutunun 5MB'dan küçük olduğundan ve desteklenen formatlarda (JPG, PNG) olduğundan emin olun. Fotoğrafların çözünürlüğünün çok yüksek olmadığını kontrol edin. Sorun devam ederse teknik destek ekibimize yazabilirsiniz.

Satıcıyla iletişime geçemiyorum, ne yapmalıyım?
Satıcı iletişim bilgilerini güncellememiş olabilir veya ilanını yayından kaldırmış olabilir. Birkaç gün içinde tekrar deneyebilir veya alternatif olarak başka ilanlara göz atabilirsiniz.

Dolandırıcılıktan nasıl korunabilirim?
Şüpheli tekliflerden kaçının, fiyatı piyasa değerinin çok altında olan araçlardan şüphelenin, araçları mutlaka yerinde görün ve kaparo/ödeme için güvenli yöntemler kullanın. Emin olmadığınız durumlarda destek ekibimizle iletişime geçebilirsiniz."""  # Mevcut prompt aynen kalabilir

        # 5. Güvenli Yanıt Üretme
        try:
            response = model.generate_content(
                contents=[
                    {
                        "role": "user",
                        "parts": [{
                            "text": f"{system_prompt}\n\nKullanıcı Sorusu: {user_message}"
                        }]
                    }
                ],
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 200,
                    "top_p": 0.9,
                    "top_k": 40
                },
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH'
                }
            )

            # 6. Gelişmiş Yanıt İşleme
            response_text = ""
            
            # Çoklu yanıt formatı desteği
            if hasattr(response, 'text'):
                response_text = response.text
            elif (response.candidates and 
                  hasattr(response.candidates[0], 'content') and 
                  hasattr(response.candidates[0].content, 'parts')):
                response_text = "".join(part.text for part in response.candidates[0].content.parts)
            
            # Boş yanıt ve minimum uzunluk kontrolü
            response_text = response_text.strip() or "Anlayamadım, lütfen sorunuzu tekrar ifade edin."
            if len(response_text) < 3:
                raise ValueError("Yanıt çok kısa")

            # 7. Güvenlik Filtre Kontrolü
            if (hasattr(response, 'prompt_feedback') and 
                response.prompt_feedback and 
                response.prompt_feedback.block_reason):
                logging.warning(f"Blocked content: {response.prompt_feedback.block_reason}")
                return jsonify({
                    'status': 'error',
                    'code': 'CONTENT_BLOCKED',
                    'message': 'Soru içeriği politikamıza uymuyor',
                    'block_reason': str(response.prompt_feedback.block_reason)
                }), 400

            # Başarılı yanıt
            return jsonify({
                'status': 'success',
                'data': {
                    'response': response_text[:500],  # Karakter sınırı
                    'safety_ratings': (response.prompt_feedback.safety_ratings 
                                      if hasattr(response, 'prompt_feedback') and response.prompt_feedback 
                                      else None)
                }
            })

        except genai.core.exceptions.BlockedPromptException as e:
            logging.warning(f"Blocked prompt: {str(e)}")
            return jsonify({
                'status': 'error',
                'code': 'PROMPT_BLOCKED',
                'message': 'Soru içeriği güvenlik politikalarımıza uymuyor'
            }), 400

    except ValueError as e:
        logging.error(f"ValueError: {str(e)}")
        return jsonify({
            'status': 'error',
            'code': 'INVALID_RESPONSE',
            'message': 'Yapay zeka geçerli yanıt oluşturamadı'
        }), 503

    except Exception as e:
        logging.error(f"Unexpected error: {type(e).__name__}: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'code': 'INTERNAL_ERROR',
            'message': 'Teknik bir aksaklık oluştu',
            'error_type': type(e).__name__,
            'debug_info': str(e) if os.getenv('FLASK_ENV') == 'development' else None
        }), 500
@app.route('/araclarim')
def my_vehicles():
    try:
        # Check if user is logged in
        if 'username' not in session:
            flash('Bu sayfayı görüntülemek için giriş yapmalısınız.', 'warning')
            return redirect(url_for('login_page'))

        # Get database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve username and user ID from session
        username = session.get('username')

        # First, get the user ID based on the username
        cursor.execute("SELECT KullaniciID FROM Kullanıcılar WHERE KullaniciAdi = ?", (username,))
        user_result = cursor.fetchone()

        if not user_result:
            flash('Kullanıcı bilgisi bulunamadı.', 'error')
            return redirect(url_for('login_page'))

        user_id = user_result[0]

        # Updated SQL query to fetch only user's vehicles
        query = """
            SELECT a.ArabaID, a.Marka, a.Model, a.UretimYili, a.Kilometre, a.Fiyat, 
                   a.YakitTuru, a.MotorHacmi, a.MotorGucu, a.VitesTuru, a.KasaTuru, 
                   a.YolcuKapasitesi, a.BagajHacmi, a.HasarDurumu, a.HasarMaliyeti, 
                   a.KapiSayisi, a.Renk, a.Foto
            FROM Arabalar a
            JOIN Kullanıcılar
             ka ON a.SahipID = ka.KullaniciID
            WHERE ka.KullaniciID = ?
        """

        # Execute the query with user ID
        cursor.execute(query, (user_id,))
        vehicles = cursor.fetchall()

        # Get column names
        column_names = [description[0] for description in cursor.description]

        # Convert vehicles to dictionary list
        vehicles_dict = []
        for vehicle in vehicles:
            vehicle_dict = {column: vehicle[i] for i, column in enumerate(column_names)}

            # Convert BLOB photo to Base64
            if vehicle_dict.get('Foto') is not None and vehicle_dict['Foto']:
                try:
                    image_data = base64.b64encode(vehicle_dict['Foto']).decode('utf-8')
                    vehicle_dict['Foto'] = f"data:image/jpeg;base64,{image_data}"
                except Exception as e:
                    app.logger.error(f"Fotoğraf dönüştürme hatası: {str(e)}")
                    vehicle_dict['Foto'] = "/static/images/default_car.jpg"
            else:
                vehicle_dict['Foto'] = "/static/images/default_car.jpg"

            vehicles_dict.append(vehicle_dict)

        # Close cursor and connection
        cursor.close()
        conn.close()

        # Render template with vehicles
        return render_template('araclarim.html',
                               username=username,
                               vehicles=vehicles_dict)

    except sqlite3.Error as db_error:
        # Specific database error handling
        app.logger.error(f"Veritabanı hatası: {str(db_error)}")
        return render_template('error.html',
                               error_message="Veritabanı bağlantısında bir hata oluştu."), 500

    except Exception as e:
        # Catch-all error handling
        app.logger.error(f"Araçlarım sayfası yüklenirken hata oluştu: {str(e)}", exc_info=True)

        try:
            return render_template('error.html',
                                   error_message="Araçlar yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin."), 500
        except:
            # Fallback error page if template rendering fails
            return """
            <html>
                <head><title>Hata</title></head>
                <body>
                    <h1>Bir Hata Oluştu</h1>
                    <p>Araçlar yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.</p>
                    <a href="/">Ana Sayfaya Dön</a>
                </body>
            </html>
            """, 500

@app.route('/delete_vehicle/<int:vehicle_id>', methods=['POST'])
def delete_vehicle(vehicle_id):
    try:
        # Check if user is logged in
        if 'username' not in session:
            flash('Bu işlemi gerçekleştirmek için giriş yapmalısınız.', 'warning')
            return jsonify({'status': 'error', 'message': 'Giriş yapılmamış'}), 401

        # Get database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve username and user ID from session
        username = session.get('username')

        # First, get the user ID based on the username
        cursor.execute("SELECT KullaniciID FROM Kullanıcılar WHERE KullaniciAdi = ?", (username,))
        user_result = cursor.fetchone()

        if not user_result:
            return jsonify({'status': 'error', 'message': 'Kullanıcı bulunamadı'}), 403

        user_id = user_result[0]

        # Check if the vehicle belongs to the current user
        cursor.execute("SELECT SahipID FROM Arabalar WHERE ArabaID = ?", (vehicle_id,))
        vehicle_result = cursor.fetchone()

        if not vehicle_result or vehicle_result[0] != user_id:
            return jsonify({'status': 'error', 'message': 'Bu aracı silme yetkiniz yok'}), 403

        # Delete the vehicle
        cursor.execute("DELETE FROM Arabalar WHERE ArabaID = ?", (vehicle_id,))
        conn.commit()

        # Close cursor and connection
        cursor.close()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Araç başarıyla silindi'}), 200

    except sqlite3.Error as db_error:
        app.logger.error(f"Araç silme hatası: {str(db_error)}")
        return jsonify({'status': 'error', 'message': 'Veritabanı hatası'}), 500

    except Exception as e:
        app.logger.error(f"Araç silme sırasında hata oluştu: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Bilinmeyen bir hata oluştu'}), 500



@app.route('/add_vehicle')
def add_vehicle():
    if 'username' in session:
        return render_template('add_vehicle.html', username=session['username'])
    return redirect(url_for('login_page'))


@app.route('/save_vehicle', methods=['POST'], endpoint='save_vehicle_new')
def save_vehicle():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    # Debug için session değerini yazdıralım
    print(f"Session username: {session.get('username')}")

    try:
        # Get user ID from session
        conn = get_db_connection()
        cursor = conn.cursor()

        # Veritabanındaki kullanıcıları listeleyelim
        cursor.execute("SELECT KullaniciID, KullaniciAdi FROM dbo.[Kullanıcılar]")
        all_users = cursor.fetchall()
        print("Veritabanındaki tüm kullanıcılar:", all_users)

        # SQL Server için uygun sorgu - normal parametre geçişi
        cursor.execute("SELECT KullaniciID FROM dbo.[Kullanıcılar] WHERE KullaniciAdi = ?", (session['username'],))
        user_result = cursor.fetchone()

        if not user_result:
            # Kullanıcı bulunamadı, veritabanında ilk kullanıcıyı kullanalım
            cursor.execute("SELECT TOP 1 KullaniciID FROM dbo.[Kullanıcılar]")
            user_result = cursor.fetchone()

            if not user_result:
                conn.close()
                return jsonify({"success": False, "message": "Veritabanında hiç kullanıcı yok."}), 400

            print("Kullanıcı bulunamadı, ilk kullanıcı kullanılıyor:", user_result)

        sahip_id = user_result[0]

        # Get form data with correct field names from HTML
        marka = request.form['marka']
        model = request.form['model']
        uretim_yili = int(request.form['uretimYili'])
        kilometre = int(request.form['kilometre'])
        yakit_turu = request.form['yakitTuru']
        vites_turu = request.form['vitesTuru']
        yakit_tuketimi = request.form['yakitTuketimi']
        motor_hacmi = int(request.form['motorHacmi'])
        motor_gucu = int(request.form['motorGucu'])
        govde_turu = request.form['govdeTuru']
        kasa_turu = request.form['kasaTuru']
        yolcu_kapasitesi = int(request.form['yolcuKapasitesi'])
        bagaj_hacmi = int(request.form['bagajHacmi'])
        kapi_sayisi = int(request.form['kapiSayisi'])
        fiyat = float(request.form['fiyat'])
        renk = request.form['renk']
        hasar_durumu = request.form['hasarDurumu']
        hasar_maliyeti = float(request.form['hasarMaliyeti'])

        # Resim için BLOB verisi
        image_blob = None
        if 'vehicle_image' in request.files:
            file = request.files['vehicle_image']
            if file and allowed_file(file.filename):
                # Dosyayı okuyup BLOB olarak saklayalım
                image_blob = file.read()

        # Foto sütununu içeren INSERT sorgusu
        cursor.execute("""
            INSERT INTO dbo.[Arabalar] (
                Marka, Model, UretimYili, Kilometre, YakitTuru, VitesTuru, 
                YakitTuketimi, MotorHacmi, MotorGucu, GovdeTuru, KasaTuru,
                YolcuKapasitesi, BagajHacmi, KapiSayisi, Fiyat, Renk,
                HasarDurumu, HasarMaliyeti, SahipID, OlusturulmaTarihi, Foto
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            marka, model, uretim_yili, kilometre, yakit_turu, vites_turu,
            yakit_tuketimi, motor_hacmi, motor_gucu, govde_turu, kasa_turu,
            yolcu_kapasitesi, bagaj_hacmi, kapi_sayisi, fiyat, renk,
            hasar_durumu, hasar_maliyeti, sahip_id, time.strftime('%Y-%m-%d %H:%M:%S'),
            image_blob  # Foto sütununa BLOB verisi eklendi
        ))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Araç başarıyla eklendi!"})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"success": False, "message": f"Bir hata oluştu: {str(e)}"}), 500

def default_car_image():
    """Varsayılan araç görüntüsünü döndürür."""
    return send_from_directory('static/images', 'default-car.jpg')

@app.route('/catalog')
def catalog():
    try:
        # Get all vehicles from database
        vehicles = get_all_vehicles_from_database()

        # Initialize Gemini with minimal vehicle data
        initialize_gemini_catalog(vehicles)

        # Get filter parameters from the request
        brand = request.args.get('brand', '')
        year_min = request.args.get('year_min', '')
        year_max = request.args.get('year_max', '')
        price_min = request.args.get('price_min', '')
        price_max = request.args.get('price_max', '')
        fuel_type = request.args.get('fuel_type', '')

        # Convert empty strings to None for SQL parameters
        brand_param = brand if brand else None
        year_min_param = int(year_min) if year_min else None
        year_max_param = int(year_max) if year_max else None
        price_min_param = int(price_min) if price_min else None
        price_max_param = int(price_max) if price_max else None
        fuel_type_param = fuel_type if fuel_type else None

        conn = get_db_connection()
        cursor = conn.cursor()


        # SQL sorgusunu oluştur
        query = """
            SELECT ArabaID, Marka, Model, UretimYili, Kilometre, Fiyat, YakitTuru, 
                   MotorHacmi, MotorGucu, VitesTuru, KasaTuru, YolcuKapasitesi, 
                   BagajHacmi, HasarDurumu, HasarMaliyeti, KapiSayisi, Renk, Foto
            FROM Arabalar
            WHERE 1=1
        """

        params = []
        if brand_param:
            query += " AND Marka = ?"
            params.append(brand_param)
        if year_min_param:
            query += " AND UretimYili >= ?"
            params.append(year_min_param)
        if year_max_param:
            query += " AND UretimYili <= ?"
            params.append(year_max_param)
        if price_min_param:
            query += " AND Fiyat >= ?"
            params.append(price_min_param)
        if price_max_param:
            query += " AND Fiyat <= ?"
            params.append(price_max_param)
        if fuel_type_param:
            query += " AND YakitTuru = ?"
            params.append(fuel_type_param)

        # Dinamik SQL sorgusunu çalıştır
        cursor.execute(query, params)
        vehicles = cursor.fetchall()

        # Sonuçları sözlük listesine dönüştür
        column_names = [description[0] for description in cursor.description]
        vehicles_dict = []
        for vehicle in vehicles:
            vehicle_dict = {column: vehicle[i] for i, column in enumerate(column_names)}

            # BLOB Fotoğrafı Base64'e Çevir
            if vehicle_dict.get('Foto') is not None and vehicle_dict['Foto']:  # Eğer BLOB veri varsa ve boş değilse
                try:
                    image_data = base64.b64encode(vehicle_dict['Foto']).decode('utf-8')
                    vehicle_dict['Foto'] = f"data:image/jpeg;base64,{image_data}"
                except Exception as e:
                    app.logger.error(f"Fotoğraf dönüştürme hatası: {str(e)}")
                    vehicle_dict['Foto'] = "/static/images/default_car.jpg"
            else:
                # Varsayılan resim (BLOB yoksa)
                vehicle_dict['Foto'] = "/static/images/default_car.jpg"

            vehicles_dict.append(vehicle_dict)

        # Cursor ve bağlantıyı kapat
        cursor.close()
        conn.close()

        # Eğer vehicles None ise boş liste oluştur
        if vehicles is None:
            vehicles = []

        # Araçları katalog sayfasına gönder
        return render_template('catalog.html', username=session.get('username'), vehicles=vehicles_dict)

    except Exception as e:
        app.logger.error(f"Katalog sayfası yüklenirken hata oluştu: {str(e)}")

        try:
            return render_template('error.html',
                                  error_message="Araç kataloğu yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin veya yönetici ile iletişime geçin."), 500
        except:
            return """
            <html>
                <head><title>Hata</title></head>
                <body>
                    <h1>Bir Hata Oluştu</h1>
                    <p>Araç kataloğu yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.</p>
                    <a href="/">Ana Sayfaya Dön</a>
                </body>
            </html>
            """, 500





# Sepete ekleme route'u
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        # JSON verisini al
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Geçersiz istek'}), 400

        vehicle_id = data.get('vehicle_id')
        name = data.get('name')
        price = data.get('price')

        # Gerekli alanların kontrolü
        if not vehicle_id or not name or not price:
            return jsonify({'success': False, 'error': 'Eksik bilgi'}), 400

        # Sepete ekleme işlemi (örneğin, session kullanarak)
        if 'cart' not in session:
            session['cart'] = []

        # Aracı sepete ekle
        session['cart'].append({
            'vehicle_id': vehicle_id,
            'name': name,
            'price': price
        })

        # Session'ı kaydet
        session.modified = True

        return jsonify({'success': True, 'message': 'Araç sepete eklendi'})

    except Exception as e:
        # Hata loglaması yap
        app.logger.error(f"Sepete ekleme sırasında hata: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'error': 'Bir hata oluştu'}), 500

def initialize_gemini_catalog(vehicles):
    """
    Initialize Gemini with minimal vehicle data (just brands and models)
    to keep in context for future comparison requests
    """
    try:
        # Create minimal vehicle data with just brand and model
        minimal_vehicles = []
        for vehicle in vehicles:
            minimal_vehicles.append({
                "brand": vehicle.get('brand', ''),
                "model": vehicle.get('model', '')
            })

        # Convert to JSON - using minimal data to save prompt space
        vehicles_json = json.dumps(minimal_vehicles, ensure_ascii=False)
        
        # Create instruction - combine system instruction with user data
        full_prompt = """
        Bu araç kataloğunu yorum yapmadan belleğine kaydet. 
        Sadece araç ID'lerini, markalarını ve modellerini hatırla.
        Herhangi bir cevap verme, sadece bilgileri belleğine al.
        
        Araç Listesi:
        """ + vehicles_json

        # Print what is being sent to Gemini
        print("Prompt being sent to Gemini:")
        print(full_prompt)

        # Create cache key based on vehicle data
        cache_key = hashlib.md5(vehicles_json.encode()).hexdigest()
        cache_file = os.path.join("gemini_cache", f"catalog_{cache_key}.txt")
        
        # Check if we already initialized this catalog
        if os.path.exists(cache_file):
            logger.info("Using cached catalog initialization")
            return True
            
        # Send data to Gemini with correct role format
        model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
        response = model.generate_content(
            contents=[
                {"role": "user", "parts": [{"text": full_prompt}]}
            ],
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 100
            }
        )
        
        # Cache the initialization to avoid redundant calls
        os.makedirs("gemini_cache", exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write("initialized")
            
        return True
        
    except Exception as e:
        logger.error(f"Gemini catalog initialization error: {str(e)}", exc_info=True)
        return False        
@app.route('/vehicle-details/<int:vehicle_id>')
def vehicle_details(vehicle_id):
    query = """
        SELECT ArabaID, Marka, Model, UretimYili, Kilometre, Fiyat, YakitTuru, 
               MotorHacmi, MotorGucu, VitesTuru, KasaTuru, YolcuKapasitesi, 
               BagajHacmi, HasarDurumu, HasarMaliyeti, KapiSayisi, Renk , Foto
        FROM Arabalar 
        WHERE ArabaID = ?
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        app.logger.info(f"Executing SQL: {query}")
        app.logger.info(f"With parameters: {vehicle_id}")

        # Sorguyu çalıştır
        cursor.execute(query, (vehicle_id,))

        vehicle = cursor.fetchone()

        if vehicle:

            if vehicle:
                # BLOB verisini base64'e dönüştür
                foto_data = None
                if vehicle[17]:  # Foto sütunu
                    import base64
                    foto_base64 = base64.b64encode(vehicle[17]).decode('utf-8')
                    foto_data = f"data:image/jpeg;base64,{foto_base64}"

            # Araç detaylarını JSON formatında döndür
            return jsonify({
                'ArabaID': vehicle[0],
                'Marka': vehicle[1],
                'Model': vehicle[2],
                'UretimYili': vehicle[3],
                'Kilometre': vehicle[4],
                'Fiyat': float(vehicle[5]) if vehicle[5] else 0.0,
                'YakitTuru': vehicle[6],
                'MotorHacmi': vehicle[7],
                'MotorGucu': vehicle[8],
                'VitesTuru': vehicle[9],
                'KasaTuru': vehicle[10],
                'YolcuKapasitesi': vehicle[11],
                'BagajHacmi': vehicle[12],
                'HasarDurumu': vehicle[13],
                'HasarMaliyeti': float(vehicle[14]) if vehicle[14] else 0.0,
                'KapiSayisi': vehicle[15],
                'Renk': vehicle[16],
                'Foto': foto_data
            })
        else:
            return jsonify({'error': 'Araç bulunamadı'}), 404

    except Exception as e:
        # Hata loglaması yap
        app.logger.error(f"Araç detayları alınırken hata oluştu: {str(e)}")
        return jsonify({'error': 'Araç bilgileri alınırken bir hata oluştu', 'details': str(e)}), 500

    finally:
        # Bağlantıyı kapat
        if conn:
            conn.close()



class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

@app.route('/compare', methods=['POST'])
def compare_vehicles():
    # Initialize debug information dictionary
    debug_info = {
        'timestamps': {
            'start': datetime.datetime.now().isoformat()
        },
        'steps': {},
        'errors': []
    }

    try:
        # Step 1: Validate incoming request
        debug_info['steps']['request_validation'] = {
            'status': 'started',
            'details': {}
        }
        
        if not request.is_json:
            error_msg = "Request content type is not JSON"
            debug_info['errors'].append(error_msg)
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")  # Console logging
            debug_info['steps']['request_validation']['status'] = 'failed'
            return jsonify({
                'success': False,
                'error': error_msg,
                'debug': debug_info
            }), 400

        data = request.get_json()
        print(f"[REQUEST] Received vehicle comparison request: {data}")  # Console logging
        debug_info['steps']['request_validation']['details']['raw_data'] = str(data)[:200] + "..." if data else None

        # Step 2: Validate required fields
        required_fields = ['vehicles', 'user_preference']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            debug_info['errors'].append(error_msg)
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")  # Console logging
            return jsonify({
                'success': False,
                'error': error_msg,
                'debug': debug_info
            }), 400

        vehicles = data['vehicles']
        user_preference = data['user_preference']
        lang = data.get('lang', 0)

        debug_info['steps']['request_validation']['status'] = 'completed'
        debug_info['steps']['request_validation']['details']['processed_data'] = {
            'vehicles_count': len(vehicles),
            'user_preference': user_preference,
            'lang': lang
        }

        # Step 2: Validate required fields
        required_fields = ['vehicles', 'user_preference']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            debug_info['errors'].append(error_msg)
            logger.error(error_msg)
            return jsonify({
                'success': False,
                'error': error_msg,
                'debug': debug_info
            }), 400

        vehicles = data['vehicles']
        user_preference = data['user_preference']
        lang = data.get('lang', 0)

        debug_info['steps']['request_validation']['status'] = 'completed'
        debug_info['steps']['request_validation']['details']['processed_data'] = {
            'vehicles_count': len(vehicles),
            'user_preference': user_preference,
            'lang': lang
        }

        # Step 3: Prepare vehicle details
        debug_info['steps']['vehicle_preparation'] = {
            'status': 'started',
            'details': {}
        }
        
        vehicles_details = []
        for idx, vehicle in enumerate(vehicles):
            try:
                vehicle_info = {
                    "id": str(vehicle.get('id', '')),
                    "name": str(vehicle.get('name', ''))
                }
                vehicles_details.append(vehicle_info)
                debug_info['steps']['vehicle_preparation']['details'][f'vehicle_{idx}'] = vehicle_info
            except Exception as e:
                error_msg = f"Error processing vehicle {idx}: {str(e)}"
                debug_info['errors'].append(error_msg)
                logger.error(error_msg)

        debug_info['steps']['vehicle_preparation']['status'] = 'completed'

        # Step 4: Cache handling
        debug_info['steps']['cache_handling'] = {
            'status': 'started',
            'details': {}
        }
        
        try:
            cache_key = f"{hashlib.md5(json.dumps(vehicles_details).encode()).hexdigest()}_{hashlib.md5(user_preference.encode()).hexdigest()}_{lang}"
            cache_file = os.path.join("gemini_cache", f"compare_{cache_key}.json")
            debug_info['steps']['cache_handling']['details']['cache_key'] = cache_key
            debug_info['steps']['cache_handling']['details']['cache_file'] = cache_file

            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_content = f.read()
                    debug_info['steps']['cache_handling']['details']['cache_content_length'] = len(cache_content)
                    
                    if cache_content.strip():
                        try:
                            cached_result = json.loads(cache_content)
                            debug_info['steps']['cache_handling']['status'] = 'cache_hit'
                            logger.info("Using cached comparison result")
                            return jsonify({
                                'success': True,
                                'result': cached_result,
                                'debug': debug_info
                            })
                        except json.JSONDecodeError as e:
                            error_msg = f"Cache JSON decode error: {str(e)}"
                            debug_info['errors'].append(error_msg)
                            logger.error(error_msg)
                            debug_info['steps']['cache_handling']['details']['cache_error'] = error_msg
        except Exception as e:
            error_msg = f"Cache handling error: {str(e)}"
            debug_info['errors'].append(error_msg)
            logger.error(error_msg)
            debug_info['steps']['cache_handling']['details']['cache_error'] = error_msg

        debug_info['steps']['cache_handling']['status'] = 'cache_miss'

        # Step 5: Generate Gemini prompt and get response
        debug_info['steps']['gemini_interaction'] = {
            'status': 'started',
            'details': {}
        }
        
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
            lang_text = "Türkçe" if lang == 0 else "English"
            
            prompt = f"""
            Respond in {lang_text}.
            
            Compare these vehicles:
            {json.dumps(vehicles_details, indent=2)}
            
            User preference: {user_preference}
            
            Return response in this exact JSON format:
            {{
              "recommended": {{
                "id": "vehicle_id",
                "name": "Vehicle name",
                "reasons": ["reason1", "reason2"]
              }},
              "alternative": {{
                "id": "vehicle_id",
                "name": "Vehicle name",
                "reasons": ["reason1", "reason2"]
              }}
            }}
            """
            
            debug_info['steps']['gemini_interaction']['details']['prompt'] = prompt
            
            response = model.generate_content(prompt)
            ai_response = response.text.strip()
            debug_info['steps']['gemini_interaction']['details']['raw_response'] = ai_response
            
            # Step 6: Parse and validate response
            debug_info['steps']['response_parsing'] = {
                'status': 'started',
                'details': {}
            }
            
            # Clean response
            cleaned_response = ai_response
            for marker in ['```json', '```']:
                if cleaned_response.startswith(marker):
                    cleaned_response = cleaned_response[len(marker):]
                if cleaned_response.endswith(marker):
                    cleaned_response = cleaned_response[:-len(marker)]
            cleaned_response = cleaned_response.strip()
            
            debug_info['steps']['response_parsing']['details']['cleaned_response'] = cleaned_response
            
            try:
                result = json.loads(cleaned_response)
                debug_info['steps']['response_parsing']['status'] = 'completed'
                
                # Validate response structure
                required_keys = ['recommended', 'alternative']
                if not all(key in result for key in required_keys):
                    raise ValueError("Missing required keys in response")
                
                # Step 7: Enhance with database data
                debug_info['steps']['database_enhancement'] = {
                    'status': 'started',
                    'details': {}
                }
                
                try:
                    for vehicle_type in ['recommended', 'alternative']:
                        vehicle_id = result[vehicle_type].get('id')
                        vehicle_data = get_vehicle_from_database(vehicle_id)
                        
                        if vehicle_data:
                            result[vehicle_type]['price'] = float(vehicle_data.get('price', 0))
                            debug_info['steps']['database_enhancement']['details'][f'{vehicle_type}_data'] = vehicle_data
                
                    debug_info['steps']['database_enhancement']['status'] = 'completed'
                    
                    # Final result preparation
                    final_result = {
                        'success': True,
                        'result': result,
                        'user_preference': user_preference
                    }
                    
                    # Cache the result using DecimalEncoder
                    os.makedirs("gemini_cache", exist_ok=True)
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(final_result, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)
                    
                    debug_info['timestamps']['end'] = datetime.datetime.now().isoformat()
                    final_result['debug'] = debug_info
                    
                    # Use DecimalEncoder when printing or converting to JSON
                    print("[COMPARISON] Final Result:")
                    print(json.dumps(final_result, indent=2, cls=DecimalEncoder))

                    return jsonify(final_result)
                
                except Exception as e:
                    error_msg = f"Database enhancement error: {str(e)}"
                    debug_info['errors'].append(error_msg)
                    logger.error(error_msg)
                    debug_info['steps']['database_enhancement']['status'] = 'failed'
                    raise
                    
            except (json.JSONDecodeError, ValueError) as e:
                error_msg = f"Response parsing error: {str(e)}"
                debug_info['errors'].append(error_msg)
                logger.error(error_msg)
                debug_info['steps']['response_parsing']['status'] = 'failed'
                debug_info['steps']['response_parsing']['details']['error'] = error_msg
                raise
                
        except Exception as e:
            error_msg = f"Gemini interaction error: {str(e)}"
            debug_info['errors'].append(error_msg)
            logger.error(error_msg)
            debug_info['steps']['gemini_interaction']['status'] = 'failed'
            raise
  
    except Exception as e:
        error_msg = f"Comparison failed: {str(e)}"
        debug_info['errors'].append(error_msg)
        logger.error(error_msg, exc_info=True)
        debug_info['timestamps']['end'] = datetime.datetime.now().isoformat()
        
        return jsonify({
            'success': False,
            'error': "Vehicle comparison failed",
            'debug': debug_info
        }), 500


# Handle fallback when Gemini API fails
# Modify handle_gemini_fallback to add console logging
def handle_gemini_fallback(vehicles, user_preference, lang):
    try:
        import random
        
        vehicles_copy = vehicles.copy()
        random.shuffle(vehicles_copy)
        
        recommended = {
            "id": vehicles_copy[0].get('id', ''),
            "name": vehicles_copy[0].get('name', ''),
            "reasons": ["Sistemimiz şu anda yoğun, basit karşılaştırma kullanıldı."]
        }
        
        alternative = {
            "id": vehicles_copy[1].get('id', ''),
            "name": vehicles_copy[1].get('name', ''),
            "reasons": ["Sistemimiz şu anda yoğun, basit karşılaştırma kullanıldı."]
        }
        
        # Add price data from database
        recommended_vehicle = get_vehicle_from_database(recommended["id"])
        if recommended_vehicle:
            recommended["price"] = recommended_vehicle.get("price", "")
            
        alternative_vehicle = get_vehicle_from_database(alternative["id"])
        if alternative_vehicle:
            alternative["price"] = alternative_vehicle.get("price", "")
        
        # Add console logging
        print("[FALLBACK] Generating comparison using fallback mechanism:")
        print(f"Recommended Vehicle: {recommended}")
        print(f"Alternative Vehicle: {alternative}")
        
        return jsonify({
            "success": True,
            "recommended": recommended,
            "alternative": alternative,
            "user_preference": user_preference,
            "fallback_used": True
        })
        
    except Exception as e:
        logger.error(f"Fallback mechanism failed: {str(e)}", exc_info=True)
        print(f"[FALLBACK ERROR] {str(e)}")  # Console logging
        return jsonify({
            "success": False,
            "error": "Karşılaştırma yapılamadı ve yedek sistem de çalışmadı. Teknik ekibimiz bilgilendirildi."
        }), 500


def get_vehicle_from_database(vehicle_id):
    """
    Get vehicle information from database by ID
    """
    conn = None
    try:
        # Open database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query
        query = """
        SELECT 
            ArabaID, Marka, Model, Fiyat
        FROM Arabalar
        WHERE ArabaID = ?
        """
        
        # Execute query
        cursor.execute(query, (vehicle_id,))
        row = cursor.fetchone()

        # If vehicle is found, return as dictionary
        if row:
            vehicle_info = {
                "id": row.ArabaID,
                "brand": row.Marka,
                "model": row.Model,
                "price": row.Fiyat
            }
            return vehicle_info
        else:
            return None

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()


def get_all_vehicles_from_database():
    """
    Get all vehicles from database for catalog
    """
    conn = None
    try:
        # Open database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query
        query = """
        SELECT 
            ArabaID, Marka, Model
        FROM Arabalar
        """
        
        # Execute query
        cursor.execute(query)
        rows = cursor.fetchall()

        # Convert to list of dictionaries
        vehicles = []
        for row in rows:
            vehicle = {
                "id": row.ArabaID,
                "brand": row.Marka,
                "model": row.Model
            }
            vehicles.append(vehicle)
            
        return vehicles

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()


def parse_ai_response(text, lang=0):
    """
    Parse AI response and return structured data.
    This is a fallback for non-JSON formatted responses.
    """
    # Headers for recommended and alternative vehicles
    recommended_header = '[Önerilen Araç]' if lang == 0 else '[Recommended Vehicle]'
    alternative_header = '[Alternatif Araç]' if lang == 0 else '[Alternative Vehicle]'
    
    # Default vehicle info
    recommended = {
        "id": "",
        "name": "Önerilen Araç",
        "reasons": []
    }
    
    alternative = {
        "id": "",
        "name": "Alternatif Araç",
        "reasons": []
    }
    
    # Try to extract vehicle info from text
    try:
        # Extract recommended vehicle
        recommended_match = re.search(
            f'{re.escape(recommended_header)}(.*?)(?={re.escape(alternative_header)}|$)',
            text, 
            re.DOTALL
        )
        
        # Extract alternative vehicle
        alternative_match = re.search(
            f'{re.escape(alternative_header)}(.*?)(?=\[|$)',
            text, 
            re.DOTALL
        )

        # Parse recommended vehicle
        if recommended_match:
            recommended_text = recommended_match.group(1).strip()
            lines = [line.strip() for line in recommended_text.split('\n') if line.strip()]
            
            if lines:
                # First line might be the vehicle name
                first_line = lines[0]
                if not first_line.startswith('-'):
                    recommended["name"] = first_line
                    lines = lines[1:]
                
                # Other lines contain reasons
                for line in lines:
                    if line.startswith('-'):
                        recommended["reasons"].append(line[1:].strip())
                    else:
                        recommended["reasons"].append(line.strip())
        
        # Parse alternative vehicle
        if alternative_match:
            alternative_text = alternative_match.group(1).strip()
            lines = [line.strip() for line in alternative_text.split('\n') if line.strip()]
            
            if lines:
                # First line might be the vehicle name
                first_line = lines[0]
                if not first_line.startswith('-'):
                    alternative["name"] = first_line
                    lines = lines[1:]
                
                # Other lines contain reasons
                for line in lines:
                    if line.startswith('-'):
                        alternative["reasons"].append(line[1:].strip())
                    else:
                        alternative["reasons"].append(line.strip())
    
    except Exception as e:
        logger.error(f"Parse error: {str(e)}")
    
    return recommended, alternative



# Placeholder route'u
@app.route('/api/placeholder/<int:width>/<int:height>')
def placeholder(width, height):
    try:
        # Placeholder resmi oluşturma işlemi (örneğin, bir resim URL'si döndür)
        placeholder_url = f"https://via.placeholder.com/{width}x{height}"
        return jsonify({'url': placeholder_url})

    except Exception as e:
        # Hata loglaması yap
        app.logger.error(f"Placeholder oluşturulurken hata: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Placeholder oluşturulamadı'}), 500

# Genel hata yakalama decorator'ı (Flask app'ine eklenecek)
@app.errorhandler(Exception)
def handle_exception(e):
    # Hatayı logla
    app.logger.error(f"Beklenmeyen hata: {str(e)}")
    
    # Yanıt API endpoint'i için mi istemci için mi olduğunu belirle
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Beklenmeyen bir hata oluştu', 'details': str(e)}), 500
    else:
        return render_template('error.html', error_message="Beklenmeyen bir hata oluştu. Lütfen daha sonra tekrar deneyin."), 500
@app.route('/register', methods=['POST'])
def register():
    # Form verilerini al
    KullaniciAdi = request.form['username']
    Eposta = request.form['email']
    Sifre = request.form['password']  # Gerçek uygulamada şifreyi hashleyin!
    Telefon = request.form['phone']
    DogumTarihi = request.form['birth_date']
    Cinsiyet = request.form['gender']
    Adres = request.form['address']
    image_data = request.form.get('image_data', '')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Kullanıcı adı veya e-posta daha önce kullanılmış mı kontrol et
        cursor.execute("SELECT KullaniciID FROM Kullanıcılar WHERE KullaniciAdi = ? OR Eposta = ? OR Telefon = ?",
                       (KullaniciAdi, Eposta, Telefon))
        user = cursor.fetchone()

        if user:
            flash('Bu kullanıcı adı, e-posta veya telefon numarası zaten kayıtlı!', 'danger')
            return redirect(url_for('register_page'))

        if not image_data:
            flash('Görüntü alınamadı. Lütfen kamera izni verdiğinizden emin olun.', 'danger')
            return redirect(url_for('register_page'))

        # Base64 görüntüyü çöz
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # Yüz tanıma işlemi
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if not face_locations:
            flash('Yüz tespit edilemedi. Lütfen kameraya düzgün bakın.', 'danger')
            return redirect(url_for('register_page'))

        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if not face_encodings:
            flash('Yüz kodlaması yapılamadı. Lütfen tekrar deneyin.', 'danger')
            return redirect(url_for('register_page'))

        # **Tüm kayıtlı yüz verilerini çek**
        cursor.execute("SELECT KisiID, YuzVerisi FROM YuzVerileri")
        registered_faces = cursor.fetchall()

        new_face_encoding = face_encodings[0]

        for kisi_id, yuz_verisi in registered_faces:
            stored_encoding = np.frombuffer(yuz_verisi, dtype=np.float64)

            # **Yüz karşılaştırması yap**
            match_results = face_recognition.compare_faces([stored_encoding], new_face_encoding)

            if match_results[0]:  # Eğer eşleşme varsa
                flash('Bu yüz zaten sistemde kayıtlı! Farklı bir kullanıcıyla giriş yapın.', 'danger')
                return redirect(url_for('register_page'))

        # Kullanıcıyı veritabanına ekle
        cursor.execute("""
        INSERT INTO Kullanıcılar 
        (KullaniciAdi, Eposta, Sifre, Telefon, DogumTarihi, Cinsiyet, Adres) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (KullaniciAdi, Eposta, Sifre, Telefon, DogumTarihi, Cinsiyet, Adres))

        cursor.execute("SELECT @@IDENTITY AS ID")
        kullanici_id = cursor.fetchone()[0]

        face_encoding_binary = new_face_encoding.tobytes()
        altin_oran = 1.618
        face_landmarks = face_recognition.face_landmarks(rgb_frame, face_locations)
        landmarks_json = json.dumps(face_landmarks[0] if face_landmarks else {})

        cursor.execute("""
        INSERT INTO YuzVerileri 
        (KisiID, YuzVerisi, AltinOran, YuzIsaretleri) 
        VALUES (?, ?, ?, ?)
        """, (kullanici_id, pyodbc.Binary(face_encoding_binary), altin_oran, landmarks_json))

        conn.commit()

        flash(f'{KullaniciAdi} başarıyla kaydedildi!', 'success')
        return redirect(url_for('login_page'))

    except pyodbc.DatabaseError as e:
        flash(f'Veritabanı hatası: {str(e)}', 'danger')
        return redirect(url_for('register_page'))

    except Exception as e:
        flash(f'Bir hata oluştu: {str(e)}', 'danger')
        return redirect(url_for('register_page'))

    finally:
        if 'conn' in locals():
            conn.close()


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email=request.form['email']  
        print(email)
        try:
            # Get user data from database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if the user exists
            cursor.execute("SELECT KullaniciID, KullaniciAdi, Eposta FROM Kullanıcılar WHERE KullaniciAdi = ?", (username,))
            user = cursor.fetchone()
            kullanici_id = user[0]
            kullanici_mail=user[2]
            
            if not user:
                flash('Kullanıcı bulunamadı.', 'error')
                return redirect(url_for('login_page'))

            if not kullanici_mail==email:
                flash('E-Posta Hatalı.', 'error')
                return redirect(url_for('login_page'))
            
            # Kamera erişimi için base64 kodlu görüntüyü al
            image_data = request.form.get('image_data', '')
            
            if not image_data:
                flash('Görüntü alınamadı. Lütfen kamera izni verdiğinizden emin olun.', 'error')
                return redirect(url_for('login_page'))
            
            # Base64 formatındaki resmi çöz
            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            # Yüz tanıma işlemi
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            
            if not face_locations:
                flash('Yüz tespit edilemedi. Lütfen kameraya düzgün bakın.', 'error')
                return redirect(url_for('login_page'))
            
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            if not face_encodings:
                flash('Yüz kodlaması yapılamadı. Lütfen tekrar deneyin.', 'error')
                return redirect(url_for('login_page'))
            
            # Get the stored face encoding for this user
            cursor.execute("SELECT YuzVerisi FROM YuzVerileri WHERE KisiID = ?", (kullanici_id,))
            stored_face = cursor.fetchone()
            
            if not stored_face:
                flash('Yüz verisi bulunamadı. Lütfen sistem yöneticisiyle iletişime geçin.', 'error')
                return redirect(url_for('login_page'))
            
            # Convert stored binary face data to numpy array
            stored_encoding = np.frombuffer(stored_face[0], dtype=np.float64)
            
            # Compare faces
            results = face_recognition.compare_faces([stored_encoding], face_encodings[0])
            
            if results[0]:
                session['username'] = username  # Kullanıcıyı oturumda sakla
                flash(f'Hoş geldiniz, {username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Yüz doğrulaması başarısız. Lütfen tekrar deneyin.', 'error')
                return redirect(url_for('login_page'))
            
        except Exception as e:
            flash(f'Bir hata oluştu: {str(e)}', 'error')
            return redirect(url_for('login_page'))
        
        finally:
            if 'conn' in locals():
                conn.close()
    
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)
@app.route('/odeme')
def odeme():
    vehicle_ids = request.args.get('vehicles', '').split(',')
    # vehicle_ids listesini kullanarak gerekli işlemleri yapabilirsiniz
    return render_template('odeme.html', vehicle_ids=vehicle_ids)


if __name__ == '__main__':
    app.run(debug=True)