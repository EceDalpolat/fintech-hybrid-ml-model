# DİJİTAL ÖDEME TERCİHLERİ - DANIŞMAN HOCA SUNUMU VE LİTERATÜR SAVUNMASI

## 1. Literatürde Ne Var, Biz Ne Farklı Yapıyoruz? (Research Gap)

**Hocaya Söylenecek (Teori):** 
"Hocam, literatür taramasını detaylıca incelediğimde makine öğrenmesi modellerinin hiper-parametre optimizasyonunda genellikle iki yol izlendiğini gördüm: İlki çok hantal olan Grid Search, ikincisi ise tekil sürü zekâları (sadece PSO veya ABC). Biz, finansal veriler gibi gürültülü (noisy) bir veri setinde PSO'nun 'erken yakınsama (premature convergence)' tuzağına düştüğünü gördük. Bu yüzden ABC'nin kaşif arılarının yerel tuzağı bozma yeteneğini PSO'ya entegre ettik."

**Hoca Sorarsa ("Kodda Bunu Nasıl Yaptın?"):**
"Hocam algoritmaları sıfırdan yazarak tekerleği yeniden icat etmedim. Python'daki **`NiaPy`** (Nature-Inspired Algorithms in Python) kütüphanesinin altyapısını kullanarak kendi özel optimizasyon sınıfımı yazdım. Kodlarımın içindeki **`src/optimization_niapy.py`** dosyasında görebileceğiniz üzere `HyperparameterOptimizationProblem` isimli özel bir sınıf (class) yarattım. Bu sınıf, arıların ve kuşların 0 ile 1 arasındaki arama uzayını, Random Forest'ın hiper-parametre aralıklarına (`n_estimators: 50-300`, vb.) matematiksel olarak dönüştürüyor ve her denemeyi 3-Fold Cross-Validation (`cross_val_score`) ile test ediyor."

---

## 2. Ön İşleme Farkımız: Veriyi Nasıl Evcilleştirdik?

**Hocaya Söylenecek (Teori):**
"Literatürde genelde veri ön işleme standart bırakılırken, biz yüksek kardinaliteli finansal kategorilere *Rare Encoding* ve *Target Encoding* uygulayarak özellik uzayımızı şişirmekten kurtardık."

**Hoca Sorarsa ("Kodda Nerede ve Hangi Kütüphaneyle Yaptın?"):**
"Bunu **`src/train.py`** dosyasındaki `build_preprocessor()` fonksiyonunda inşa ettim. 
*   **Rare Encoding:** Bunun için hazır bir kütüphane kullanmak yerine `BaseEstimator` ve `TransformerMixin` sınıflarından miras alan tamamen bana ait özel (custom) bir `RareEncoder` Python sınıfı yazdım.
*   **Target Encoding:** Scikit-Learn'ün (`sklearn.preprocessing`) en güncel `TargetEncoder` modülünü kullandım.
*   **Özellik Seçimi:** Aynı dosyada `sklearn.feature_selection` kütüphanesinden `SelectFromModel` kullanarak gürültülü sütunları otomatik çöpe attım."

---

## 3. Teknik Olarak Nasıl Üstünüz? (Sonuçların Kanıtı)

**Hocaya Söylenecek:**
"Hocam, algoritmamızın matematiksel olarak ne kadar üstün olduğunu şu iki kanıtla sunabilirim: 10 ile 200 iterasyon arası testlerimizde hibrit modelimiz kademeli olarak yükselerek **150. iterasyonda** mutlak tepe noktasına (Global Optimum) ulaştı. Sadece PSO kullansaydık doğruluk %75.78'de takılıyordu, hibrit yapı bunu aşamalı olarak **%82.15'e** taşıdı."

**Hoca Sorarsa ("Değerlendirme Metriklerini Nasıl Aldın?"):**
"Modellerin değerlendirmesini **`src/train.py`** içindeki `evaluate_model()` fonksiyonunda yaptım. Scikit-learn'ün `classification_report` fonksiyonunu kullanarak sadece doğruluğa (Accuracy) değil; sınıf dengesizliğini kontrol etmek için Ağırlıklı F1-Skoruna (Weighted F1) ve Precision-Recall metriklerine baktım."

---

## 4. Kara Kutu (Black-Box) Problemini Nasıl Çözdük?

**Hocaya Söylenecek (Teori):**
"Hocam, Random Forest gibi ağaçların en büyük eleştirisi 'Kara Kutu' olmalarıdır. Ben literatürdeki bu kısıtlamayı aşmak için sisteme **Açıklanabilir Yapay Zekâ (XAI)** entegre ettim."

**Hoca Sorarsa ("Bunu Kodda Nasıl Yaptın?"):**
"Bu işlemi **`src/visualize_results.py`** dosyamda Python'un **`shap`** (SHapley Additive exPlanations) kütüphanesini kullanarak yaptım. Özelliklerin model kararına etkisini ağaç tabanlı bir yaklaşım olan `TreeExplainer` ile analiz ettim ve `shap.summary_plot` kullanarak değişkenlerin yönlü etkilerini görselleştirdim."
