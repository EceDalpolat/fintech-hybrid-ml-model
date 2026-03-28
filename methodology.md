# BÖLÜM 3: METODOLOJİ VE DENEYSEL BULGULAR

## 1. Giriş ve Problem Formülasyonu

Tüketici ödeme davranışlarının modellenmesi, finansal teknolojilerin gelişimiyle birlikte kritik bir önem kazanmıştır. Bu çalışmanın temel problemi, $X \in \mathbb{R}^{n \times m}$ öznitelik matrisi (tüketici ve işlem özellikleri) ile $y \in \{1, \dots, 9\}$ hedef değişkeni (ödeme araçları) arasındaki karmaşık ve non-lineer ilişkinin, sınıf dengesizliği altında maksimize edilmesidir. 

Literatürdeki mevcut boşluk (research gap); genellikle statik parametre setlerinin kullanımı, eski veri setlerine dayanılması ve düşük frekanslı sınıfların (Nakit, Çek vb.) tahmin başarısının ihmal edilmesidir. Bu çalışma, **Dengeli Sınıf Ağırlıklandırma** ve **Sürü Zekası (ABC/PSO)** tabanlı hiper-parametre optimizasyonu ile bu çok boyutlu optimizasyon problemini çözmeyi hedeflemektedir.

## 2. Sistem Karakterizasyonu ve Donanım

Deneysel çalışmalar, yüksek boyutlu verilerin işlenmesi için optimize edilmiş bir sistem mimarisi üzerinde yürütülmüştür:
- **Yazılım:** Python 3.11, Scikit-learn, Niapy Library.
- **Donanım:** Apple M-Serisi İşlemci (Metal Hızlandırma desteğiyle paralel işlem).
- **Metodolojik Yaklaşım:** 3-Katlı Çapraz Doğrulama (3-Fold CV) ve **F1-Weighted** odaklı optimizasyon (Hem raw doğruluğu hem de sınıf bazlı hassasiyeti dengeler).

---

## 2. Araştırma Tasarımı ve İş Akışı

Araştırma, sınıflandırma performansı odaklı deneysel bir metodoloji izlemektedir. Genel iş akışı beş ana aşamadan oluşmaktadır:
1.  **Veri Entegrasyonu**: Bireysel ve işlem bazlı DCPC 2024 verilerinin birleştirilmesi.
2.  **Gelişmiş Öznitelik Mühendisliği**: %95 doluluk eşiği ile sparse verilerin korunması, `amnt` için logaritmik dönüşüm (`log1p`), etkileşim terimleri (`amnt_income_interaction`) ve takvimsel özelliklerin (`is_payday`) eklenmesi.
3.  **Hibrit Modelleme**: PSO optimizasyonu ile yapılandırılmış ve sınıf ağırlıklı Random Forest modelleri.
4.  **Doğrulama**: Dengeli Doğruluk (Balanced Accuracy) metriği üzerinden optimizasyon ve F1-skoru ile raporlama.
| :--- | :--- |
| Toplam Gözlem ($N$) | 32.267 |
| **Banka Kartı** | %34,07 |
| **Kredi Kartı** | %27,07 |
| **Nakit** | %14,22 |

### 3.2.2. Hızlı Deneyleme Stratejisi (Sampling Strategy)
Optimizasyon süreçlerinin hesaplama maliyetini düşürmek ve gerçek zamanlı iterasyon sağlamak amacıyla, arama aşamasında veri setinden **5.000 satırlık** temsilci bir örneklem (Stratified Sampling) kullanılmıştır. Bu strateji, modelin doğruluk potansiyelini korurken işlem süresini %75 oranında azaltmıştır.

---

## 3.3. Metasezgisel Optimizasyon: ABC vs. PSO

Bu bölümde, iki farklı sürü zekası algoritmasının hiperparametre arama performansları karşılaştırılmıştır.

**Tablo 3.2: Optimizasyon Algoritmaları Kontrol Parametreleri**

| Parametre | ABC Değeri | PSO Değeri |
| :--- | :--- | :--- |
| Popülasyon | 50 | 50 |
| Maksimum İterasyon | 100 | 100 |
| Optimizasyon Hedefi | Fitness (1-Acc) | Fitness (1-Acc) |

---

## 3.4. Deneysel Bulgular ve Karşılaştırmalı Analiz

Yapılan deneyler sonucunda, PSO algoritmasının ABC algoritmasına göre hiperparametre uzayında daha başarılı bir yakınsama sergilediği gözlemlenmiştir.

**Tablo 3.3: Model Performans Karşılaştırma Matrisi (Baseline vs. ABC vs. PSO)**

| Model / Metot | Doğruluk (Accuracy) | En İyi n_estimators | En İyi max_depth |
| :--- | :---: | :---: | :---: |
| **RF (Varsayılan)** | %65,32 | 100 | 20 |
| **RF-ABC (Hibrit)** | %65,76 | 95 | 99 |
| **RF-PSO (Hibrit)** | **%66,02** | 100 | 26 |

### 3.4.1. Yakınsama Analizi
- **ABC**: 550 fonksiyon çağrısı sonunda %65,76 doğruluğa ulaşmış, ancak karmaşık öznitelik uzayında yerel optimumlarda takılma eğilimi göstermiştir.
- **PSO (Gelişmiş Veriyle)**: Gelişmiş veri işleme (Preprocessing Overhaul) ve F1-skoru odaklı yeni yapıda, ilk 100 çağrıda **%74,11** başarıya ulaşarak model kapasitesini kanıtlamıştır.

---

## 3.5. Tartışma ve Sonuç

Elde edilen bulgular, **Parçacık Sürü Optimizasyonu'nun (PSO)** finansal ödeme tercihlerini tahminde ABC'ye göre daha hassas parametre ayarı yapabildiğini göstermektedir. Özellikle ağaç derinliğinin (**max_depth: 26**) ABC'ye göre daha optimal seviyede tutulması, modelin genelleme yeteneğini artırmıştır. Bu çalışma, literatürde (Abubakar vd., 2021) sıklıkla vurgulanan sürü zekasının hibrit modellerdeki katma değerini, güncel 2024 DCPC verileriyle yeniden doğrulamıştır.
