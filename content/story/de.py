"""Deutsches Paket für story.py (aktienadler.com). Drei Formulierungen je Tatsache."""
import datetime

MES = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']


def _d(v, d):
    s = ('{:,.%df}' % d).format(v)
    return s.replace(',', '\x00').replace('.', ',').replace('\x00', '.')


class F:
    @staticmethod
    def money(v):
        a = abs(v)
        if a >= 1e12: return '%s Bio. US-Dollar' % _d(v / 1e12, 2)
        if a >= 1e9: return '%s Mrd. US-Dollar' % _d(v / 1e9, 1)
        if a >= 1e6: return '%s Mio. US-Dollar' % _d(v / 1e6, 0)
        return '%s Tsd. US-Dollar' % _d(v / 1e3, 0)

    @staticmethod
    def pct(v, d=0):
        return _d(v * 100, d) + ' %'

    @staticmethod
    def mpct(v):
        return _d(v * 100, 1 if abs(v) < 0.1 else 0) + ' %'

    @staticmethod
    def spct(v):
        if abs(v) < 0.005:
            v = 0.0
        return ('' if v == 0 else '+' if v > 0 else '−') + _d(abs(v) * 100, 0) + ' %'

    @staticmethod
    def num(v):
        return _d(v, 1)

    @staticmethod
    def times(v):
        return '%s-mal' % _d(v, 1 if v < 10 else 0)

    @staticmethod
    def price(v):
        a = abs(v); d = 2
        if 0 < a < 0.005:
            d = 3 if a >= 0.0005 else 4
        return '%s%s US-Dollar' % ('−' if v < 0 and round(a, d) else '', _d(a, d))

    @staticmethod
    def years(ys):
        ys = [str(y) for y in ys]
        return ys[0] if len(ys) == 1 else ', '.join(ys[:-1]) + ' und ' + ys[-1]


def qdate(s):
    try:
        d = datetime.date.fromisoformat(str(s)[:10])
        return 'Quartal bis %s %d' % (MES[d.month - 1], d.year)
    except Exception:
        return 'Berichtsquartal'


def month(m):
    return MES[m - 1]


T = {
    'eps_up': ['Der verwässerte Gewinn je Aktie stieg von {e0} im Geschäftsjahr {fy0} auf {e1} im Geschäftsjahr {fy1}, um etwa {g} pro Jahr.',
               'Der Gewinn je Aktie entwickelte sich zwischen dem Geschäftsjahr {fy0} und {fy1} von {e0} auf {e1} ({g} pro Jahr).', 'Der Gewinn je Aktie wächst um etwa {g} pro Jahr: von {e0} im Geschäftsjahr {fy0} auf {e1} im Geschäftsjahr {fy1}.'],
    'eps_faster': ['Der Gewinn je Aktie wuchs schneller als der Umsatz, von {e0} im Geschäftsjahr {fy0} auf {e1} im Geschäftsjahr {fy1} ({g} pro Jahr): Die Margen haben sich unterwegs verbessert.',
                   'Der Gewinn je Aktie lief dem Umsatz davon: von {e0} auf {e1} zwischen dem Geschäftsjahr {fy0} und {fy1}, etwa {g} pro Jahr.',
                   'Unter dem Strich lief es besser als beim Umsatz: Der Gewinn je Aktie steigt um etwa {g} pro Jahr, bis auf {e1} (Geschäftsjahr {fy0}: {e0}).'],
    'eps_down': ['Der verwässerte Gewinn je Aktie fiel von {e0} im Geschäftsjahr {fy0} auf {e1} im Geschäftsjahr {fy1}, um etwa {g} pro Jahr.',
                 'Der Gewinn je Aktie sank zwischen dem Geschäftsjahr {fy0} und {fy1} von {e0} auf {e1}.', 'Der Gewinn je Aktie ist niedriger als früher: {e1} im Geschäftsjahr {fy1} gegenüber {e0} im Geschäftsjahr {fy0}.'],
    'opm_up': ['Die operative Marge liegt mit {now} im letzten Jahr über dem Fünfjahresdurchschnitt ({avg}).', 'Die operative Rentabilität hat sich verbessert: {now} im letzten Jahr gegenüber einem Fünfjahresdurchschnitt von {avg}.',
               'Die operative Marge des letzten Jahres, {now}, übertraf den Fünfjahresdurchschnitt ({avg}).'],
    'opm_down': ['Die operative Marge liegt mit {now} im letzten Jahr unter dem Fünfjahresdurchschnitt ({avg}).', 'Die operative Rentabilität ist zurückgegangen: {now} im letzten Jahr gegenüber einem Fünfjahresdurchschnitt von {avg}.',
                 'Die operative Marge des letzten Jahres, {now}, blieb unter dem Fünfjahresdurchschnitt ({avg}).'],
    'rnd': ['Das Unternehmen gibt {v} pro Jahr für Forschung und Entwicklung aus, {p} des Umsatzes.', 'Forschung und Entwicklung beanspruchen {p} des Umsatzes ({v} pro Jahr).', 'Die F&E-Ausgaben von {v} entsprechen {p} des Umsatzes.'],
    'capex': ['Die Investitionen in Sachanlagen sind hoch: {v} pro Jahr, {p} des Umsatzes.', 'Das Unternehmen reinvestiert {p} des Umsatzes in Anlagen und Ausrüstung ({v} pro Jahr).', 'Die Investitionen in Sachanlagen liegen bei rund {v}, {p} des Umsatzes.'],
    'int_tight': ['Der operative Gewinn deckt die Zinslast von {ie} nur {x}-fach: ein dünnes Polster.', 'Zinsen von {ie} pro Jahr zehren einen guten Teil des operativen Gewinns auf (Zinsdeckung {x}-fach).',
                  'Bei einer Zinsdeckung von {x}-fach auf {ie} Zinsen bleibt wenig Spielraum für ein schlechtes Jahr.'],
    'int_easy': ['Der operative Gewinn deckt die Zinsen {x}-fach: Die Schulden drücken nicht.', 'Die Zinsen fallen kaum ins Gewicht, sie sind {x}-fach durch den operativen Gewinn gedeckt.', 'Die Zinsdeckung ist großzügig: {x}-fach.'],
    'fy_end': ['Das Geschäftsjahr endet im {m}.', 'Achtung: Das Geschäftsjahr endet im {m}, nicht im Dezember.', 'Die Geschäftsjahre enden im {m}.'],
    'head': ['{name} in Zahlen: was die Historie sagt', 'Die Historie von {name}, Jahr für Jahr', 'So lesen Sie die Zahlen von {name}'],
    'size_top': ['{name} ist das größte der {n} in den USA notierten Unternehmen aus dem Bereich {ind}, die wir verfolgen: Es ist {mcap} wert, etwa {x} so viel wie das zweitgrößte, {other}.',
                 'Mit {mcap} führt {name} die Gruppe {ind} in unserer Liste an: {n} Unternehmen, und das zweitgrößte, {other}, ist {x} kleiner.',
                 'Kein in den USA notiertes Unternehmen aus dem Bereich {ind} in unserer Liste ist größer: {name} ist {mcap} wert, {x} so viel wie {other}, die Nummer zwei von {n}.'],
    'size_rank': ['{name} ist {mcap} wert und nach Größe die Nummer {rank} unter den {n} in den USA notierten Unternehmen aus dem Bereich {ind}, die wir verfolgen.',
                  'Mit einem Börsenwert von {mcap} belegt {name} Platz {rank} von {n} im Bereich {ind} unserer Liste.',
                  'Unter {n} in den USA notierten Unternehmen aus dem Bereich {ind} ist {name} nach Börsenwert die Nummer {rank} ({mcap}).'],
    'size_between': ['Direkt darüber liegt {bigger}, direkt darunter {smaller}.', 'Die nächsten Nachbarn nach Größe sind {bigger} (größer) und {smaller} (kleiner).',
                     'Nach Größe liegt es zwischen {bigger} und {smaller}.'],
    'size_last': ['Es ist das kleinste der Gruppe; das nächste ist {bigger}.', 'Kein Unternehmen der Gruppe ist kleiner; am ähnlichsten nach Größe ist {bigger}.',
                  'Es bildet nach Größe das Schlusslicht, direkt hinter {bigger}.'],
    'size_share': ['Allein macht es {share} des gemeinsamen Werts der Branche aus.', 'Das entspricht {share} dessen, was die ganze Gruppe zusammen wert ist.',
                   'Sein Gewicht in der Gruppe ist groß: {share} des gemeinsamen Werts.'],
    'size_alone': ['{name} hat einen Börsenwert von {mcap}.', 'Die Börse bewertet {name} mit {mcap}.', '{name} ist an der Börse {mcap} wert.'],
    'hist_cagr_up': ['Der Umsatz stieg von {r0} im Geschäftsjahr {fy0} auf {r1} im Geschäftsjahr {fy1}, um etwa {g} pro Jahr über {n} Jahre.',
                     'In {n} Jahren stieg der Umsatz von {r0} (Geschäftsjahr {fy0}) auf {r1} (Geschäftsjahr {fy1}): etwa {g} pro Jahr, aufs Jahr gerechnet.',
                     'Der Umsatz wächst seit dem Geschäftsjahr {fy0} um {g} pro Jahr, von {r0} auf {r1} im Geschäftsjahr {fy1}.'],
    'hist_cagr_flat': ['Der Umsatz hat sich in {n} Jahren kaum bewegt: {r0} im Geschäftsjahr {fy0} und {r1} im Geschäftsjahr {fy1}.',
                       'Der Umsatz steht da, wo er vor {n} Jahren stand: {r1} im Geschäftsjahr {fy1} gegenüber {r0} im Geschäftsjahr {fy0}.',
                       'Der Umsatz von {r1} im Geschäftsjahr {fy1} liegt sehr nah an den {r0} im Geschäftsjahr {fy0}.'],
    'hist_cagr_down': ['Der Umsatz fiel von {r0} im Geschäftsjahr {fy0} auf {r1} im Geschäftsjahr {fy1}, um etwa {g} pro Jahr.',
                       'Das Geschäft ist kleiner als früher: {r1} Umsatz im Geschäftsjahr {fy1} gegenüber {r0} im Geschäftsjahr {fy0} (etwa {g} pro Jahr).',
                       'In {n} Jahren sank der Umsatz um etwa {g} pro Jahr, von {r0} auf {r1}.'],
    'hist_no_down': ['Der Umsatz ist in jedem der letzten {n} Jahre unserer Daten gestiegen, ohne ein einziges Jahr mit Rückgang.',
                     'In den letzten {n} Jahren gab es kein Jahr mit Rückgang: Der Umsatz ist immer gewachsen.', 'Die Historie zeigt in {n} Jahren in Folge keinen Umsatzrückgang.'],
    'hist_down_one': ['Das einzige Jahr mit sinkendem Umsatz war das Geschäftsjahr {fy}, {g}.', 'Das Geschäftsjahr {fy} ist der einzige Ausrutscher: Der Umsatz fiel in diesem Jahr um {g}.',
                      'Der Umsatz ging nur einmal zurück, im Geschäftsjahr {fy} ({g} weniger).'],
    'hist_down_many': ['Der Umsatz ging in {n} Jahren zurück ({years}); am schlimmsten war das Geschäftsjahr {worst} mit einem Minus von {g}.',
                       'Es ist keine gerade Linie: Der Umsatz fiel {years}, vor allem im Geschäftsjahr {worst} ({g}).',
                       'Es gab {n} Jahre mit Rückgang, {years}, und das Geschäftsjahr {worst} war das härteste, mit {g} weniger Umsatz.'],
    'hist_best': ['Das beste Jahr war das Geschäftsjahr {fy}, als der Umsatz um {g} sprang.', 'Das stärkste Wachstumsjahr war das Geschäftsjahr {fy}: {g} mehr Umsatz.',
                  'Heraus sticht das Geschäftsjahr {fy}, mit einem Umsatzplus von {g}.'],
    'hist_record': ['Der Umsatz im Geschäftsjahr {fy} war der höchste in unseren Daten.', 'Das letzte Jahr, das Geschäftsjahr {fy}, brachte einen Umsatzrekord.',
                    'Der Umsatz im Geschäftsjahr {fy} war ein historisches Hoch.'],
    'hist_below_peak': ['Der Umsatz liegt noch {g} unter dem Höchststand von {peak} im Geschäftsjahr {fy}.',
                        'Der Umsatz hat die {peak} aus dem Geschäftsjahr {fy} nicht wieder erreicht; es fehlen {g}.', 'Der Umsatz erreichte im Geschäftsjahr {fy} mit {peak} seinen Höchststand und liegt heute {g} darunter.'],
    'prof_all': ['In jedem der {n} Jahre, die wir haben, wurde ein Gewinn erzielt.', 'Alle letzten {n} Jahre waren profitabel.', 'In den {n} erfassten Jahren gibt es kein Verlustjahr.'],
    'prof_never': ['In keinem der {n} Jahre, die wir haben, gab es einen Jahresgewinn.', 'Alle {n} erfassten Jahre endeten mit Verlust.',
                   'Der Gewinn lässt noch auf sich warten: {n} Jahre, {n} Verluste.'],
    'prof_turn': ['Nach Verlusten {years} schrieb das Unternehmen im Geschäftsjahr {fy} erstmals Gewinn und blieb dabei.',
                  'Das Geschäftsjahr {fy} war die Wende: seitdem profitabel, nachdem {years} Geld verloren wurde.',
                  'Seit dem Geschäftsjahr {fy} schwarze Zahlen; davor Verluste {years}.'],
    'prof_slip': ['Im Geschäftsjahr {fy} rutschte das Unternehmen mit {loss} wieder in die Verlustzone.', 'Das Geschäftsjahr {fy} unterbrach die Gewinnserie mit einem Verlust von {loss}.',
                  'Das letzte Jahr, das Geschäftsjahr {fy}, endete nach einem Gewinnjahr mit einem Verlust von {loss}.'],
    'prof_mixed': ['Die Gewinne kommen und gehen: {n} Verlustjahre in {span} Jahren ({years}).', 'In {n} von {span} Jahren wurde Geld verloren ({years}).',
                   'Die Gewinne sind unregelmäßig, mit Verlusten {years}.'],
    'prof_margin_off': ['Die Nettomarge erreichte im Geschäftsjahr {fy} {peak} und liegt heute bei {now}.',
                        'Die Rentabilität liegt unter ihrem besten Stand: Nettomarge heute {now} gegenüber {peak} im Geschäftsjahr {fy}.',
                        'Die Margen sind von {peak} im Geschäftsjahr {fy} auf {now} gesunken.'],
    'prof_margin_best': ['Die letzte Nettomarge von {m} ist die beste seit {n} Jahren.', 'Mit {m} ist die Nettomarge die höchste der {n} erfassten Jahre.',
                         'So profitabel war das Unternehmen in unseren Daten noch nie: Nettomarge {m}.'],
    'fcf_all': ['Der Free Cashflow war in allen {n} Jahren positiv.', 'Das Unternehmen hat in jedem der {n} Jahre freien Cashflow erzeugt.', 'Das Geld nach Investitionen war jedes Jahr positiv ({n} von {n}).'],
    'fcf_none': ['Der Free Cashflow war in allen {n} Jahren negativ: Das Geschäft verbraucht Geld.', 'In keinem der {n} Jahre wurde freier Cashflow erzeugt.',
                 'In jedem der {n} Jahre ging mehr Geld hinaus als herein.'],
    'fcf_one': ['Der Free Cashflow war nur in einem von {n} Jahren positiv.', 'Freier Cashflow entstand in nur einem von {n} Jahren.', 'Nur eines der {n} Jahre brachte einen positiven Free Cashflow.'],
    'fcf_most': ['Der Free Cashflow war in {pos} von {n} Jahren positiv.', 'Freier Cashflow entstand in {pos} der {n} Jahre.', 'In {pos} von {n} Jahren war der freie Cashflow positiv.'],
    'fcf_some': ['Der Free Cashflow war in {pos} von {n} Jahren positiv.', 'Freier Cashflow entstand in {pos} von {n} Jahren.', 'Die Cash-Erzeugung ist unregelmäßig: positiv in {pos} von {n} Jahren.'],
    'q_up': ['Im {q} lag der Umsatz bei {rev}, {g} mehr als ein Jahr zuvor.', 'Der Umsatz belief sich im {q} auf {rev}, {g} mehr als im Vorjahresquartal.',
             'Im {q} erzielte das Unternehmen {rev} Umsatz, ein Plus von {g} gegenüber dem Vorjahr.'],
    'q_flat': ['Im {q} lag der Umsatz bei {rev}, fast genauso hoch wie ein Jahr zuvor.', 'Im {q} blieb der Umsatz mit {rev} gegenüber dem Vorjahr stabil.',
               'Im {q} erzielte das Unternehmen {rev} Umsatz, auf dem Niveau des Vorjahres.'],
    'q_down': ['Im {q} lag der Umsatz bei {rev}, {g} weniger als ein Jahr zuvor.', 'Der Umsatz sank im {q} gegenüber dem Vorjahr um {g} auf {rev}.',
               'Im {q} erzielte das Unternehmen {rev} Umsatz, {g} weniger als ein Jahr zuvor.'],
    'q_streak': ['Das sind {n} Quartale in Folge mit Wachstum gegenüber dem Vorjahr.', 'Es sind bereits {n} Quartale in Folge mit Wachstum gegenüber dem Vorjahr.', 'Die Wachstumsserie reicht über {n} Quartale.'],
    'q_profit': ['Der Nettogewinn des Quartals lag bei {ni}.', 'In diesem Quartal verdiente das Unternehmen {ni}.', 'Nettoergebnis des Quartals: {ni} Gewinn.'],
    'q_loss': ['Das Quartal endete mit einem Nettoverlust von {ni}.', 'In diesem Quartal verlor das Unternehmen {ni}.', 'Nettoergebnis des Quartals: ein Verlust von {ni}.'],
    'peer_margin_hi': ['Die Nettomarge von {m} liegt deutlich über dem Median von {med} der Unternehmen aus dem Bereich {ind}.',
                       'Mit {m} bleibt von jedem Umsatzdollar mehr übrig als beim typischen Unternehmen aus dem Bereich {ind} ({med}).',
                       'Die Rentabilität ist eine Stärke: Nettomarge von {m} gegenüber einem Branchenmedian von {med}.'],
    'peer_margin_lo': ['Die Nettomarge von {m} liegt unter dem Median von {med} der Unternehmen aus dem Bereich {ind}.',
                       'Vom Umsatz bleibt weniger übrig als bei den meisten Konkurrenten: {m} gegenüber einem Median von {med}.',
                       'Die Rentabilität hinkt der Gruppe hinterher: Nettomarge von {m}, Median {med}.'],
    'peer_loss_hi': ['Das Unternehmen verliert Geld (Nettomarge {m}), aber weniger als das typische Unternehmen aus dem Bereich {ind} ({med}).',
                     'Die Nettomarge von {m} ist ein Verlust, wenn auch kleiner als der Branchenmedian ({med}).', 'Die Verluste sind leichter als bei den meisten der Gruppe: {m} gegenüber einem Median von {med}.'],
    'peer_loss_lo': ['Die Nettomarge von {m} ist ein größerer Verlust als der Median von {med} der Unternehmen aus dem Bereich {ind}.',
                     'Je verkauftem Dollar geht mehr verloren als bei den meisten Konkurrenten: {m} gegenüber {med}.', 'Die Verluste wiegen schwerer als in der Gruppe, {m} gegenüber einem Median von {med}.'],
    'peer_margin_eq': ['Die Nettomarge von {m} liegt nahe am Branchenmedian von {med}.', 'Mit {m} liegt die Rentabilität im Rahmen der Gruppe ({med}).',
                       'Die Margen sind typisch für Unternehmen aus dem Bereich {ind}: {m} gegenüber {med}.'],
    'peer_growth_hi_ttm': ["Das Umsatzwachstum der letzten zwölf Monate, {g}, übertraf den Branchenmedian ({med}).", "In den letzten zwölf Monaten wuchs das Unternehmen schneller als die meisten Konkurrenten ({g} gegenüber einem Median von {med}).", "In den letzten zwölf Monaten lag das Wachstum über dem der Gruppe: {g} gegenüber {med}."],
    'peer_growth_lo_ttm': ["Das Umsatzwachstum der letzten zwölf Monate, {g}, blieb unter dem Branchenmedian ({med}).", "Die Konkurrenten wuchsen in den letzten zwölf Monaten stärker: Median {med}, hier {g}.", "In den letzten zwölf Monaten blieb das Wachstum hinter der Gruppe zurück, {g} gegenüber {med}."],
    'peer_growth_eq_ttm': ["Das Umsatzwachstum der letzten zwölf Monate, {g}, entsprach dem Branchenmedian ({med}).", "In den letzten zwölf Monaten wuchs das Unternehmen im Gleichschritt mit den Konkurrenten: {g} gegenüber {med}.", "Das Wachstum der letzten zwölf Monate, {g}, lag nahe am Median der Gruppe, {med}."],
    'opm_up_ttm': ["Die operative Marge liegt mit {now} in den letzten zwölf Monaten über dem Fünfjahresdurchschnitt ({avg}).", "Die operative Rentabilität hat sich verbessert: {now} in den letzten zwölf Monaten gegenüber einem Fünfjahresdurchschnitt von {avg}."],
    'opm_down_ttm': ["Die operative Marge liegt mit {now} in den letzten zwölf Monaten unter dem Fünfjahresdurchschnitt ({avg}).", "Die operative Rentabilität ist gesunken: {now} in den letzten zwölf Monaten gegenüber einem Fünfjahresdurchschnitt von {avg}."],
    'peer_growth_hi': ['Das Umsatzwachstum des letzten Jahres, {g}, übertraf den Branchenmedian ({med}).', 'Im letzten Jahr wuchs das Unternehmen schneller als die meisten Konkurrenten ({g} gegenüber einem Median von {med}).',
                       'Das Wachstum übertraf das der Gruppe: {g} gegenüber {med}.'],
    'peer_growth_lo': ['Das Umsatzwachstum des letzten Jahres, {g}, blieb unter dem Branchenmedian ({med}).', 'Die Konkurrenten wuchsen im letzten Jahr stärker: Median {med}, hier {g}.',
                       'Das Wachstum blieb hinter der Gruppe zurück, {g} gegenüber {med}.'],
    'peer_growth_eq': ['Das Umsatzwachstum des letzten Jahres, {g}, entsprach dem Branchenmedian ({med}).', 'Im letzten Jahr wuchs das Unternehmen im Gleichschritt mit den Konkurrenten: {g} gegenüber {med}.',
                       'Das Wachstum des letzten Jahres, {g}, lag nahe am Median der Gruppe, {med}.'],
    'peer_pe_hi': ['Der Markt zahlt das {pe}-Fache des Gewinns, {x} so viel wie der Branchenmedian ({med}): Er erwartet von diesem Unternehmen mehr als von den Konkurrenten.',
                   'Mit einem KGV von {pe} gegenüber einem Branchenmedian von {med} wird die Aktie mit einem Aufschlag gehandelt, {x} so hoch wie das Multiple der Gruppe.',
                   'Die Bewertung ist im Vergleich zu den Konkurrenten anspruchsvoll: KGV {pe}, Branchenmedian {med}.'],
    'peer_pe_lo': ['Das KGV von {pe} liegt unter dem Branchenmedian ({med}): Der Markt ist bei diesem Unternehmen vorsichtiger als bei den Konkurrenten.',
                   'Beim {pe}-Fachen des Gewinns ist die Aktie günstiger als der typische Konkurrent ({med}); die Frage ist, ob dieser Abschlag gerechtfertigt ist.',
                   'Die Aktie wird mit einem Abschlag zur Gruppe gehandelt: KGV {pe} gegenüber {med}.'],
    'peer_pe_eq': ['Das KGV von {pe} liegt nahe am Branchenmedian von {med}.', 'Die Bewertung liegt im Rahmen der Konkurrenz: KGV {pe}, Median {med}.',
                   'Beim {pe}-Fachen des Gewinns wird die Aktie wie die Gruppe gehandelt ({med}).'],
    'peer_pe_none': ['Ein KGV gibt es nicht, weil das Unternehmen keinen Gewinn macht; {n} der {tot} Unternehmen der Branche sind profitabel.',
                     'Ohne Gewinn gibt es kein KGV zum Vergleichen; {n} der {tot} Konkurrenten verdienen Geld.',
                     'Der KGV-Vergleich greift noch nicht: Das Unternehmen verliert Geld, während {n} von {tot} Konkurrenten profitabel sind.'],
    'roic_hi': ['Eine Rendite auf das investierte Kapital von {roic} ist hoch, ein Zeichen für ein Geschäft mit Preissetzungsmacht oder wenig Kapitalbedarf.',
                'Das Unternehmen verdient {roic} auf das investierte Kapital, deutlich mehr, als dieses Kapital kostet.', 'Die Rendite auf das investierte Kapital ist solide: {roic}.'],
    'roic_lo': ['Die Rendite auf das investierte Kapital beträgt nur {roic}, niedrig für ein profitables Unternehmen.', 'Auf das investierte Kapital verdient das Unternehmen nur {roic}.',
                'Die Kapitalrendite ist schwach: {roic} auf das investierte Kapital.'],
    'bs_cash': ['Das Unternehmen hat {net} mehr Barmittel als Schulden, {p} des Börsenwerts.', 'Die Nettoliquidität von {net} deckt {p} des Börsenwerts.',
                'Die Bilanz weist {net} Nettoliquidität aus, {p} dessen, was das Unternehmen wert ist.'],
    'bs_debt_x': ['Die Nettoverschuldung beträgt {net}, etwa das {x}-Fache eines Jahres an operativem Cash-Gewinn (EBITDA).', 'Das Unternehmen schuldet {net} mehr, als es an Barmitteln hat, das {x}-Fache des EBITDA.',
                  'Eine Nettoverschuldung von {net} entspricht {x} Jahren EBITDA.'],
    'bs_debt_p': ['Die Nettoverschuldung beträgt {net}, {p} des Börsenwerts.', 'Das Unternehmen trägt {net} Nettoschulden, {p} des Börsenwerts.', 'Schulden abzüglich Barmittel: {net} ({p} des Börsenwerts).'],
    'bs_runway': ['In den letzten zwölf Monaten verbrauchte das Unternehmen {burn} an Barmitteln; die verfügbaren Mittel reichen bei diesem Tempo etwa {x} Jahre.',
                  'Beim jüngsten Tempo von {burn} pro Jahr reichen die Barmittel etwa {x} Jahre.', 'Der Mittelabfluss lag in zwölf Monaten bei {burn}, etwa {x} Jahre Reichweite.'],
    'bs_runway_short': ['In den letzten zwölf Monaten verbrauchte das Unternehmen {burn} an Barmitteln, und die Mittel reichen nur etwa {x} Jahre: Neue Aktien oder neue Schulden sind zu erwarten.',
                        'Die Reichweite ist kurz: {burn} Mittelabfluss pro Jahr gegenüber Barmitteln für etwa {x} Jahre, eine weitere Finanzierung ist also wahrscheinlich.',
                        'Bei {burn} Mittelabfluss pro Jahr reichen die Barmittel etwa {x} Jahre; eine Kapitalerhöhung würde nicht überraschen.'],
    'sh_dilute': ['Die Zahl der Aktien ist in drei Jahren um etwa {p} pro Jahr gestiegen, was die Aktionäre verwässert.', 'Die Aktionäre wurden drei Jahre lang um etwa {p} pro Jahr verwässert.',
                  'Neue Aktien kommen jährlich um etwa {p} hinzu.'],
    'sh_buyback': ['Die Zahl der Aktien ist in drei Jahren dank Rückkäufen um etwa {p} pro Jahr gesunken.', 'Rückkäufe haben die Aktienzahl um etwa {p} pro Jahr verringert.',
                   'Jedes Jahr gibt es weniger Aktien: in drei Jahren etwa {p} weniger pro Jahr.'],
    'div_yes': ['Das Unternehmen zahlt eine Dividende mit einer Rendite von {y} und hat in {n} der Jahre unserer Daten gezahlt.', 'Die Dividende bringt {y}; die Zahlungen reichen in unseren Daten {n} Jahre zurück.',
                'Wer Erträge sucht, erhält {y}, gezahlt über {n} erfasste Jahre.'],
    'sbc_heavy': ['Die aktienbasierte Vergütung entspricht {p} des Free Cashflows, echte Kosten, die die Cashflow-Zahlen nicht zeigen.',
                  'Die aktienbasierte Vergütung ist hoch: {p} des Free Cashflows.', 'Der Free Cashflow schmeichelt dem Unternehmen: Die aktienbasierte Vergütung macht {p} dieser Zahl aus.'],
    'an_up': ['Die Analysten haben ihre Schätzungen angehoben: {up} nach oben und {dn} nach unten in den letzten 30 Tagen.', 'Die Revisionen zeigen nach oben: {up} Anhebungen gegenüber {dn} Senkungen in 30 Tagen.',
              'Im letzten Monat haben {up} Analysten ihre Zahlen angehoben und {dn} gesenkt.'],
    'an_down': ['Die Analysten haben ihre Schätzungen gekürzt: {dn} nach unten und {up} nach oben in den letzten 30 Tagen.', 'Die Revisionen zeigen nach unten: {dn} Senkungen gegenüber {up} Anhebungen in 30 Tagen.',
                'Im letzten Monat haben {dn} Analysten ihre Zahlen gesenkt und nur {up} angehoben.'],
    'an_mixed': ['Die Revisionen der Schätzungen sind gemischt: {up} nach oben und {dn} nach unten in 30 Tagen.', 'Die Analysten sind sich über die Richtung uneins: {up} Anhebungen und {dn} Senkungen im letzten Monat.',
                 'In 30 Tagen wurden {up} Schätzungen angehoben und {dn} gesenkt.'],
    'an_range': ['Die Kursziele von {n} Analysten reichen von {lo} bis {hi}.', 'Die {n} Kursziele reichen von {lo} bis {hi}.',
                 'Die Kursziele gehen weit auseinander: {lo} am unteren und {hi} am oberen Ende ({n} Analysten).'],
    'an_next': ['Für das {q} erwartet der Konsens einen Gewinn je Aktie von {eps} bei einem Umsatz von {rev}.', 'Der nächste Bericht betrifft das {q}: Konsens {eps} je Aktie und {rev} Umsatz.',
                'Die Analysten erwarten für das {q} {eps} je Aktie und {rev} Umsatz.'],
    'an_next_eps': ['Für das {q} erwartet der Konsens einen Gewinn je Aktie von {eps}.', 'Der nächste Bericht betrifft das {q}; der Konsens liegt bei {eps} je Aktie.', 'Die Analysten erwarten für das {q} {eps} je Aktie.'],
}
