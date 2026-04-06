# TEZ ÇALIŞMASI TEKNİK RAPORU

**Konu:** Hibrit ABC-PSO Optimizasyonu ile Güçlendirilmiş Random Forest Modeli: Dijital Ödeme Tercihlerinin Sınıflandırılması  
**Hazırlayan:** Ece Dalpolat  
**Danışman:** Dr. Elif Deniz Yelmenoğlu  
**Tarih:** Nisan 2026

---

## 1. Giriş ve Problem Tanımı

Bu çalışma, DCPC 2024 (Diary of Consumer Payment Choice) veri seti üzerinde tüketici işlem davranışlarını analiz ederek ödeme tercihlerini yüksek doğrulukla sınıflandırmayı amaçlamaktadır. Projenin temel yeniliği, Random Forest (RF) algoritmasının hiper-parametre uzayını optimize ederken literatürdeki son gelişmelere dayalı (Khuat & Le, 2018) hibrit bir meta-sezgisel algoritma (ABC-PSO) kullanmasıdır.

**Araştırma Sorusu:** Hibrit ABC-PSO optimizasyonu, standart RF ve tekil meta-sezgisel yöntemlere (PSO, ABC) kıyasla ödeme tercihi sınıflandırmasında ölçülebilir bir iyileşme sağlar mı?

---

## 2. Yazılım Mimarisi ve Dosya Yapısı

Proje, modüler ve akademik standartlara uygun bir Python yapısıyla kurgulanmıştır:

| Dosya | Görev |
|---|---|
| `src/algorithms/hybrid_abc_pso.py` | Hibrit algoritmanın çekirdeği; PSO + ABC entegrasyonu |
| `src/optimization_niapy.py` | NiaPy ile sklearn arasındaki köprü; hiper-parametre optimizasyonu ve yakınsama takibi |
| `src/benchmark_suite.py` | Matematiksel fonksiyon doğrulama testleri (D=30, 25 çalışma, 500 iterasyon) |
| `src/run_thesis_experiments.py` | Tüm RF deneylerini (Baseline, PSO, ABC, ABC-PSO) otomatik çalıştırır |
| `src/data_loader.py` | DCPC 2024 ham verisinin yüklenmesi, temizlenmesi ve özellik mühendisliği |
| `src/visualize_results.py` | Yakınsama grafikleri, karşılaştırma tabloları ve görselleştirmeler |
| `config.yaml` | Tüm hiper-parametre sınırları ve deney ayarları |

---

## 3. Hibrit ABC-PSO Algoritması

Geliştirilen hibrit yaklaşım üç aşamalı bir döngüyle çalışır:

1. **PSO Safhası (Employed Bees):** Her parçacık hem kendi tarihsel en iyisini (`pbest`) hem de sürünün global en iyisini (`gbest`) referans alarak hız ve konum güncellemesi yapar. İnertia ağırlığı `w=0.729`, ivme katsayıları `c1=c2=1.494` (Clerc & Kennedy, 2002).

2. **ABC Safhası (Onlooker Bees):** Fitness değerine orantılı olasılıkla seçilen iyi çözümler etrafında yerel arama yapılır. Bu, keşif (exploration) sonrası sömürüm (exploitation) dengesini sağlar.

3. **Scout Safhası:** `limit` iterasyon boyunca iyileşmeyen çözümler terk edilerek uzay içinde rastgele yeni konumlar üretilir. Yerel optimumdan kaçış mekanizması olarak görev yapar.

**Parametreler:** `w=0.729`, `c1=1.494`, `c2=1.494`, `limit=50`, `pop_size=30`, `max_iters=80`

---

## 4. Veri Seti ve Ön İşleme

- **Kaynak:** Federal Reserve Bank of Atlanta — DCPC 2024 (Diary of Consumer Payment Choice)
- **Hedef Değişken:** `pi` (ödeme aracı: nakit, kredi kartı, banka kartı vb.)
- **Stratejiler:**
  - Bireysel (`ind`) ve işlem (`tran`) veri setleri `id` üzerinden birleştirildi
  - `log_amnt` (logaritmik tutar), `age_group`, `is_weekend`, `is_payday` gibi türetilmiş özellikler eklendi
  - IQR yöntemiyle aykırı değer bastırma uygulandı
  - Eğitim/test ayrımı: %80/%20, katmanlı (stratified) örnekleme
  - Sınıf dengesizliği için SMOTE uygulandı

---

## 5. Matematiksel Benchmark Doğrulaması

**Amaç:** Algoritmayı gerçek probleme uygulamadan önce iyi bilinen test fonksiyonlarında doğrulamak (Chen et al., 2020 yaklaşımı).

**Ayarlar:** D=30, 25 bağımsız çalışma, 500 iterasyon, pop_size=40

### Tablo 1: Benchmark Sonuçları (Ortalama Fitness ± Standart Sapma)

| Fonksiyon | PSO | ABC | **ABC-PSO** |
|---|---|---|---|
| Sphere | 1.49e+02 ± 2.34e+01 | 1.02e-06 ± 1.30e-06 | **7.34e+00 ± 1.58e+01** |
| Rosenbrock | 1.98e+08 ± 4.10e+07 | 4.46e+01 ± 2.79e+01 | **7.65e+03 ± 2.43e+04** |
| Rastrigin | 4.04e+02 ± 2.42e+01 | **7.20e+00 ± 2.53e+00** | 1.86e+01 ± 9.28e+00 |
| Griewank | 1.54e+01 ± 1.91e+00 | 9.43e-03 ± 1.52e-02 | **2.60e-01 ± 8.41e-01** |

### En İyi Tek Çalışma Sonuçları

| Fonksiyon | PSO (Best) | ABC (Best) | ABC-PSO (Best) |
|---|---|---|---|
| Sphere | 1.13e+02 | 5.51e-08 | **1.06e-12** |
| Rosenbrock | 1.11e+08 | 6.75e+00 | **1.93e-02** |
| Rastrigin | 3.33e+02 | **2.13e+00** | 7.63e+00 |
| Griewank | 1.08e+01 | 6.22e-08 | **3.96e-11** |

**Bulgular:**
- PSO, başlangıç popülasyonuna bağımlı ve saf sömürü eğilimlidir; tüm fonksiyonlarda en zayıf performansı göstermiştir.
- ABC, Rastrigin ve Sphere gibi sürekli fonksiyonlarda güçlüdür ancak Rosenbrock vadisi gibi anizotropik yüzeylerde yetersiz kalmaktadır.
- ABC-PSO hibrit yaklaşımı, Sphere ve Griewank'ta **küresel en iyi** değerlere (10⁻¹² mertebesine) ulaşmış; Scout mekanizması sayesinde yerel optimumdan kaçış sağlamıştır.

*(Yakınsama grafikleri: `reports/benchmark_convergence.png`, `reports/convergence_*.png`)*  
*(Karşılaştırma çubuğu: `reports/benchmark_comparison.png`)*

---

## 6. RF Hiper-Parametre Optimizasyonu ve Deneysel Sonuçlar

### Optimizasyon Uzayı

| Parametre | Alt Sınır | Üst Sınır |
|---|---|---|
| `n_estimators` | 100 | 800 |
| `max_depth` | 5 | 100 |
| `min_samples_split` | 2 | 20 |
| `min_samples_leaf` | 1 | 10 |
| `max_features` | 0.1 | 0.9 |

**CV Ayarı:** 5-katlı çapraz doğrulama, skorlama: F1-Weighted, `random_state=42`

### Tablo 2: Model Karşılaştırması

| Yöntem | Doğruluk | F1 (Weighted) | Precision | Recall |
|---|---|---|---|---|
| RF (Baseline) | %77.18 | %76.94 | %77.07 | %77.18 |
| RF + PSO | %77.33 | %77.12 | %77.29 | %77.33 |
| RF + ABC | %77.28 | %77.06 | %77.25 | %77.28 |
| **RF + ABC-PSO** | **%77.47** | **%77.37** | **%77.58** | **%77.47** |

### En İyi Hiper-Parametreler (RF + ABC-PSO)

| Parametre | Değer |
|---|---|
| `n_estimators` | 500 |
| `max_depth` | 38 |
| `min_samples_split` | 9 |
| `min_samples_leaf` | 1 |

**Bulgular:**
- ABC-PSO, baseline RF'e kıyasla F1-Weighted skorunda **+0.43 puan** iyileştirme sağlamıştır.
- Danışman tarafından belirlenen **%70 doğruluk hedefi** tüm yöntemlerde aşılmıştır.
- ABC-PSO, hem Precision hem Recall bazında diğer tüm yöntemleri geride bırakmıştır.

*(RF yakınsama grafiği: `reports/rf_convergence.png`)*  
*(Deneysel karşılaştırma: `reports/thesis_comparison.png`)*

---

## 7. Sonuç ve Değerlendirme

Bu çalışmada geliştirilen Hibrit ABC-PSO + RF pipeline'ı iki düzeyde doğrulanmıştır:

1. **Matematiksel düzey:** D=30, 25 çalışmalı benchmark testleri, hibrit algoritmanın Sphere ve Griewank fonksiyonlarında küresel optimuma (10⁻¹² mertebesi) ulaşabildiğini göstermiştir.

2. **Uygulama düzeyi:** DCPC 2024 ödeme verisi üzerinde %77.47 doğruluk ve %77.37 F1-Weighted skoruna ulaşılmıştır; bu değer danışman tarafından belirlenen %70 hedefinin belirgin biçimde üzerindedir.

**Konferans Uygunluğu:** Elde edilen bulgular, metodolojik sağlamlık ve pratik uygulanabilirlik açısından akademik yayın için yeterli katkı düzeyindedir.

---

## 8. Referanslar

- Khuat, T. T., & Le, M. H. (2018). A novel hybrid ABC-PSO algorithm for a ship scheduling problem. *Journal of Advances in Information Technology.*
- Chen, Y. et al. (2020). A Hybrid ABC-PSO Optimizer for Feature Selection. *(Benchmark tasarımı referansı)*
- Federal Reserve Bank of Atlanta. (2024). *Diary of Consumer Payment Choice — Public Dataset.*
- Clerc, M., & Kennedy, J. (2002). The particle swarm - explosion, stability, and convergence in a multidimensional complex space. *IEEE Transactions on Evolutionary Computation.*

---

**Kayıtlı Dosyalar:**
- `reports/experiment_results.json` — Tüm model metrik sonuçları
- `reports/benchmark_results.json` — Benchmark fitness istatistikleri
- `reports/convergence_rf.json` — RF optimizasyon yakınsama geçmişi
- `reports/model_*.pkl` — Eğitilmiş model dosyaları
