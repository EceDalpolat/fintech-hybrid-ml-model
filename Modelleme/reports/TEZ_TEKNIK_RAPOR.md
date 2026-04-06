# TEZ ÇALIŞMASI TEKNİK RAPORU (Nisan 2024)

**Konu:** Hibrit ABC-PSO Optimizasyonu ile Güçlendirilmiş Random Forest Modeli: Dijital Ödeme Tercihlerinin Sınıflandırılması

## 1. Giriş ve Problem Tanımı
Bu çalışma, tüketici işlem davranışlarını analiz ederek ödeme tercihlerini yüksek doğrulukla sınıflandırmayı amaçlamaktadır. Projenin temel yeniliği, Random Forest (RF) algoritmasının hiper-parametre uzayını tararken, literatürdeki son gelişmelere dayalı (Khuat & Le, 2018) hibrit bir meta-sezgisel algoritma (ABC-PSO) kullanmasıdır.

## 2. Yazılım Mimarisi ve Dosya Yapısı
Proje, modüler ve akademik standartlara uygun bir Python yapısıyla kurgulanmıştır:

- **`src/algorithms/hybrid_abc_pso.py`:** Çalışmanın kalbi olan hibrit algoritma dosyasıdır. Yapay Arı Kolonisi (ABC) ve Parçacık Sürü Optimizasyonu (PSO) yöntemlerini entegre eder.
- **`src/optimization_niapy.py`:** Scikit-learn modellerini (RF) `NiaPy` framework'ü ile bağlayan köprüdür. Hiper-parametreleri evrimsel bir sürece sokar.
- **`src/benchmark_suite.py`:** Literatürde kabul görmüş matematiksel fonksiyonlar (Sphere, Rosenbrock vb.) üzerinde algoritmaların ham performansını test eder.
- **`src/run_thesis_experiments.py`:** Tüm deneyleri (Baseline, RF-PSO, RF-ABC, RF-ABC-PSO) otomatik olarak çalıştıran ana script.
- **`src/data_loader.py`:** Ham verinin (DCPC 2024) yüklenmesi, temizlenmesi ve özellik mühendisliğinden sorumludur.
- **`config.yaml`:** Tüm hiper-parametre sınırları ve deney ayarları tek bir noktadan yönetilir.

## 3. Hibrit ABC-PSO Algoritma Mantığı
Geliştirilen hibrit yaklaşım şu adımları izler:
1. **PSO Safhası (Employed Bees):** Her parçacık (arı) hem kendi hem de sürünün en iyi çözümünden etkilenerek global optimuma yönelir. Bu, keşif yeteneğini artırır.
2. **ABC Safhası (Onlooker Bees):** İyi çözümler etrafında daha yoğun arama yapılır. Bu, çözüm hassasiyetini (exploitation) artırır.
3. **Scout Bees Safhası:** Çıkmaza giren (trial sınırı dolan) çözümler terk edilerek rastgele yeni başlangıçlar yapılır. Bu, yerel optimumdan kaçışı sağlar.

## 4. Benchmark Doğrulama Sonuçları
Algoritmayı gerçek probleme uygulamadan önce matematiksel olarak doğruladık. Elde edilen bulgular hibrit ABC-PSO'nun üstünlüğünü kanıtlamıştır:

- **Sphere Fonksiyonu:** ABC-PSO, standart PSO'dan (1.03e+01) kat kat daha iyi bir performans sergileyerek **5.63e-15** fitness değerine ulaşmıştır.
- **Rosenbrock & Rastrigin:** ABC ve ABC-PSO modelleri, karmaşık yüzeylerde yerel minimumlara takılmadan global çözüme en çok yaklaşan algoritmalar olmuştur.
*(İlgili grafik: reports/benchmark_comparison.png)*

## 5. Deneysel Sonuçlar (RF Pipeline)
Tüm modeller (Baseline, PSO, ABC, ABC-PSO) üzerinde gerçekleştirilen kapsamlı deneyler sonucunda en yüksek başarım **RF-ABC-PSO** hibrit modeli ile elde edilmiştir:

- **En İyi Doğruluk (Accuracy):** %77,47
- **En İyi F1-Skoru (Weighted):** %77,37
- **İyileştirme:** Baz modele göre F1-skorunda yaklaşık **%0,43**'lük bir artış sağlanmıştır.

*(Detaylı karşılaştırma grafiği: reports/thesis_comparison.png)*

---
**Hazırlayan:** Ece Dalpolat  
**İletişim:** [Danışman Bilgisi]
