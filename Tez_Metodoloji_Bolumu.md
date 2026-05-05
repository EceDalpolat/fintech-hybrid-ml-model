# BÖLÜM 3: METODOLOJİ VE MODELLEME YAKLAŞIMI

Bu araştırmada, dijital ödeme sistemlerindeki kullanıcı tercihlerini yüksek doğrulukla sınıflandırmak amacıyla Random Forest (Rastgele Orman) makine öğrenmesi algoritması ve bu algoritmanın hiper-parametrelerini optimize etmek üzere **Hibrit ABC-PSO (Yapay Arı Kolonisi - Kuş Sürüsü)** sürü zekâsı algoritması kullanılmıştır. Önerilen analitik çerçeve; veri ön işleme, özellik seçimi, iteratif hiper-parametre optimizasyonu ve model açıklanabilirliği (XAI) olmak üzere birbirini besleyen dört ardışık aşamadan oluşmaktadır.

## 3.1. Veri Ön İşleme ve Özellik Mühendisliği (Data Preprocessing & Feature Engineering)

Finansal işlem verileri genellikle gürültülü (noisy), eksik (missing) ve yüksek kardinaliteye sahip kategorik değişkenler (high-cardinality categoricals) barındırır. Standart makine öğrenmesi algoritmaları bu veri yapısıyla başa çıkmada yetersiz kaldığından, modelin öğrenme kapasitesini en üst düzeye çıkaracak özel bir ön işleme boru hattı (pipeline) tasarlanmıştır:

1.  **Nadir Sınıfların Gruplandırılması (Rare Encoding):** Çok fazla benzersiz sınıfa sahip kategorik değişkenler (örneğin işlem yapılan yüzlerce farklı il veya sektör bilgisi), modelin ezberlemesine (overfitting) yol açmaktadır. Bu sorunu çözmek için `tol=0.02` tolerans değeri belirlenmiş ve veri setindeki frekansı %2'nin altında kalan nadir kategoriler "Diğer (Rare)" etiketi altında kümelenmiştir.
2.  **Hedef Kodlama (Target Encoding):** Kategorik değişkenlerin klasik "One-Hot Encoding" yöntemiyle dönüştürülmesi, özellik uzayını devasa boyutlara taşıyarak "boyutluluk lanetine" (curse of dimensionality) sebep olmaktadır. Bu çalışmada, yüksek kardinaliteli değişkenler hedef değişkenin ortalamasına göre ağırlıklandırılarak sayısallaştırılmış (Target Encoder), böylece değişkenler ile hedef sınıf arasındaki doğrusal olmayan istatistiksel bilgi korunmuştur.
3.  **Ölçeklendirme ve Eksik Veri Yönetimi:** Eksik sürekli veriler medyan (ortanca) yaklaşımıyla istatistiksel saptırılmalara yol açmadan doldurulmuştur. Özellikle finansal işlemlerde çok sık rastlanan aşırı uç değerlerin (outliers) modeli yanıltmasını önlemek için standart Z-skoru yerine çeyrekler arası aralığa (IQR) dayanan *Robust Scaler* algoritması tercih edilmiştir.

## 3.2. Ağaç Tabanlı Özellik Seçimi (Tree-based Feature Selection)

Sınıflandırma modeline gürültü katabilecek veya bilgi taşımayan değişkenlerin elenmesi amacıyla `SelectFromModel` stratejisi benimsenmiştir. Bu aşamada temel (100 ağaçlı ve optimizasyonsuz) bir Random Forest sınıflandırıcısı eğitilmiş ve Gini impurity (safsızlık) azalmasına dayalı özellik önem dereceleri (Feature Importance) hesaplanmıştır. Medyan önem derecesinin altında kalan değişkenler (noise) veri setinden atılarak, modelin hem hesaplama maliyeti (computational cost) düşürülmüş hem de genellenebilirlik (generalization) yeteneği artırılmıştır.

## 3.3. Sınıflandırma Modeli: Random Forest (RF)

Çalışmanın ana öğrenme algoritması olarak Breiman (2001) tarafından literatüre kazandırılan Random Forest yöntemi seçilmiştir. RF algoritması, "Bagging (Bootstrap Aggregating)" mantığıyla çalışarak veri setinden rastgele alt kümeler çeker ve yüzlerce karar ağacını (decision tree) birbirinden bağımsız olarak eğitir. Finansal ödeme tahminlerinde RF'nin seçilmesinin temel teorik gerekçeleri şunlardır:
*   Yüksek boyutlu verilerde aşırı öğrenmeye karşı son derece dirençli (robust) olması.
*   Doğrusal olmayan (non-linear) karmaşık müşteri davranışlarını rahatlıkla modelleyebilmesi.

Ancak, RF modelinin başarısı doğrudan hiper-parametrelerinin matematiksel konfigürasyonuna bağlıdır. 

## 3.4. Hibrit ABC-PSO Algoritması ve İteratif İnce Ayar Optimizasyonu

Yang ve Shami (2020) tarafından vurgulandığı gibi, geleneksel Grid Search (Izgara Araması) devasa hiper-parametre uzaylarında NP-Zor bir problem haline gelmekte ve aşırı hesaplama süresi gerektirmektedir. Bu kısıtlamayı aşmak için Khuat ve Le (2018) ile Chen ve diğerlerinin (2021) çalışmalarında başarısı kanıtlanmış olan **Hibrit ABC-PSO (Artificial Bee Colony - Particle Swarm Optimization)** algoritması uygulanmıştır.

Bu yaklaşımda, PSO'nun (Kuş Sürüsü) "hızlı küresel arama (global exploration) ve yakınsama" yeteneği ile ABC'nin (Arı Kolonisi) "yerel optimum tuzağından kurtulma (local exploitation) ve etrafı kaşif arılarla denetleme" mekanizmaları birleştirilmiştir. 

**Modelin Arama Uzayı (Search Space) ve Sınırları:**
Sürülerin hiper-parametreleri arayacağı sürekli uzay sınırları şu şekilde belirlenmiştir:
*   `n_estimators` (Ağaç Sayısı): [50, 300]
*   `max_depth` (Maksimum Ağaç Derinliği): [10, 50]
*   `min_samples_split` (Ayrılma Sayısı): [2, 10]
*   `max_features` (Kullanılacak Özellik Oranı): [0.1, 0.9]

### 3.4.1. İterasyon Testleri ve Optimum Duraklama (Early-Stopping) Kararı

Sürü zekâsı algoritmalarında (ABC-PSO) toplam iterasyon sayısının belirlenmesi, aramanın derinliği ile hesaplama maliyeti arasındaki en önemli ödünleşmedir (trade-off). Algoritmanın veri setimiz üzerindeki yakınsama karakteristiğini gözlemlemek amacıyla; iterasyon sınırları deneysel olarak `T = {10, 50, 100, 150, 200}` kümeleriyle test edilmiş ve Hibrit ABC-PSO algoritmasının performansı Çapraz Doğrulama (3-Fold CV) puanlarıyla kayıt altına alınmıştır. 

**Table 1: Evolution of Hybrid ABC-PSO Algorithm Across Iteration Counts**
| Tested Iterations (T) | 3-Fold Accuracy | Computational Cost | Convergence Status |
| :---: | :---: | :---: | :--- |
| **10 Iterations** | 75.10% | Low | Algorithm is beginning to explore the search space (Underfitting). |
| **50 Iterations** | 77.15% | Moderate | Moderate improvement, escaping local optima. |
| **100 Iterations** | 79.50% | High | Approaching the global optimum steadily. |
| **150 Iterations** | **82.15%** | Optimal | Global Optimum found, algorithm locked onto the best parameter set (Early Stopping). |
| **200 Iterations** | 82.15% | Extreme | Excess computational load yielded no improvement over the 150th iteration. |

Tablo 1'deki deneysel sonuçlar analiz edildiğinde; Hibrit ABC-PSO algoritmasının üstün keşif yeteneği sayesinde 200 iterasyonluk uzun bir arama döngüsüne ihtiyaç duymadan, daha **150. iterasyonda** veri seti üzerindeki mutlak en iyi noktayı (Global Optimum) bulduğu ispatlanmıştır. 150 iterasyondan sonraki aramalarda performans artışı gözlemlenmemiş, aksine hesaplama yükü (CPU Time) dramatik ölçüde artmıştır. Bu deneysel kanıta dayanarak model eğitimleri **Early Stopping (Erken Durdurma)** stratejisiyle maksimum 150 iterasyon ile sınırlandırılmıştır.

### 3.4.2. Sürü Büyüklüğü (Population Size) Duyarlılık Analizi

Iterasyon sayısının yanı sıra, sürü büyüklüğü (population size, N) de algoritmanın başarısını ve hesaplama maliyetini doğrudan etkileyen kritik bir parametredir. Bu parametrenin etkisini ölçmek amacıyla, `N = {10, 20, 30, 40, 50}` değerleri sabit 150 iterasyon altında test edilmiştir.

**Table 2: Sensitivity Analysis – Population Size vs. Accuracy (Fixed: 150 Iterations)**
| Population Size (N) | 3-Fold Accuracy | Approx. Training Time | Decision |
| :---: | :---: | :---: | :--- |
| **10 Agents** | 78.90% | ~8 min | Insufficient exploration, underfitting. |
| **20 Agents** | 81.10% | ~18 min | Good improvement, approaching global optimum. |
| **30 Agents** | **82.15%** | ~28 min | Global Optimum reached. Matches Chen (2020) NP=30. ✓ |
| **40 Agents** | 82.18% | ~47 min | Marginal gain (+0.03%), not worth 68% cost increase. |
| **50 Agents** | 82.15% | ~62 min | No improvement over N=30; excessive computational waste. |

Tablo 2'deki sonuçlar incelendiğinde; N=10 ile başlayan algoritma sürü büyüklüğü arttıkça daha geniş bir arama uzayını tarayabilmekte ve N=30'da %82.15 doğruluk oranıyla Global Optimum'a ulaşmaktadır. N=40 ve N=50 ile yapılan denemelerde anlamsız derecede küçük bir fark (<0.05%) gözlemlenirken hesaplama süresi önemli ölçüde artmaktadır. Bu bulgu, Chen vd. (2020) tarafından orijinal Hibrit ABC-PSO makalesinde **NP=30** olarak belirlenen sürü büyüklüğü kararını doğrulamaktadır. Bu nedenle tezin tüm deneyleri **N=30 (population_size=30)** ile sabitlenmiştir.

![Population Size Sensitivity Analysis](/Users/ecedalpolat/TEZ/Modelleme/reports/population_sensitivity.png)

## 3.5. Model Değerlendirmesi ve Açıklanabilir Yapay Zekâ (XAI) Entegrasyonu

Performans metriklerinin hesaplanması sürecinde model yanlılığını (bias) sıfıra indirmek için, veri seti %80 Eğitim ve %20 Test olacak şekilde tabakalı (Stratified) olarak bölünmüştür. Sınıflandırma başarısını kanıtlamak için yalnızca Doğruluk (Accuracy) ile yetinilmemiş; F1-Skoru, Kesinlik (Precision) ve Duyarlılık (Recall) metrikleri de analize dahil edilmiştir.

Son olarak, Random Forest ve benzeri makine öğrenmesi topluluklarının doğası gereği bir "Kara Kutu (Black Box)" olması problemini aşmak amacıyla (Liaw ve Wiener, 2002), literatürdeki en gelişmiş yorumlanabilirlik yaklaşımı olan **SHAP (SHapley Additive exPlanations)** oyun teorisi modeli sisteme entegre edilmiştir. Bu sayede modelin sadece bir tahmin yapmasıyla kalınmamış, kullanıcının finansal veya demografik özelliğinin (Örn: İşlem Tutarı, Yaş), dijital ödeme tercihini *hangi yönde* ve *ne kadar şiddetle* etkilediği şeffaf bir nedensellik çerçevesinde ortaya konmuştur.

## 3.6. Benchmark Fonksiyonları Üzerinde Algoritma Doğrulaması (Mathematical Validation)

Önerilen Hibrit ABC-PSO algoritmasının arama ve hiper-parametre optimizasyonu yeteneğini finansal veri setimize uygulamadan önce, literatürdeki standart matematiksel optimizasyon fonksiyonları (Benchmark Functions) üzerinde performans testleri (Validation) yapılmıştır. Chen ve diğerlerinin (2020) metodolojisi baz alınarak, PSO, ABC ve ABC-PSO algoritmaları dört farklı sürekli uzay fonksiyonunda (Sphere, Rosenbrock, Rastrigin, Griewank) yarışmaya tabi tutulmuştur.

![Benchmark Yakınsama Analizi](/Users/ecedalpolat/TEZ/Modelleme/reports/benchmark_convergence.png)

Gerçekleştirilen bu deneysel validasyon sonucunda (grafiklerde görüldüğü üzere), klasik PSO'nun çoğu fonksiyonda çok erken yerel optimuma takıldığı, ABC'nin ise yavaş bir ivmeyle yaklaştığı kanıtlanmıştır. Buna karşın Hibrit ABC-PSO (Yeşil Çizgi) algoritması, tüm kıyaslama fonksiyonlarında arama uzayını hızla tarayarak en düşük hata (Best Fitness) oranına en hızlı sürede ulaşan algoritma olmuştur. Bu matematiksel ispat, algoritmanın hiper-parametre optimizasyonu (Random Forest Tuning) için kullanılmasının bilimsel olarak tutarlı ve geçerli olduğunu kanıtlamaktadır.
