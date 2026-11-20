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
    h1='Dünyanın en büyük 50 ETF’si',
    sub='Portföy, ağırlıklar ve değerleme · güncellendi',
    lead='Dünyanın en büyük elli borsa yatırım fonu: her biri ne işe yarıyor, içinde ne var ve '
         'içindeki şirketler ne ediyor.',
    intro='Bu sayfalardaki F/K oranını fondan almıyoruz. Her pozisyon, o şirket için bizim kendi '
          'sayfamızla eşleştiriliyor ve rakamlar fonun kendi ağırlıklarıyla ağırlıklandırılıyor. '
          'Yani bir ETF’nin F/K’sı, bu sitedeki her hisse sayfasıyla aynı SEC bildirimlerinden '
          'çıkıyor — ve herhangi bir pozisyona tıklayıp şirketi okuyabilirsiniz.',
    idea='Fikir', ret='Getiri', fund='İçindeki şirketler ne ediyor',
    holds='En büyük pozisyonlar', made='Neyden oluşuyor',
    where='Yaşadığınız yerden alabilir misiniz?', company='Şirket', weight='Ağırlık',
    all50='Elli fon yan yana',
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
    i_title='En büyük 50 ETF: portföy, F/K ve getiri',
    i_desc='Dünyanın en büyük elli ETF’si; portföyleri, ağırlıkları, bir yıllık getirileri ve her '
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
         'oluyor. Karşılığında eşsiz bir likiditesi ve opsiyon piyasası var; trader’ların bunu '
         'kullanmasının, uzun vadeli yatırımcının genelde kullanmaması gerekmesinin sebebi bu.'),
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
 'SPLG': ('State Street’in ucuz S&P 500 fonu: işlem için değil, elde tutmak için.',
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
