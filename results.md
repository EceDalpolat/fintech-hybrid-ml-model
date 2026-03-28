# BÖLÜM: BULGULAR VE TARTIŞMA

Bu bölümde, Diary of Consumer Payment Choice (DCPC) veri seti üzerinde gerçekleştirilen analizlerin sonuçları, Yapay Arı Kolonisi (ABC) algoritması ile optimize edilen modellerin performans çıktıları ve elde edilen bulguların literatür ışığında tartışılması yer almaktadır.

## 1. Veri Seti Betimsel İstatistikleri

Çalışmada kullanılan birleştirilmiş veri seti toplam **32.267 satır** ve **356 öznitelikten** oluşmaktadır. Öznitelik mühendisliği aşamasında türetilen zaman bazlı değişkenler ve etkileşim terimleri ile birlikte toplam değişken sayısı 365'e yükselmiştir.

### 1.1. Hedef Değişken Dağılımı (Ödeme Araçları)
Tüketicilerin ödeme aracı tercihlerini temsil eden `pi` (Payment Instrument) değişkeninin dağılımı, veri setinde sınıf dengesizliği olduğunu göstermektedir. En çok tercih edilen ödeme yöntemleri şunlardır:
*   **Banka Kartı (Class 3.0)**: %34,07
*   **Kredi Kartı (Class 4.0)**: %27,07
*   **Nakit (Class 1.0)**: %14,22

Bu dağılım, dijital ödeme yöntemlerinin (banka ve kredi kartı) toplamda %60'ın üzerinde bir paya sahip olduğunu, nakit kullanımının ise üçüncü sırada kaldığını kanıtlamaktadır.

## 2. ABC Optimizasyon Süreci ve Yakınsama Analizi

Çalışmanın en özgün kısmını oluşturan hibrit modelleme aşamasında, Yapay Arı Kolonisi (ABC) algoritması hiper-parametre alanını 100 iterasyon boyunca taramıştır.

### 2.1. Optimizasyon Performansı
ABC algoritması, 50 arıdan oluşan bir popülasyonla başlatılmış ve toplamda **5.050 fonksiyon çağrısı** gerçekleştirmiştir. Optimizasyon sürecine dair önemli dönüm noktaları şöyledir:
*   **Başlangıç Doğruluğu**: İlk rastgele atamalarda %71,93 civarında seyreden doğruluk oranı, işçi ve gözcü arıların yerel arama stratejileri ile kademeli olarak artmıştır.
*   **Yakınsama**: 1.300. çağrı civarında %72,11 seviyesine ulaşan model, 2.550. çağrıdan sonra en iyi değer olan **%72,12** doğruluğa (0.2788 hata oranı) sabitlenmiştir.

### 2.2. Belirlenen Optimal Hiper-parametreler
ABC algoritması tarafından tespit edilen ve modelin en yüksek başarımı sergilemesini sağlayan optimal parametre seti Tablo 1'de sunulmuştur:

| Parametre | Optimal Değer |
|---|---|
| n_estimators (Ağaç Sayısı) | 284 |
| max_depth (Maksimum Derinlik) | 36 |
| min_samples_split | 6 |
| min_samples_leaf | 1 |

## 3. Sınıflandırma Başarısı ve Metrikler

Optimize edilmiş hibrit model, test veri seti üzerinde **%72,12 doğruluk (accuracy)** değerine ulaşmıştır. Sınıf bazlı performans analizleri (Precision, Recall, F1-Score), modelin özellikle popüler olan kartlı ödeme yöntemlerini (Class 3.0 ve 4.0) yüksek hassasiyetle ayırt edebildiğini göstermiştir.

Nispeten düşük frekanslı sınıflarda (örneğin; Class 8.0, %0,15) performansın düştüğü gözlemlenmiş, bu durumun veri setindeki doğal dengesizlikten kaynaklandığı değerlendirilmiştir.

## 4. Öznitelik Önem Düzeyleri (Feature Importance)

Modelin karar verme sürecinde en etkili olan değişkenler analiz edildiğinde;
1.  **İşlem Tutarı (`amnt`)**: Ödeme aracı seçiminde birincil belirleyici olarak öne çıkmaktadır.
2.  **Hanehalkı Geliri (`hhincome`)**: Tüketicinin finansal kapasitesinin teknoloji benimseme hızıyla doğru orantılı olduğu görülmüştür.
3.  **Harcama Tipi / Merchant (`merch`)**: İşlemin yapıldığı yerin (market, online alışveriş vb.) kullanılan aracı doğrudan etkilediği doğrulanmıştır.
4.  **Türetilen Etkileşim Değişkeni (`amnt_income_interaction`)**: Tutarların gelir seviyesine göre normalize edildiği bu değişkenin, modelin tahmin gücüne anlamlı katkı sağladığı saptanmıştır.

## 5. Tartışma ve Literatürle Karşılaştırma

Elde edilen %72,12'lik doğruluk oranı, DCPC veri setinin karmaşıklığı ve çok sınıflı yapısı göz önüne alındığında literatürdeki benzer (Sari, 2024; Jafri vd., 2024) çalışmalarla paralellik göstermektedir. ABC algoritmasının kullanımı, standart bir Random Forest modeline kıyasla parametrelerin daha hassas ayarlanmasına imkan tanımış ve özellikle aşırı öğrenme (overfitting) riskini `max_depth` ve `min_samples_split` dengesi ile minimize etmiştir.

Sonuçlar, tüketicilerin ödeme davranışlarının sadece demografik özellikleriyle değil, aynı zamanda işlemin bağlamsal özellikleri (tutar, zaman, yer) ile de sıkı bir ilişki içinde olduğunu kanıtlamaktadır. Bu bulgular, bankacılık sektöründe kişiselleştirilmiş ödeme çözümleri sunulması için stratejik bir temel oluşturmaktadır.
