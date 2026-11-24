"""story.py için Türkçe paket (borsakartal.com). Şirket adlarına ve sayılara ek getirilmez (ünlü uyumu hatası olmasın diye)."""
import datetime

AY = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']


def _d(v, d):
    s = ('{:,.%df}' % d).format(v)
    return s.replace(',', '\x00').replace('.', ',').replace('\x00', '.')


class F:
    @staticmethod
    def money(v):
        a = abs(v)
        if a >= 1e12: return '%s trilyon dolar' % _d(v / 1e12, 2)
        if a >= 1e9: return '%s milyar dolar' % _d(v / 1e9, 1)
        if a >= 1e6: return '%s milyon dolar' % _d(v / 1e6, 0)
        return '%s bin dolar' % _d(v / 1e3, 0)

    @staticmethod
    def pct(v, d=0):
        return ('−' if v < 0 else '') + '%' + _d(abs(v) * 100, d)

    @staticmethod
    def mpct(v):
        return ('−' if v < 0 else '') + '%' + _d(abs(v) * 100, 1 if abs(v) < 0.1 else 0)

    @staticmethod
    def spct(v):
        if abs(v) < 0.005:
            v = 0.0
        return ('' if v == 0 else '+' if v > 0 else '−') + '%' + _d(abs(v) * 100, 0)

    @staticmethod
    def num(v):
        return _d(v, 1)

    @staticmethod
    def times(v):
        return _d(v, 1 if v < 10 else 0)

    @staticmethod
    def price(v):
        a = abs(v); d = 2
        if 0 < a < 0.005:   # sub-cent EPS: show it, not "$0.00" (23 Nov 2026)
            d = 3 if a >= 0.0005 else 4
        return '%s%s dolar' % ('−' if v < 0 and round(a, d) else '', _d(a, d))

    @staticmethod
    def years(ys):
        ys = [str(y) for y in ys]
        return ys[0] if len(ys) == 1 else ', '.join(ys[:-1]) + ' ve ' + ys[-1]


def qdate(s):
    try:
        d = datetime.date.fromisoformat(str(s)[:10])
        return '%s %d ile biten çeyrek' % (AY[d.month - 1], d.year)
    except Exception:
        return 'son çeyrek'


def month(m):
    return AY[m - 1]


T = {
    'eps_up': ['Seyreltilmiş hisse başına kâr {fy0} mali yılında {e0} iken {fy1} mali yılında {e1} oldu; yılda yaklaşık {g} artış.', 'Hisse başına kâr {fy0} ile {fy1} mali yılları arasında {e0} seviyesinden {e1} seviyesine çıktı (yılda {g}).',
               'Hisse başına kâr yılda yaklaşık {g} büyüyor: {fy0} mali yılında {e0}, {fy1} mali yılında {e1}.'],
    'eps_faster': ['Hisse başına kâr satışlardan hızlı büyüdü: {fy0} mali yılında {e0}, {fy1} mali yılında {e1} (yılda {g}); bu süreçte marjlar genişledi.',
                   'Hisse başına kâr ciroyu geride bıraktı: {fy0} ile {fy1} mali yılları arasında {e0} seviyesinden {e1} seviyesine, yılda yaklaşık {g}.',
                   'Alt satır üst satırdan iyi gitti; hisse başına kâr yılda yaklaşık {g} artarak {e1} oldu ({fy0} mali yılı: {e0}).'],
    'eps_down': ['Seyreltilmiş hisse başına kâr {fy0} mali yılında {e0} iken {fy1} mali yılında {e1} seviyesine indi; yılda yaklaşık {g} düşüş.', 'Hisse başına kâr {fy0} ile {fy1} mali yılları arasında {e0} seviyesinden {e1} seviyesine geriledi.',
                 'Hisse başına kâr eskisinden düşük: {fy1} mali yılında {e1}, {fy0} mali yılında ise {e0}.'],
    'opm_up': ['Faaliyet kâr marjı geçen yıl {now} oldu; beş yıllık ortalama olan {avg} rakamının üstünde.', 'Faaliyet kârlılığı iyileşti: geçen yıl {now}, beş yıllık ortalama {avg}.',
               'Geçen yılki {now} faaliyet marjı beş yıllık ortalamayı ({avg}) geçti.'],
    'opm_down': ['Faaliyet kâr marjı geçen yıl {now} oldu; beş yıllık ortalama olan {avg} rakamının altında.', 'Faaliyet kârlılığı geriledi: geçen yıl {now}, beş yıllık ortalama {avg}.',
                 'Geçen yılki {now} faaliyet marjı beş yıllık ortalamanın ({avg}) gerisinde kaldı.'],
    'rnd': ['Araştırma ve geliştirmeye yılda {v} harcıyor; bu, gelirin {p} kadarı.', 'Ar-Ge harcaması satışların {p} kadarını alıyor (yılda {v}).', '{v} Ar-Ge harcaması gelirin {p} kadarına denk.'],
    'capex': ['Yatırım harcaması yüksek: yılda {v}, gelirin {p} kadarı.', 'Satışlarının {p} kadarını tesis ve ekipmana yeniden yatırıyor (yılda {v}).', 'Duran varlık yatırımı {v} düzeyinde; gelirin {p} kadarı.'],
    'int_tight': ['Faaliyet kârı {ie} faiz yükünü yalnızca {x} kat karşılıyor; ince bir tampon.', 'Yılda {ie} faiz, faaliyet kârının büyük kısmını yiyor (karşılama {x} kat).',
                  '{ie} faiz yüküne karşı {x} katlık faiz karşılama oranıyla kötü bir yıla pek yer yok.'],
    'int_easy': ['Faaliyet kârı faizi {x} kat karşılıyor: borç bir yük değil.', 'Faiz neredeyse önemsiz; faaliyet kârı onu {x} kat karşılıyor.', 'Faiz karşılama oranı rahat: {x} kat.'],
    'fy_end': ['Mali yılı {m} ayında kapanıyor.', 'Dikkat: mali yıl aralıkta değil, {m} ayında bitiyor.', 'Mali yılları {m} ayında sona eriyor.'],
    'head': ['Rakamlarla {name}: geçmiş ne söylüyor', 'Yıl yıl {name} karnesi', '{name} rakamlarını okumak'],
    'size_top': ['{name}, takip ettiğimiz ABD borsalarındaki {n} {ind} şirketi arasında en büyüğü: değeri {mcap}, ikinci sıradaki {other} şirketinin yaklaşık {x} katı.',
                 '{mcap} değerle {name}, listemizdeki {ind} grubunun başında: grupta {n} şirket var ve ikinci sıradaki {other} bundan {x} kat küçük.',
                 'Listemizde ABD borsalarında işlem gören hiçbir {ind} şirketi daha büyük değil: {name} için biçilen değer {mcap}, bu da {n} şirket içinde ikinci olan {other} değerinin {x} katı.'],
    'size_rank': ['{name} şirketinin piyasa değeri {mcap}; takip ettiğimiz {n} {ind} şirketi arasında büyüklükte {rank}. sırada.',
                  '{mcap} piyasa değeriyle {name}, listemizdeki {ind} sektöründe {n} şirket içinde {rank}. sırada yer alıyor.',
                  'ABD borsalarındaki {n} {ind} şirketi arasında {name}, piyasa değerine göre {rank}. sırada ({mcap}).'],
    'size_between': ['Hemen üstünde {bigger}, hemen altında {smaller} var.', 'Büyüklükte en yakın komşuları {bigger} (daha büyük) ve {smaller} (daha küçük).',
                     'Büyüklük olarak {bigger} ile {smaller} arasında duruyor.'],
    'size_last': ['Grubun en küçüğü; bir üstteki şirket {bigger}.', 'Grupta daha küçüğü yok; büyüklükte en yakını {bigger}.', 'Büyüklük sıralamasını {bigger} şirketinin hemen arkasında kapatıyor.'],
    'size_share': ['Tek başına sektörün toplam piyasa değerinin {share} kadarını oluşturuyor.', 'Bu, grubun toplam değerinin {share} kadarı demek.',
                   'Gruptaki ağırlığı büyük: toplam değerin {share} kadarı.'],
    'size_alone': ['{name} şirketinin piyasa değeri {mcap}.', 'Borsa {name} için {mcap} değer biçiyor.', '{name} borsada {mcap} ediyor.'],
    'hist_cagr_up': ['Gelir, {fy0} mali yılındaki {r0} seviyesinden {fy1} mali yılında {r1} seviyesine çıktı; {n} yılda yıllık ortalama yaklaşık {g} büyüme.',
                     '{n} yılda satışlar {r0} ({fy0} mali yılı) seviyesinden {r1} ({fy1} mali yılı) seviyesine geldi: bileşik olarak yılda yaklaşık {g}.',
                     'Satışlar {fy0} mali yılından bu yana yılda yaklaşık {g} büyüyor; {r0} seviyesinden {fy1} mali yılında {r1} seviyesine.'],
    'hist_cagr_flat': ['Gelir {n} yılda neredeyse hiç değişmedi: {fy0} mali yılında {r0}, {fy1} mali yılında {r1}.',
                       'Ciro {n} yıl önceki yerinde: {fy1} mali yılında {r1}, {fy0} mali yılında ise {r0}.',
                       '{fy1} mali yılındaki {r1} satış, {fy0} mali yılındaki {r0} rakamına çok yakın.'],
    'hist_cagr_down': ['Gelir {fy0} mali yılındaki {r0} seviyesinden {fy1} mali yılında {r1} seviyesine geriledi; yılda yaklaşık {g} düşüş.',
                       'İşletme eskisinden küçük: {fy1} mali yılında {r1} gelir, {fy0} mali yılında ise {r0} (yılda yaklaşık {g} gerileme).',
                       '{n} yılda satışlar yılda yaklaşık {g} azalarak {r0} seviyesinden {r1} seviyesine indi.'],
    'hist_no_down': ['Verilerimizdeki son {n} yılın her birinde gelir arttı; düşüş yılı yok.', 'Son {n} yılda hiç düşüş yılı yok: gelir her yıl büyüdü.',
                     'Karnede art arda {n} yıl boyunca hiç gelir düşüşü görünmüyor.'],
    'hist_down_one': ['Gelirin düştüğü tek yıl {fy} mali yılı oldu; düşüş {g}.', 'Tek kara leke {fy} mali yılı: o yıl gelir {g} geriledi.',
                      'Gelir yalnızca bir kez, {fy} mali yılında düştü ({g} daha düşük).'],
    'hist_down_many': ['Gelir {n} yıl düştü ({years}); en kötüsü {worst} mali yılıydı, düşüş {g}.',
                       'Düz bir çizgi değil: satışlar {years} yıllarında geriledi, en sert düşüş {worst} mali yılında ({g}).',
                       '{n} düşüş yılı var: {years}. En zoru {worst} mali yılıydı, gelir {g} geriledi.'],
    'hist_best': ['En güçlü yıl {fy} mali yılıydı; gelir {g} sıçradı.', 'Büyüme açısından en iyi yılı {fy} mali yılı oldu: {g} daha fazla gelir.',
                  '{fy} mali yılı öne çıkıyor; gelir {g} arttı.'],
    'hist_record': ['{fy} mali yılı geliri, verilerimizdeki en yüksek seviye oldu.', 'Son yıl, yani {fy} mali yılı, gelir rekoru getirdi.', '{fy} mali yılında gelir yeni zirveye çıktı.'],
    'hist_below_peak': ['Gelir hâlâ {fy} mali yılındaki {peak} zirvesinin {g} altında.', 'Ciro, {fy} mali yılındaki {peak} seviyesine dönmüş değil; arada {g} fark var.',
                        'Satışlar {fy} mali yılında {peak} ile zirve yaptı, şimdi {g} daha düşük.'],
    'prof_all': ['Elimizdeki {n} yılın her birinde kâr etti.', 'Son {n} yılın tamamı kârlı geçti.', 'Kayıtlı {n} yılda tek bir zarar yılı yok.'],
    'prof_never': ['Elimizdeki {n} yılın hiçbirinde yıllık kâr elde etmedi.', 'Kayıtlı {n} yılın hepsi zararla kapandı.', 'Kâr henüz gelmedi: {n} yıl, {n} zarar.'],
    'prof_turn': ['{years} yıllarındaki zararların ardından {fy} mali yılında kâra geçti ve orada kaldı.',
                  'Dönüm noktası {fy} mali yılı oldu: o zamandan beri kârlı; öncesinde {years} yıllarında zarar etmişti.',
                  '{fy} mali yılından beri kârda; daha önce {years} yıllarında zarar etti.'],
    'prof_slip': ['{fy} mali yılında yeniden zarara düştü; zarar {loss}.', '{fy} mali yılı, {loss} zararla kâr serisini bozdu.',
                  'Son yıl, yani {fy} mali yılı, kârlı bir yılın ardından {loss} zararla kapandı.'],
    'prof_mixed': ['Kâr gelip gidiyor: {span} yılın {n} tanesi zararlı ({years}).', '{span} yılın {n} tanesinde zarar etti ({years}).', 'Kazançlar düzensiz; {years} yıllarında zarar var.'],
    'prof_margin_off': ['Net kâr marjı {fy} mali yılında {peak} ile zirve yaptı, şimdi {now}.', 'Kârlılık en iyi döneminin gerisinde: bugün {now} net marj, {fy} mali yılında ise {peak}.',
                        'Marjlar {fy} mali yılındaki {peak} seviyesinden {now} seviyesine indi.'],
    'prof_margin_best': ['Son net kâr marjı ({m}) son {n} yılın en iyisi.', '{m} ile net marj, kayıtlı {n} yılın en yükseği.', 'Verilerimizde hiç bu kadar kârlı olmamıştı: net marj {m}.'],
    'fcf_all': ['Serbest nakit akışı {n} yılın hepsinde pozitifti.', '{n} yılın her birinde serbest nakit üretti.', 'Yatırım sonrası nakit akışı her yıl pozitif oldu ({n} yılda {n}).'],
    'fcf_none': ['Serbest nakit akışı {n} yılın hepsinde negatifti: işletme nakit tüketiyor.', '{n} yılın hiçbirinde serbest nakit üretmedi.', '{n} yılın her birinde girenden fazla nakit harcandı.'],
    'fcf_one': ['Serbest nakit akışı {n} yılın yalnızca birinde pozitifti.', '{n} yıl içinde sadece bir yıl serbest nakit üretti.', '{n} yılın yalnızca biri pozitif serbest nakit akışı bıraktı.'],
    'fcf_most': ['Serbest nakit akışı {n} yılın {pos} tanesinde pozitifti.', '{n} yılın {pos} tanesinde serbest nakit üretti.', 'Serbest nakit {n} yılın {pos} tanesinde pozitif oldu.'],
    'fcf_some': ['Serbest nakit akışı {n} yılın {pos} tanesinde pozitifti.', '{n} yılın {pos} tanesinde serbest nakit üretti.', 'Nakit üretimi düzensiz: {n} yılın {pos} tanesinde pozitif.'],
    'q_up': ['{q} döneminde gelir {rev} oldu; bir yıl öncesine göre {g} fazla.', '{q} için gelir {rev}; geçen yılın aynı çeyreğine göre {g} artış.',
             '{q} döneminde {rev} gelir geldi; yıllık bazda {g} artış.'],
    'q_flat': ['{q} döneminde gelir {rev}; bir yıl öncesiyle hemen hemen aynı.', '{q} için {rev} gelir, geçen yıla göre yatay.', '{q} döneminde satışlar {rev}; bir yıl önceki seviyede.'],
    'q_down': ['{q} döneminde gelir {rev} oldu; bir yıl öncesine göre {g} az.', '{q} için gelir yıllık bazda {g} düşerek {rev} oldu.', '{q} döneminde {rev} gelir geldi; bir yıl öncesine göre {g} düşüş.'],
    'q_streak': ['Böylece art arda {n} çeyrek yıllık büyüme var.', 'Yıllık bazda büyüme artık {n} çeyrektir kesintisiz sürüyor.', 'Büyüme serisi {n} çeyreğe ulaştı.'],
    'q_profit': ['Çeyreğin net kârı {ni}.', 'O çeyrekte {ni} kazandı.', 'Çeyreğin net sonucu: {ni} kâr.'],
    'q_loss': ['Çeyrek {ni} net zararla kapandı.', 'O çeyrekte {ni} zarar etti.', 'Çeyreğin net sonucu: {ni} zarar.'],
    'peer_margin_hi': ['{m} net kâr marjı, {ind} şirketlerinin {med} medyanının belirgin şekilde üstünde.', '{m} ile her dolarlık satıştan tipik bir {ind} şirketinden ({med}) daha fazlasını tutuyor.',
                       'Kârlılık güçlü bir yanı: {m} net marj, sektör medyanı {med}.'],
    'peer_margin_lo': ['{m} net kâr marjı, {ind} şirketlerinin {med} medyanının gerisinde.', 'Satışlarından eşlerinin çoğundan daha azını tutuyor: {m}, medyan {med}.',
                       'Kârlılık grubun gerisinde: net marj {m}, medyan {med}.'],
    'peer_loss_hi': ['Zarar ediyor ({m} net marj), ama tipik bir {ind} şirketinden ({med}) daha az.', '{m} net marj bir zarar, ancak sektör medyanından ({med}) daha hafif.',
                     'Zararlar grubun çoğundan daha hafif: {m}, medyan {med}.'],
    'peer_loss_lo': ['{m} net marj, {ind} şirketlerinin {med} medyanından daha derin bir zarar.', 'Satılan her dolar başına eşlerinin çoğundan fazla zarar ediyor: {m}, karşısında {med}.',
                     'Zararlar gruptakinden ağır: {m}, medyan {med}.'],
    'peer_margin_eq': ['{m} net kâr marjı, {med} sektör medyanına yakın.', '{m} ile kârlılık grupla uyumlu ({med}).', 'Marjlar {ind} şirketleri için olağan düzeyde: {m}, karşısında {med}.'],
    'peer_growth_hi_ttm': ["Son on iki aydaki {g} gelir büyümesi sektör medyanını ({med}) geçti.", "Son on iki ayda eşlerinin çoğundan hızlı büyüdü ({g}, medyan {med}).", "Son on iki ayda büyüme grubun önünde: {g}, karşısında {med}."],
    'peer_growth_lo_ttm': ["Son on iki aydaki {g} gelir büyümesi sektör medyanının ({med}) altında kaldı.", "Eşleri son on iki ayda daha hızlı büyüdü: medyan {med}, burada {g}.", "Son on iki ayda büyüme grubun gerisinde: {g}, karşısında {med}."],
    'peer_growth_eq_ttm': ["Son on iki aydaki {g} gelir büyümesi sektör medyanıyla ({med}) aynı düzeyde.", "Son on iki ayda eşleriyle uyumlu büyüdü: {g}, karşısında {med}.", "Son on iki aydaki büyüme ({g}), grup medyanı olan {med} rakamına yakın."],
    'opm_up_ttm': ["Son on iki aydaki {now} faaliyet marjı, beş yıllık ortalaması olan {avg} rakamının üzerinde.", "Faaliyet kârlılığı iyileşti: son on iki ayda {now}, beş yıllık ortalama {avg}."],
    'opm_down_ttm': ["Son on iki aydaki {now} faaliyet marjı, beş yıllık ortalaması olan {avg} rakamının altında.", "Faaliyet kârlılığı geriledi: son on iki ayda {now}, beş yıllık ortalama {avg}."],
    'peer_growth_hi': ['Geçen yılki {g} gelir büyümesi sektör medyanını ({med}) geçti.', 'Geçen yıl eşlerinin çoğundan hızlı büyüdü ({g}, medyan {med}).', 'Büyüme grubun önünde: {g}, karşısında {med}.'],
    'peer_growth_lo': ['Geçen yılki {g} gelir büyümesi sektör medyanının ({med}) altında kaldı.', 'Eşleri geçen yıl daha hızlı büyüdü: medyan {med}, burada {g}.', 'Büyüme grubun gerisinde: {g}, karşısında {med}.'],
    'peer_growth_eq': ['Geçen yılki {g} gelir büyümesi sektör medyanıyla ({med}) aynı düzeyde.', 'Geçen yıl eşleriyle uyumlu büyüdü: {g}, karşısında {med}.',
                       'Geçen yılki büyüme ({g}), grup medyanı olan {med} rakamına yakın.'],
    'peer_pe_hi': ['Piyasa bu şirket için kazancının {pe} katını ödüyor; bu, sektör medyanının ({med}) {x} katı: eşlerinden daha fazlasını bekliyor.',
                   'Sektör medyanı {med} iken {pe} F/K ile hisse grup çarpanının {x} katından işlem görüyor.', 'Eşlerine göre değerleme yüksek: F/K {pe}, sektör medyanı {med}.'],
    'peer_pe_lo': ['{pe} F/K oranı sektör medyanının ({med}) altında: piyasa bu şirkete eşlerinden daha temkinli bakıyor.',
                   'Kazancının {pe} katıyla tipik eşinden ({med}) daha ucuz; asıl soru bu iskontonun hak edilip edilmediği.', 'Hisse gruba göre iskontolu: F/K {pe}, karşısında {med}.'],
    'peer_pe_eq': ['{pe} F/K oranı {med} sektör medyanına yakın.', 'Değerleme eşleriyle uyumlu: F/K {pe}, medyan {med}.', 'Kazancının {pe} katıyla grup gibi fiyatlanıyor ({med}).'],
    'peer_pe_none': ['Kârlı olmadığı için F/K oranı yok; sektöründeki {tot} şirketin {n} tanesi kârlı.', 'Kâr olmadan karşılaştırılacak bir F/K de yok; {tot} eşinden {n} tanesi para kazanıyor.',
                     'F/K karşılaştırması henüz geçerli değil: zarar ediyor, oysa {tot} eşinden {n} tanesi kârlı.'],
    'roic_hi': ['Yatırılan sermaye getirisinin {roic} olması yüksek; fiyatlama gücü olan ya da az varlıkla çalışan bir işin işareti.',
                'Kendisine yatırılan sermaye üzerinden {roic} kazanıyor; bu, sermayenin maliyetinin epey üstünde.', 'Yatırılan sermaye getirisi güçlü: {roic}.'],
    'roic_lo': ['Yatırılan sermaye getirisi yalnızca {roic}; kârlı bir şirket için düşük.', 'Yatırılan sermaye üzerinden sadece {roic} kazanıyor.', 'Sermaye getirisi zayıf: yatırılan sermaye üzerinden {roic}.'],
    'bs_cash': ['Borcundan {net} daha fazla nakdi var; bu, piyasa değerinin {p} kadarı.', '{net} net nakit, piyasa değerinin {p} kadarını karşılıyor.',
                'Bilançoda {net} net nakit var; şirket değerinin {p} kadarı.'],
    'bs_debt_x': ['Net borç {net}; bu, yaklaşık {x} yıllık faaliyet nakit kazancına (FAVÖK) denk.', 'Nakdinden {net} fazla borcu var; FAVÖK rakamının {x} katı.',
                  '{net} net borç, {x} yıllık FAVÖK ediyor.'],
    'bs_debt_p': ['Net borç {net}; piyasa değerinin {p} kadarı.', '{net} net borç taşıyor; bu, piyasa değerinin {p} kadarı.', 'Nakit düşüldükten sonra borç: {net} (piyasa değerinin {p} kadarı).'],
    'bs_runway': ['Son on iki ayda {burn} nakit harcadı; eldeki nakit bu hızla yaklaşık {x} yıl yeter.', 'Yılda {burn} olan son harcama hızıyla nakdi yaklaşık {x} yıl dayanır.',
                  'On iki ayda nakit yakımı {burn} oldu; yaklaşık {x} yıllık pay.'],
    'bs_runway_short': ['Son on iki ayda {burn} nakit harcadı ve nakit yalnızca yaklaşık {x} yıl yetiyor: yeni hisse ya da yeni borç beklenebilir.',
                        'Pay kısa: yılda {burn} nakit yakımına karşı yaklaşık {x} yıllık nakit var; ek finansman ihtiyacı muhtemel.',
                        'Yılda {burn} nakit yakımıyla kasa yaklaşık {x} yıl dayanır; bir sermaye artırımı şaşırtmaz.'],
    'sh_dilute': ['Hisse sayısı üç yılda yılda yaklaşık {p} arttı; bu, mevcut ortakların payını sulandırıyor.', 'Ortaklar üç yıldır yılda yaklaşık {p} sulanıyor.',
                  'Yeni hisseler her yıl sayıya yaklaşık {p} ekliyor.'],
    'sh_buyback': ['Geri alımlarla hisse sayısı üç yılda yılda yaklaşık {p} azaldı.', 'Geri alımlar hisse sayısını yılda yaklaşık {p} düşürdü.', 'Her yıl daha az hisse var: üç yılda yılda yaklaşık {p} eksilme.'],
    'div_yes': ['{y} getirili temettü ödüyor ve verilerimizdeki {n} yılda temettü dağıttı.', 'Temettü getirisi {y}; ödemeler verilerimizde {n} yıl geriye gidiyor.',
                'Gelir odaklı yatırımcı {y} getiri alıyor; kayıtlarda {n} yıl ödeme var.'],
    'sbc_heavy': ['Hisse bazlı ödemeler serbest nakit akışının {p} kadarına denk; nakit rakamlarının göstermediği gerçek bir maliyet.', 'Hisse bazlı ücretlendirme büyük: serbest nakit akışının {p} kadarı.',
                  'Serbest nakit akışı şirketi olduğundan iyi gösteriyor: hisse bazlı ödemeler bunun {p} kadarı.'],
    'an_up': ['Analistler tahminlerini yükseltiyor: son 30 günde {up} yukarı, {dn} aşağı revizyon.', 'Revizyonlar olumlu yönde: 30 günde {up} artırıma karşı {dn} indirim.',
              'Son bir ayda {up} analist rakamlarını yükseltti, {dn} analist düşürdü.'],
    'an_down': ['Analistler tahminlerini düşürüyor: son 30 günde {dn} aşağı, {up} yukarı revizyon.', 'Revizyonlar olumsuz yönde: 30 günde {dn} indirime karşı {up} artırım.',
                'Son bir ayda {dn} analist rakamlarını düşürdü, yalnızca {up} analist yükseltti.'],
    'an_mixed': ['Tahmin revizyonları karışık: 30 günde {up} yukarı, {dn} aşağı.', 'Analistler yön konusunda bölünmüş: son bir ayda {up} artırım ve {dn} indirim.',
                 '30 günde {up} tahmin yükseldi, {dn} tahmin düştü.'],
    'an_range': ['{n} analistin hedef fiyatları {lo} ile {hi} arasında.', '{n} hedef fiyat {lo} ile {hi} aralığına yayılıyor.', 'Hedefler geniş bir aralıkta: altta {lo}, üstte {hi} ({n} analist).'],
    'an_next': ['{q} için beklenti hisse başına {eps} kâr ve {rev} gelir.', 'Sıradaki rapor {q} dönemini kapsıyor: beklenti hisse başına {eps}, gelir {rev}.',
                'Analistler {q} için hisse başına {eps} ve {rev} gelir bekliyor.'],
    'an_next_eps': ['{q} için beklenti hisse başına {eps} kâr.', 'Sıradaki rapor {q} dönemini kapsıyor; beklenti hisse başına {eps}.', 'Analistler {q} için hisse başına {eps} bekliyor.'],
}
