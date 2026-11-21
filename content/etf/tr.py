# -*- coding: utf-8 -*-
"""Dünyanın en büyük 50 ETF'si, borsakartal.com için Türkçe yazıldı.

Çeviri değil: Türkiye Avrupa Ekonomik Alanı'nın dışında, dolayısıyla Madrid'deki okura verilen cevap
buradaki okura uymuyor. İspanya'da emir reddediliyor; Türkiye'de ABD fonlarına yurt dışı piyasa
sunan aracı kurumlar veya uluslararası brokerlar üzerinden ulaşılabiliyor. Asıl maliyet, lirayı
dolara çevirme adımı.

Rakamlar burada değil: fiyat, getiri, portföy ve çarpanlar her gün etf_data.py içinde hesaplanıyor.
"""

UI = dict(
    home='Ana sayfa', etfs='ETF', other='Diğer', fundcol='Fon',
    h1='Dünyanın en büyük {N} ETF’si',
    sub='Portföy, ağırlıklar ve değerleme · güncellendi',
    lead='Dünyanın en büyük {N} borsa yatırım fonu: her biri ne işe yarıyor, içinde ne var ve '
         'içindeki şirketler ne ediyor.',
    intro='Bu sayfalardaki F/K oranını fondan almıyoruz. Her pozisyon, o şirket için bizim kendi '
          'sayfamızla eşleştiriliyor ve rakamlar fonun kendi ağırlıklarıyla ağırlıklandırılıyor. '
          'Yani bir ETF’nin F/K’sı, bu sitedeki her hisse sayfasıyla aynı SEC bildirimlerinden '
          'çıkıyor — ve herhangi bir pozisyona tıklayıp şirketi okuyabilirsiniz.',
    idea='Fikir', ret='Getiri', fund='İçindeki şirketler ne ediyor',
    holds='En büyük pozisyonlar', made='Neyden oluşuyor',
    where='Yaşadığınız yerden alabilir misiniz?', company='Şirket', weight='Ağırlık',
    all50='{N} fon yan yana',
    y1='Son 1 yıl', y3='Son 3 yıl', y5='Son 5 yıl', ytd='Yıl başından beri',
    m1='Son 1 ay', m3='Son 3 ay',
    price='Fiyat', pe='F/K', ps='Fiyat / satış',
    growth='Satış büyümesi, geçen yıl', margin='Net kâr marjı', score='Ortalama puanımız',
    holdings='Pozisyon',
    chartcap='Bu sayfadaki tüm fonların bir yıllık fiyat getirisi. Açmak için bir çubuğa tıklayın.',
    linecap='%(year)s yılından bu yana fiyat. Temettüler dahil değil.',
    note_ret='Yalnızca fiyat getirisi. Temettü dağıtan bir fon bundan fazlasını kazandırdı; temettüyü '
             'içinde biriktiren ise kazandırmadı.',
    note_pe='Fondan alınmadı. Her pozisyon o şirket için bizim kendi sayfamızla eşleştiriliyor ve '
            'rakamlar fonun kendi ağırlıklarıyla ağırlıklandırılıyor; yani sitenin geri kalanıyla '
            'aynı bildirimlerden çıkıyor. Bu fonun ağırlıkça %(cov)s’ini kapsıyoruz (%(n)s / %(total)s pozisyon).',
    note_holds='%(total)s pozisyonun en büyük %(n)d tanesi, fonun kendi yayımladığı portföyünden%(asof)s. Bağlantılı '
               'şirket adlarının bu sitede tam sayfası var.',
    note_ctry='Genel durum; belirli bir aracı kurum ya da vergi tavsiyesi değil. Bir fon '
              'alınamıyorsa bunu yapan, aracı kurum değil, Avrupa’nın belge kuralı.',
    note_tbl='F/K sütunu, her fonun içindeki şirketlerden, fonun kendi ağırlıklarıyla ve hisse '
             'sayfalarımızdaki aynı rakamlarla hesaplanıyor. Fon hisse senedi tutmuyorsa ve fon '
             'ağırlıklı olarak ABD dışında işlem gören şirketlerden oluşuyorsa — ki onları '
             'kapsamıyoruz — boş kalıyor.',
    no_pe_h='Burada neden F/K yok',
    no_pe_bond='Bu fon şirket hissesi tutmuyor, dolayısıyla fiyatı bölecek bir kâr yok. Onun yerine '
               'önemli olan kime ve ne vadeyle borç verdiği: bir tahvil fonunda kredi kalitesi ve '
               'vade, altında veya bitcoin’de ise varlığın kendi fiyatı. %(n)s pozisyonu var.',
    no_pe_thin='Şirket verilerimiz ABD’de işlem gören şirketleri kapsıyor. Bu fonun %(n)s pozisyonu var '
               've ağırlığının yalnızca %(cov)s’i kapsadığımız şirketlerde. O parçadan hesaplanan bir F/K, '
               'fonun kendisini değil bir dilimini anlatırdı. Cevap gibi görünen bir sayı basmaktansa '
               'boş bırakmayı tercih ediyoruz. Aşağıdaki portföy ve ağırlıklar fonun kendisine ait.',
    priips='%(fund)s Amerika Birleşik Devletleri’nde kurulu. ABD fonları, Avrupa kurallarının istediği '
           'temel bilgi belgesini yayımlamıyor; bu yüzden Avrupa Birliği’ndeki veya Birleşik '
           'Krallık’taki bireysel yatırımcı bu fonu alamıyor — hangi aracı kurum olursa olsun emir '
           'reddediliyor. Türkiye bu alanın dışında: yurt dışı piyasa sunan aracı kurumlar ve '
           'uluslararası brokerlar üzerinden ulaşılabiliyor.',
    in_europe='Avrupa’daysanız:',
    vs_sp='Aynı ölçüyle S&P 500 %(sp)s kat, yani bu fon %(diff)s %(dir)s.',
    more_exp='daha pahalı', cheaper='daha ucuz',
    shariah='İslami kurallara uygun alternatif',
    dis='Portföy, fonun SEC’e verdiği kendi bildirimlerinden; şirket rakamları SEC bildirimlerinden, '
        'her gün yeniden hesaplanıyor. Eğitim amaçlıdır, yatırım tavsiyesi değildir.',
    i_title='En büyük {N} ETF: portföy, F/K ve getiri',
    i_desc='Dünyanın en büyük {N} ETF’si; portföyleri, ağırlıkları, bir yıllık getirileri ve her '
           'birinin gerçekten içinde tuttuğu şirketlerden hesaplanmış F/K oranı.',
    d_title='%(t)s ETF: portföy, F/K ve getiri',
    d_desc='%(name)s (%(t)s) portföyü, ağırlıkları ve getirisi; içinde gerçekten tuttuğu '
           'şirketlerden hesaplanmış F/K ile. %(idea)s',
    s_blocked='Alınamıyor', s_open='Alınabiliyor',
    s_local='Alınabiliyor, ayrıca yerel borsada da işlem görüyor',
    s_hard='İzinli ama pratikte zor', s_sanctions='Erişilemiyor',
    groups=[
        ('ABD piyasasının çekirdeği', ['US large cap', 'US total market']),
        ('Büyüme ve değer', ['US large cap growth', 'US mega cap growth', 'US large cap value', 'US quality factor']),
        ('Temettü', ['US dividend', 'US dividend growth']),
        ('Daha küçük şirketler', ['US mid cap', 'US small cap']),
        ('ABD dışı', ['developed ex-US', 'global ex-US', 'global', 'emerging markets', 'Europe']),
        ('Sektörler', ['technology', 'semiconductors', 'financials', 'healthcare', 'energy', 'industrials', 'real estate']),
        ('Tahvil, altın ve bitcoin', ['US investment grade bonds', 'international bonds', 'gold', 'bitcoin']),
    ],
    # the countries this reader is actually in
    **{
        'c_Turkey': 'Türkiye', 'c_Germany': 'Almanya', 'c_Netherlands': 'Hollanda',
        'c_Austria': 'Avusturya', 'c_United Kingdom': 'Birleşik Krallık',
        'c_United States': 'Amerika Birleşik Devletleri',
        'w_Turkey': 'Türkiye Avrupa Ekonomik Alanı’nın dışında, bu yüzden Avrupa’nın belge kuralı '
                    'burada geçerli değil. ABD fonlarına yurt dışı piyasa sunan Türk aracı kurumları '
                    've uluslararası brokerlar üzerinden ulaşılabiliyor. Maliyet yaratan adım, lirayı '
                    'dolara çevirmek.',
        'w_Germany': 'Avrupa kuralları, paketlenmiş bir ürünün bireysel yatırımcıya satılabilmesi için '
                     'resmî bir AB dilinde temel bilgi belgesi istiyor. ABD fon şirketleri bunu '
                     'hazırlamıyor, dolayısıyla emir reddediliyor — sizin aracı kurumunuza özel bir '
                     'durum değil. Yukarıda adı geçen Avrupa fonu aynı endeksi izliyor ve bu belgeyle '
                     'satılıyor. Almanya’daki Türkiyeli yatırımcıların karşılaştığı durum budur.',
        'w_Netherlands': 'Aynı Avrupa belge kuralı geçerli: emir reddediliyor. Yukarıdaki Avrupa fonu '
                         'aynı endeksi izliyor.',
        'w_Austria': 'Aynı Avrupa belge kuralı geçerli: emir reddediliyor. Yukarıdaki Avrupa fonu '
                     'aynı endeksi izliyor.',
        'w_United Kingdom': 'Birleşik Krallık, Avrupa Birliği’nden ayrıldıktan sonra aynı kuralı '
                            'sürdürdü; ABD’de kurulu bir fon hâlâ bireysel yatırımcıya satılamıyor. '
                            'Yukarıdaki Avrupa fonu Londra’da işlem görüyor.',
        'w_United States': 'Fon zaten burada kurulu; herhangi bir hisse gibi alınıyor.',
    },
)

T = {
 'VOO': ('ABD’nin en büyük 500 şirketi, sektördeki en düşük maliyetle.',
         'S&P 500’deki her şirketi piyasa değeriyle orantılı olarak tutuyor; yani en büyükler baskın. '
         'İnsan kararı yok: endeks komitesi bir şirketi eklediğinde giriyor, çıkardığında çıkıyor. '
         'Ağırlıklar piyasa değerini izlediği için fonun yaklaşık üçte biri en büyük on şirkette — '
         'çoğu yatırımcının beklediğinden çok daha yoğun.'),
 'IVV': ('VOO ile aynı 500 şirket, farklı bir fon şirketinden ve aynı maliyetle.',
         'S&P 500’ü tüm bileşenlerini endeks ağırlığıyla tutarak izliyor. Yıllarca elde tutacak biri '
         'için bununla VOO arasındaki seçim, fonlara dair bir farktan değil, kullandığı aracı '
         'kurumdan ve o gün hangisinin daha dar makasla işlem gördüğünden ibaret.'),
 'SPY': ('Orijinal S&P 500 fonu: dünyanın en çok işlem gören menkul kıymeti.',
         'ABD’nin en eski ETF’si ve modern bir fon değil, bir unit investment trust olarak kurulu. '
         'Bu da menkul kıymet ödünç veremediği ve temettüleri ödemeler arasında yeniden yatıramadığı '
         'anlamına geliyor. Uzun vadeli yatırımcıya her yıl VOO ve IVV karşısında biraz pahalıya mal '
         'oluyor. Karşılığında eşsiz bir likiditesi ve opsiyon piyasası var; bu yüzden kısa vadeli '
         'işlem yapanlar SPY’yi seçerken uzun vadeli yatırımcı için VOO ya da IVV genelde daha mantıklı.'),
 'VTI': ('ABD’nin yatırım yapılabilir tüm halka açık şirketleri, tek bir pozisyonda.',
         'En büyüklerden küçüklere binlerce şirketi piyasa değerine göre tutuyor. Pratikte bir S&P '
         '500 fonuyla neredeyse aynı davranıyor, çünkü onu farklı kılan küçük şirketler toplamda '
         'ağırlığın birkaç yüzdesi. Fark, küçüklerin öne geçtiği o seyrek dönemlerde ortaya çıkıyor.'),
 'QQQ': ('Nasdaq’ın finans dışı en büyük 100 şirketi — pratikte büyük teknolojiye bir bahis.',
         'Finans şirketlerini tamamen dışarıda bırakan ve bir şirketi ne yaptığına değil nerede işlem '
         'gördüğüne göre tanımlayan Nasdaq-100’ü izliyor. Bu kuruluş tesadüfü, fonun neden teknolojide '
         'bu kadar yoğunlaştığını ve S&P 500’ü kimi zaman neden geride bıraktığını, kimi zaman neden '
         'ondan çok daha sert düştüğünü açıklıyor. İlk on pozisyon genelde fonun yarısına yakın.'),
 'VUG': ('Büyük ABD şirketlerinin daha hızlı büyüyen yarısı, kurallara dayalı bir büyüme tanımıyla.',
         'ABD büyük şirket evrenini kâr büyümesi, satış büyümesi ve defter değeri gibi ölçülerle '
         'büyüme ve değer olarak ikiye ayırıp büyüme tarafını piyasa değerine göre tutuyor. En büyük '
         'teknoloji şirketleri büyüme tarafında puanlandığı için fon onlarda ciddi biçimde '
         'yoğunlaşıyor: adının çağrıştırdığından çok, QQQ’ya yakın davranıyor.'),
 'VTV': ('Büyük ABD şirketlerinin daha ucuz yarısı: bankalar, sağlık ve sanayi.',
         'VUG’u üreten aynı bölünmenin öbür yarısı. Fiyat/defter değeri, F/K ve temettü verimine göre '
         'değer tarafında puanlanan büyük ABD şirketlerini piyasa değerine göre tutuyor. Sonuç, S&P '
         '500’e kıyasla çok daha fazla finans, sağlık ve enerji, çok daha az teknoloji ve daha yüksek '
         'temettü.'),
 'VIG': ('En az on yıldır üst üste temettüsünü artıran şirketler.',
         'Uzun ve kesintisiz bir temettü artışı geçmişi arıyor, sonra bu testi geçenlerin en yüksek '
         'verimli çeyreğini eliyor. Asıl zekice olan bu ikinci adım: çok yüksek bir temettü verimi '
         'genelde cömertliğin değil, düşmüş bir hisse fiyatının işareti; onları çıkarmak temettü '
         'kesintilerinin çoğunu önlüyor. Ortaya yüksek gelirli bir fon değil, üstelik temettü de '
         'ödeyen bir kalite fonu çıkıyor.'),
 'SCHD': ('Yalnızca verime göre değil, bilanço sağlamlığına göre de elenmiş yüz temettü ödeyicisi.',
          'On yıl kesintisiz temettü şartı koyuyor, sonra kalanları nakit akışı/borç, özkaynak '
          'kârlılığı, temettü verimi ve temettü büyümesine göre sıralıyor. Bu bileşim, ödeyemeyeceği '
          'temettüyü dağıtan şirketleri dışarıda bırakıyor — yüksek verimli fonların klasik hatası '
          'budur. Ağırlıklar sınırlandırılmış, böylece tek bir şirket ya da sektör baskın olamıyor.'),
 'VYM': ('ABD piyasasının temettü verimi yüksek yarısı, büyüklüğe göre ağırlıklandırılmış.',
         'ABD şirketlerini beklenen temettü verimine göre sıralayıp piyasa değerine göre üst yarıyı '
         'alıyor, gayrimenkul ortaklıklarını hariç tutuyor. Hiçbir kalite filtresi uygulamıyor; bu da '
         'onu SCHD’den daha basit ve daha geniş yapıyor ama verimi hisse düştüğü için yüksek olan '
         'şirketleri de içeride bırakıyor.'),
 'DGRO': ('Beş yıldır temettüsünü artıran ve artırmaya devam edecek alanı olan ABD şirketleri.',
          'Beş yıl kesintisiz temettü büyümesi ve %75’in altında bir dağıtım oranı istiyor; bu da '
          'sürdüremeyeceğinden fazlasını dağıtanları eliyor. VIG ile aynı gerekçeyle en yüksek '
          'verimli yüzde onu dışarıda bırakıyor. VIG’den daha geniş ve biraz daha yüksek verimli.'),
 'IWF': ('En büyük bin ABD şirketinin büyüme yarısı, Russell’ın tanımıyla.',
         'Russell, büyük şirket evrenini defter değeri/fiyat ve beklenen büyümeyle ayırıyor ve bir '
         'şirketin kısmen büyümede kısmen değerde yer almasına izin veriyor. Pratik sonuç teknolojide '
         'yüksek ağırlık; VUG’a benziyor ama yeniden dengeleme takvimi farklı: Russell’ın her '
         'haziranda yaptığı yeniden yapılandırma yılın en büyük işlem olaylarından biri.'),
 'IWD': ('En büyük bin ABD şirketinin değer yarısı.',
         'IWF’nin ayna görüntüsü: defter değeri/fiyat ve düşük beklenen büyümeye göre ucuz puanlanan '
         'şirketler. Finans, sağlık ve sanayi baskın. IWF ile birlikte Russell 1000’in tamamını '
         'yeniden kuruyor.'),
 'IWM': ('İki bin küçük ABD şirketi — ABD küçük şirketleri için en çok kullanılan gösterge.',
         'Piyasa değerine göre 1.001’inciden 3.000’inciye kadar olan şirketleri tutuyor. Endeksin '
         'kayda değer bir bölümü kâr etmiyor; büyük şirket endekslerinden çok farklı davranmasının '
         'sebebi bu: faize ve iç ekonomiye çok daha duyarlı ve çok daha oynak.'),
 'IJH': ('S&P 500 ile küçükler arasında kalan 400 orta ölçekli ABD şirketi.',
         'S&P’nin orta ölçek endeksi girişte kârlılık şartı arıyor; Russell endeksleri aramıyor. Bu '
         'tek kural, ABD orta ölçekli şirketlerini tarihsel olarak küçüklerden daha kaliteli bir '
         'evren hâline getirdi ve ikisi arasındaki uzun vadeli getiri farkının önemli bir kısmını '
         'açıklıyor.'),
 'IJR': ('Kârlılığa göre elenmiş altı yüz küçük ABD şirketi.',
         'Bir şirketin girebilmek için kâr etmesini şart koşan S&P SmallCap 600’ü izliyor. Russell '
         '2000’den temel farkı bu ve piyasanın aynı bölümünü kapsamalarına rağmen iki küçük şirket '
         'endeksinin uzun dönemler boyunca neden ayrıştığının sebebi de bu.'),
 'VO': ('Orta ölçekli ABD şirketleri, toplam piyasa değerinde nereye düştüklerine göre tanımlanmış.',
        'ABD piyasasının kümülatif değerce yaklaşık yüzde 70 ile 85 arasındaki dilimini alıyor. '
        'S&P’nin orta ölçek endeksinin aksine kârlılık filtresi yok; dolayısıyla daha geniş ve biraz '
        'daha düşük kaliteli bir küme tutuyor, daha ucuza.'),
 'VB': ('Küçük ABD şirketleri, para kazanıp kazanmadıklarına bakılmadan.',
        'ABD piyasasının kümülatif değerce alt dilimini, binden fazla şirketle kapsıyor. IJR’den daha '
        'geniş ve daha ucuz, ama S&P’nin küçük şirket endeksinin dışarıda bıraktığı zarar eden '
        'şirketleri de içeriyor.'),
 'SPYM': ('State Street’in ucuz S&P 500 fonu: işlem için değil, elde tutmak için.',
          'SPY ile aynı endeks, modern bir fon yapısında ve çok daha düşük maliyetle. State Street bunu '
          'tam da SPY’nin trust yapısı uzun vadeli yatırımcı için cazip olmadığı için çıkardı. SPY’den '
          'daha düşük işlem hacmi var; bu da yalnızca büyük hacimle işlem yapıyorsanız önemli.'),
 'RSP': ('S&P 500 ile aynı 500 şirket, ama hepsi eşit ağırlıkta.',
         'Her şirkete fonun yaklaşık %0,2’sini veriyor ve her çeyrek yeniden dengeliyor; bu da sistemli '
         'biçimde yükseleni satıp düşeni almak demek. En büyüklerdeki yoğunlaşmayı tamamen ortadan '
         'kaldırıyor: pratik etkisi orta ölçek ve değere doğru bir eğilim. Piyasa genişlediğinde '
         'standart S&P 500’ü geçiyor, birkaç dev çektiğinde fena hâlde geride kalıyor.'),
 'QUAL': ('Özkaynak kârlılığı iyi, kârı istikrarlı ve borcu az ABD şirketleri.',
          'Üç ölçüye göre sıralıyor — özkaynak kârlılığı, kâr oynaklığı ve borç/özkaynak — ve her '
          'sektörün içindeki en iyileri tutuyor; böylece fon kazara bir sektör bahsine dönüşmüyor. '
          'Kalite, düşüşlerde tarihsel olarak piyasadan iyi dayandı, sert toparlanmalarda geride kaldı.'),
 'MGK': ('Yalnızca ABD’nin en büyük büyüme şirketleri — onlara sahip olmanın en yoğun yolu.',
         'Büyüme evreninin mega ölçek ucuyla sınırlı; yani birkaç düzine pozisyon ve en büyük teknoloji '
         'şirketlerinde aşırı yoğunlaşma. QQQ’dan daha yoğun, VUG’dan çok daha yoğun. Yalnızca bu '
         'maruziyeti bilerek isteyen biri için anlamlı.'),
 'VV': ('ABD piyasasının büyük şirket bölümü, bir komite yerine büyüklükle tanımlanmış.',
        'ABD piyasasının kümülatif değerce üst %85’ini kapsıyor; yani S&P 500’den fazla şirket tutuyor '
        've S&P üyeliğine karar veren komiteyi devre dışı bırakıyor. Pratikte getirisi S&P 500’ü çok '
        'yakından izliyor.'),
 'ITOT': ('Tüm ABD piyasası tek bir fonda, BlackRock’tan.',
          'ABD piyasasının tamamını, büyükten mikroya, endeks ağırlıklarıyla tutuyor. VTI’nin doğrudan '
          'rakibi; esasen aynı maruziyet, aynı maliyet, aynı davranış.'),
 'SCHX': ('En büyük 750 ABD şirketi, piyasadaki en düşük maliyetlerden biriyle.',
          'S&P 500’den fazla şirketi kapsayan geniş bir büyük şirket fonu ve maliyeti sektörün dibinde. '
          'Anlamlı herhangi bir dönemde VV ve S&P 500 ile neredeyse aynı davranıyor.'),
 'VEA': ('ABD dışındaki gelişmiş ülke şirketleri: Avrupa, Japonya, Kanada, Avustralya.',
         'ABD hariç gelişmiş piyasalardan binlerce şirketi piyasa değerine göre tutuyor; bu da Japonya '
         've Birleşik Krallık’ı büyük pozisyonlar hâline getiriyor. MSCI versiyonunun aksine Kanada ve '
         'Güney Kore’yi içeriyor. Getiri büyük ölçüde dolara bağlı: zayıf dolar işine yarıyor, güçlü '
         'dolar aleyhine çalışıyor.'),
 'VXUS': ('ABD dışındaki yatırım yapılabilir tüm dünya şirketleri.',
          'ABD dışındaki gelişmiş ve gelişmekte olan piyasaları tek fonda, piyasa ağırlıklarıyla ve '
          'birkaç bin şirketle birleştiriyor. VTI ile birlikte iki pozisyonla eksiksiz bir küresel '
          'portföy kuruyor.'),
 'IEFA': ('Gelişmiş Avrupa, Avustralasya ve Uzak Doğu — standart uluslararası ölçüt.',
          'MSCI’ın ABD ve Kanada’yı dışarıda bırakan EAFE evrenini izliyor; büyük, orta ve küçük '
          'şirketleri kapsıyor. ABD portföylerinde en çok kullanılan uluslararası dağılım ve '
          'uluslararası fon yöneticilerinin kendisiyle ölçüldüğü referans.'),
 'VWO': ('Gelişmekte olan ekonomilerin şirketleri; Çin, Hindistan ve Tayvan baskın.',
         'Gelişmekte olan piyasa şirketlerini piyasa ağırlığıyla tutuyor; bu da fonu birkaç ülkede ve '
         'birkaç çok büyük teknoloji ve internet şirketinde yoğunlaştırıyor. FTSE Güney Kore’yi '
         'gelişmiş sayıyor, dolayısıyla MSCI versiyonunun aksine bu fonda Kore şirketleri yok.'),
 'IEMG': ('MSCI’ın tanımıyla gelişmekte olan piyasalar — Güney Kore dahil.',
          'VWO’dan temel farkı ülke sınıflandırması: MSCI Güney Kore’yi gelişmekte olan sayıyor, bu '
          'yüzden bu fonda VWO’da olmayan büyük Kore şirketleri var. Küçüklere de daha derin iniyor. '
          'Onun dışında benzer davranıyorlar.'),
 'EFA': ('Orijinal uluslararası gelişmiş piyasa fonu; yalnızca büyük ve orta ölçek.',
         'IEFA’dan daha eski ve daha pahalı; aynı piyasaları kapsıyor ama küçükler yok. Elde tutulacak '
         'daha iyi fon olduğu için değil, derin opsiyon piyasası ve kurumsal mandalardaki ölçüt rolü '
         'sayesinde ayakta.'),
 'VT': ('Gezegendeki yatırım yapılabilir tüm hisse senedi piyasası, tek bir pozisyonda.',
        'Gelişmiş ve gelişmekte olan piyasalardan yaklaşık on bin şirketi piyasa ağırlığıyla tutuyor; '
        'bu da bugün yaklaşık üçte iki ABD demek. Küresel piyasa portföyüne sahip olmanın mevcut en '
        'yakın hâli ve hiçbir ülkeye ne kadar ayıracağınıza karar vermenizi gerektirmiyor.'),
 'VGK': ('Avrupa şirketleri; Birleşik Krallık ve İsviçre’den İskandinavya’ya.',
         'Gelişmiş Avrupa’ya piyasa ağırlıklı maruziyet; bu da fonu ilaç, lüks tüketim, yarı iletken '
         'ekipmanı ve bankacılıktaki birkaç çok büyük şirkette yoğunlaştırıyor. Euro, sterlin ve dolar '
         'arasındaki hareketler herhangi bir yılın getirisinin önemli bir kısmını açıklıyor.'),
 'VEU': ('ABD dışındaki dünya; yalnızca büyük ve orta ölçek.',
         'VXUS’a çok yakın ama küçükler yok; bu da onu ABD dışı endekslere hâkim büyük çokuluslularda '
         'biraz daha yoğun bırakıyor. Portföyde ikisi de aynı işi görüyor.'),
 'VGT': ('ABD teknoloji şirketleri; donanım ve yarı iletken üreticileri dahil.',
         'Teknoloji sektörünü MSCI’ın tanımıyla kapsıyor: yazılım, donanım ve yarı iletkenler var ama '
         'iletişim hizmetleri sayılan büyük internet ve medya şirketleri yok; tüketim sayılan Amazon '
         've Tesla da yok. Bu dışlamalar çoğu yatırımcının sandığından önemli ve QQQ ile asıl farkı '
         'oluşturuyor.'),
 'XLK': ('S&P 500’ün içindeki teknoloji şirketleri — sadece onlar.',
         'S&P 500 üyesi olup teknoloji sınıfındaki şirketlerle sınırlı; bu da onu VGT’den çok daha '
         'yoğun yapıyor: genelde 70’ten az pozisyon ve ilk ikisi fonun %40’ına yaklaşıyor. Sektör '
         'tanımları dönem dönem gözden geçiriliyor ve bu revizyonlar fonu bir gecede ciddi biçimde '
         'değiştirebiliyor.'),
 'SMH': ('En büyük 25 halka açık yarı iletken şirketi — çip döngüsünü oynamanın en yoğun yolu.',
         'Yalnızca 25 şirket tutuyor; bu da onu aşırı yoğun yapıyor: ilk iki ya da üç pozisyon fonun '
         'üçte biri olabiliyor. Yabancı çip üreticilerini ABD kotasyonları üzerinden içeriyor; SOXX '
         'tarihsel olarak bunu yapmıyordu. Yarı iletken talebi döngüsel ve bu fon her iki yönde de '
         'piyasadan çok daha fazla hareket ediyor.'),
 'SOXX': ('ABD’de işlem gören otuz yarı iletken şirketi; SMH’den biraz daha dağılmış.',
          'Tek bir pozisyonun ne kadar büyüyebileceğini sınırlayan tavanları olan bir ABD yarı iletken '
          'endeksini izliyor; yani SMH kadar tepesi ağır değil. Endeks metodolojisi birden fazla kez '
          'değişti — uzun vadeli performansını herhangi bir şeyle karşılaştırmadan önce bunu bilmekte '
          'fayda var.'),
 'XLF': ('S&P 500’ün içindeki bankalar, sigortacılar ve ödeme şirketleri.',
         'S&P 500 finans şirketlerini tavanlı piyasa ağırlıklarıyla tutuyor. Gayrimenkul kendi sektörüne '
         'ayrıldığından beri fon bankacılık, sigorta ve sermaye piyasalarına daha temiz bir bahis. '
         'Faize ve kredi koşullarına son derece duyarlı; onu almanın ya da ondan kaçınmanın asıl '
         'sebebi de bu.'),
 'XLV': ('Büyük ABD sağlık sektörü: ilaç, tıbbi cihaz, sigorta ve dağıtım.',
         'S&P 500 sağlık şirketlerini kapsıyor; bu da çok farklı işleri harmanlıyor: patente bağımlı '
         'ilaç üreticileri, istikrarlı cihaz üreticileri ve ekonomisini kamu politikasının belirlediği '
         'sigortacılar. ABD’de ilaç fiyatlaması ve sağlık politikası hepsini etkiliyor; sektörün siyasi '
         'haberlerle çoğundan fazla hareket etmesinin sebebi bu.'),
 'XLE': ('ABD petrol ve doğal gazı, iki devin hâkimiyetinde.',
         'S&P 500 enerji şirketlerini tutuyor ve sektörün tepesi çok ağır olduğu için en büyük iki '
         'entegre petrol şirketi genelde fonun %40’ı civarında. Üreticilerin faaliyet kaldıracıyla '
         'birlikte petrol fiyatına doğrudan bir bahis.'),
 'XLI': ('ABD sanayisi: havacılık, demiryolu, makine ve büyük holdingler.',
         'S&P 500 sanayi şirketlerini tutuyor; yıllara yayılan sipariş defteri olan savunma '
         'yüklenicilerinden döngüye bağlı makine üreticilerine uzanan gerçekten çeşitli bir grup. ABD '
         'imalatı ve altyapı harcamaları hakkındaki bir görüşü doğrudan ifade etmek için sık kullanılıyor.'),
 'VNQ': ('ABD gayrimenkulü, halka açık gayrimenkul ortaklıkları üzerinden.',
         'Veri merkezi, lojistik deposu, baz istasyonu kulesi, konut, perakende ve ofis alanlarında ABD '
         'REIT’lerini tutuyor. REIT’ler gelirlerinin çoğunu dağıtmak zorunda olduğu için fon yüksek '
         'temettü ödüyor ve faize olağanüstü duyarlı: yüksek faiz hem gayrimenkulün finanse edildiği '
         'borcu pahalılaştırıyor hem de aynı anda temettüyü daha az cazip kılıyor.'),
 'VHT': ('Tüm ABD sağlık sektörü, küçük biyoteknoloji şirketleri dahil.',
         'XLV’den daha geniş, çünkü S&P 500’ün ötesine orta ve küçük ölçeğe uzanıyor; bu da ona uzun '
         'bir biyoteknoloji kuyruğu kazandırıyor. O kuyruk, yalnızca büyüklerden oluşan bir sağlık '
         'fonunda olmayan bir oynaklık ve olağanüstü getiri ihtimali ekliyor.'),
 'BND': ('ABD yatırım yapılabilir tahvil piyasası: devlet, ipotek ve şirket borcu bir arada.',
         'Binlerce yatırım yapılabilir tahvili endeks ağırlığıyla tutuyor; bu da yaklaşık üçte iki '
         'devlet ve devlet destekli ipotek borcu demek. Faizler yükselince fiyatı düşüyor, düşünce '
         'yükseliyor; yaklaşık altı yıllık durasyonu bunun ne kadar olacağını söylüyor. Bir portföyde '
         'getiri kaynağı değil, standart denge unsuru.'),
 'AGG': ('BND ile aynı ABD tahvil piyasası, BlackRock’tan.',
         'Bloomberg US Aggregate endeksini düzeltilmemiş hâliyle izliyor. BND ile pratik farkı ihmal '
         'edilebilir: biraz farklı bir dolaşım düzeltmesi ve marjinal bir maliyet farkı. Aracı '
         'kurumunuzda hangisi daha ucuza işlem görüyorsa o.'),
 'BNDX': ('ABD dışından yatırım yapılabilir tahviller, kur riski korunmuş.',
          'ABD dışı yatırım yapılabilir borcu, çoğunlukla Avrupa ve Japonya devlet tahvillerini tutuyor '
          've kur maruziyetini dolara karşı koruyor. Asıl önemli nokta bu koruma: korunmamış bir yabancı '
          'tahvil esasen bir kur bahsidir; korumak onu ABD faizlerine karşı gerçek bir çeşitlendiriciye '
          'dönüştürüyor.'),
 'GLD': ('Londra’da bir kasada tutulan fiziki altın, paylara bölünmüş.',
         'Her pay, tahsisli saklamadaki altının bir ons kesrini temsil ediyor. Gelir ve kâr yok: getiri, '
         'altın fiyatı eksi saklama maliyeti; bu maliyet her yıl az miktarda altın satılarak düşülüyor, '
         'dolayısıyla pay başına altın yavaşça azalıyor. ABD’de vergilemesi hisse senedinden farklı, bu '
         'da vergiye tabi hesaplarda önemli.'),
 'IAU': ('GLD ile aynı fiziki altın, daha düşük yıllık maliyetle.',
         'Özü itibarıyla GLD ile aynı — tahsisli fiziki altın, gelir yok, maliyet metalden düşülüyor — '
         'ama daha az kesiyor; on yılda bileşiklenince bu kayda değer bir fark. GLD’nin işlem hacmi ve '
         'opsiyon piyasası daha derin.'),
 'IBIT': ('Bir saklayıcıda tutulan bitcoin; hisse gibi alınıp satılıyor.',
          'Bitcoin’i doğrudan kurumsal bir saklayıcıda tutuyor, dolayısıyla pay fiyatı bitcoin fiyatını '
          'eksi komisyon izliyor. Özel anahtar yönetme ya da kripto borsası kullanma ihtiyacını ortadan '
          'kaldırıyor; tarihteki hiçbir ETF lansmanından daha hızlı para toplamasının sebebi tam olarak '
          'bu. Dayanak varlık nakit akışı üretmiyor, yani onu değerleyecek bir şey yok.'),
}

# columns of the index box: the type tag, the localised name grammar and the P/E note
UI.update({
    'type': 'Tür',
    'avg_yr': 'Yıllık ortalama',
    'pe_avg': 'Ortalama F/K',
    'name_pattern': '%(issuer)s %(index)s',
    'note_peavg': 'Bir fonun geçmiş F/K’sını kimse yayımlamıyor, çünkü o fonun o tarihte ne tuttuğuna bağlı. Bu yüzden kendi kaydımızı %(since)s tarihinde başlattık. Ortalama sütunu yaklaşık bir aylık veri birikince dolmaya başlıyor.',
    'note_peavg_none': 'Ortalama F/K sütunu, her günün değerini kaydettikçe doluyor.',
    'focus_labels': {'US large cap': 'ABD büyük', 'US total market': 'Tüm ABD piyasası', 'US large cap growth': 'ABD büyüme', 'US mega cap growth': 'Mega büyüme', 'US large cap value': 'ABD değer', 'US quality factor': 'ABD kalite', 'US dividend': 'ABD temettü', 'US dividend growth': 'Temettü büyümesi', 'US mid cap': 'ABD orta', 'US small cap': 'ABD küçük', 'developed ex-US': 'Gelişmiş, ABD hariç', 'global ex-US': 'Global, ABD hariç', 'global': 'Global', 'emerging markets': 'Gelişmekte olan', 'Europe': 'Avrupa', 'technology': 'Teknoloji', 'semiconductors': 'Yarı iletken', 'financials': 'Finans', 'healthcare': 'Sağlık', 'energy': 'Enerji', 'industrials': 'Sanayi', 'real estate': 'Gayrimenkul', 'US investment grade bonds': 'ABD tahvil', 'international bonds': 'Uluslararası tahvil', 'gold': 'Altın', 'bitcoin': 'Bitcoin'},
})

UI['pe_short'] = 'F/K'

# the European-alternative wording from etf_list.py, in this edition's language
UCITS = {'VUAA accumulates dividends, VUSA pays them out.': 'VUAA temettüyü biriktiriyor, VUSA dağıtıyor.', 'The same index from the same manager, in a European wrapper.': 'Aynı yöneticiden aynı endeks, Avrupa kabında.', 'No European fund replicates SPY’s trust structure, and none needs to.': 'SPY’nin trust yapısını hiçbir Avrupa fonu taklit etmiyor, buna gerek de yok.', 'Closest European equivalent; it includes Canada, which VTI does not.': 'En yakın Avrupa karşılığı; VTI’nin içermediği Kanada’yı içeriyor.', 'Both track the same index; CNDX accumulates, EQQQ distributes.': 'İkisi de aynı endeksi izliyor; CNDX biriktiriyor, EQQQ dağıtıyor.', 'Several providers offer one; there is no single obvious equivalent.': 'Birkaç sağlayıcıda var; tek bir bariz karşılığı yok.', 'Available from several providers; check which value definition it uses.': 'Birkaç sağlayıcıda var; hangi değer tanımını kullandığına bakın.', 'The ten-year increase screen is uncommon in European wrappers.': 'On yıllık artış filtresi Avrupa kaplarında yaygın değil.', 'Nothing in Europe replicates the Dow Jones 100 methodology exactly.': 'Avrupa’da Dow Jones 100 metodolojisini birebir tekrarlayan bir ürün yok.', 'Global rather than US-only, but the same family and methodology.': 'Yalnız ABD değil küresel, ama aynı aile ve aynı metodoloji.', 'IWDA includes the US; VEVE ex-US variants differ by provider.': 'IWDA ABD’yi içeriyor; ABD hariç sürümler sağlayıcıya göre değişiyor.', 'VWRL includes the US as well; there is no exact ex-US twin in the range.': 'VWRL ABD’yi de içeriyor; seride ABD hariç birebir eşi yok.', 'World includes the US; EAFE-only UCITS versions exist but are less traded.': 'Dünya endeksi ABD’yi içeriyor; yalnızca EAFE olan UCITS sürümleri var ama daha az işlem görüyor.', 'VWCE accumulates dividends, VWRL distributes them.': 'VWCE temettüyü biriktiriyor, VWRL dağıtıyor.', 'European equivalents are exchange-traded commodities, not UCITS funds.': 'Avrupa’daki karşılıkları UCITS fonu değil, borsada işlem gören emtia ürünleri.', 'UCITS rules do not permit a single-asset crypto fund.': 'UCITS kuralları tek varlıklı bir kripto fonuna izin vermiyor.', 'A UCITS ETF tracking a US large-cap growth index': 'ABD büyük şirket büyüme endeksini izleyen bir UCITS ETF', 'A UCITS ETF tracking a US large-cap value index': 'ABD büyük şirket değer endeksini izleyen bir UCITS ETF', 'A UCITS ETF tracking a US dividend growth index': 'ABD temettü büyümesi endeksini izleyen bir UCITS ETF', 'A UCITS ETF tracking a quality US dividend index': 'ABD kaliteli temettü endeksini izleyen bir UCITS ETF', 'A UCITS ETF tracking the Russell 1000 Growth index': 'Russell 1000 Growth endeksini izleyen bir UCITS ETF', 'A UCITS ETF tracking the Russell 1000 Value index': 'Russell 1000 Value endeksini izleyen bir UCITS ETF', 'A UCITS ETF tracking the Russell 2000': 'Russell 2000’i izleyen bir UCITS ETF', 'A UCITS ETF tracking the S&P MidCap 400': 'S&P MidCap 400’ü izleyen bir UCITS ETF', 'A UCITS ETF tracking the S&P SmallCap 600': 'S&P SmallCap 600’ü izleyen bir UCITS ETF', 'A UCITS ETF tracking a US mid-cap index': 'ABD orta ölçek endeksini izleyen bir UCITS ETF', 'A UCITS ETF tracking a US small-cap index': 'ABD küçük ölçek endeksini izleyen bir UCITS ETF', 'A UCITS ETF tracking the S&P 500 Equal Weight index': 'S&P 500 Eşit Ağırlık endeksini izleyen bir UCITS ETF', 'A UCITS ETF tracking a US mega-cap growth index': 'ABD mega ölçek büyüme endeksini izleyen bir UCITS ETF', 'A UCITS ETF tracking US or world information technology': 'ABD ya da dünya bilgi teknolojisini izleyen bir UCITS ETF', 'A UCITS ETF tracking global semiconductors': 'Küresel yarı iletkenleri izleyen bir UCITS ETF', 'A UCITS ETF tracking US or developed-market property': 'ABD ya da gelişmiş piyasa gayrimenkulünü izleyen bir UCITS ETF', 'A UCITS ETF tracking US health care': 'ABD sağlık sektörünü izleyen bir UCITS ETF', 'European investors use exchange-traded products rather than UCITS funds': 'Avrupalı yatırımcılar UCITS fonu yerine borsada işlem gören ürünleri kullanıyor', 'A EUR-hedged global aggregate bond UCITS ETF': 'Euro’ya kur korumalı küresel tahvil UCITS ETF’i', 'A USD-hedged global or US aggregate bond UCITS ETF': 'Dolara kur korumalı küresel ya da ABD tahvil UCITS ETF’i', 'Screened US dividend UCITS funds': 'Filtrelenmiş ABD temettü UCITS fonları'}

UCITS.update({'Invesco EQQQ Nasdaq-100 UCITS ETF, or iShares Nasdaq 100 UCITS ETF': 'Invesco EQQQ Nasdaq-100 UCITS ETF ya da iShares Nasdaq 100 UCITS ETF', 'Vanguard FTSE Developed World UCITS ETF, or iShares Core MSCI World': 'Vanguard FTSE Developed World UCITS ETF ya da iShares Core MSCI World', 'Vanguard FTSE Emerging Markets UCITS ETF, or iShares Core MSCI EM IMI': 'Vanguard FTSE Emerging Markets UCITS ETF ya da iShares Core MSCI EM IMI'})

# phone layout: return ranking, fund finder, quick keys (etf_pages.py, web_src/etfm.*)
UI.update({'rank_h': 'Getiri sıralaması', 'rank_all': '%(n)s fonun tümünü göster ▾', 'rank_less': 'Yalnızca ilk 10 ▴', 'rank_note': 'Temettü hariç fiyat getirisi. Sayfasını açmak için bir fona dokunun.', 'find_ph': '{N} fon içinde ara: kod, ad veya tür', 'sort_big': 'En büyük', 'sort_pe': 'En düşük F/K', 'n_funds': '%n fon', 'no_fund': 'Aramayla eşleşen fon yok.', 'more': 'Devamını oku ▾', 'less': 'Daha az göster ▴', 'holds_all': '%(n)s varlığın tümünü göster ▾', 'holds_less': 'Yalnızca ilk 10 ▴', 'k_idea': 'Fikir', 'k_val': 'Değerleme', 'k_ret': 'Getiri', 'k_hold': 'Varlıklar', 'k_sec': 'Sayfa bölümleri', 'k_find': 'Ara', 'k_ph': 'Hisse veya ETF ara', 'k_none': 'Sonuç yok', 'l_y1': 'Son 1 yıl', 'l_avg': 'Yıllık ort.', 'l_hold': 'Varlık', 'l_pe': 'F/K'})

# ---- funds 51-100 (Nov 2026)
UI['focus_labels'].update({'US treasury bonds': 'ABD Hazine tahvilleri', 'US corporate bonds': 'ABD şirket tahvilleri', 'high yield bonds': 'Yüksek getirili tahviller', 'municipal bonds': 'Belediye tahvilleri', 'US covered call': 'Opsiyonla gelir', 'consumer discretionary': 'İsteğe bağlı tüketim', 'consumer staples': 'Temel tüketim', 'utilities': 'Kamu hizmetleri', 'materials': 'Hammadde', 'communication services': 'İletişim', 'biotech': 'Biyoteknoloji', 'aerospace and defense': 'Havacılık ve savunma', 'banks': 'Bankalar', 'gold miners': 'Altın madencileri', 'oil and gas': 'Petrol ve gaz', 'cybersecurity': 'Siber güvenlik', 'clean energy': 'Temiz enerji', 'innovation': 'İnovasyon', 'US momentum': 'ABD momentum', 'US low volatility': 'ABD düşük oynaklık', 'Japan': 'Japonya', 'China': 'Çin', 'India': 'Hindistan', 'Brazil': 'Brezilya', 'silver': 'Gümüş', 'ether': 'Ether'})

_G = UI['groups']
_G[1][1].extend(['US momentum', 'US low volatility'])
_G[2][1].append('US covered call')
_G[4][1].extend(['Japan', 'China', 'India', 'Brazil'])
_G[5][1].extend(['consumer discretionary', 'consumer staples', 'utilities', 'materials', 'communication services', 'biotech', 'aerospace and defense', 'banks', 'gold miners', 'oil and gas', 'cybersecurity', 'clean energy', 'innovation'])
_G[6][1].extend(['US treasury bonds', 'US corporate bonds', 'high yield bonds', 'municipal bonds', 'silver', 'ether'])
T.update({'ACWI': ('Gelişmiş ve gelişmekte olan piyasalarda yaklaşık 2.500 büyük ve orta ölçekli şirket.',
          'Dünya borsasını büyüklüğe göre tutuyor, yaklaşık üçte ikisi ABD; VT’ye benzer ama küçük şirketler olmadan tek fonluk küresel portföy.'),
 'ARKK': ('Cathie Wood’un yıkıcı teknolojiye aktif ve yoğun bahsi.', 'Yöneticinin seçtiği birkaç düzine şirket; 2020’de %150’den fazla yükseldi, sonra zirvesinden yaklaşık %75 düştü.'),
 'BIL': ('Bir-üç ay vadeli Hazine bonoları: en eski nakit benzeri ETF.',
         'SGOV ile aynı işi biraz daha yüksek ücretle yapıyor ve faizi aylık dağıtıyor; uzun geçmişi onu nakit getirisinin referansı yapıyor.'),
 'BSV': ('Kısa vadeli ABD devlet ve kaliteli şirket tahvilleri tek bir ucuz fonda.',
         'Bir-beş yıl vadeli tahviller; üçte ikisi devlet, üçte biri yatırım yapılabilir şirket. Nakitten bir adım ötesi için muhafazakâr bir seçenek.'),
 'CIBR': ('Yazılımdan ağ ekipmanına siber güvenlik şirketleri.',
          'CrowdStrike, Palo Alto Networks ve Cisco var, en büyüklere tavan uygulanıyor. Güvenlik harcaması zayıf BT bütçelerinde bile dayanıklı kaldı.'),
 'EEM': ('Orijinal gelişmekte olan piyasalar ETF’si; uzun vadeli yatırımcıdan çok trader kullanıyor.',
         'Neredeyse aynı şirketleri tutan IEMG ve VWO’dan pahalı, ama işlem ve opsiyon için en likit fon.'),
 'ETHA': ('Ethereum ağının para birimi ether, normal bir aracı kurum hesabından.', 'Ether bitcoinden daha oynak ve değeri Ethereum ağındaki faaliyete bağlı.'),
 'EWJ': ('Büyük ve orta ölçekli Japon şirketleri.', 'Toyota, Sony ve Mitsubishi UFJ gibi şirketler; dolar yatırımcısı için getiri hem Japon borsasına hem yıllardır zayıf olan yene bağlı.'),
 'EWZ': ('Brezilya’nın en büyük şirketleri: emtia, bankalar ve yüksek temettü.', 'Petrobras, Vale ve Itaú ağırlıklı; emtia, real ve Brezilya siyasetine göre dalgalanıyor.'),
 'FBTC': ('Fidelity’nin kendisinin sakladığı spot bitcoin, en büyük ikinci bitcoin ETF’si.', 'Fidelity bir kripto borsasına bağlı kalmadan kendi saklayıcısı; fiyat bitcoin eksi ücreti izliyor.'),
 'FXI': ('Hong Kong’da işlem gören en büyük 50 Çin şirketi.',
         'MCHI’den daha yoğun; bankalar, internet platformları ve devlet şirketleri ağır. Teşvik ya da gümrük vergisi haberlerine hızlı bahis için kullanılıyor.'),
 'GDX': ('Altın madencileri: altını kaldıraçlı biçimde tutmanın yolu.', 'Maliyetleri büyük ölçüde sabit olduğu için kârları altından hızlı yükseliyor ve hızlı düşüyor.'),
 'GLDM': ('GLD’den daha düşük ücretli ve pay fiyatlı fiziki altın.',
          'GLD gibi Londra’da külçe tutuyor ama çok daha az ücret alıyor; uzun vadede bu önemli. Büyük işlemciler likidite için yine GLD’yi tercih ediyor.'),
 'HYG': ('Hurda tahviller: daha riskli ABD şirketlerine borç vererek daha yüksek gelir.',
         'Getiri yüksek çünkü bazı ihraççılar batıyor; resesyonda neredeyse hisseler kadar düşebiliyor, yani güvenli bir varlıktan çok hisse-tahvil karışımı.'),
 'IBB': ('Büyüklüğe göre ağırlıklı ABD biyoteknoloji şirketleri, ürünü piyasada olan büyüklerin önderliğinde.', 'Amgen, Gilead ve Vertex ağır basıyor; bu yüzden XBI’den daha istikrarlı.'),
 'ICLN': ('Dünya genelinde güneş, rüzgâr ve yenilenebilir enerji şirketleri.', 'Faizlere ve teşviklere çok bağlı; 2020’de uçtu, sonra faizler yükselince kazancının çoğunu geri verdi.'),
 'IEF': ('On yıllık Hazine tahvilleri: resesyona karşı klasik portföy koruması.',
         'Uzun vadeli faizdeki her puanda fiyatı %7-8 değişiyor. Büyüme korkusuyla hisseler düşerken genellikle yükseliyor, enflasyon faizi itince 2022’deki gibi düşüyor.'),
 'INDA': ('Büyük ve orta ölçekli Hint şirketleri.',
          'HDFC Bank, Reliance, Infosys ve ICICI Bank. Hindistan’ın hızlı büyümesi borsasına dünyanın en yüksek değerlemelerinden birini verdi; hata payı az.'),
 'ITA': ('ABD savunma şirketleri ve uçak üreticileri.', 'Savunma bütçeleri uzun sözleşmeler ve görünürlük sağlıyor; ticari kısım hava trafiğini izliyor.'),
 'IXUS': ('ABD dışındaki tüm borsalar, tek ucuz fonda.', 'iShares’in VXUS karşılığı ve iki fonlu bir portföyde ABD fonunun olağan eşi.'),
 'JEPI': ('Defansif ABD hisseleri artı opsiyon geliri: yükselişi sınırlamak karşılığında yüksek aylık ödeme.',
          'Alım opsiyonu satarak gelecekteki kazancın bir kısmını aylık gelire çeviriyor. Düşüşlerde daha az kaybediyor, güçlü yükselişlerde çok geride kalıyor; yüksek getirinin bir kısmı '
          'yatırımcının kendi yükselişinin geri ödenmesi.'),
 'JEPQ': ('Nasdaq-100 hisseleri artı opsiyon geliri: QQQ’dan az yükselişle çift haneli getiri.',
          'Nasdaq opsiyonları pahalı olduğu için ödeme yüksek, ama güçlü bir teknoloji rallisinde fon kazancın yalnızca bir kısmını alıyor.'),
 'JNK': ('State Street’in yüksek getirili tahvil fonu, HYG’nin ana rakibi.', 'HYG’yi çok yakından izliyor; farklar küçük endeks kurallarından ve ücretlerden geliyor.'),
 'KRE': ('Eşit ağırlıklı ABD bölgesel bankaları: iç ekonomiye ve getiri eğrisine bahis.',
         'Mevduat ile kredi faizi arasındaki farktan kazanıyor ve ticari gayrimenkul kredisi taşıyorlar; 2023 banka iflaslarının gösterdiği gibi faize ve kredi korkusuna çok duyarlılar.'),
 'LQD': ('En çok işlem gören ABD şirket tahvili fonu, uzun vadelerle.',
         'Şirket kredisi ile uzun vadeyi birleştirdiği için VCIT’ten fazla dalgalanıyor; kurumlar onu kredi piyasasında hızlı işlem için kullanıyor.'),
 'MCHI': ('Hong Kong, ABD ve Çin anakarasında işlem gören Çin şirketleri.',
          'Tencent, Alibaba, PDD ve Meituan; getiri şirket sonuçları kadar Çin büyümesine, Pekin politikasına ve ABD-Çin ilişkilerine bağlı.'),
 'MTUM': ('Son dönemde en çok yükselen ABD hisseleri, yılda iki kez yenileniyor.',
          'Altı-on iki ayda en çok yükselenleri alıyor; trendleri iyi yakalıyor ama piyasa liderliği aniden değişince zarar görüyor.'),
 'MUB': ('ABD eyalet ve şehirlerinin vergiden muaf tahvilleri.',
         'Faiz ABD federal vergisinden muaf; bu avantaj yalnızca ABD’de vergi ödeyenler için geçerli, yabancı yatırımcı için düşük getiri pek anlam taşımıyor.'),
 'SCHB': ('Büyük ve küçük yaklaşık 2.500 ABD şirketi, neredeyse bedavaya.', 'Schwab’ın VTI’ya cevabı ve neredeyse aynı getiriyi veriyor.'),
 'SCHF': ('ABD dışındaki gelişmiş ülkelerin büyük şirketleri.', 'Avrupa, Japonya, İngiltere, Kanada ve Avustralya çok düşük maliyetle; VEA ve IEFA’ya neredeyse aynı getirili bir alternatif.'),
 'SCHG': ('En düşük maliyetlerden biriyle büyük ABD büyüme şirketleri.', 'Büyük teknoloji ağırlıklı; VUG ve QQQ’ya çok benziyor, QQQ’dan biraz daha geniş.'),
 'SGOV': ('Üç aydan kısa vadeli ABD Hazine bonoları: kısa vadeli faizi ödeyen bir nakit ikamesi.',
          'Yalnızca üç aydan kısa vadeli bonolar tuttuğu için fiyatı neredeyse hiç oynamıyor; getirisi Fed’in politika faizi eksi küçük bir ücret. Fed faiz indirince geliri hemen düşüyor.'),
 'SHV': ('Bir yıldan kısa vadeli Hazine tahvilleri: biraz daha fazla getirili nakit.',
         'Üç aylık bir fondan biraz daha fazla faize duyarlı, ama değer kaybetmemesi gereken para için hâlâ uygun bir yer.'),
 'SHY': ('Bir-üç yıl vadeli Hazine tahvilleri: düşük risk, faiz düşünce küçük bir kazanç.',
         'Faizdeki her bir puanlık değişimde fiyatı yaklaşık %2 oynuyor; Fed indirince biraz kazanıyor, artırınca biraz kaybediyor.'),
 'SLV': ('Kasalarda saklanan fiziki gümüş.', 'Gümüş kısmen değerli metal, kısmen güneş paneli ve elektronikte kullanılan sanayi metali; bu yüzden altından daha oynak.'),
 'TIP': ('Enflasyona karşı korumalı Hazine tahvilleri: anapara TÜFE ile artıyor.',
         'Enflasyon beklentiyi aşınca normal tahvilleri geçiyor, ama reel faizler yükselince yine düşüyor; bu 2022’de birçok yatırımcıyı şaşırttı.'),
 'TLT': ('Yirmi yıldan uzun vadeli Hazine tahvilleri: kredi riski olmadan faiz düşüşüne kaldıraçlı bir bahis.',
         'Uzun faizde bir puanlık düşüş onu yaklaşık %16 yükseltiyor, bir puanlık artış da aynı kadar düşürüyor; bu yüzden 2020-2023 arasında değerinin neredeyse yarısını kaybetti.'),
 'USMV': ('Mümkün olan en az dalgalanmayı verecek şekilde bir araya getirilmiş ABD hisseleri.',
          'Kamu hizmetleri, temel tüketim ve sağlığa eğilimli; düşüşlerde daha az kaybediyor, güçlü yükselişlerde geride kalıyor.'),
 'VCIT': ('Büyük ABD şirketlerinin beş-on yıl vadeli tahvilleri: Hazine’den yüksek getiri, biraz kredi riski.',
          'Şirketlere borç vermenin karşılığında Hazine üzerine bir prim alınıyor; resesyonda bu prim açılıyor ve devlet tahvilleri yükselse bile fon düşüyor.'),
 'VCSH': ('Büyük ABD şirketlerinin kısa vadeli tahvilleri: nakde göre biraz daha fazla getiri.',
          'Kısa vadeler hem faiz riskini hem temerrüt kayıplarını küçük tutuyor; normal dönemlerde daha yüksek getirili bir para piyasası fonu gibi davranıyor.'),
 'VGIT': ('Vanguard’ın düşük maliyetiyle üç-on yıl vadeli Hazine tahvilleri.',
          'Getiri eğrisinin ortasını tutuyor; faize duyarlılıkta SHY ile IEF arasında ve uzun vadelilerin dalgalanması olmadan devlet tahvili isteyenler için yaygın bir çekirdek.'),
 'VTEB': ('Vanguard’ın vergiden muaf ABD belediye tahvilleri sepeti.',
          'MUB gibi yalnızca ABD’de vergi ödeyenler için mantıklı; onlar için vergisiz gelir, vergili bir tahvilin daha yüksek getirisinden değerli.'),
 'XBI': ('Eşit ağırlıklı ABD biyoteknoloji şirketleri: küçük ilaç geliştiricilerine ve satın almalara bahis.',
         'Klinik aşamadaki küçükler büyükler kadar ağırlık taşıyor; faiz, deney sonuçları ve satın almalara göre bir yılda %50 inip çıkabiliyor.'),
 'XLB': ('S&P 500’ün kimya, endüstriyel gaz, metal ve ambalaj şirketleri.',
         'Kârları küresel sanayi talebini ve emtia fiyatlarını izliyor; döngüsel ve toparlanmanın başında en iyi performansı gösteriyor.'),
 'XLC': ('Meta, Alphabet, Netflix ve S&P 500’ün telekom şirketleri.', 'Meta ve Alphabet fonun neredeyse yarısı; getirisi büyük ölçüde dijital reklama bağlı.'),
 'XLP': ('Gıda, içecek, ev ürünleri ve süpermarketler: ekonomi endişelendirdiğinde tutulan hisseler.',
         'Talep resesyonda istikrarlı, bu da sektörü defansif yapıyor; ama yavaş büyüme, özel markalar ve zayıflama ilaçları baskı yarattı.'),
 'XLRE': ('S&P 500’ün gayrimenkul şirketleri: kuleler, depolar, veri merkezleri ve konutlar.', 'GYO’lar kârın çoğunu dağıtıyor ve faize duyarlı; tahvil getirileri düşünce fon genellikle yükseliyor.'),
 'XLU': ('Elektrik ve gaz şirketleri: temettü, düzenleme ve şimdi yapay zekânın enerji talebi.',
         'Eskiden tahvil benzeri bir gelir sektörüydü; artık kısmen yapay zekâ bahsi, çünkü veri merkezleri çok büyük miktarda elektrik istiyor.'),
 'XLY': ('S&P 500’ün ertelenebilir tüketim şirketleri, Amazon ve Tesla ağırlıklı.',
         'Perakendeciler, otomobil üreticileri, restoranlar ve oteller var; ama Amazon ve Tesla o kadar ağır ki tüketiciye bahisten çok büyük teknoloji fonu gibi davranıyor.'),
 'XOP': ('Eşit ağırlıklı ABD petrol ve gaz üreticileri: petrol fiyatına neredeyse doğrudan bahis.',
         'Küçük kaya petrolü üreticileri büyükler kadar ağır; bu yüzden Exxon ve Chevron ağırlıklı XLE’den daha çok petrolle hareket ediyor.')})
UCITS.update({'A UCITS 0-5 year USD corporate bond ETF': '0-5 yıl vadeli dolar şirket tahvili UCITS ETF’si',
 'A UCITS 1-3 year US Treasury ETF': '1-3 yıl vadeli ABD Hazine UCITS ETF’si',
 'A UCITS 20+ year US Treasury ETF': '20 yıldan uzun vadeli ABD Hazine UCITS ETF’si',
 'A UCITS 7-10 year US Treasury ETF': '7-10 yıl vadeli ABD Hazine UCITS ETF’si',
 'A UCITS ETF tracking the whole US market': 'tüm ABD piyasasını izleyen bir UCITS ETF’si',
 'A UCITS US TIPS ETF': 'ABD enflasyona endeksli tahvil UCITS ETF’si',
 'A UCITS US Treasury ETF': 'ABD Hazine UCITS ETF’si',
 'A UCITS US communication services sector ETF': 'ABD iletişim sektörü UCITS ETF’si',
 'A UCITS US consumer discretionary sector ETF': 'ABD isteğe bağlı tüketim UCITS ETF’si',
 'A UCITS US consumer staples sector ETF': 'ABD temel tüketim UCITS ETF’si',
 'A UCITS US materials sector ETF': 'ABD hammadde UCITS ETF’si',
 'A UCITS US property ETF': 'ABD gayrimenkul UCITS ETF’si',
 'A UCITS US utilities sector ETF': 'ABD kamu hizmetleri UCITS ETF’si',
 'A UCITS USD corporate bond ETF': 'dolar şirket tahvili UCITS ETF’si',
 'A UCITS USD high yield bond ETF': 'dolar yüksek getirili tahvil UCITS ETF’si',
 'A UCITS aerospace and defence ETF': 'havacılık ve savunma UCITS ETF’si',
 'A UCITS cybersecurity ETF': 'siber güvenlik UCITS ETF’si',
 'A UCITS developed-markets ex-US ETF': 'ABD hariç gelişmiş piyasalar UCITS ETF’si',
 'A UCITS ex-US world ETF': 'ABD hariç dünya UCITS ETF’si',
 'A UCITS short-term US aggregate bond ETF': 'kısa vadeli ABD toplam tahvil UCITS ETF’si',
 'A UCITS ultrashort US Treasury ETF': 'çok kısa vadeli ABD Hazine UCITS ETF’si',
 'Choose one matching the 3-10 year maturity range.': '3-10 yıl vade aralığına uyan birini seçin.',
 'European bank ETFs hold European banks.': 'Avrupa banka ETF’leri Avrupa bankalarını tutuyor.',
 'European biotech ETFs are weighted by size.': 'Avrupa biyoteknoloji ETF’leri büyüklüğe göre ağırlıklı.',
 'European energy ETFs are dominated by the integrated majors.': 'Avrupa enerji ETF’lerinde entegre devler baskın.',
 'European funds mix in European defence companies.': 'Avrupa fonları Avrupa savunma şirketlerini de içeriyor.',
 'European investors use physically backed gold ETCs': 'Avrupalı yatırımcılar fiziki altın ETC’leri kullanıyor',
 'European investors use physically backed silver ETCs': 'Avrupalı yatırımcılar fiziki gümüş ETC’leri kullanıyor',
 'Few European funds exclude the US; most investors use a world fund instead.': 'ABD’yi dışlayan Avrupa fonu az; çoğu yatırımcı dünya fonu kullanıyor.',
 'Few European funds hold small US companies; an S&P 500 fund is the usual substitute.': 'Küçük ABD şirketlerini tutan Avrupa fonu az; olağan ikame bir S&P 500 fonu.',
 'No UCITS equivalent': 'UCITS karşılığı yok',
 'No exact UCITS equivalent': 'tam bir UCITS karşılığı yok',
 'Several providers offer 0-1 or 0-3 month Treasury funds in Europe.': 'Avrupa’da birçok şirket 0-1 ya da 0-3 aylık Hazine fonu sunuyor.',
 'Several providers offer one.': 'Birçok şirket sunuyor.',
 'The tax exemption only benefits US taxpayers.': 'Vergi muafiyeti yalnızca ABD’de vergi ödeyenlere yarıyor.',
 'UCITS rules do not permit a single-commodity fund.': 'UCITS kuralları tek emtialı fona izin vermiyor.',
 'iShares and others list one in Europe.': 'iShares ve diğerleri Avrupa’da listeliyor.'})

# ---- karşılaştırmalar ve "hangi ETF’ler tutuyor"
UI.update({
    'c_title': '%(a)s mı %(b)s mi? Getiri, F/K ve örtüşme karşılaştırması',
    'c_h1': '%(a)s ile %(b)s karşılaştırması', 'c_crumb': '%(a)s – %(b)s',
    'c_sub': 'Getiri, tuttukları şirketlerin değerlemesi ve ne kadar örtüştükleri yan yana.',
    'c_what': 'Her biri nedir', 'c_side': 'Yan yana', 'c_says': 'Rakamlar ne diyor',
    'c_shared': 'Ortak en büyük pozisyonlar', 'c_issuer': 'Fon şirketi', 'c_index': 'Endeks',
    'c_with': '%(t)s ile karşılaştır',
    'v_ret': '%(w)s son bir yılda daha çok kazandırdı: %(x)s, karşısında %(y)s.',
    'v_pe': '%(w)s bizim F/K ölçümüze göre daha ucuz şirketler tutuyor: %(x)s, karşısında %(y)s.',
    'v_ov': '%(a)s fonunun en büyük pozisyonlarının ağırlıkça %(ov)s kadarı %(b)s fonunda da var; ikisini birden tutmak sanıldığı kadar çeşitlendirmiyor.',
    'v_noov': '%(a)s ile %(b)s en büyük pozisyonlarının hiçbirini paylaşmıyor; portföyde farklı işler görüyorlar.',
    'hold_slug': '%s-hangi-etflerde',
    'h_title': '%(name)s (%(t)s) hangi ETF’lerde var? Ağırlıklar ve getiri',
    'h_h1': '%(name)s hangi ETF’lerde var?',
    'h_lead': 'İzlediğimiz %(N)s ETF’nin %(n)s tanesi %(name)s hissesini en büyük pozisyonları arasında tutuyor.',
    'h_top': 'En yüksek ağırlık %(f)s fonunda: %(name)s fonun %(w)s kadarı.',
    'h_stock': '%(name)s için tam analizimizi okuyun ›',
    'h_note': 'Her fonun yayımladığı portföyden; yalnızca en büyük pozisyonlar kontrol edildiği için küçük pozisyonlar listede yok.',
})
