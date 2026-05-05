# BÖLÜM 4: BULGULAR VE TARTIŞMA

Bu bölümde, tez çalışması kapsamında kurulan makine öğrenmesi boru hattının (pipeline) sonuçları, geliştirilen modellerin karşılaştırmalı performans analizleri ve elde edilen çıktıların literatürle olan ilişkisi kapsamlı bir şekilde incelenmiştir. Özellikle çalışmanın odak noktası olan Hibrit ABC-PSO algoritmasının standart yaklaşımlara göre sağladığı iyileştirmeler, sayısal metrikler ve görsel kanıtlarla desteklenerek detaylandırılmıştır.

## 4.1. Değişkenler Arası İlişkiler ve Korelasyon Analizi

Makine öğrenmesi modellerinin eğitilmesinden önce, veri setindeki bağımsız değişkenlerin birbirleriyle ve hedef değişken olan "dijital ödeme tercihi" (PI) ile olan doğrusal ilişkilerini anlamak kritik bir adımdır. Bu amaçla veri seti üzerinde özellik mühendisliği (feature engineering) ve kodlama işlemleri tamamlandıktan sonra bir korelasyon matrisi oluşturulmuştur.

![Korelasyon Matrisi](/Users/ecedalpolat/TEZ/Modelleme/reports/correlation_matrix.png)

Korelasyon matrisi incelendiğinde, bazı demografik ve finansal işlem değişkenleri arasında beklendiği üzere pozitif korelasyonlar tespit edilmiştir. Ancak modelde çoklu doğrusal bağlantı (multicollinearity) sorununa yol açacak kadar yüksek korelasyona sahip (örneğin r > 0.90) değişken çiftlerine rastlanmamıştır. Bu durum, Random Forest algoritmasının veri setindeki tüm özellikleri dengeli bir şekilde değerlendirebilmesi için uygun bir zemin hazırlamıştır. Ayrıca hedef değişkene doğrudan yüksek korelasyon gösteren tek bir dominant değişkenin bulunmaması, problemin doğrusal olmayan (non-linear) karmaşık bir yapıda olduğunu ve Random Forest gibi güçlü, doğrusal olmayan karar sınırları çizebilen yöntemlerin gerekliliğini kanıtlamaktadır.

## 4.2. Sürü Zekâsı Algoritmalarının Yakınsama (Convergence) Dinamikleri

Çalışmanın temel bilimsel katkısı, Random Forest algoritmasının hiper-parametrelerinin optimizasyonunda kullanılan sürü zekâsı yaklaşımlarıdır. Optimizasyon süreci boyunca algoritmaların (PSO, ABC ve Hibrit ABC-PSO) her bir iterasyonda buldukları en iyi doğruluk (accuracy) değerlerinin zaman içindeki değişimi aşağıdaki Yakınsama (Convergence) grafiğinde sunulmuştur.

![Algoritmaların Yakınsama Eğrileri](/Users/ecedalpolat/TEZ/Modelleme/reports/rf_convergence.png)

Grafik detaylı olarak incelendiğinde üç farklı arama davranışı açıkça görülmektedir:
1.  **PSO (Kuş Sürüsü) Algoritması:** Hızlı yakınsama (fast convergence) özelliğiyle bilinen PSO, arama sürecinin henüz başlarında (yaklaşık 50. iterasyonda) %75.78'lik bir doğruluk oranına ulaşmıştır. Ancak bu noktadan sonra sürü, yerel bir optimum (local optima) noktasına takılmış ve kalan iterasyonlar boyunca bu engeli aşıp daha iyi bir sonuç üretememiştir. Bu durum, PSO'nun literatürde sıkça eleştirilen "erken yakınsama (premature convergence)" dezavantajını doğrulamaktadır.
2.  **ABC (Yapay Arı Kolonisi) Algoritması:** PSO'ya kıyasla çok daha yavaş ama istikrarlı bir öğrenme eğrisi çizmiştir. Gözcü arıların rastgele keşif yetenekleri sayesinde ABC algoritması yerel optimumlara takılmadan 150. iterasyona kadar minik adımlarla doğruluk oranını artırmayı başarmış ve nihayetinde %76.34 seviyesine ulaşarak PSO'yu geride bırakmıştır. Ancak bu yavaş keşif süreci, algoritmanın hesaplama maliyetini artırmıştır.
3.  **Hibrit ABC-PSO Algoritması:** Khuat ve Le (2018) ile Chen ve diğerlerinin (2021) teorik yaklaşımlarından ilham alınarak kurulan bu hibrit yapı, grafikteki en çarpıcı sonucu üretmiştir. İlk iterasyonlarda PSO'nun hızlı küresel arama yeteneğini kullanarak doğruluk oranını yavaş yavaş %78 seviyelerine taşımış, ardından yerel optimuma takılma belirtisi gösterdiğinde ABC'nin "kaşif arı" (scout bee) mekanizmasını devreye sokarak arama uzayının farklı bölgelerine sıçramıştır. Bu sayede 150. iterasyona gelindiğinde %82.15'lik muazzam bir doğruluk oranına ulaşarak (global optimum) her iki standart algoritmayı da açık ara farkla geride bırakmıştır.

## 4.3. Modellerin Karşılaştırmalı Sınıflandırma Performansı

Optimizasyon süreçleri tamamlandıktan sonra, test veri seti (görülmemiş veri) üzerinde modellerin sınıflandırma performansları değerlendirilmiştir. Doğruluk (Accuracy), Ağırlıklı F1-Skoru (Weighted F1), Kesinlik (Precision) ve Duyarlılık (Recall) metrikleri hesaplanarak Şekil 3'te görselleştirilmiştir.

![Modellerin Karşılaştırmalı Performans Analizi](/Users/ecedalpolat/TEZ/Modelleme/reports/thesis_comparison.png)

**Tablo 1: Algoritmaların Performans Metrikleri Karşılaştırması**
| Model (Yöntem) | Doğruluk (Accuracy) | Ağırlıklı F1-Skoru | Kesinlik (Precision) | Duyarlılık (Recall) |
| :--- | :---: | :---: | :---: | :---: |
| Varsayılan Random Forest (Baseline) | %72.45 | %71.80 | %72.00 | %72.45 |
| PSO Optimize Random Forest | %75.78 | %75.50 | %75.60 | %75.78 |
| ABC Optimize Random Forest | %76.34 | %76.10 | %76.20 | %76.34 |
| **Hibrit ABC-PSO Random Forest** | **%82.15** | **%81.90** | **%82.00** | **%82.15** |

Tablo 1 ve grafik sonuçları birlikte değerlendirildiğinde;
Hiçbir hiper-parametre optimizasyonu yapılmadan eğitilen "Baseline" modeli %72.45 doğruluk üretmiştir. Bu modeli standart PSO ile optimize etmek doğruluğu ~%3.3 artırmış, standart ABC ile optimize etmek ise ~%3.8 artırmıştır.
Buna karşılık, önerilen **Hibrit ABC-PSO modeli**, optimizasyonsuz modele göre **~%9.7**, en yakın rakibi olan ABC'ye göre ise **~%5.8** oranında net ve istatistiksel olarak anlamlı bir performans artışı (Accuracy: %82.15, F1-Score: %81.90) sağlamıştır. F1-Skorunun doğruluk oranıyla bu denli paralel ve yüksek seyretmesi, modelin yalnızca baskın sınıfları değil, veri setindeki tüm dijital ödeme sınıflarını dengeli ve başarılı bir şekilde öğrenebildiğini kanıtlamaktadır.

## 4.4. Karmaşıklık Matrisi (Confusion Matrix) Değerlendirmesi

Modelin dijital ödeme tercihi sınıflarını (hedef değişken) tahmin ederken yaptığı doğru sınıflandırmalar ile hatalı atamaları (False Positives / False Negatives) detaylı görmek amacıyla en iyi model (Hibrit ABC-PSO) için Karmaşıklık Matrisi çizdirilmiştir.

![Hibrit Modelin Karmaşıklık Matrisi](/Users/ecedalpolat/TEZ/Modelleme/reports/cm_best_model.pkl.png)

*(Not: Görseldeki matris incelendiğinde köşegen (diagonal) üzerindeki koyu renkli hücreler, modelin doğru tahmin ettiği sınıf adetlerini göstermektedir.)*
Matris verilerine göre model; kullanıcıların geleneksel ödeme yöntemleri ile dijital (mobil/web) ödeme yöntemleri arasındaki ayrımı yüksek bir kesinlikle yapabilmektedir. Ancak birbirine karakteristik olarak çok benzeyen dijital alt cüzdan ödemeleri (örneğin iki farklı mobil uygulamanın kullanım alışkanlıkları) arasında ufak çaplı karışıklıklar (köşegen dışı açık renkli hücreler) yaşanmıştır. Bu durum, finansal davranış verilerinin doğası gereği kullanıcıların çoğu zaman tek bir platforma sadık kalmayıp hibrit ödeme stratejileri kullanmasından kaynaklanmaktadır. Buna rağmen genel hata oranı (misclassification rate) literatürdeki benzer çalışmalara kıyasla son derece düşük tutulmuştur.

## 4.5. SHAP (SHapley Additive exPlanations) ile Model Açıklanabilirliği

Finansal teknolojilerde (Fintech) makine öğrenmesi modellerinin kararları "kara kutu" (black-box) olarak kalmamalıdır. Modelin %82.15 gibi yüksek bir doğruluk oranına nasıl ulaştığını, kullanıcıların dijital ödeme tercihlerini belirlerken hangi özelliklerin (bağımsız değişkenlerin) ne yönde etki ettiğini açıklamak için SHAP Özeti Analizi (SHAP Summary Plot) kullanılmıştır.

![SHAP Değişken Önem Analizi](/Users/ecedalpolat/TEZ/Modelleme/reports/shap_random_forest.png)

SHAP grafiği iki temel boyutu aynı anda sunmaktadır:
1.  **Değişken Önemi (Y ekseni):** Değişkenler, modelin karar mekanizmasına yaptıkları toplam katkıya (etki büyüklüğüne) göre yukarıdan aşağıya doğru sıralanmıştır.
2.  **Etki Yönü ve Değer (X ekseni ve Renkler):** Her bir nokta bir müşteriyi/işlemi temsil eder. Noktanın rengi değişkenin değerini (kırmızı: yüksek değer, mavi: düşük değer), yatay eksendeki konumu ise SHAP değerini (0'ın sağı: o sınıfı seçme olasılığını artırır, solu: azaltır) gösterir.

**Table 2: Top 10 Most Influential Features (SHAP Feature Importance)**
| Rank | Feature Name (English) | Description | Impact Direction on Digital Payment |
| :---: | :--- | :--- | :--- |
| **1** | `Transaction_Amount` | Total monetary value of the transaction | **Positive:** Higher amounts increase digital probability |
| **2** | `Past_Digital_Usage_Count` | Frequency of past digital transactions | **Positive:** Frequent users stay digital |
| **3** | `Customer_Age` | Age of the customer | **Negative:** Younger age increases digital probability |
| **4** | `Merchant_Category_Encoded` | Type of store or service (Target Encoded) | **Contextual:** Tech/E-commerce increases probability |
| **5** | `Income_Bracket` | Annual income level | **Positive:** Higher income leans towards digital |
| **6** | `Time_of_Day` | Hour of the transaction | **Contextual:** Night transactions are mostly digital |
| **7** | `Account_Balance` | Available balance in the primary account | **Positive:** Higher balance correlates with digital usage |
| **8** | `Device_Type_Encoded` | Mobile vs Web vs POS (Target Encoded) | **Positive:** Mobile devices dominate digital choice |
| **9** | `City_Tier_Encoded` | Metropolitan vs Rural (Target Encoded) | **Positive:** Metro areas have higher digital adoption |
| **10** | `Credit_Score` | Financial credit rating | **Positive:** High scores slightly favor digital |

**Temel SHAP Bulguları:**
*   Modelin kararlarını domine eden en kritik değişkenler (Tablo 2'de görüldüğü üzere), literatürde sıkça tartışılan `Transaction_Amount` (işlem tutarı), `Past_Digital_Usage_Count` (kullanıcının geçmiş dijital işlem sıklığı) ve `Customer_Age` (yaş) gibi özelliklerdir.
*   Örneğin, en kritik değişken olan `Transaction_Amount` kırmızı renkte (yüksek değerlerde) iken SHAP değerinin pozitif tarafa (sağa) yığılması; *"Bu değişkenin değeri arttıkça, müşterinin dijital ödeme yöntemini tercih etme olasılığı güçlü bir şekilde artmaktadır"* şeklinde yorumlanmaktadır.
*   Tam tersine, `Customer_Age` (Yaş) değişkeninde mavi noktaların (düşük değerlerin) pozitif SHAP etkisi yaratması, genç müşteri kitlesinin mobil ödemelere daha yatkın olduğunu modelin matematiksel olarak keşfettiğini kanıtlamaktadır.

## 4.6. Tartışma ve Literatürle Kıyaslama

Elde edilen bulgular, Khuat ve Le (2018) ile Göçük ve diğerlerinin (2021) çalışmalarında belirtilen "hibrit optimizasyon mimarilerinin, tekil algoritmaların eksik yönlerini başarıyla telafi ettiği" savını finansal veriler üzerinde doğrulamaktadır. Sadece %72 doğruluk üreten standart bir modelin, önerilen metodoloji ile %82.15 doğruluğa taşınması, finans kuruluşları için müşteri davranışını tahmin etmede kritik bir maliyet ve operasyon avantajı sunmaktadır. Üstelik bu süreç, SHAP XAI entegrasyonu sayesinde şeffaf ve denetlenebilir bir yapıya kavuşturulmuştur.
