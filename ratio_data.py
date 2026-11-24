"""Live market tables for the P/E and P/B explainers, in es / tr / fa / ar (the English twin is tools/ratio_data_en.py).

Search Console (Nov 2026) on the English site: the P/E explainer got ~490 impressions a month at position ~70 for
"p/e ratio", "average pe ratio", "what is a good pe ratio"; the formula is on every site, today's numbers are not.
These tables add what nobody else shows: the market's P/E right now, by sector, for the biggest companies, and the
cheapest large caps, rebuilt from the data on every build. Persian/Arabic pages keep tickers inside <bdi dir="ltr">
and use local company names when we have them, so right-to-left text is never broken by Latin words."""
import json, os, statistics, html as H

e = lambda s: H.escape(str(s if s is not None else ''), quote=True)
FA_DIG = str.maketrans('0123456789.', '۰۱۲۳۴۵۶۷۸۹٫')

P = {
 'es': dict(stock='/acciones/%s/', screener='/screener-de-acciones/', dec=',', rtl=False,
   sec={'Technology': 'Tecnología', 'Finance': 'Finanzas', 'Health Care': 'Salud', 'Consumer Discretionary': 'Consumo discrecional', 'Consumer Staples': 'Consumo básico',
        'Industrials': 'Industria', 'Energy': 'Energía', 'Utilities': 'Servicios públicos', 'Real Estate': 'Inmobiliario', 'Basic Materials': 'Materiales', 'Telecommunications': 'Telecomunicaciones'},
   pe_h='El PER del mercado hoy',
   pe_p='Entre las 500 mayores empresas que cotizan en EE. UU. que seguimos, el PER ponderado por capitalización (valor total de mercado dividido entre el beneficio total de las rentables) es <b>{pe}</b>, y la empresa mediana cotiza a <b>{med}</b> veces sus beneficios de los últimos doce meses. Con las estimaciones de los analistas para los próximos doce meses, el PER ponderado es <b>{fpe}</b>. {loss} de las 500 perdieron dinero en el último año y no tienen PER. La cifra ponderada se inclina hacia los gigantes; por eso la mediana es mejor guía para una acción «típica».',
   sec_h='PER medio por sector', sec_p='Cada sector cotiza con múltiplos muy distintos, así que compara una empresa con su propio sector. Empresas de 2.000 millones de dólares o más, solo las rentables:',
   sec_cols=['Sector', 'Empresas', 'PER mediano', 'PER ponderado', 'PER estimado mediano'],
   big_h='PER de las mayores empresas de EE. UU.', big_cols=['Empresa', 'Capitalización', 'PER (12 meses)', 'PER estimado'],
   low_h='Grandes empresas con el PER más bajo', low_p='Empresas de 10.000 millones de dólares o más con PER inferior a 12 y nota de salud financiera de al menos 3 sobre 5. Un PER bajo es un punto de partida, no una señal de compra: averigua por qué el mercado desconfía.',
   low_cols=['Empresa', 'Sector', 'PER', 'PER estimado', 'Nota'], scr='Crea tu propia lista con el <a href="{u}">screener de acciones</a>.',
   pb_h='El precio/valor contable del mercado hoy', pb_p='Entre las 500 mayores empresas que cotizan en EE. UU., la mediana del ratio precio/valor contable es <b>{pb}</b>. Las empresas con pocos activos físicos (software, marcas, plataformas) suelen cotizar a muchas veces su valor contable; bancos, aseguradoras e industriales, mucho más cerca de él.',
   pbs_h='Precio/valor contable medio por sector', pbs_p='Empresas de 2.000 millones de dólares o más con patrimonio positivo:', pbs_cols=['Sector', 'Empresas', 'P/VC mediano'],
   fin_h='Grandes financieras por precio/valor contable', fin_p='El P/VC importa sobre todo en bancos y aseguradoras, cuyos activos son en su mayoría financieros.', fin_cols=['Empresa', 'Capitalización', 'P/VC', 'PER'],
   note='Cifras de los informes de las empresas y precios de mercado a {d}; se recalculan en cada actualización.', loss='pérdidas',
   q_pe='¿Cuál es el PER medio de la bolsa hoy?', a_pe='Entre las 500 mayores empresas cotizadas en EE. UU., el PER ponderado es de unos {pe} y la empresa mediana cotiza a unas {med} veces sus beneficios (datos a {d}).',
   q_sec='¿Qué sector tiene el PER más alto?', a_sec='Hoy es {hi}, con un PER ponderado de unos {hiv}; el más bajo es {lo}, con unos {lov}.',
   q_pb='¿Cuál es un ratio precio/valor contable típico hoy?', a_pb='La mediana entre las 500 mayores empresas cotizadas en EE. UU. es de unos {pb} (datos a {d}).'),
 'tr': dict(stock='/hisseler/%s/', screener='/hisse-tarama/', dec=',', rtl=False,
   sec={'Technology': 'Teknoloji', 'Finance': 'Finans', 'Health Care': 'Sağlık', 'Consumer Discretionary': 'İsteğe bağlı tüketim', 'Consumer Staples': 'Temel tüketim',
        'Industrials': 'Sanayi', 'Energy': 'Enerji', 'Utilities': 'Kamu hizmetleri', 'Real Estate': 'Gayrimenkul', 'Basic Materials': 'Hammadde', 'Telecommunications': 'Telekom'},
   pe_h='Piyasanın bugünkü F/K oranı',
   pe_p='Takip ettiğimiz ABD borsalarındaki en büyük 500 şirkette piyasa değeri ağırlıklı F/K (toplam piyasa değeri bölü kârlı şirketlerin toplam kârı) <b>{pe}</b>, medyan şirket ise son on iki aylık kârının <b>{med}</b> katından işlem görüyor. Analistlerin önümüzdeki on iki ay tahminleriyle ağırlıklı F/K <b>{fpe}</b>. 500 şirketin {loss} tanesi son bir yılda zarar etti, bu yüzden F/K oranları yok. Ağırlıklı rakam devlere doğru kayar; “tipik” bir hisse için medyan daha iyi bir rehberdir.',
   sec_h='Sektörlere göre ortalama F/K oranı', sec_p='Sektörler çok farklı çarpanlarla işlem görür; bir şirketi kendi sektörüyle karşılaştırın. 2 milyar dolar ve üzeri, yalnızca kârlı şirketler:',
   sec_cols=['Sektör', 'Şirket', 'Medyan F/K', 'Ağırlıklı F/K', 'Medyan ileriye dönük F/K'],
   big_h='En büyük ABD şirketlerinin F/K oranı', big_cols=['Şirket', 'Piyasa değeri', 'F/K (12 ay)', 'İleriye dönük F/K'],
   low_h='F/K oranı en düşük büyük şirketler', low_p='Piyasa değeri 10 milyar dolar ve üzeri, F/K oranı 12’nin altında ve finansal sağlık puanı en az 3/5 olan şirketler. Düşük F/K bir araştırma başlangıcıdır, alım sinyali değildir.',
   low_cols=['Şirket', 'Sektör', 'F/K', 'İleriye dönük F/K', 'Puan'], scr='Kendi listenizi <a href="{u}">hisse tarama</a> aracıyla oluşturun.',
   pb_h='Piyasanın bugünkü PD/DD oranı', pb_p='ABD borsalarındaki en büyük 500 şirkette medyan PD/DD oranı <b>{pb}</b>. Varlığı hafif işletmeler (yazılım, markalar, platformlar) çoğu zaman defter değerinin kat kat üzerinde işlem görür; bankalar, sigortacılar ve sanayi şirketleri ona çok daha yakındır.',
   pbs_h='Sektörlere göre ortalama PD/DD oranı', pbs_p='2 milyar dolar ve üzeri, özsermayesi pozitif şirketler:', pbs_cols=['Sektör', 'Şirket', 'Medyan PD/DD'],
   fin_h='PD/DD oranına göre büyük finans şirketleri', fin_p='PD/DD en çok bankalar ve sigortacılarda anlamlıdır; varlıkları çoğunlukla finansaldır.', fin_cols=['Şirket', 'Piyasa değeri', 'PD/DD', 'F/K'],
   note='Rakamlar şirket raporlarından ve piyasa fiyatlarından, {d} itibarıyla; her güncellemede yeniden hesaplanır.', loss='zarar',
   q_pe='Borsanın bugünkü ortalama F/K oranı kaç?', a_pe='ABD’de işlem gören en büyük 500 şirkette ağırlıklı F/K yaklaşık {pe}, medyan şirket ise kârının yaklaşık {med} katından işlem görüyor ({d} verisi).',
   q_sec='F/K oranı en yüksek sektör hangisi?', a_sec='Bugün {hi}, ağırlıklı F/K yaklaşık {hiv}; en düşük {lo}, yaklaşık {lov}.',
   q_pb='Bugün tipik bir PD/DD oranı kaç?', a_pb='ABD’de işlem gören en büyük 500 şirkette medyan yaklaşık {pb} ({d} verisi).'),
 'fa': dict(stock='/pages/stocks/%s', screener='/pages/screener', dec='٫', rtl=True,
   sec={'Technology': 'فناوری', 'Finance': 'مالی', 'Health Care': 'سلامت و دارو', 'Consumer Discretionary': 'کالاهای مصرفی غیرضروری', 'Consumer Staples': 'کالاهای مصرفی ضروری',
        'Industrials': 'صنعتی', 'Energy': 'انرژی', 'Utilities': 'خدمات عمومی', 'Real Estate': 'املاک و مستغلات', 'Basic Materials': 'مواد اولیه', 'Telecommunications': 'مخابرات'},
   pe_h='نسبت قیمت به سود بازار آمریکا امروز',
   pe_p='در میان ۵۰۰ شرکت بزرگ بورس آمریکا که دنبال می‌کنیم، نسبت قیمت به سود وزنی (ارزش کل بازار تقسیم بر سود کل شرکت‌های سودده) <b>{pe}</b> است و شرکت میانه حدود <b>{med}</b> برابر سود ۱۲ ماه گذشته‌اش معامله می‌شود. با پیش‌بینی تحلیلگرها برای ۱۲ ماه آینده، این نسبت <b>{fpe}</b> است. {loss} شرکت از این ۵۰۰ شرکت در سال گذشته زیان داده‌اند و نسبت قیمت به سود ندارند. عدد وزنی به سمت غول‌ها متمایل است؛ برای یک سهم «معمولی» عدد میانه راهنمای بهتری است.',
   sec_h='میانگین نسبت قیمت به سود در هر صنعت', sec_p='صنایع با ضریب‌های بسیار متفاوتی معامله می‌شوند؛ هر شرکت را با صنعت خودش مقایسه کنید. شرکت‌های ۲ میلیارد دلار و بیشتر، فقط سودده‌ها:',
   sec_cols=['صنعت', 'تعداد', 'میانه', 'وزنی', 'میانه‌ی آینده‌نگر'],
   big_h='نسبت قیمت به سود بزرگ‌ترین شرکت‌های آمریکا', big_cols=['شرکت', 'ارزش بازار', 'قیمت به سود', 'آینده‌نگر'],
   low_h='شرکت‌های بزرگ با کمترین نسبت قیمت به سود', low_p='شرکت‌های ۱۰ میلیارد دلار و بیشتر با نسبت قیمت به سود زیر ۱۲ و امتیاز سلامت مالی دست‌کم ۳ از ۵. نسبت پایین نقطه‌ی شروع بررسی است، نه سیگنال خرید: اول ببینید چرا بازار محتاط است.',
   low_cols=['شرکت', 'صنعت', 'قیمت به سود', 'آینده‌نگر', 'امتیاز'], scr='فهرست خودتان را با <a href="{u}">غربالگر سهام</a> بسازید.',
   pb_h='نسبت قیمت به ارزش دفتری بازار امروز', pb_p='در میان ۵۰۰ شرکت بزرگ بورس آمریکا، میانه‌ی نسبت قیمت به ارزش دفتری <b>{pb}</b> است. شرکت‌هایی با دارایی فیزیکی کم (نرم‌افزار، برند، پلتفرم) معمولاً چند برابر ارزش دفتری معامله می‌شوند و بانک‌ها، بیمه‌ها و شرکت‌های صنعتی خیلی نزدیک‌تر به آن.',
   pbs_h='میانگین قیمت به ارزش دفتری در هر صنعت', pbs_p='شرکت‌های ۲ میلیارد دلار و بیشتر با حقوق صاحبان سهام مثبت:', pbs_cols=['صنعت', 'تعداد', 'میانه'],
   fin_h='شرکت‌های بزرگ مالی بر اساس قیمت به ارزش دفتری', fin_p='این نسبت بیش از همه برای بانک‌ها و بیمه‌ها معنا دارد، چون دارایی‌هایشان بیشتر مالی است.', fin_cols=['شرکت', 'ارزش بازار', 'قیمت به ارزش دفتری', 'قیمت به سود'],
   note='عددها از گزارش‌های رسمی شرکت‌ها و قیمت بازار، به تاریخ {d}؛ با هر به‌روزرسانی دوباره حساب می‌شوند.', loss='زیان‌ده',
   q_pe='میانگین نسبت قیمت به سود بورس آمریکا امروز چقدر است؟', a_pe='در میان ۵۰۰ شرکت بزرگ بورس آمریکا نسبت وزنی حدود {pe} است و شرکت میانه حدود {med} برابر سودش معامله می‌شود (داده‌ی {d}).',
   q_sec='کدام صنعت بالاترین نسبت قیمت به سود را دارد؟', a_sec='امروز «{hi}» با نسبت وزنی حدود {hiv}؛ پایین‌ترین «{lo}» با حدود {lov}.',
   q_pb='نسبت قیمت به ارزش دفتری معمول امروز چقدر است؟', a_pb='میانه در میان ۵۰۰ شرکت بزرگ بورس آمریکا حدود {pb} است (داده‌ی {d}).'),
 'ar': dict(stock='/stocks/%s/', screener='/screener/', dec='.', rtl=True,
   sec={'Technology': 'التكنولوجيا', 'Finance': 'القطاع المالي', 'Health Care': 'الرعاية الصحية', 'Consumer Discretionary': 'السلع الكمالية', 'Consumer Staples': 'السلع الأساسية',
        'Industrials': 'الصناعة', 'Energy': 'الطاقة', 'Utilities': 'المرافق', 'Real Estate': 'العقارات', 'Basic Materials': 'المواد الأساسية', 'Telecommunications': 'الاتصالات'},
   pe_h='مكرر الربحية للسوق الأمريكية اليوم',
   pe_p='بين أكبر 500 شركة مدرجة في أمريكا نتابعها، يبلغ مكرر الربحية المرجّح بالقيمة السوقية (القيمة السوقية الإجمالية مقسومة على إجمالي أرباح الشركات الرابحة) <b>{pe}</b>، وتتداول الشركة الوسيطة عند <b>{med}</b> ضعف أرباحها في آخر 12 شهراً. وبتقديرات المحللين للأشهر الاثني عشر القادمة يبلغ المكرر المرجّح <b>{fpe}</b>. وخسرت {loss} شركة من الـ500 أموالاً في العام الماضي، فلا مكرر ربحية لها. الرقم المرجّح يميل نحو العمالقة، لذلك الوسيط دليل أفضل للسهم «العادي».',
   sec_h='متوسط مكرر الربحية حسب القطاع', sec_p='تتداول القطاعات بمكررات مختلفة جداً، فقارن الشركة بقطاعها. الشركات بقيمة ملياري دولار فأكثر، الرابحة فقط:',
   sec_cols=['القطاع', 'عدد الشركات', 'المكرر الوسيط', 'المكرر المرجّح', 'المكرر المستقبلي الوسيط'],
   big_h='مكرر الربحية لأكبر الشركات الأمريكية', big_cols=['الشركة', 'القيمة السوقية', 'المكرر الحالي', 'المكرر المستقبلي'],
   low_h='الشركات الكبرى ذات أدنى مكرر ربحية', low_p='شركات بقيمة 10 مليارات دولار فأكثر بمكرر ربحية أقل من 12 ودرجة صحة مالية 3 من 5 على الأقل. المكرر المنخفض نقطة بداية للبحث، لا إشارة شراء.',
   low_cols=['الشركة', 'القطاع', 'المكرر', 'المكرر المستقبلي', 'الدرجة'], scr='ابنِ قائمتك الخاصة عبر <a href="{u}">فلتر الأسهم</a>.',
   pb_h='مضاعف القيمة الدفترية للسوق اليوم', pb_p='بين أكبر 500 شركة مدرجة في أمريكا، يبلغ الوسيط لمضاعف القيمة الدفترية <b>{pb}</b>. الشركات قليلة الأصول المادية (البرمجيات والعلامات التجارية والمنصات) تتداول غالباً بأضعاف قيمتها الدفترية، بينما تقترب منها البنوك وشركات التأمين والصناعة.',
   pbs_h='متوسط مضاعف القيمة الدفترية حسب القطاع', pbs_p='الشركات بقيمة ملياري دولار فأكثر ذات حقوق مساهمين موجبة:', pbs_cols=['القطاع', 'عدد الشركات', 'المضاعف الوسيط'],
   fin_h='كبرى الشركات المالية حسب مضاعف القيمة الدفترية', fin_p='يهم هذا المضاعف أكثر في البنوك وشركات التأمين لأن أصولها مالية في معظمها.', fin_cols=['الشركة', 'القيمة السوقية', 'مضاعف القيمة الدفترية', 'مكرر الربحية'],
   note='الأرقام من تقارير الشركات وأسعار السوق بتاريخ {d}، وتُحدَّث مع كل تحديث للبيانات.', loss='خسارة',
   q_pe='كم يبلغ متوسط مكرر الربحية للسوق الأمريكية اليوم؟', a_pe='بين أكبر 500 شركة مدرجة في أمريكا يبلغ المكرر المرجّح نحو {pe}، وتتداول الشركة الوسيطة عند نحو {med} ضعف أرباحها (بيانات {d}).',
   q_sec='أي قطاع لديه أعلى مكرر ربحية؟', a_sec='اليوم قطاع {hi} بمكرر مرجّح نحو {hiv}، والأدنى قطاع {lo} بنحو {lov}.',
   q_pb='كم يبلغ مضاعف القيمة الدفترية المعتاد اليوم؟', a_pb='الوسيط بين أكبر 500 شركة مدرجة في أمريكا نحو {pb} (بيانات {d}).'),
}


def rows(sd):
    d = json.load(open(os.path.join(sd, 'data', 'screener.json')))
    c = {k: i for i, k in enumerate(d['cols'])}
    out = [{k: r[i] for k, i in c.items()} for r in d['rows'] if r[c['cur']] in (None, 'USD') and r[c['mcap']]]
    seen, uniq = set(), []
    for x in sorted(out, key=lambda x: -x['mcap']):   # one row per company (share classes would count profits twice)
        k = (x.get('n') or x['t']).lower()
        if k not in seen:
            seen.add(k); uniq.append(x)
    return uniq, d.get('as_of')


def agg(xs, key='pe'):
    num = sum(x['mcap'] for x in xs if x.get(key) and x[key] > 0)
    den = sum(x['mcap'] / x[key] for x in xs if x.get(key) and x[key] > 0)
    return num / den if den else None


def med(v):
    v = [x for x in v if x is not None and x > 0]
    return statistics.median(v) if v else None


class R:
    def __init__(self, sd, lang, names=None):
        self.L, self.lang, self.names = P[lang], lang, names or {}
        self.rs, self.as_of = rows(sd)
        self.big = self.rs[:500]
        self.sec = {}
        for x in self.rs:
            s = self.L['sec'].get(x.get('sector'))
            if s and x['mcap'] >= 2e9:
                self.sec.setdefault(s, []).append(x)

    def n(self, v, d=1):
        if v is None:
            return '—'
        s = ('%.' + str(d) + 'f') % v
        if self.lang == 'fa':
            return s.translate(FA_DIG)
        return s.replace('.', self.L['dec'])

    def i(self, v):
        s = str(v)
        return s.translate(FA_DIG) if self.lang == 'fa' else s

    def usd(self, v):
        if not v:
            return '—'
        if self.lang == 'fa':
            return ('%s هزار میلیارد دلار' % self.n(v / 1e12, 2)) if v >= 1e12 else ('%s میلیارد دلار' % self.i(int(round(v / 1e9))))
        if self.lang == 'ar':
            return ('%s تريليون $' % self.n(v / 1e12, 2)) if v >= 1e12 else ('%s مليار $' % self.i(int(round(v / 1e9))))
        if self.lang == 'es':
            return ('%s billones $' % self.n(v / 1e12, 2)) if v >= 1e12 else ('%s mil M$' % self.i(int(round(v / 1e9))))
        return ('%s trilyon $' % self.n(v / 1e12, 2)) if v >= 1e12 else ('%s milyar $' % self.i(int(round(v / 1e9))))

    def date(self):
        d = self.as_of or ''
        return d.translate(FA_DIG) if self.lang == 'fa' else d

    def link(self, x):
        t = x['t']
        nm = self.names.get(t)
        if self.L['rtl']:
            nm = nm or None
            tk = '<bdi dir="ltr">%s</bdi>' % e(t)
            return '<a href="%s">%s</a>' % (e(self.L['stock'] % t.lower().replace('.', '-')), ('%s %s' % (e(nm), tk)) if nm else tk)
        return '<a href="%s">%s</a> <span class="tk">%s</span>' % (e(self.L['stock'] % t.lower().replace('.', '-')), e(nm or x.get('n') or t), e(t))

    def table(self, head, body):
        return ('<div class="tw" style="overflow-x:auto"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
                % (''.join('<th>%s</th>' % h for h in head), ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r) for r in body)))

    def pe(self):
        L, big = self.L, self.big
        loss = sum(1 for x in big if not x.get('pe') or x['pe'] <= 0)
        h = '<h2>%s</h2><p>%s</p>' % (L['pe_h'], L['pe_p'].format(pe=self.n(agg(big)), med=self.n(med([x['pe'] for x in big])), fpe=self.n(agg(big, 'fwd_pe')), loss=self.i(loss)))
        srt = sorted(self.sec.items(), key=lambda kv: -(agg(kv[1]) or 0))
        h += '<h2>%s</h2><p>%s</p>' % (L['sec_h'], L['sec_p']) + self.table(L['sec_cols'], [[e(s), self.i(len(xs)), self.n(med([x['pe'] for x in xs])), self.n(agg(xs)), self.n(med([x['fwd_pe'] for x in xs]))] for s, xs in srt])
        h += '<h2>%s</h2>' % L['big_h'] + self.table(L['big_cols'], [[self.link(x), self.usd(x['mcap']), self.n(x['pe']) if x.get('pe') and x['pe'] > 0 else L['loss'], self.n(x.get('fwd_pe'))] for x in big[:20]])
        low = sorted((x for x in self.rs if x['mcap'] >= 10e9 and x.get('pe') and 0 < x['pe'] < 12 and (x.get('s_health') or 0) >= 3), key=lambda x: x['pe'])[:15]
        if low:
            h += '<h2>%s</h2><p>%s</p>' % (L['low_h'], L['low_p']) + self.table(L['low_cols'], [[self.link(x), e(L['sec'].get(x.get('sector')) or ''), self.n(x['pe']), self.n(x.get('fwd_pe')), self.n(x.get('s_total'))] for x in low])
        h += '<p>%s</p><p class="note">%s</p>' % (L['scr'].format(u=L['screener']), L['note'].format(d=self.date()))
        hi, lo = srt[0], srt[-1]
        qa = [(L['q_pe'], L['a_pe'].format(pe=self.n(agg(big)), med=self.n(med([x['pe'] for x in big])), d=self.date())),
              (L['q_sec'], L['a_sec'].format(hi=hi[0], hiv=self.n(agg(hi[1])), lo=lo[0], lov=self.n(agg(lo[1]))))]
        return h, qa

    def pb(self):
        L = self.L
        pbm = med([x['pb'] for x in self.big])
        h = '<h2>%s</h2><p>%s</p>' % (L['pb_h'], L['pb_p'].format(pb=self.n(pbm)))
        srt = sorted(self.sec.items(), key=lambda kv: (med([x['pb'] for x in kv[1]]) or 0))
        h += '<h2>%s</h2><p>%s</p>' % (L['pbs_h'], L['pbs_p']) + self.table(L['pbs_cols'], [[e(s), self.i(len(xs)), self.n(med([x['pb'] for x in xs]))] for s, xs in srt])
        fin = sorted((x for x in self.rs if x.get('sector') == 'Finance' and x['mcap'] >= 10e9 and x.get('pb') and x['pb'] > 0 and x.get('pe') and x['pe'] > 0), key=lambda x: x['pb'])[:12]
        if fin:
            h += '<h2>%s</h2><p>%s</p>' % (L['fin_h'], L['fin_p']) + self.table(L['fin_cols'], [[self.link(x), self.usd(x['mcap']), self.n(x['pb']), self.n(x['pe'])] for x in fin])
        h += '<p class="note">%s</p>' % L['note'].format(d=self.date())
        return h, [(L['q_pb'], L['a_pb'].format(pb=self.n(pbm), d=self.date()))]


_C = {}


def extra(sd, lang, kind, names=None):
    """kind: 'pe' or 'pb' -> (html, [(q, a)]); ('', []) if anything fails, so the page still builds."""
    try:
        if lang not in _C:
            _C[lang] = R(sd, lang, names)
        return getattr(_C[lang], kind)()
    except Exception as ex:
        print('ratio_data: off', lang, kind, ex)
        return '', []
