CREATE TABLE Kullanýcýlar (
    KullaniciID INT IDENTITY(1,1) PRIMARY KEY,
    KullaniciAdi VARCHAR(50) NOT NULL,
    Eposta VARCHAR(45) UNIQUE NOT NULL,
    Sifre VARCHAR(25) NOT NULL,
    Telefon CHAR(10) UNIQUE NOT NULL, -- Telefon numarasý
    Adres VARCHAR(100) NOT NULL, -- Kullanýcýnýn adresi
    DogumTarihi DATE NOT NULL, -- Kullanýcýnýn doðum tarihi
    Cinsiyet CHAR(5) CHECK (Cinsiyet IN ('Erkek', 'Kadýn')) NOT NULL, -- Cinsiyet bilgisi
    KayitTarihi DATETIME DEFAULT GETDATE(),
    
    -- Doðum tarihi kontrolü
    CONSTRAINT ck_DogumTarihi CHECK (
        DogumTarihi <= GETDATE() -- Gelecekteki tarihleri engelle
        AND DogumTarihi >= DATEADD(YEAR, -100, GETDATE()) -- Maksimum 100 yaþýnda olmalý
        AND DogumTarihi <= DATEADD(YEAR, -18, GETDATE()) -- En az 18 yaþýnda olmalý
    ),

    -- Þifre kontrolü
    CONSTRAINT ck_Sifre CHECK (
        LEN(Sifre) >= 8 AND 
        Sifre LIKE '%[0-9]%' AND 
        Sifre LIKE '%[A-Z]%' COLLATE Latin1_General_BIN AND 
        Sifre LIKE '%[a-z]%'
    ),

    -- Telefon numarasý kontrolü
    CONSTRAINT ck_Telefon CHECK (
        Telefon LIKE '5[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'
    ),

    -- E-posta kontrolü
    CONSTRAINT ck_Eposta CHECK (
        Eposta LIKE '%@gmail.com'
    )
);

-- Yüz verileri tablosu
CREATE TABLE YuzVerileri (
    YuzVeriID INT IDENTITY(1,1) PRIMARY KEY,
    KisiID INT,
    YuzVerisi VARBINARY(MAX) NOT NULL,  -- OpenCV yüz vektörü (face encoding)
    AltinOran FLOAT,  -- Yüzün altýn oran deðeri
    YuzIsaretleri NVARCHAR(MAX),  -- JSON formatýnda yüz noktalarý
    YuzKayitTarihi DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (KisiID) REFERENCES Kullanýcýlar(KullaniciID) ON DELETE CASCADE
);

CREATE TABLE Arabalar (
    ArabaID INT IDENTITY(1,1) PRIMARY KEY, -- Aracýn benzersiz kimliði
    Marka VARCHAR(100) NOT NULL, -- Araç markasý (BMW, Mercedes vb.)
    Model VARCHAR(100) NOT NULL, -- Araç modeli (X5, C200 vb.)
    UretimYili INT NOT NULL, -- Üretim yýlý
    Kilometre INT NOT NULL, -- Kilometre bilgisi
    Fiyat DECIMAL(10,2) NOT NULL, -- Fiyat (TL, Dolar vb.)
    YakitTuru VARCHAR(10) NOT NULL CHECK (YakitTuru IN ('Benzin', 'Dizel', 'Hibrit', 'Elektrik')), -- Yakýt türü
    YakitTuketimi VARCHAR(50) NOT NULL, -- Yakýt tüketimi (örneðin: 6.5 L/100km)
    MotorHacmi INT NOT NULL, -- Motor hacmi (cc)
    MotorGucu INT NOT NULL, -- Motor gücü (hp/bg)
    VitesTuru VARCHAR(15) NOT NULL CHECK (VitesTuru IN ('Manuel', 'Otomatik', 'Yarý Otomatik')), -- Vites türü
    GovdeTuru VARCHAR(15) NOT NULL CHECK (GovdeTuru IN ('Otomobil', 'SUV', 'Ticari', 'Motosiklet')), -- Gövde türü
    KasaTuru VARCHAR(15) NOT NULL CHECK (KasaTuru IN ('Sedan', 'Hatchback', 'Coupe', 'Cabrio', 'Station Wagon', 'Pickup', 'Minivan')), -- Kasa tipi
    YolcuKapasitesi TINYINT NOT NULL, -- Yolcu kapasitesi
    BagajHacmi INT NOT NULL, -- Bagaj hacmi (litre)
    HasarDurumu VARCHAR(255) NOT NULL, -- Hasar bilgisi (Aðýr hasarlý, boya var/yok, kaza geçmiþi vb.)
    HasarMaliyeti DECIMAL(10,2) NOT NULL, -- Hasarýn tamir maliyeti (Opsiyonel)
    KapiSayisi TINYINT NOT NULL CHECK (KapiSayisi IN (2, 4)), -- Kapý sayýsý (2 veya 4)
    OlusturulmaTarihi DATETIME NOT NULL DEFAULT GETDATE(), -- Araç kaydýnýn oluþturulma tarihi
    Renk VARCHAR(15) NOT NULL,

	 -- Arabalarýn sahibi zorunlu olmalý
    SahipID INT NOT NULL,
    FOREIGN KEY (SahipID) REFERENCES Kullanýcýlar(KullaniciID) ON DELETE CASCADE
);

INSERT INTO Kullanýcýlar (KullaniciAdi, Eposta, Sifre, Telefon, Adres, DogumTarihi, Cinsiyet)
VALUES 
    ('Ahmet Yýlmaz', 'ahmet.yilmaz@gmail.com', 'Sifre123', '5051234567', 'Beylikdüzü, Ýstanbul', '1990-05-20', 'Erkek'),
    ('Mehmet Demir', 'mehmet.demir@gmail.com', 'Sifre123', '5052345678', 'Kadýköy, Ýstanbul', '1995-08-15', 'Erkek'),
    ('Ayþe Kaya', 'ayse.kaya@gmail.com', 'Sifre123', '5053456789', 'Beþiktaþ, Ýstanbul', '1992-02-10', 'Kadýn'),
    ('Fatma Aydýn', 'fatma.aydin@gmail.com', 'Sifre123', '5054567890', 'Üsküdar, Ýstanbul', '1994-11-25', 'Kadýn'),
    ('Emre Can', 'emre.can@gmail.com', 'Sifre123', '5055678901', 'Beyoðlu, Ýstanbul', '1998-12-30', 'Erkek'),
    ('Selin Çelik', 'selin.celik@gmail.com', 'Sifre123', '5056789012', 'Kadýköy, Ýstanbul', '1993-03-18', 'Kadýn'),
    ('Mehmet Öz', 'mehmet.oz@gmail.com', 'Sifre123', '5057890123', 'Maltepe, Ýstanbul', '1988-07-05', 'Erkek'),
    ('Aylin Akbulut', 'aylin.akbulut@gmail.com', 'Sifre123', '5058901234', 'Sancaktepe, Ýstanbul', '1991-01-22', 'Kadýn'),
    ('Murat Korkmaz', 'murat.korkmaz@gmail.com', 'Sifre123', '5059012345', 'Üsküdar, Ýstanbul', '1997-06-17', 'Erkek'),
    ('Zeynep Yalçýn', 'zeynep.yalcin@gmail.com', 'Sifre123', '5050123456', 'Pendik, Ýstanbul', '1999-04-10', 'Kadýn');

	select * from Kullanýcýlar

	INSERT INTO Arabalar (Marka, Model, UretimYili, Kilometre, Fiyat, YakitTuru, YakitTuketimi, MotorHacmi, MotorGucu, VitesTuru, GovdeTuru, KasaTuru, YolcuKapasitesi, BagajHacmi, HasarDurumu, HasarMaliyeti, KapiSayisi, Renk, SahipID)
VALUES 
    -- Otomobiller
    ('BMW', '3 Serisi', 2022, 25000, 1800000, 'Benzin', '7.5 L/100km', 2000, 184, 'Otomatik', 'Otomobil', 'Sedan', 5, 480, 'Hasar yok', 0, 4, 'Siyah', 1),
    ('Mercedes', 'C200', 2021, 30000, 1950000, 'Benzin', '6.8 L/100km', 1600, 184, 'Otomatik', 'Otomobil', 'Sedan', 5, 455, 'Hasar yok', 0, 4, 'Beyaz', 2),
    ('Toyota', 'Corolla', 2020, 45000, 1100000, 'Hibrit', '4.5 L/100km', 1800, 122, 'Otomatik', 'Otomobil', 'Sedan', 5, 470, 'Boyasýz', 0, 4, 'Gri', 3),
    ('Volkswagen', 'Golf', 2022, 15000, 1250000, 'Benzin', '5.2 L/100km', 1400, 150, 'Manuel', 'Otomobil', 'Hatchback', 5, 380, 'Hasar yok', 0, 4, 'Mavi', 4),
    ('Audi', 'A3', 2021, 27000, 1450000, 'Dizel', '5.6 L/100km', 2000, 150, 'Otomatik', 'Otomobil', 'Hatchback', 5, 350, 'Kaza geçmiþi yok', 0, 4, 'Kýrmýzý', 5),
    
    -- SUV Araçlar
    ('Volvo', 'XC60', 2023, 5000, 2350000, 'Hibrit', '5.8 L/100km', 2000, 250, 'Otomatik', 'SUV', 'Station Wagon', 5, 635, 'Hasar yok', 0, 4, 'Lacivert', 6),
    ('Land Rover', 'Range Rover Evoque', 2021, 38000, 2750000, 'Dizel', '7.0 L/100km', 2000, 180, 'Otomatik', 'SUV', 'Station Wagon', 5, 650, 'Kaputta boya var', 5000, 4, 'Gri', 7),
    ('Ford', 'Ranger Raptor', 2022, 10000, 2200000, 'Dizel', '8.5 L/100km', 2000, 213, 'Otomatik', 'Ticari', 'Pickup', 5, 1200, 'Hasar yok', 0, 4, 'Turuncu', 8),

    -- Ticari Araçlar
    ('Peugeot', 'Rifter', 2020, 60000, 900000, 'Dizel', '6.0 L/100km', 1600, 120, 'Manuel', 'Ticari', 'Minivan', 7, 775, 'Sað çamurluk deðiþmiþ', 2000, 4, 'Beyaz', 9),
    ('Volkswagen', 'Transporter', 2019, 85000, 1450000, 'Dizel', '8.0 L/100km', 2000, 150, 'Manuel', 'Ticari', 'Minivan', 9, 900, 'Ön tampon deðiþmiþ', 3000, 4, 'Siyah', 10),

    -- Motosikletler
    ('Honda', 'CBR650R', 2023, 8000, 450000, 'Benzin', '4.5 L/100km', 650, 95, 'Manuel', 'Motosiklet', 'Coupe', 2, 0, 'Hasar yok', 0, 2, 'Kýrmýzý', 1),
    ('Yamaha', 'MT-07', 2022, 12000, 375000, 'Benzin', '4.3 L/100km', 700, 75, 'Manuel', 'Motosiklet', 'Coupe', 2, 0, 'Hasar yok', 0, 2, 'Mavi', 2),
    ('Kawasaki', 'Ninja 400', 2021, 15000, 320000, 'Benzin', '3.8 L/100km', 400, 49, 'Manuel', 'Motosiklet', 'Coupe', 2, 0, 'Ön grenaj deðiþmiþ', 2500, 2, 'Yeþil', 3),
    ('BMW', 'R 1250 GS', 2023, 5000, 550000, 'Benzin', '5.2 L/100km', 1250, 136, 'Manuel', 'Motosiklet', 'Coupe', 2, 0, 'Hasar yok', 0, 2, 'Gri', 4),
    ('Harley-Davidson', 'Sportster S', 2022, 9000, 680000, 'Benzin', '5.5 L/100km', 1252, 121, 'Manuel', 'Motosiklet', 'Coupe', 2, 0, 'Hasar yok', 0, 2, 'Siyah', 5);


	INSERT INTO Arabalar (Marka, Model, UretimYili, Kilometre, Fiyat, YakitTuru, YakitTuketimi, MotorHacmi, MotorGucu, VitesTuru, GovdeTuru, KasaTuru, YolcuKapasitesi, BagajHacmi, HasarDurumu, HasarMaliyeti, KapiSayisi, Renk, SahipID)
VALUES 
-- Sedan bir araç
('BMW', '320i', 2020, 45000, 1200000.00, 'Benzin', '7.2 L/100km', 1998, 184, 'Otomatik', 'Otomobil', 'Sedan', 5, 480, 'Boya yok, kaza geçmiþi var', 15000.00, 4, 'Siyah', 1),

-- SUV bir araç
('Toyota', 'RAV4', 2019, 60000, 950000.00, 'Hibrit', '5.5 L/100km', 2487, 222, 'Otomatik', 'SUV', 'Station Wagon', 5, 580, 'Hasarsýz', 0.00, 4, 'Beyaz', 2),

-- Hatchback bir araç
('Volkswagen', 'Golf', 2021, 30000, 850000.00, 'Benzin', '6.0 L/100km', 1498, 150, 'Manuel', 'Otomobil', 'Hatchback', 5, 380, 'Boya var, deðiþen yok', 8000.00, 4, 'Mavi', 3),

-- Ticari bir araç
('Ford', 'Transit', 2018, 120000, 750000.00, 'Dizel', '8.5 L/100km', 2198, 130, 'Manuel', 'Ticari', 'Minivan', 3, 600, 'Kaza geçmiþi var, deðiþen var', 25000.00, 4, 'Gri', 4),

-- Motosiklet
('Honda', 'CBR500R', 2022, 5000, 350000.00, 'Benzin', '3.5 L/100km', 471, 47, 'Manuel', 'Motosiklet', 'Coupe', 2, 30, 'Hasarsýz', 0.00, 2, 'Kýrmýzý', 5);


SELECT * FROM Arabalar