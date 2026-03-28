# Özet Taslağı / Abstract Draft

## Türkçe Özet

**Başlık:** Dijital Ödeme Sistemlerinde Ödeme Tercihlerinin Hibrit Makine Öğrenmesi Modelleri ile Sınıflandırılması: DCPC 2024 Analizi

**Amaç:** Bu çalışmanın amacı, tüketicilerin dijital ödeme aracı tercihlerini etkileyen dinamikleri anlamak ve bu seçimleri yüksek doğrulukla tahmin edebilen sürdürülebilir bir hibrit makine öğrenmesi modeli geliştirmektir. Özellikle sınıf dengesizliği altında model performansını maksimize eden metasezgisel algoritmaların etkinliği araştırılmıştır.

**Materyal ve Yöntem:** Araştırmada, Atlanta Federal Rezerv Bankası tarafından yayınlanan güncel "Digital Consumer Payment Choice (DCPC) 2024" veri seti (N=32.267) kullanılmıştır. Temel sınıflandırıcı olarak Rastgele Orman (Random Forest) algoritması tercih edilmiştir. Modelin hiper-parametrelerini optimize etmek amacıyla doğadan esinlenen Parçacık Sürü Optimizasyonu (PSO) ve Yapay Arı Kolonisi (ABC) algoritmaları entegre edilmiştir. Özellik mühendisliği aşamasında sürekli değişkenlerin ayrıklaştırılması, etkileşim terimleri ve 3-katlı çapraz doğrulama yöntemleri uygulanmıştır.

**Bulgular:** Yapılan deneysel çalışmalar sonucunda, PSO algoritması ile optimize edilen hibrit modelin (RF-PSO) %77,12 doğruluk (accuracy) oranına ulaşarak en yüksek başarımı sergilediği görülmüştür. Bu performans, ABC-Tabanlı model (%76,10) ve varsayılan Random Forest modelinden (%75,82) daha yüksektir. Öznitelik önem düzeyi analizinde, işlem tutarı ve hanehalkı gelirinin ödeme aracı seçiminde birincil belirleyiciler olduğu saptanmıştır.

**Sonuç:** Sürü zekası algoritmalarının, özellikle PSO'nun, finansal veri setlerinde hiper-parametre uzayını taramadaki üstünlüğü kanıtlanmıştır. Elde edilen bulgular, FinTech sektöründe kişiselleştirilmiş pazarlama stratejileri ve sahtekarlık önleme sistemleri için güçlü bir akademik temel sunmaktadır.

**Anahtar Kelimeler:** Dijital Ödemeler, Rastgele Orman, Sürü Zekası, PSO, ABC, Tüketici Davranışı.

---

## English Abstract

**Title:** Classification of Payment Preferences in Digital Payment Systems using Hybrid Machine Learning Models: A DCPC 2024 Analysis

**Aim:** The objective of this study is to understand the dynamics influencing consumers' digital payment instrument preferences and to develop a robust hybrid machine learning model capable of predicting these choices with high accuracy, particularly under class imbalance conditions.

**Material and Method:** The research utilizes the most recent "Digital Consumer Payment Choice (DCPC) 2024" dataset (N=32,267) provided by the Federal Reserve Bank of Atlanta. Random Forest was selected as the base classifier. To maximize performance, bio-inspired metaheuristic algorithms, specifically Particle Swarm Optimization (PSO) and Artificial Bee Colony (ABC), were integrated for hyperparameter optimization. Data preprocessing included feature engineering (discretization, interaction terms) and 3-fold cross-validation.

**Findings:** Experimental results demonstrate that the PSO-optimized hybrid model (RF-PSO) achieved the highest performance with an accuracy of 77.12%. This outscored the ABC-based model (76.10%) and the default Random Forest model (75.82%). Feature importance analysis revealed that transaction amount and household income are the primary determinants in payment instrument selection.

**Result:** The superiority of swarm intelligence algorithms, especially PSO, in navigating hyperparameter spaces for financial datasets has been validated. These findings provide a strong academic foundation for personalized marketing strategies and fraud detection systems in the FinTech sector.

**Keywords:** Digital Payments, Random Forest, Swarm Intelligence, PSO, ABC, Consumer Behavior.
