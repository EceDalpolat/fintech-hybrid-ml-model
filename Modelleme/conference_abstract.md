# Konferans Özeti (Taslak)

**Başlık:** Dijital Ödeme Sistemlerinde Ödeme Tercihlerinin Hibrit Makine Öğrenmesi Modelleri ile Sınıflandırılması: DCPC 2024 Analizi

**Özet:**
Tüketici ödeme davranışlarının analizi, finansal teknolojilerin geliştirilmesi ve dijital dönüşüm süreçlerinin yönetimi açısından kritik öneme sahiptir. Bu çalışmada, 2024 yılı Digital Consumer Payment Choice (DCPC) veri seti kullanılarak bireylerin dijital ödeme tercihleri analiz edilmiştir. Sınıflandırma performansını artırmak amacıyla, Random Forest (RF) algoritmasının hiper-parametreleri doğadan esinlenen hibrit bir optimizasyon yaklaşımı olan ABC-PSO (Artificial Bee Colony - Particle Swarm Optimization) algoritması ile optimize edilmiştir.

Önerilen hibrit ABC-PSO algoritması, öncelikle standart PSO ve ABC algoritmaları ile kararlı matematiksel benchmark fonksiyonları (Sphere, Rosenbrock, Rastrigin, Griewank) üzerinde kıyaslanmış; özellikle yakınsama hızı ve global optimumu bulma yeteneği açısından üstün performans sergilemiştir (örneğin Sphere fonksiyonunda 1.02e-14 hata payı ile en iyi sonucu vermiştir).

Deneysel aşamada, temel RF modeli ile PSO, ABC ve hibrit ABC-PSO ile optimize edilmiş modeller karşılaştırılmıştır. İlk bulgular, hibrit yaklaşımın modelin genelleme kapasitesini artırdığını ve F1-skoru gibi metriklerde iyileşme sağladığını göstermektedir. Bu çalışma, karmaşık tüketici verilerinin analizinde hibrit meta-sezgisel algoritmaların etkinliğini ortaya koymakta ve fintech sektörü için karar destek mekanizmalarına katkıda bulunmaktadır.

**Anahtar Kelimeler:** Hibrit ABC-PSO, Random Forest, Dijital Ödeme Sistemleri, Fintech, Makine Öğrenmesi.
