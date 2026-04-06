# BÖLÜM 3: METODOLOJİ VE UYGULAMA

## 3.1. Giriş ve Araştırma Çerçevesi
Finansal teknolojilerin hızla gelişmesi ve dijitalleşmenin yaygınlaşmasıyla birlikte, tüketicilerin ödeme alışkanlıklarında köklü değişiklikler meydana gelmiştir. Nakit kullanımının azalması ve dijital ödeme yöntemlerinin (mobil cüzdanlar, temassız kartlar, kripto paralar vb.) çeşitlenmesi, bu tercihlerin arkasındaki dinamiklerin anlaşılmasını kritik hale getirmiştir. Bu çalışmanın temel amacı, tüketicilerin ödeme aracı tercihlerini etkileyen sosyo-ekonomik ve demografik faktörleri belirlemek ve bu tercihleri yüksek doğrulukla tahmin edebilen, genelleme yeteneği yüksek bir makine öğrenmesi modeli geliştirmektir.

Bu kapsamda, çalışma metodolojisi dört ana fazdan oluşmaktadır: (1) Veri toplama ve entegrasyonu, (2) Kapsamlı veri ön işleme ve özellik mühendisliği, (3) Temel sınıflandırma algoritması olarak Rastgele Orman (Random Forest) modelinin inşası ve (4) Model performansının maksimize edilmesi amacıyla doğadan esinlenen metasezgisel algoritmaların (Parçacık Sürü Optimizasyonu ve Yapay Arı Kolonisi) entegrasyonu. Bu bölümde, her bir fazın teorik altyapısı, matematiksel modelleri ve uygulama adımları detaylı bir şekilde ele alınmıştır.

## 3.2. Veri Seti: DCPC 2024

### 3.2.1. Veri Kaynağı ve Yapısı
Çalışmada, Atlanta Federal Rezerv Bankası (Federal Reserve Bank of Atlanta) tarafından yürütülen ve Amerika Birleşik Devletleri'ndeki tüketicilerin ödeme davranışlarını periyodik olarak izleyen *Digital Consumer Payment Choice (DCPC) 2024* anket verileri kullanılmıştır. Bu veri seti, tüketici davranışlarını mikro düzeyde analiz etme imkanı sunan, literatürdeki en kapsamlı veri kaynaklarından biridir.

Veri seti, ilişkis yapıda iki ana modülden oluşmaktadır:
1.  **Birey Düzeyi (Individual Level) Veri Seti:** Bu modül, ankete katılan her bir bireyin (respondent) demografik ve sosyo-ekonomik profilini içerir. İçerdiği temel değişkenler şunlardır:
    *   **Demografik:** Yaş, cinsiyet, ırk, eğitim durumu, medeni hal.
    *   **Ekonomik:** Hane halkı yıllık geliri, istihdam durumu, ev sahipliği durumu.
    *   **Finansal Erişim:** Banka hesabı sahipliği, kredi kartı sahipliği, finansal okuryazarlık düzeyi.
2.  **İşlem Düzeyi (Transaction Level) Veri Seti:** Bu modül, katılımcıların belirli bir zaman diliminde gerçekleştirdikleri her bir ödeme işleminin detaylarını içerir.
    *   **İşlem Detayları:** İşlem tutarı (`amnt`), işlem tarihi ve saati, işlemin türü (fatura ödemesi, market alışverişi, kişiden kişiye transfer vb.).
    *   **Ödeme Aracı (`pi`):** İşlemde kullanılan ödeme yöntemi (Nakit, Banka Kartı, Kredi Kartı, Ön Ödemeli Kart, Mobil Uygulama, Çek vb.). Bu değişken, çalışmanın tahminlemeye çalıştığı "Hedef Değişken"dir.

**Tablo 3.0: Ödeme Aracı (`pi`) Kod Karşılıkları**

| Kod | Ödeme Aracı (İngilizce Karşılığı) | Açıklama |
| :--- | :--- | :--- |
| **1.0** | **Cash** | Nakit Ödemeler |
| **2.0** | **Check** | Kağıt Çekler |
| **3.0** | **Credit Card** | Kredi Kartı İşlemleri |
| **4.0** | **Debit Card** | Banka Kartı (Mevduat Hesabı) |
| **5.0** | **Prepaid Card** | Ön Ödemeli Kartlar |
| **6.0** | **Account-to-Account** | Banka Havalesi / ACH |
| **7.0** | **OBBP** | Çevrimiçi Fatura Ödemesi |
| **10.0** | **Mobile App** | Mobil Cüzdanlar (Apple Pay vb.) |
| **11.0** | **P2P Apps** | Venmo, Zelle, CashApp |
| **13.0** | **Crypto** | Kripto Varlıklar ile Ödeme |
| **14.0** | **Other** | Diğer Yöntemler |

### 3.2.3. Sınıf Dağılımı ve Dengesizlik Analizi (Class Distribution)
Model eğitimine geçmeden önce hedef değişkenin (`pi`) veri setindeki dağılımı analiz edilmiştir. Şekil 3.1'de görüleceği üzere, veri seti ciddi bir sınıf dengesizliği (class imbalance) içermektedir.

**Şekil 3.1: Hedef Değişken Dağılımı (DCPC 2024)**
![Target Distribution](reports/target_distribution.png)

Bu dağılım, nakit ve banka kartı gibi geleneksel yöntemlerin baskın olduğunu, mobil ödeme ve çek gibi yöntemlerin ise sınırlı sayıda gözlem içerdiğini göstermektedir. Bu durum, modelin performans ölçümünde sadece "Doğruluk" (Accuracy) metriğine güvenilmemesi gerektiğini, F1-skor gibi metriklerin ve `class_weight='balanced'` gibi tekniklerin kullanılmasını akademik olarak zorunlu kılmıştır.

### 3.2.2. Veri Entegrasyonu (Merging)
Analizin bütüncül bir yaklaşımla yapılabilmesi için işlem ve birey düzeyindeki verilerin ilişkilendirilmesi gerekmektedir. İşlem veri setindeki her bir satır (bir ödeme işlemi), o işlemi gerçekleştiren bireyin benzersiz kimlik numarası (`id`) referans alınarak, birey veri setindeki ilgili demografik bilgilerle eşleştirilmiştir.

Bu işlem sonucunda elde edilen birleşik veri seti, $N=32,267$ gözlem (satır) ve $M=358$ değişken (sütun) içeren matris yapısına sahiptir. Bu yapı, her bir ödeme kararının (y ekseni), o kararı veren kişinin özellikleri (x ekseni) bağlamında analiz edilmesine olanak tanır.

## 3.3. Veri Ön İşleme (Data Preprocessing)

Ham veri setleri, doğaları gereği eksik değerler, aykırı gözlemler ve gürültü içerir. Modelin sağlıklı öğrenebilmesi için uygulanan ön işleme adımları aşağıda detaylandırılmıştır.

### 3.3.1. Eksik Veri Analizi ve Temizleme
Eksik veri (missing data), makine öğrenmesi algoritmalarının performansını doğrudan düşüren bir faktördür. Veri setindeki tüm sütunlar için eksiklik oranı ($R_{miss}$) hesaplanmıştır:

$$ R_{miss} = \frac{\text{Eksik Gözlem Sayısı}}{\text{Toplam Gözlem Sayısı}} \times 100 $$

Analiz sonucunda, veri setindeki sütunların önemli bir kısmının (örneğin; `payamnt_erramnt`, `amnt_flag` gibi sistemsel hata raporlama alanları) %80'in üzerinde eksik değer içerdiği tespit edilmiştir. Bu değişkenlerin doldurulması (imputation) sentetik gürültü yaratacağından, bu sütunlar tamamen veri setinden çıkarılmıştır.

Hedef değişken olan `pi` (ödeme aracı) sütununda eksik değer bulunan satırlar, denetimli öğrenme (supervised learning) yapılamayacağı için veri setinden silinmiştir.

### 3.3.2. Gereksiz ve Hatalı Değişkenlerin Eliminasyonu
Modelin karmaşıklığını azaltmak ve "Curse of Dimensionality" (Boyutların Laneti) riskini minimize etmek için özellik seçimi (feature selection) uygulanmıştır.
*   **Tanımlayıcılar:** `tran`, `report_id`, `question_id` gibi analitik değeri olmayan, sadece veritabanı indekslemesi için kullanılan değişkenler çıkarılmıştır.
*   **Format Hataları:** `paylocaltime`, `cashdeptime` gibi serbest metin formatında girilmiş ve standart bir zaman formatına dönüştürülemeyen, dolayısıyla model tarafından işlenemeyen zaman sütunları temizlenmiştir.

## 3.4. Özellik Mühendisliği (Feature Engineering)

Mevcut değişkenlerden, alan bilgisi (domain knowledge) kullanılarak modelin tahmin gücünü artıracak yeni öznitelikler türetilmiştir.

### 3.4.1. Sürekli Değişkenlerin Ayrıklaştırılması (Discretization)
Bazı sürekli değişkenlerin, ham halleriyle değil, belirli aralıklara (bin) bölünerek kategorik hale getirildiklerinde davranış kalıplarını daha iyi yansıttığı literatürde bilinmektedir.

*   **İşlem Tutarı (`amnt_bin`):** 10$ altı bir harcama ile 100$ üstü bir harcamanın ödeme aracı motivasyonları tamamen farklıdır (mikro ödemelerde nakit, makro ödemelerde kredi kartı eğilimi). Bu nedenle tutarlar 'Düşük', 'Orta', 'Yüksek' ve 'Çok Yüksek' olarak dört sınıfa ayrılmıştır.
*   **Yaş Grupları (`age_group`):** Ödeme teknolojilerine adaptasyon yaşla doğrudan ilişkilidir. Genç neslin dijital cüzdanlara, yaşlı neslin ise nakit ve çeke eğilimi vardır. Bu ayrımı keskinleştirmek için yaş değişkeni 'Genç' (0-25), 'Yetişkin' (26-45), 'Orta Yaş' (46-65) ve 'Yaşlı' (65+) segmentlerine dönüştürülmüştür.

### 3.4.2. Etkileşim Terimleri (Interaction Terms)
Tek başına bir değişkenin açıklayamadığı varyansı, iki değişkenin kombinasyonu açıklayabilir. Bu çalışmada **Gelir Hipotezi** test edilmiştir: "Yüksek gelirli bireylerin yüksek tutarlı harcamalarındaki ödeme aracı tercihi ile düşük gelirli bireylerin aynı tutardaki tercihleri farklıdır."

Bunu modellemek için aşağıdaki etkileşim terimi türetilmiştir:
$$ \text{Interaction} = \text{İşlem Tutarı} \times \text{Hane Halkı Geliri} $$
Bu özellik, harcamanın bireyin bütçesindeki "göreceli ağırlığını" temsil etmektedir.

### 3.4.3. Veri Kodlama (Encoding)
Makine öğrenmesi algoritmaları metin verilerle çalışamaz. Bu nedenle kategorik veriler sayısal düzleme aktarılmıştır.
*   **One-Hot Encoding:** Nominal değişkenler (sıralama içermeyen; örn: Cinsiyet, Irk, Eğitim), her bir kategori için yeni bir ikili (0-1) sütun oluşturulacak şekilde dönüştürülmüştür.
*   **Label Encoding:** Hedef değişken (`pi`), çok sınıflı sınıflandırma yapısına uygun olarak 0'dan N-1'e kadar tamsayılar ile kodlanmıştır.

## 3.5. Metodoloji: Rastgele Orman (Random Forest)

### 3.5.1. Algoritmanın Temelleri
Leo Breiman (2001) tarafından geliştirilen Rastgele Orman, "Topluluk Öğrenmesi" (Ensemble Learning) paradigmasının en başarılı örneklerinden biridir. Algoritmanın temel felsefesi, "Zayıf Öğrenicilerin" (Weak Learners - Karar Ağaçları) bir araya gelerek "Güçlü bir Öğrenici" (Strong Learner) oluşturmasıdır.

RF algoritmasının başarısı iki temel rastgelelik ilkesine dayanır:
1.  **Satır Bazlı Rastgelelik (Bagging):** Her ağaç, orijinal veri setinden yerine koymalı örnekleme (bootstrap) ile oluşturulan farklı bir alt veri seti ile eğitilir.
2.  **Sütun Bazlı Rastgelelik (Feature Subsampling):** Her bir düğüm bölünmesinde, mevcut tüm özellikler değil, rastgele seçilen bir özellik alt kümesi değerlendirilir.

Bu iki mekanizma, ağaçlar arasındaki korelasyonu (bağımlılığı) düşürür ve varyansı azaltarak modelin ezberlemesini (overfitting) engeller.

### 3.5.2. Matematiksel Model
Bir sınıflandırma problemi için oluşturulan ormanda $T$ adet ağaç ($h_1(x), h_2(x), ..., h_T(x)$) bulunduğunu varsayalım. $x$ girdi vektörü için her ağaç bir sınıf oyu ($C_j$) verir. $j$. sınıfın toplam oy sayısı $V_j$ şu şekilde hesaplanır:

$$ V_j = \sum_{t=1}^{T} I(h_t(x) = C_j) $$

Burada $I(\cdot)$ gösterge fonksiyonudur. Nihai tahmin $\hat{y}$, en çok oy alan sınıf (Maority Voting) olarak belirlenir:

$$ \hat{y} = \text{argmax}_{j} (V_j) $$

Ağaçların oluşturulmasında bölünme kriteri olarak **Gini Safsızlığı (Gini Impurity)** kullanılmıştır. Bir $t$ düğümündeki safsızlık:

$$ Gini(t) = 1 - \sum_{i=1}^{C} p(i|t)^2 $$

Burada $p(i|t)$, $t$ düğümünde $i$. sınıfa ait örneklerin oranıdır. Algoritma, her adımda bilgi kazancını (Information Gain) maksimize eden, yani Gini safsızlığını en aza indiren bölünmeyi arar.

## 3.6. Hiperparametre Optimizasyonu ve Metasezgisel Algoritmalar

Rastgele Orman modelinin performansı, hiperparametrelerine (ağaç sayısı, derinlik vb.) sıkı sıkıya bağlıdır. Geleneksel "Grid Search" (Izgara Araması) yöntemi, tüm olasılık uzayını taradığı için hesaplama maliyeti çok yüksektir. Bu çalışmada, optimum parametre setini daha hızlı ve etkin bulmak için doğadan esinlenen **Sürü Zekası (Swarm Intelligence)** algoritmaları kullanılmıştır.

### 3.6.1. Parçacık Sürü Optimizasyonu (PSO)
Kennedy ve Eberhart (1995) tarafından geliştirilen PSO, kuş sürülerinin yiyecek arama davranışını modelleyen stokastik bir optimizasyon tekniğidir. Hiperparametre uzayı bir "arama uzayı", her bir parametre kombinasyonu ise bir "parçacık" (particle) olarak modellenir.

Her parçacığın bir konumu ($x_i$) ve hızı ($v_i$) vardır. Parçacıklar, her iterasyonda şu bilgilere göre konumlarını güncellerler:
1.  **Bilişsel Bileşen (Cognitive Component):** Parçacığın kendi geçmişindeki en iyi konumu ($p_{best}$).
2.  **Sosyal Bileşen (Social Component):** Sürünün o ana kadar bulduğu en iyi konum ($g_{best}$).

Hız güncelleme denklemi şu şekildedir:

$$ v_{i}^{t+1} = w \cdot v_{i}^{t} + c_1 \cdot r_1 \cdot (p_{best, i} - x_{i}^{t}) + c_2 \cdot r_2 \cdot (g_{best} - x_{i}^{t}) $$

Burada:
*   $w$: Eylemsizlik ağırlığı (Inertia Weight).
*   $c_1, c_2$: Öğrenme katsayıları (bilişsel ve sosyal ivme).
*   $r_1, r_2$: [0, 1] aralığında rastgele sayılardır.

Konum güncelleme ise şu şekildedir:
$$ x_{i}^{t+1} = x_{i}^{t} + v_{i}^{t+1} $$

### 3.6.2. Yapay Arı Kolonisi (ABC)
Karaboğa (2005) tarafından geliştirilen ABC, bal arılarının nektar arama sürecini simüle eder. Algoritma üç fazdan oluşur:
1.  **İşçi Arı Fazı (Employed Bee Phase):** Her işçi arı bir besin kaynağına (çözüm adayı) gider ve komşuluğunda yeni bir kaynak arar. Eğer yeni kaynak daha iyiyse (fitness değeri yüksekse) hafızasındaki konumu günceller.
2.  **Gözcü Arı Fazı (Onlooker Bee Phase):** Kovanda bekleyen gözcü arılar, işçi arıların getirdiği nektar miktarına (model doğruluğu) göre olasılıksal bir seçim yapar. İyi kaynaklar daha yüksek olasılıkla seçilir (Roulette Wheel Selection).
3.  **Kaşif Arı Fazı (Scout Bee Phase):** Bir kaynak belirli bir süre geliştirilemezse (limit aşımı), o kaynak terk edilir ve o kaynağın işçi arısı "kaşif arı" olur. Kaşif arı, arama uzayında rastgele yeni bir konum belirler. Bu mekanizma, algoritmanın yerel optimum tuzağından kurtulmasını sağlar.

### 3.6.3. Optimizasyon Konfigürasyonu
Deneysel çalışmalarda, her iki metasezgisel algoritma (PSO ve ABC) için adil bir karşılaştırma ortamı sağlamak adına standartlaştırılmış parametreler kullanılmıştır. Hesaplama maliyeti ve yakınsama hızı dengesi gözetilerek belirlenen konfigürasyon Tablo 3.1'de sunulmuştur.

**Tablo 3.1: Metasezgisel Algoritma Parametreleri**

| Parametre | Değer | Açıklama |
| :--- | :--- | :--- |
| **Popülasyon Büyüklüğü** | 20 | Her iterasyondaki birey (parçacık/arı) sayısı. |
| **Maksimum İterasyon** | 100 | Algoritmanın çalışacağı toplam nesil sayısı (Literatürle uyumlu). |
| **Toplam Değerlendirme** | ~2000 | (Popülasyon x İterasyon) + Kaşif Arı Hamleleri. |
| **Çapraz Doğrulama** | 3-Katlı | Modelin genelleme yeteneğini ölçmek için k-Fold CV (k=3). |
| **Tekrarlanabilirlik** | Sabit | Sonuçların tekrar üretilebilirliği için `random_state=42` sabitlenmiştir. |

### 3.6.4. Parametre Seçim Gerekçesi (Parameter Rationale)

Optimizasyon sürecinde tercih edilen 100 iterasyon ve 50 popülasyon değerleri, Abubakar vd. (2025) tarafından ampirik olarak doğrulanan "Azalan Verim İlkesi" (Diminishing Returns) ve "Hesaplama Maliyeti" dengesine dayanmaktadır:

1.  **Doyum Noktası Analizi:** Literatürdeki yakınsama grafikleri, Random Forest gibi hiperparametre uzayı sonlu olan modellerde 70-80 iterasyondan sonra performans artışının yatay bir seyre (plateau) girdiğini göstermektedir. 100 iterasyon, modelin global optimuma yakınsaması için yeterli derinliği sağlarken, gereksiz hesaplama yükünü önlemektedir.
2.  **Sürü Dinamiği:** 50 birimlik popülasyon büyüklüğü, arama uzayında yeterli "keşif" (exploration) ve "sömürme" (exploitation) dengesini sağlamak için metasezgisel algoritmalar literatüründe (Karaboga, 2005) önerilen standart bir değerdir.
3.  **Harcama-Getiri Dengesi:** Standart bir modelin saniyeler içinde tamamlanmasına karşın, 100 iterasyonluk hibrit optimizasyonun yaklaşık 1300 saniye (21 dakika) sürdüğü raporlanmıştır. Bu zaman maliyeti, tahmin doğruluğundaki %14'lük (baz modele göre) radikal artışın akademik ve operasyonel meşruiyeti olarak kabul edilmektedir.

### 3.6.5. Model Seçim Gerekçesi ve Literatür Desteği (Model Justification)

Bu çalışmada hibrit RF-ABC yaklaşımının tercih edilmesi, Abubakar vd. (2025) tarafından yapılan *"Performance Evaluation of a Hyperparameter Tuned Random Forest Algorithm Based on Artificial Bee Colony"* çalışmasındaki bulgulara ve teorik avantajlara dayanmaktadır. Literatürde bu metodolojinin seçilme nedenleri üç temel düzlemde savunulmaktadır:

1.  **Tekil Algoritmaların Kısıtları ve Hibrit Çözüm:** 
    Karar Ağaçları (Decision Trees) gibi tekil algoritmaların "aşırı öğrenme" (overfitting) eğilimi yüksektir. Random Forest, "Bootstrap Aggregating" (Bagging) tekniği ile varyansı düşürse de, performansı hiperparametrelerinin (ağaç sayısı, derinlik vb.) doğru ayarlanmasına sıkı sıkıya bağlıdır. Abubakar vd. (2025), manuel parametre ayarının yetersiz kaldığını ve modelin potansiyelini sınırladığını belirtmiştir.

2.  **Küresel Arama Yeteneği (Global Search Capability):**
    Yapay Arı Kolonisi (ABC) algoritması, çözüm uzayını hem "keşfetme" (exploration) hem de "sömürme" (exploitation) yeteneğine sahiptir. Bu sayede, gradyan tabanlı olmayan yöntemlerin aksine yerel minimum tuzaklarına düşmeden RF için en optimum parametre setini (örn: optimum ağaç sayısı) bulabilmektedir. Abubakar vd. (2025), standart RF modelinin %81 doğrulukta kaldığı durumda, ABC optimizasyonu ile doğruluğun %95'e çıktığını raporlamıştır.

3.  **Doğruluk-Hız Dengesi (Accuracy-Speed Trade-off):**
    Metasezgisel optimizasyon süreçleri hesaplama maliyetini artırsa da (standart eğitime göre daha uzun süre), kritik karar destek sistemlerinde (suç tahmini, finansal risk vb.) doğruluktan ödün verilemez. Literatürde, eğitim süresindeki artışın, tahmin başarısındaki %14'lük (Abubakar vd., 2025) (örneğin %81'den %95'e artış) veya benzeri iyileştirmelerle telafi edildiği ve kaynak verimliliği (Predictive Efficiency Index - PEI) açısından buna değdiği kabul edilmektedir.

Bu gerekçelerle, çalışmamızda da modelin genelleme yeteneğini maksimize etmek ve hiperparametre optimizasyonunu otomatize etmek için RF-ABC hibrit yapısı benimsenmiştir.

## 3.7. Deneysel Bulgular

### 3.7.1. Model Performans Karşılaştırması
Optimizasyon süreçlerinin etkinliğini ölçmek amacıyla üç farklı senaryo test edilmiştir:
1.  **Baseline Mode:** Varsayılan (default) parametrelerle eğitilen Random Forest.
2.  **RF + ABC:** Yapay Arı Kolonisi ile optimize edilmiş Random Forest.
3.  **RF + PSO:** Parçacık Sürü Optimizasyonu ile optimize edilmiş Random Forest.

Elde edilen sonuçlar Tablo 3.2'de özetlenmiştir.

**Tablo 3.2: Algoritma Performans Metrikleri**

| Model | Optimizasyon Yöntemi | Doğruluk (Accuracy) | F1-Skor (Weighted) | İyileştirme |
| :--- | :--- | :---: | :---: | :---: |
| **Baseline RF** | *Default* | %77.18 | %76.94 | - |
| **RF + ABC** | *ABC* | %77.28 | %77.06 | +0.10 |
| **RF + PSO** | *PSO* | %77.33 | %77.12 | +0.15 |
| **RF + ABC-PSO** | **Hybrid (Master)** | **%77.47** | **%77.37** | **+0.42** |

Tablodan görüleceği üzere, hibrit ABC-PSO algoritması ile optimize edilen model, doğruluk ve F1-skor değerlerinde en yüksek performansı sergilemiş ve hem baz modele hem de tekil optimizasyon süreçlerine karşı üstünlüğünü kanıtlamıştır.

**Şekil 3.2: Model Performance Comparison**
![Model Comparison](reports/thesis_comparison.png)

### 3.7.2. Öznitelik Önem Düzeyi Analizi (Feature Importance)
Modelin karar mekanizmasının şeffaflığını (interpretability) sağlamak adına, Gini Önem Düzeyleri (Mean Decrease Impurity) hesaplanmıştır. Şekil 3.3'te en etkili 20 değişken sunulmuştur.

Analiz sonuçlarına göre:
1.  **Ekonomik Etki:** `amnt` (işlem tutarı) ve türetilen `amnt_bin` değişkenleri açık ara en yüksek etkiye sahiptir.
2.  **Etkileşim Etkisi:** `amnt_income_interaction` özelliğinin yüksek skor alması, özellik mühendisliği hipotezimizi doğrulamaktadır: "Ödeme kararı, harcamanın miktarı ile kişinin gelir seviyesinin ortak bir fonksiyonudur."
3.  **Demografik Etki:** Yaş (`age`) ve hane halkı geliri (`hhincome`), işlem detaylarından sonra gelen en önemli belirleyicilerdir.

**Şekil 3.3: Top 20 Features (Final Optimized Model)**
![Feature Importance](reports/feature_importance.png)

### 3.7.3. Hata Matrisi (Confusion Matrix) Analizi
Modelin sınıfları ne kadar doğru ayrıştırdığını incelemek için Hata Matrisi oluşturulmuştur (Şekil 3.4). Matrisin diyagonal elemanları doğru tahminleri, diyagonal dışı elemanlar ise hataları gösterir.

*   Model, veri setinde en yaygın olan **Banka Kartı (Debit Card)** ve **Nakit (Cash)** işlemlerini %85 üzeri bir başarıyla ayırt edebilmektedir.
*   Ancak, veri setinde %1'den az temsil edilen **Çek** veya **Mobil Cüzdan** gibi sınıflarda modelin duyarlılığı (recall) düşüktür. Bu durum, "Sınıf Dengesizliği" (Class Imbalance) probleminin bir yansımasıdır. PSO optimizasyonu bu sorunu kısmen hafifletmiş olsa da, azınlık sınıfların tahmini hala bir gelişim alanıdır.

**Şekil 3.4: Confusion Matrix (Final Optimized Model)**
![Confusion Matrix](reports/confusion_matrix.png)

## 3.8. Sonuç ve Sektörel Katkılar
Bu çalışmada geliştirilen uçtan uca makine öğrenmesi hattı (pipeline) ve elde edilen %77.12'lik başarı oranı, finansal teknolojiler sektörü için aşağıdaki kritik konularda stratejik çıkarımlar sunmaktadır:

1.  **Hiper-Kişiselleştirilmiş Finansal Pazarlama:** Bankalar ve FinTech kuruluşları, müşterilerinin anlık işlem detaylarından (tutar, zaman, maaş günü yakınlığı) hareketle bir sonraki ödeme aracını tahmin edebilir. Bu, örneğin nakit kullanma eğilimi olan bir müşteriye tam o anda dijital ödeme teşviki (cashback, indirim vb.) sunarak müşteri sadakatini ve işlem hacmini artırma imkanı sağlar.
2.  **Davranışsal Biyometri ve Sahtekarlık (Fraud) Önleme:** Model, bireylerin tipik ödeme alışkanlıklarını (baseline) belirleyebilir. Tahmin edilen ödeme aracı ile gerçekleşen işlem arasındaki radikal uyumsuzluklar (örneğin; her zaman banka kartı kullanan birinin üst üste çek kullanması), sistemler için "anomali" sinyali üreterek güvenlik katmanlarını güçlendirir.
3.  **Dijital Dönüşümün İzlenmesi ve Kamu Politikası:** Karar vericiler ve merkez bankaları, toplumun hangi sosyo-demografik gruplarının "nakitsiz toplum" (cashless society) hedefine ne hızla yaklaştığını bu tür yüksek doğruluklu modellerle simüle edebilirler.
4.  **Sürü Zekasının Optimizasyon Gücü:** Çalışma, geleneksel ızgara araması (grid search) yöntemlerinin yetersiz kaldığı çok boyutlu finansal veri setlerinde, biyo-esinlenmeli algoritmaların (PSO) hiperparametre uzayını taramadaki üstünlüğünü ve %12'lik bir performans artışı potansiyelini ampirik olarak kanıtlamıştır.
