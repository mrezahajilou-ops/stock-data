# -*- coding: utf-8 -*-
"""Die größten ETFs der Welt, auf Deutsch beschrieben für aktienadler.com.

Auf Deutsch geschrieben, nicht übersetzt: Die Leser sitzen in Deutschland, Österreich oder der
Schweiz. Wer in der EU wohnt, bekommt bei einem US-ETF eine abgelehnte Order und muss wissen, warum
und welcher europäische Fonds (UCITS) dasselbe abbildet.

Die Zahlen stehen nicht hier. Kurs, Rendite, Bestände und Kennzahlen werden täglich in
etf_data.py berechnet.
"""

UI = dict(
    home='Start', etfs='ETFs', other='Sonstige', fundcol='Fonds',
    ps='Kurs / Umsatz', growth='Umsatzwachstum, letztes Jahr',
    margin='Nettomarge', score='Unsere Durchschnittsnote',
    no_pe_h='Warum hier kein KGV steht',
    in_europe='Wenn Sie in Europa wohnen:',
    more_exp='teurer', cheaper='günstiger',
    shariah='Scharia-konforme Alternative',
    vs_sp='Der S&P 500 liegt nach demselben Maßstab beim %(sp)s-Fachen, dieser Fonds ist also %(diff)s %(dir)s.',
    priips='%(fund)s hat seinen Sitz in den USA. US-Fonds veröffentlichen nicht das Basisinformationsblatt, '
           'das die EU-Regeln (PRIIPs) vorschreiben, deshalb können Privatanleger in der EU, also auch in '
           'Deutschland und Österreich, ihn nicht kaufen: Die Order wird bei jedem Broker abgelehnt, ob Trade '
           'Republic, Scalable Capital, comdirect oder ING. In der Schweiz gilt diese EU-Regel nicht, und viele '
           'Broker wie Swissquote bieten US-ETFs an. Für Anleger in der EU ist ein europäischer Fonds (UCITS) '
           'mit demselben Index der übliche Weg.',
    note_tbl='Die KGV-Spalte wird aus den Unternehmen berechnet, die der jeweilige Fonds hält, gewichtet mit '
             'den Gewichten des Fonds selbst und mit denselben Zahlen wie auf unseren Aktienseiten. Sie bleibt '
             'leer, wenn der Fonds keine Aktien hält oder überwiegend aus Unternehmen besteht, die außerhalb '
             'der USA notiert sind und die wir nicht abdecken.',
    i_title='Die {N} größten ETFs: Bestände, KGV und Rendite',
    i_desc='Die {N} größten ETFs der Welt mit Beständen, Gewichten und 12-Monats-Rendite sowie einem KGV, '
           'das aus den Unternehmen berechnet wird, die jeder Fonds tatsächlich hält.',
    d_title='ETF %(t)s: Bestände, KGV und Rendite',
    d_desc='%(name)s (%(t)s): Bestände, Gewichte und Rendite, mit einem KGV, das aus den gehaltenen '
           'Unternehmen berechnet wird. %(idea)s',
    h1='Die {N} größten ETFs der Welt',
    sub='Bestände, Gewichte und Bewertung · aktualisiert',
    lead='Die {N} größten börsengehandelten Indexfonds der Welt: wofür jeder gut ist, was er enthält und '
         'wie die Unternehmen darin bewertet sind.',
    intro='Das KGV auf diesen Seiten veröffentlicht nicht der Fonds. Jede Position wird mit unserer eigenen '
          'Seite zu diesem Unternehmen abgeglichen und mit den Gewichten des Fonds gewichtet, das KGV eines '
          'ETFs stammt hier also aus denselben SEC-Berichten wie jede Aktienseite dieser Website. Jede '
          'Position lässt sich anklicken, um mehr über das Unternehmen zu lesen.',
    idea='Die Idee',
    ret='Rendite',
    fund='Wie die enthaltenen Unternehmen bewertet sind',
    holds='Größte Positionen',
    made='Woraus der Fonds besteht',
    where='Können Sie ihn dort kaufen, wo Sie wohnen?',
    faq='Häufige Fragen',
    company='Unternehmen',
    weight='Gewicht',
    all50='Die {N} Fonds im Vergleich',
    y1='1 Jahr', y3='3 Jahre', ytd='Seit Jahresbeginn', m1='Letzter Monat', m3='3 Monate', y5='5 Jahre',
    price='Kurs', pe='KGV', holdings='Positionen',
    chartcap='Rendite der letzten 12 Monate, alle Fonds dieser Seite. Tippen Sie auf einen Balken, um den Fonds zu öffnen.',
    linecap='Kurs seit %(year)s. Ohne Dividenden.',
    note_ret='Nur die Kursveränderung. Ein ausschüttender Fonds hat mehr erwirtschaftet; ein thesaurierender '
             'nicht.',
    note_pe='Diese Zahl stammt nicht vom Fonds. Jede Position wird mit unserer Seite zu diesem Unternehmen '
            'abgeglichen und mit den Gewichten des Fonds gewichtet, die Zahlen stammen also aus denselben '
            'Berichten wie der Rest der Website. Wir decken %(cov)s des Fonds nach Gewicht ab (%(n)s von %(total)s Positionen).',
    note_holds='Die %(n)d größten von %(total)s Positionen laut dem vom Fonds veröffentlichten Bestand%(asof)s. '
               'Verlinkte Namen haben eine vollständige Seite auf dieser Website.',
    note_ctry='Die allgemeine Lage, keine Empfehlung zu einem bestimmten Broker oder zu Steuern. Wenn ein Fonds '
              'nicht gekauft werden kann, liegt das an der EU-Regel zum Basisinformationsblatt, nicht am Broker.',
    no_pe_bond='Dieser Fonds hält keine Unternehmensaktien, es gibt also keinen Gewinn, durch den man den Kurs '
               'teilen könnte. Bei ihm zählt, wem er Geld leiht und wie lange: Bonität und Duration bei einem '
               'Anleihefonds, beim Gold oder Bitcoin der Preis des Basiswerts selbst. Er hat %(n)s Positionen.',
    no_pe_thin='Unsere Unternehmensdaten decken in den USA notierte Gesellschaften ab. Dieser Fonds hat '
               '%(n)s Positionen, und nur %(cov)s seines Gewichts liegt in Unternehmen, die wir abdecken. Ein '
               'KGV aus diesem Teil würde also nur ein Stück des Fonds beschreiben, nicht den Fonds. Wir '
               'lassen es lieber weg, als eine Zahl zu veröffentlichen, die wie eine Antwort aussieht. Die '
               'Bestände und Gewichte unten sind dagegen die des Fonds selbst.',
    dis='Bestände laut den Berichten des Fonds; Unternehmenszahlen laut deren Berichten an die SEC, täglich '
        'neu berechnet. Inhalt zu Bildungszwecken, keine Anlageberatung.',
    groups=[
        ('US-Gesamtmarkt', ['US large cap', 'US total market']),
        ('Wachstum und Value', ['US large cap growth', 'US mega cap growth', 'US large cap value', 'US quality factor']),
        ('Dividenden', ['US dividend', 'US dividend growth']),
        ('Kleinere Unternehmen', ['US mid cap', 'US small cap']),
        ('Außerhalb der USA', ['developed ex-US', 'global ex-US', 'global', 'emerging markets', 'Europe']),
        ('Sektoren', ['technology', 'semiconductors', 'financials', 'healthcare', 'energy', 'industrials', 'real estate']),
        ('Anleihen, Gold und Bitcoin', ['US investment grade bonds', 'international bonds', 'gold', 'bitcoin']),
    ],
)

T = {
 'VOO': ('Die 500 größten Unternehmen der USA, zu den niedrigsten Kosten am Markt.',
         'Enthält alle Unternehmen des S&P 500 im Verhältnis zu ihrem Börsenwert, die größten geben also den '
         'Ton an. Es gibt kein menschliches Urteil: Ein Unternehmen kommt hinein, wenn das Indexkomitee es '
         'aufnimmt, und fliegt heraus, wenn es gestrichen wird. Weil die Gewichte dem Börsenwert folgen, steckt '
         'fast ein Drittel des Fonds in den zehn größten Werten, viel konzentrierter, als die meisten glauben.'),
 'IVV': ('Dieselben 500 Unternehmen wie VOO, von einer anderen Fondsgesellschaft und zu denselben Kosten.',
         'Bildet den S&P 500 mit allen Mitgliedern im Indexgewicht ab. Wer jahrelang hält, wählt zwischen ihm '
         'und VOO nach dem Broker und dem besseren Spread an dem Tag, nicht nach einem echten Unterschied '
         'zwischen den Fonds.'),
 'SPY': ('Der ursprüngliche S&P-500-Fonds: das meistgehandelte Wertpapier der Welt.',
         'Er ist der älteste ETF der USA und als Unit Investment Trust aufgelegt, nicht als moderner Fonds. '
         'Deshalb darf er keine Wertpapiere verleihen und Dividenden zwischen zwei Ausschüttungen nicht '
         'wieder anlegen. Das kostet Langfristanleger im Vergleich zu VOO und IVV jedes Jahr ein wenig. Dafür '
         'hat er eine unerreichte Liquidität und einen riesigen Optionsmarkt, deshalb nutzen ihn Trader, und '
         'deshalb sollten Langfristanleger meist zu einem anderen greifen.'),
 'VTI': ('Alle investierbaren börsennotierten Unternehmen der USA in einer einzigen Position.',
         'Enthält Tausende Unternehmen, von den größten bis zu den kleinen, gewichtet nach Börsenwert. In der '
         'Praxis verhält er sich fast wie ein S&P-500-Fonds, weil die kleinen Werte zusammen nur wenige '
         'Prozentpunkte ausmachen. Der Unterschied zeigt sich in den seltenen Phasen, in denen Nebenwerte '
         'vorne liegen.'),
 'QQQ': ('Die 100 größten Nicht-Finanzwerte der Nasdaq: praktisch eine Wette auf Big Tech.',
         'Folgt dem Nasdaq-100, der Finanzwerte ganz ausschließt und sich über die Börse definiert, an der ein '
         'Unternehmen notiert ist, nicht über sein Geschäft. Dieser Zufall der Konstruktion erklärt, warum er '
         'so stark auf Technologie konzentriert ist und warum er den S&P 500 mal geschlagen hat und mal viel '
         'tiefer gefallen ist. Die zehn größten Positionen machen meist rund die Hälfte des Fonds aus.'),
 'VUG': ('Die wachstumsstärkere Hälfte der großen US-Unternehmen, nach festen Regeln bestimmt.',
         'Teilt den US-Markt der großen Unternehmen anhand von Gewinn- und Umsatzwachstum und Buchwert in '
         'Wachstum und Value und behält die Wachstumsseite, gewichtet nach Börsenwert. Weil die größten '
         'Technologiekonzerne als Wachstumswerte gelten, ist der Fonds stark auf sie konzentriert: Er ähnelt '
         'dem QQQ mehr, als der Name vermuten lässt.'),
 'VTV': ('Die günstigere Hälfte der großen US-Unternehmen: Banken, Gesundheit und Industrie.',
         'Die andere Hälfte derselben Aufteilung, aus der VUG entsteht. Enthält große US-Unternehmen, die nach '
         'Kurs-Buchwert, KGV und Dividendenrendite als Value gelten, gewichtet nach Börsenwert. Heraus kommt ein '
         'Fonds mit deutlich mehr Banken, Gesundheit und Energie, viel weniger Technologie als der S&P 500 '
         'und einer höheren Dividende.'),
 'VIG': ('Unternehmen, die ihre Dividende seit mindestens zehn Jahren in Folge erhöhen.',
         'Filtert nach einer langen, ununterbrochenen Serie von Dividendenerhöhungen und streicht dann das '
         'Viertel mit der höchsten Dividendenrendite. Dieser zweite Schritt ist der klügste: Eine sehr hohe '
         'Rendite ist meist ein Zeichen für einen gefallenen Kurs, nicht für Großzügigkeit, und ihr Ausschluss '
         'vermeidet fast alle Kürzungen. Heraus kommt ein Qualitätsfonds, der auch Dividenden zahlt, kein '
         'Hochdividendenfonds.'),
 'SCHD': ('Hundert Dividendenzahler, ausgewählt nach solider Bilanz, nicht nur nach Rendite.',
          'Verlangt zehn Jahre ununterbrochene Dividendenzahlung und sortiert den Rest nach Cashflow im '
          'Verhältnis zu den Schulden, Eigenkapitalrendite, Dividendenrendite und Dividendenwachstum. Diese '
          'Mischung lässt Unternehmen außen vor, die eine Dividende zahlen, die sie sich nicht leisten können, '
          'der typische Fehler von Hochdividendenfonds. Die Gewichte sind gedeckelt, damit kein Unternehmen '
          'und keine Branche dominiert.'),
 'VYM': ('Die Hälfte des US-Marktes mit der höchsten Dividendenrendite, gewichtet nach Größe.',
         'Sortiert US-Unternehmen nach der erwarteten Dividendenrendite und behält die obere Hälfte nach '
         'Börsenwert, ohne REITs. Ein Qualitätsfilter fehlt, das macht ihn einfacher und breiter als SCHD, '
         'lässt aber mehr Unternehmen drin, deren Rendite nur hoch ist, weil die Aktie gefallen ist.'),
 'DGRO': ('US-Unternehmen, die ihre Dividende seit fünf Jahren erhöhen und noch Spielraum haben.',
          'Verlangt fünf Jahre Dividendenwachstum in Folge und eine Ausschüttungsquote unter 75 %, was alle '
          'aussortiert, die mehr ausschütten, als sie durchhalten können. Aus demselben Grund wie bei VIG '
          'fällt das Zehntel mit der höchsten Rendite heraus. Breiter als VIG und mit etwas mehr Dividende.'),
 'IWF': ('Die Wachstumshälfte der tausend größten US-Unternehmen, nach Russell.',
         'Russell teilt sein Universum großer Unternehmen nach Buchwert zu Kurs und erwartetem Wachstum und '
         'erlaubt, dass ein Unternehmen teils als Wachstum und teils als Value zählt. In der Praxis bedeutet '
         'das viel Technologie, ähnlich wie VUG, aber mit einem anderen Anpassungskalender: Die jährliche '
         'Russell-Neuzusammensetzung im Juni ist eines der größten Handelsereignisse des Jahres.'),
 'IWD': ('Die Value-Hälfte der tausend größten US-Unternehmen.',
         'Das Spiegelbild von IWF: Unternehmen, die nach Buchwert zu Kurs günstig sind und wenig erwartetes '
         'Wachstum haben. Finanzwerte, Gesundheit und Industrie dominieren. Zusammen mit IWF ergibt er den '
         'gesamten Russell 1000.'),
 'IWM': ('Zweitausend kleine US-Unternehmen: der meistgenutzte Maßstab für Nebenwerte.',
         'Reicht vom Unternehmen Nummer 1.001 bis 3.000 nach Börsenwert. Ein beachtlicher Teil des Index '
         'schreibt keine Gewinne, deshalb verhält er sich ganz anders als die Indizes der großen Werte: Er '
         'reagiert stärker auf Zinsen und die US-Binnenwirtschaft und schwankt viel stärker.'),
 'IJH': ('Die 400 mittelgroßen US-Unternehmen zwischen dem S&P 500 und den kleinen Werten.',
         'Der Midcap-Index von S&P verlangt für die Aufnahme Gewinne, was die Russell-Indizes nicht tun. Diese '
         'eine Regel hat die mittelgroßen US-Werte historisch zu einem Universum mit besserer Qualität als die '
         'kleinen gemacht und erklärt einen guten Teil des langfristigen Renditeunterschieds zwischen beiden.'),
 'IJR': ('Sechshundert kleine US-Unternehmen, gefiltert nach Profitabilität.',
         'Folgt dem S&P SmallCap 600, der Gewinne verlangt, bevor ein Unternehmen aufgenommen wird. Das ist der '
         'Hauptunterschied zum Russell 2000 und der Grund, warum sich die beiden Nebenwerte-Indizes lange '
         'auseinanderentwickelt haben, obwohl sie denselben Marktteil abdecken.'),
 'VO': ('Mittelgroße US-Unternehmen, bestimmt nach ihrer Lage im Gesamtwert des Marktes.',
        'Deckt den Bereich des US-Marktes zwischen etwa dem 70. und 85. Perzentil des kumulierten Börsenwerts '
        'ab. Anders als der Midcap-Index von S&P ohne Gewinnfilter, also breiter und mit etwas geringerer '
        'Qualität, zu niedrigeren Kosten.'),
 'VB': ('Kleine US-Unternehmen, ohne Filter, ob sie Gewinn machen.',
        'Deckt den unteren Bereich des US-Marktes nach kumuliertem Börsenwert ab, mit über tausend '
        'Unternehmen. Breiter und günstiger als IJR, enthält aber Verlustbringer, die der Nebenwerte-Index '
        'von S&P ausschließt.'),
 'SPYM': ('Der günstige S&P 500 von State Street, zum Halten gemacht, nicht zum Handeln.',
          'Derselbe Index wie SPY in einer modernen Fondsstruktur und zu viel niedrigeren Kosten. State Street '
          'hat ihn aufgelegt, gerade weil die Trust-Struktur von SPY ihn für Langfristanleger unattraktiv '
          'machte. Weniger Handelsvolumen als SPY, was nur für sehr große Orders zählt.'),
 'RSP': ('Dieselben 500 Unternehmen wie der S&P 500, aber alle gleich gewichtet.',
         'Gibt jedem Unternehmen rund 0,2 % des Fonds und gleicht vierteljährlich aus, verkauft also '
         'systematisch, was gestiegen ist, und kauft, was gefallen ist. Die Konzentration auf die größten '
         'Werte verschwindet ganz; praktisch entsteht eine Neigung zu mittelgroßen Werten und zu Value. '
         'Schlägt den S&P 500, wenn der Aufschwung breit ist, und fällt weit zurück, wenn wenige Giganten '
         'ziehen.'),
 'QUAL': ('US-Unternehmen mit hoher Eigenkapitalrendite, stabilen Gewinnen und wenig Schulden.',
          'Sortiert nach drei Kennzahlen, Eigenkapitalrendite, Schwankung des Gewinns und Verschuldungsgrad, '
          'und nimmt die besten jeder Branche, damit der Fonds nicht zufällig zur Branchenwette wird. '
          'Historisch hat Qualität Rückgänge besser überstanden und ist in scharfen Erholungen zurückgefallen.'),
 'MGK': ('Nur die größten Wachstumsunternehmen der USA: der konzentrierteste Weg, sie zu besitzen.',
         'Beschränkt sich auf die Megacaps am oberen Ende des Wachstumsuniversums, also wenige Dutzend '
         'Positionen und eine extreme Konzentration auf die größten Technologiekonzerne. Konzentrierter als '
         'QQQ und viel konzentrierter als VUG. Sinnvoll nur für alle, die sich bewusst für dieses Engagement '
         'entschieden haben.'),
 'VV': ('Die großen Unternehmen des US-Marktes, bestimmt nach Größe statt durch ein Komitee.',
        'Deckt die oberen 85 % des US-Marktes nach kumuliertem Börsenwert ab, hat also mehr Unternehmen als '
        'der S&P 500 und kommt ohne das Komitee aus, das über die Aufnahme entscheidet. In der Praxis folgt '
        'die Rendite dem S&P 500 sehr eng.'),
 'ITOT': ('Der ganze US-Markt in einem Fonds, von BlackRock.',
          'Enthält den vollständigen US-Markt, von den großen bis zu den Microcaps, im Indexgewicht. Direkter '
          'Konkurrent von VTI, mit praktisch demselben Engagement, denselben Kosten und demselben Verhalten.'),
 'SCHX': ('Die 750 größten US-Unternehmen, mit einigen der niedrigsten Kosten überhaupt.',
          'Ein breiter Fonds großer Unternehmen mit mehr Namen als der S&P 500 und Kosten am unteren Ende des '
          'Marktes. Verhält sich in jedem relevanten Zeitraum fast genauso wie VV und der S&P 500.'),
 'VEA': ('Unternehmen aus Industrieländern außerhalb der USA: Europa, Japan, Kanada, Australien.',
         'Enthält Tausende Unternehmen aus Industrieländern ohne die USA, gewichtet nach Börsenwert, wodurch '
         'Japan und Großbritannien große Positionen sind. Anders als die MSCI-Variante schließt er Kanada und '
         'Südkorea ein. Die Rendite hängt für Euro-Anleger zusätzlich vom Wechselkurs ab: Für Sie zählt die '
         'Entwicklung der einzelnen Währungen gegenüber dem Euro, nicht nur gegenüber dem Dollar.'),
 'VXUS': ('Alle investierbaren Unternehmen der Welt außerhalb der USA.',
          'Vereint Industrie- und Schwellenländer außerhalb der USA in einem Fonds, mit Marktgewichten und '
          'mehreren Tausend Unternehmen. Zusammen mit VTI ergibt er mit zwei Positionen ein vollständiges '
          'Weltdepot.'),
 'IEFA': ('Industrieländer in Europa, Australasien und Fernost: der internationale Referenzindex.',
          'Folgt dem EAFE-Universum von MSCI, das die USA und Kanada ausschließt und große, mittlere und kleine '
          'Werte abdeckt. Es ist die meistgenutzte internationale Beimischung in US-Depots und der Maßstab, an '
          'dem internationale Fondsmanager gemessen werden.'),
 'VWO': ('Unternehmen aus Schwellenländern, dominiert von China, Indien und Taiwan.',
         'Enthält Schwellenländer-Unternehmen nach Marktgewicht, was den Fonds auf eine Handvoll Länder und '
         'wenige sehr große Technologie- und Internetkonzerne konzentriert. FTSE stuft Südkorea als '
         'Industrieland ein, deshalb enthält dieser Fonds anders als die MSCI-Variante keine koreanischen '
         'Unternehmen.'),
 'IEMG': ('Schwellenländer nach der MSCI-Definition, die Südkorea einschließt.',
          'Der Hauptunterschied zu VWO ist die Länderzuordnung: MSCI behandelt Südkorea als Schwellenland, '
          'deshalb enthält dieser Fonds große koreanische Unternehmen, die VWO nicht hat. Er reicht außerdem '
          'tiefer in die Nebenwerte. Ansonsten verhalten sich beide ähnlich.'),
 'EFA': ('Der ursprüngliche internationale Fonds für Industrieländer, nur große und mittlere Werte.',
         'Älter und teurer als IEFA, deckt dieselben Märkte ab, aber ohne die kleinen Werte. Er lebt weiter '
         'wegen seines Optionsmarktes und seiner Rolle als Referenzindex in institutionellen Mandaten, nicht '
         'weil er der beste Fonds zum Halten wäre.'),
 'VT': ('Der gesamte investierbare Aktienmarkt der Welt in einer einzigen Position.',
        'Enthält rund zehntausend Unternehmen aus Industrie- und Schwellenländern nach Marktgewicht, was heute '
        'etwa zwei Drittel USA bedeutet. Näher kommt man an das globale Marktportfolio nicht heran, und man '
        'muss für kein Land eine Quote festlegen.'),
 'VGK': ('Europäische Unternehmen, von Großbritannien und der Schweiz bis Skandinavien.',
         'Engagement in den europäischen Industrieländern nach Marktgewicht, was den Fonds auf wenige sehr '
         'große Unternehmen aus Pharma, Luxus, Halbleiterausrüstung und Banken konzentriert. Für Anleger aus '
         'dem Euroraum ist das Ihr Heimatmarkt; als US-Fonds ist er hier aber gar nicht kaufbar, der '
         'europäische Gegenpart deckt dasselbe ab.'),
 'VEU': ('Die Welt außerhalb der USA, nur große und mittlere Werte.',
         'Sehr ähnlich wie VXUS, aber ohne die kleinen Werte, dadurch etwas stärker auf die großen '
         'multinationalen Konzerne konzentriert, die die Indizes außerhalb der USA prägen. Beide erfüllen im '
         'Depot dieselbe Aufgabe.'),
 'VGT': ('US-Technologieunternehmen, einschließlich Hardware- und Halbleiterherstellern.',
         'Deckt den Technologiesektor nach der MSCI-Definition ab, die Software, Hardware und Halbleiter '
         'umfasst, aber die großen Internet- und Medienkonzerne ausklammert, die als Kommunikationsdienste '
         'gelten, und auch Amazon und Tesla, die zum Konsum zählen. Diese Ausschlüsse sind wichtiger, als '
         'viele denken, und der Hauptunterschied zum QQQ.'),
 'XLK': ('Die Technologieunternehmen im S&P 500, und nur diese.',
         'Beschränkt auf S&P-500-Mitglieder mit Technologie-Einstufung, deshalb viel konzentrierter als VGT: '
         'meist weniger als 70 Positionen, und die ersten beiden kommen auf fast 40 % des Fonds. Die '
         'Sektordefinitionen werden von Zeit zu Zeit überarbeitet, und solche Überarbeitungen können den '
         'Fonds über Nacht verändern.'),
 'SMH': ('Die 25 größten börsennotierten Halbleiterunternehmen: der konzentrierteste Weg, auf den Chip-Zyklus zu setzen.',
         'Enthält nur 25 Unternehmen und ist damit extrem konzentriert: Die ersten zwei oder drei können ein '
         'Drittel des Fonds ausmachen. Er nimmt ausländische Hersteller über ihre US-Notierungen auf, was '
         'SOXX historisch nicht tat. Die Nachfrage nach Halbleitern ist zyklisch, und dieser Fonds schwankt in '
         'beide Richtungen viel stärker als der Markt.'),
 'SOXX': ('Dreißig in den USA notierte Halbleiterunternehmen, etwas breiter gestreut als SMH.',
          'Folgt einem Index von in den USA notierten Halbleiterwerten mit Obergrenzen für das Gewicht einer '
          'einzelnen Position, ist also an der Spitze weniger lastig als SMH. Die Indexmethodik hat sich mehr '
          'als einmal geändert, was man wissen sollte, bevor man seine Historie mit irgendetwas vergleicht.'),
 'XLF': ('Die Banken, Versicherer und Zahlungsdienstleister im S&P 500.',
         'Enthält die Finanzwerte des S&P 500 mit Marktgewichten und Obergrenzen. Seit Immobilien in einen '
         'eigenen Sektor ausgegliedert wurden, ist der Fonds eine sauberere Wette auf Banken, Versicherungen '
         'und Kapitalmärkte. Er reagiert stark auf Zinsen und Kreditbedingungen, genau der Grund, ihn zu '
         'halten oder zu meiden.'),
 'XLV': ('Das große US-Gesundheitswesen: Pharma, Medizintechnik, Krankenversicherer und Großhändler.',
         'Deckt die Gesundheitsunternehmen des S&P 500 ab und mischt damit sehr unterschiedliche Geschäfte: '
         'patentabhängige Pharmakonzerne, stabile Gerätehersteller und Krankenversicherer, deren Geschäft die '
         'Politik bestimmt. Arzneimittelpreise und Gesundheitspolitik in den USA treffen alle, deshalb bewegt '
         'sich der Sektor stärker mit politischen Nachrichten als die meisten.'),
 'XLE': ('Öl und Gas aus den USA, dominiert von zwei Supergiganten.',
         'Enthält die Energieunternehmen des S&P 500, und weil der Sektor an der Spitze sehr lastig ist, '
         'machen die zwei größten integrierten Ölkonzerne meist fast 40 % des Fonds aus. Eine direkte Wette '
         'auf den Ölpreis, mit der operativen Hebelwirkung der Förderer obendrauf.'),
 'XLI': ('Die US-Industrie: Luftfahrt, Eisenbahnen, Maschinen und die großen Mischkonzerne.',
         'Enthält die Industriewerte des S&P 500, eine wirklich vielfältige Gruppe von Rüstungslieferanten '
         'mit Auftragsbüchern für mehrere Jahre bis zu Maschinenbauern, die am Konjunkturzyklus hängen. Er '
         'wird oft genutzt, um direkt eine Meinung zur US-Industrie und zu Infrastrukturinvestitionen '
         'auszudrücken.'),
 'VNQ': ('US-Immobilien über börsennotierte REITs.',
         'Enthält US-REITs aus Rechenzentren, Logistikhallen, Funktürmen, Wohnungen, Läden und Büros, das '
         'amerikanische Gegenstück zu offenen Immobilienfonds und Immobilien-AGs. Weil REITs fast ihren '
         'ganzen Gewinn ausschütten müssen, zahlt der Fonds eine hohe Dividende und reagiert besonders auf '
         'Zinsen: Höhere Zinsen verteuern die Schulden, mit denen die Immobilien finanziert sind, und machen '
         'zugleich die Dividende weniger attraktiv.'),
 'VHT': ('Der gesamte US-Gesundheitssektor, einschließlich kleiner Biotech-Unternehmen.',
         'Breiter als XLV, weil er über den S&P 500 hinaus bis zu mittleren und kleinen Werten reicht, was '
         'ihm einen langen Schwanz an Biotech-Unternehmen gibt. Dieser Schwanz bringt zusätzliche '
         'Schwankungen und die Chance auf außergewöhnliche Renditen, die ein reiner Großwerte-Gesundheitsfonds '
         'nicht hat.'),
 'BND': ('Der US-Anleihemarkt mit Investment-Grade-Rating: Staats-, Hypotheken- und Unternehmensanleihen.',
         'Enthält Tausende Anleihen mit Investment-Grade-Rating im Indexgewicht, also etwa zwei Drittel '
         'Staatsanleihen und staatlich garantierte Hypothekenpapiere. Der Kurs fällt, wenn die Zinsen steigen, '
         'und steigt, wenn sie fallen; die Duration von rund sechs Jahren sagt ungefähr, wie stark. Er ist der '
         'übliche Stabilisator im Depot, keine Renditequelle.'),
 'AGG': ('Derselbe US-Anleihemarkt wie BND, von BlackRock.',
         'Folgt dem Bloomberg US Aggregate ohne Streubesitzanpassung. Der praktische Unterschied zu BND ist '
         'vernachlässigbar: eine andere Anpassung und minimal andere Kosten. Entscheidend ist, welchen der '
         'beiden Ihr Broker günstiger handelt.'),
 'BNDX': ('Anleihen mit Investment-Grade-Rating außerhalb der USA, währungsgesichert.',
          'Enthält nicht-amerikanische Anleihen mit Investment-Grade-Rating, vor allem europäische und '
          'japanische Staatsanleihen, und sichert das Währungsrisiko gegen den Dollar ab. Die Absicherung ist '
          'der Kern: Ohne sie ist eine ausländische Anleihe vor allem eine Währungswette; mit ihr wird sie zu '
          'einem echten Diversifikator gegenüber US-Zinsen. Für Euro-Anleger ist allerdings eine '
          'Euro-Absicherung die passendere Wahl.'),
 'GLD': ('Physisches Gold, in einem Tresor in London gelagert und in Anteile aufgeteilt.',
         'Jeder Anteil steht für einen Bruchteil einer Unze Gold in zugeordneter Verwahrung. Es gibt weder '
         'Erträge noch Gewinne: Die Rendite ist der Goldpreis minus die Verwahrkosten, die durch den Verkauf '
         'einer kleinen Menge Gold pro Jahr bezahlt werden, sodass das Gold je Anteil langsam abnimmt. In der '
         'EU nutzen Anleger stattdessen börsengehandelte Rohstoffpapiere (ETC) auf Gold.'),
 'IAU': ('Dasselbe physische Gold wie GLD, mit niedrigeren jährlichen Kosten.',
         'Inhaltlich identisch mit GLD, zugeordnetes physisches Gold, keine Erträge, Kosten in Metall '
         'bezahlt, aber günstiger, was sich über zehn Jahre zu einem spürbaren Unterschied summiert. GLD hat '
         'mehr Handelsvolumen und einen tieferen Optionsmarkt.'),
 'IBIT': ('Bitcoin bei einem Verwahrer, gekauft und verkauft wie eine Aktie.',
          'Hält Bitcoin direkt bei einem institutionellen Verwahrer, der Kurs folgt also dem Bitcoin-Preis '
          'abzüglich der Gebühr. Man muss sich weder um private Schlüssel kümmern noch eine Kryptobörse '
          'nutzen, genau deshalb hat er schneller Geld eingesammelt als jeder andere ETF-Start der '
          'Geschichte. Der Basiswert erzeugt keinen Cashflow, es gibt also nichts, woran man ihn bewerten '
          'könnte.'),
}

# Die Länder der Leser dieser Ausgabe, mit der Antwort auf Deutsch. Die EU-Regel ist kein Verbot des
# Fonds: Es fehlt ein Dokument, deshalb lehnt der Broker die Order ab. In der Schweiz gilt die Regel nicht.
UI.update({
    's_blocked': 'Nicht kaufbar',
    's_open': 'Kaufbar',
    's_local': 'Kaufbar, auch an einer heimischen Börse gehandelt',
    's_hard': 'Erlaubt, in der Praxis aber schwierig',
    's_sanctions': 'Nicht zugänglich',
    'c_Germany': 'Deutschland', 'c_Austria': 'Österreich', 'c_Switzerland': 'Schweiz',
    'c_Liechtenstein': 'Liechtenstein', 'c_Luxembourg': 'Luxemburg', 'c_United States': 'USA',
    'w_Germany': 'Die EU-Regel (PRIIPs) verlangt ein Basisinformationsblatt auf Deutsch, bevor ein verpacktes '
                 'Anlageprodukt an Privatanleger verkauft werden darf. US-Fondsgesellschaften erstellen es nicht, '
                 'deshalb wird die Order abgelehnt, bei Trade Republic, Scalable Capital, comdirect, ING, flatex '
                 'und jedem anderen Broker. Der oben genannte europäische Fonds folgt demselben Index, ist an '
                 'Xetra, Tradegate oder Lang & Schwarz handelbar und oft auch als Sparplan verfügbar.',
    'w_Austria': 'Dieselbe EU-Regel wie in Deutschland: ohne Basisinformationsblatt keine Order für '
                 'Privatanleger. Der europäische Fonds oben ist der übliche Weg; achten Sie auf den Status als '
                 'steuerlicher Meldefonds, sonst wird es bei der KESt kompliziert.',
    'w_Switzerland': 'Die EU-Regel gilt hier nicht. Viele Schweizer Broker, etwa Swissquote, bieten US-ETFs '
                     'direkt an; Dividenden unterliegen der US-Quellensteuer, die über das Doppelbesteuerungsabkommen '
                     'teilweise anrechenbar ist.',
    'w_Liechtenstein': 'Als EWR-Mitglied gilt dieselbe Regel wie in der EU: Privatanleger brauchen einen Fonds mit '
                       'Basisinformationsblatt, also die europäische Variante.',
    'w_Luxembourg': 'Dieselbe EU-Regel: Die Order für den US-Fonds wird abgelehnt, die europäische Variante ist '
                    'erhältlich.',
    'w_United States': 'Der Fonds hat hier seinen Sitz; er wird wie jede Aktie gekauft.',
})

# Spalten der Indexbox: Art, Grammatik des Namens und Hinweis zum KGV
UI.update({
    'type': 'Art',
    'avg_yr': 'Ø pro Jahr',
    'pe_avg': 'Ø-KGV',
    'name_pattern': '%(index)s von %(issuer)s',
    'note_peavg': 'Niemand veröffentlicht ein historisches KGV für einen Fonds, weil es davon abhängt, was der Fonds zu jedem Zeitpunkt hielt. Deshalb zeichnen wir unseres seit %(since)s auf. Die Durchschnittsspalte wird gefüllt, sobald etwa ein Monat an Daten vorliegt.',
    'note_peavg_none': 'Die Spalte mit dem Ø-KGV füllt sich, während wir die Zahl jedes Tages aufzeichnen.',
    'focus_labels': {'US large cap': 'US-Standardwerte', 'US total market': 'US-Gesamtmarkt', 'US large cap growth': 'US-Wachstum', 'US mega cap growth': 'Wachstums-Megacaps', 'US large cap value': 'US-Value', 'US quality factor': 'US-Qualität', 'US dividend': 'US-Dividenden', 'US dividend growth': 'Dividendenwachstum', 'US mid cap': 'US-Midcaps', 'US small cap': 'US-Nebenwerte', 'developed ex-US': 'Industrieländer ohne USA', 'global ex-US': 'Welt ohne USA', 'global': 'Welt', 'emerging markets': 'Schwellenländer', 'Europe': 'Europa', 'technology': 'Technologie', 'semiconductors': 'Halbleiter', 'financials': 'Finanzwerte', 'healthcare': 'Gesundheit', 'energy': 'Energie', 'industrials': 'Industrie', 'real estate': 'Immobilien', 'US investment grade bonds': 'US-Anleihen', 'international bonds': 'Internationale Anleihen', 'gold': 'Gold', 'bitcoin': 'Bitcoin'},
})

UI['pe_short'] = 'KGV'

# der Text der europäischen Alternative aus etf_list.py, in der Sprache dieser Ausgabe
UCITS = {'VUAA accumulates dividends, VUSA pays them out.': 'VUAA thesauriert die Dividenden, VUSA schüttet sie aus.', 'The same index from the same manager, in a European wrapper.': 'Derselbe Index von derselben Fondsgesellschaft, in europäischer Hülle.', 'No European fund replicates SPY’s trust structure, and none needs to.': 'Kein europäischer Fonds bildet die Trust-Struktur von SPY nach, und keiner muss es.', 'Closest European equivalent; it includes Canada, which VTI does not.': 'Das nächste europäische Gegenstück; es enthält Kanada, das VTI nicht hat.', 'Both track the same index; CNDX accumulates, EQQQ distributes.': 'Beide folgen demselben Index; CNDX thesauriert, EQQQ schüttet aus.', 'Several providers offer one; there is no single obvious equivalent.': 'Mehrere Anbieter haben einen; ein einzelnes offensichtliches Gegenstück gibt es nicht.', 'Available from several providers; check which value definition it uses.': 'Bei mehreren Anbietern erhältlich; prüfen Sie, welche Value-Definition er nutzt.', 'The ten-year increase screen is uncommon in European wrappers.': 'Der Filter mit zehn Jahren Dividendenerhöhung ist bei europäischen Fonds selten.', 'Nothing in Europe replicates the Dow Jones 100 methodology exactly.': 'In Europa bildet nichts die Methodik des Dow Jones 100 exakt nach.', 'Global rather than US-only, but the same family and methodology.': 'Global statt nur USA, aber dieselbe Familie und Methodik.', 'IWDA includes the US; VEVE ex-US variants differ by provider.': 'IWDA enthält die USA; Varianten ohne USA unterscheiden sich je nach Anbieter.', 'VWRL includes the US as well; there is no exact ex-US twin in the range.': 'VWRL enthält ebenfalls die USA; einen exakten Zwilling ohne USA gibt es in der Reihe nicht.', 'World includes the US; EAFE-only UCITS versions exist but are less traded.': 'Der Weltindex enthält die USA; reine EAFE-Varianten als UCITS gibt es, sie werden aber weniger gehandelt.', 'VWCE accumulates dividends, VWRL distributes them.': 'VWCE thesauriert die Dividenden, VWRL schüttet sie aus.', 'European equivalents are exchange-traded commodities, not UCITS funds.': 'Die europäischen Gegenstücke sind börsengehandelte Rohstoffpapiere (ETC), keine UCITS-Fonds.', 'UCITS rules do not permit a single-asset crypto fund.': 'Die UCITS-Regeln erlauben keinen Kryptofonds auf einen einzigen Basiswert.', 'A UCITS ETF tracking a US large-cap growth index': 'ein UCITS-ETF auf einen Wachstumsindex großer US-Unternehmen', 'A UCITS ETF tracking a US large-cap value index': 'ein UCITS-ETF auf einen Value-Index großer US-Unternehmen', 'A UCITS ETF tracking a US dividend growth index': 'ein UCITS-ETF auf einen US-Dividendenwachstumsindex', 'A UCITS ETF tracking a quality US dividend index': 'ein UCITS-ETF auf einen US-Qualitätsdividendenindex', 'A UCITS ETF tracking the Russell 1000 Growth index': 'ein UCITS-ETF auf den Russell 1000 Growth', 'A UCITS ETF tracking the Russell 1000 Value index': 'ein UCITS-ETF auf den Russell 1000 Value', 'A UCITS ETF tracking the Russell 2000': 'ein UCITS-ETF auf den Russell 2000', 'A UCITS ETF tracking the S&P MidCap 400': 'ein UCITS-ETF auf den S&P MidCap 400', 'A UCITS ETF tracking the S&P SmallCap 600': 'ein UCITS-ETF auf den S&P SmallCap 600', 'A UCITS ETF tracking a US mid-cap index': 'ein UCITS-ETF auf einen Index mittelgroßer US-Unternehmen', 'A UCITS ETF tracking a US small-cap index': 'ein UCITS-ETF auf einen US-Nebenwerteindex', 'A UCITS ETF tracking the S&P 500 Equal Weight index': 'ein UCITS-ETF auf den S&P 500 Equal Weight', 'A UCITS ETF tracking a US mega-cap growth index': 'ein UCITS-ETF auf einen Index von US-Wachstums-Megacaps', 'A UCITS ETF tracking US or world information technology': 'ein UCITS-ETF auf Informationstechnologie der USA oder der Welt', 'A UCITS ETF tracking global semiconductors': 'ein UCITS-ETF auf globale Halbleiterwerte', 'A UCITS ETF tracking US or developed-market property': 'ein UCITS-ETF auf Immobilien der USA oder der Industrieländer', 'A UCITS ETF tracking US health care': 'ein UCITS-ETF auf das US-Gesundheitswesen', 'European investors use exchange-traded products rather than UCITS funds': 'europäische Anleger nutzen börsengehandelte Produkte (ETP) statt UCITS-Fonds', 'A EUR-hedged global aggregate bond UCITS ETF': 'ein UCITS-ETF auf globale Anleihen mit Euro-Absicherung', 'A USD-hedged global or US aggregate bond UCITS ETF': 'ein UCITS-ETF auf globale oder US-Anleihen mit Dollar-Absicherung', 'Screened US dividend UCITS funds': 'gefilterte UCITS-Fonds auf US-Dividenden'}
UCITS.update({'Invesco EQQQ Nasdaq-100 UCITS ETF, or iShares Nasdaq 100 UCITS ETF': 'Invesco EQQQ Nasdaq-100 UCITS ETF oder iShares Nasdaq 100 UCITS ETF', 'Vanguard FTSE Developed World UCITS ETF, or iShares Core MSCI World': 'Vanguard FTSE Developed World UCITS ETF oder iShares Core MSCI World', 'Vanguard FTSE Emerging Markets UCITS ETF, or iShares Core MSCI EM IMI': 'Vanguard FTSE Emerging Markets UCITS ETF oder iShares Core MSCI EM IMI'})

# Handy-Layout: Renditeranking, Fondssuche, Schnellzugriffe (etf_pages.py, web_src/etfm.*)
UI.update({'rank_h': 'Renditeranking', 'rank_all': 'Alle %(n)s Fonds anzeigen ▾', 'rank_less': 'Nur die ersten 10 anzeigen ▴', 'rank_note': 'Kursrendite ohne Dividenden. Tippen Sie auf einen Fonds, um seine Seite zu öffnen.', 'find_ph': 'Unter den {N} Fonds suchen: Ticker, Name oder Art', 'sort_big': 'Größte', 'sort_pe': 'Niedrigstes KGV', 'n_funds': '%n Fonds', 'no_fund': 'Kein Fonds passt zur Suche.', 'more': 'Mehr lesen ▾', 'less': 'Weniger anzeigen ▴', 'holds_all': 'Alle %(n)s Positionen anzeigen ▾', 'holds_less': 'Nur die ersten 10 anzeigen ▴', 'k_idea': 'Idee', 'k_val': 'Bewertung', 'k_ret': 'Rendite', 'k_hold': 'Bestände', 'k_sec': 'Abschnitte der Seite', 'k_find': 'Suchen', 'k_ph': 'Aktie oder ETF suchen', 'k_none': 'Keine Ergebnisse', 'l_y1': 'Letztes Jahr', 'l_avg': 'Ø pro Jahr', 'l_hold': 'Positionen', 'l_pe': 'KGV'})

# ---- Fonds 51-100 (Nov. 2026)
UI['focus_labels'].update({'US treasury bonds': 'US-Staatsanleihen', 'US corporate bonds': 'US-Unternehmensanleihen', 'high yield bonds': 'Hochzinsanleihen', 'municipal bonds': 'US-Kommunalanleihen', 'US covered call': 'Optionsprämien', 'consumer discretionary': 'Zyklischer Konsum', 'consumer staples': 'Basiskonsum', 'utilities': 'Versorger', 'materials': 'Grundstoffe', 'communication services': 'Kommunikation', 'biotech': 'Biotechnologie', 'aerospace and defense': 'Luftfahrt und Rüstung', 'banks': 'Banken', 'gold miners': 'Goldminen', 'oil and gas': 'Öl und Gas', 'cybersecurity': 'Cybersicherheit', 'clean energy': 'Saubere Energie', 'innovation': 'Innovation', 'US momentum': 'US-Momentum', 'US low volatility': 'US-Minimum-Volatilität', 'Japan': 'Japan', 'China': 'China', 'India': 'Indien', 'Brazil': 'Brasilien', 'silver': 'Silber', 'ether': 'Ether'})
_G = UI['groups']
_G[1][1].extend(['US momentum', 'US low volatility'])
_G[2][1].append('US covered call')
_G[4][1].extend(['Japan', 'China', 'India', 'Brazil'])
_G[5][1].extend(['consumer discretionary', 'consumer staples', 'utilities', 'materials', 'communication services', 'biotech', 'aerospace and defense', 'banks', 'gold miners', 'oil and gas', 'cybersecurity', 'clean energy', 'innovation'])
_G[6][1].extend(['US treasury bonds', 'US corporate bonds', 'high yield bonds', 'municipal bonds', 'silver', 'ether'])
T.update({'ACWI': ('Rund 2.500 große und mittelgroße Unternehmen aus Industrie- und Schwellenländern.',
          'Die Weltbörse nach Größe, mit fast zwei Dritteln USA: ein Weltdepot in einem Fonds, ähnlich wie VT, aber ohne die kleinen Werte. Das europäische Gegenstück ist der MSCI ACWI als UCITS-ETF.'),
 'ARKK': ('Die aktive, konzentrierte Wette von Cathie Wood auf disruptive Technologie.',
          'Hält wenige Dutzend von der Fondsmanagerin ausgewählte Unternehmen; stieg 2020 um mehr als 150 % und fiel danach um rund 75 % vom Hoch.'),
 'BIL': ('US-Schatzwechsel mit ein bis drei Monaten Laufzeit: der älteste Geldmarkt-ETF.',
         'Macht dasselbe wie SGOV mit etwas höherer Gebühr und schüttet die Zinsen monatlich aus. Die lange Historie macht ihn zum Maßstab für die Verzinsung von Dollar-Liquidität.'),
 'BSV': ('Kurze Anleihen des US-Staates und großer Unternehmen in einem günstigen Fonds.',
         'Anleihen mit einem bis fünf Jahren Laufzeit, zwei Drittel Staat und ein Drittel Unternehmen guter Bonität: ein vorsichtiger Schritt über Bargeld hinaus.'),
 'CIBR': ('Unternehmen für Cybersicherheit, von Software bis Netzwerktechnik.',
          'Enthält CrowdStrike, Palo Alto Networks und Cisco, mit Obergrenzen für die größten. Die Ausgaben für Sicherheit hielten selbst bei schwachen IT-Budgets stand.'),
 'EEM': ('Der ursprüngliche Schwellenländer-ETF, eher von Tradern als von Langfristanlegern genutzt.',
         'Kostet mehr als IEMG und VWO, die fast dieselben Unternehmen halten, ist aber am liquidesten für den Handel und für Optionen.'),
 'ETHA': ('Ether, die Währung des Ethereum-Netzwerks, in einem gewöhnlichen Depot.', 'Ether schwankt stärker als Bitcoin, und sein Wert hängt von der Aktivität im Ethereum-Netzwerk ab. In der EU gibt es dafür börsengehandelte Krypto-ETPs statt ETFs.'),
 'EWJ': ('Große und mittelgroße japanische Unternehmen.',
         'Unter anderem Toyota, Sony und Mitsubishi UFJ. Für Euro-Anleger hängt die Rendite vom japanischen Aktienmarkt und vom Yen ab, der seit Jahren schwach ist.'),
 'EWZ': ('Die größten Unternehmen Brasiliens: Rohstoffe, Banken und hohe Dividende.', 'Dominiert von Petrobras, Vale und Itaú; schwankt mit Rohstoffpreisen, dem Real und der brasilianischen Politik.'),
 'FBTC': ('Bitcoin, verwahrt von Fidelity selbst, der zweitgrößte Bitcoin-ETF.',
          'Fidelity verwahrt selbst, statt sich auf eine Kryptobörse zu verlassen; der Kurs folgt Bitcoin abzüglich der Gebühr.'),
 'FXI': ('Die 50 größten chinesischen Unternehmen mit Notierung in Hongkong.',
         'Konzentrierter als MCHI, mit viel Gewicht auf Banken, Internetplattformen und Staatskonzernen; wird genutzt, um auf Konjunkturprogramme oder Zollnachrichten zu setzen.'),
 'GDX': ('Goldminen: ein gehebelter Weg, Gold zu besitzen.', 'Weil ihre Kosten großteils fix sind, steigen ihre Gewinne schneller als der Goldpreis und fallen auch schneller.'),
 'GLDM': ('Physisches Gold mit niedrigerer Gebühr und niedrigerem Anteilspreis als GLD.',
          'Lagert Barren in London wie GLD, kostet aber viel weniger, was langfristig zählt; GLD bleibt wegen der Liquidität der Favorit großer Händler.'),
 'HYG': ('Hochzinsanleihen: mehr Ertrag dafür, riskanteren US-Unternehmen Geld zu leihen.',
         'Die Rendite ist hoch, weil manche Emittenten pleitegehen; in einer Rezession kann er fast so stark fallen wie Aktien, er ist also eher ein Zwitter aus Aktie und Anleihe als ein sicherer Hafen.'),
 'IBB': ('US-Biotech-Unternehmen nach Größe gewichtet, angeführt von den großen mit Produkten am Markt.', 'Amgen, Gilead und Vertex wiegen schwer, das macht ihn stabiler als XBI.'),
 'ICLN': ('Unternehmen für Solar-, Wind- und erneuerbare Energie aus aller Welt.',
          'Hängt stark von Zinsen und Subventionen ab: Schoss 2020 nach oben und verlor danach fast den ganzen Gewinn, als die Zinsen stiegen.'),
 'IEF': ('Zehnjährige US-Staatsanleihen: die klassische Absicherung eines Depots gegen eine Rezession.',
         'Der Kurs ändert sich um 7 bis 8 % je Prozentpunkt Bewegung der langen Zinsen. Er steigt meist, wenn Aktien aus Wachstumsangst fallen, und fällt, wenn die Inflation die Zinsen treibt, wie 2022.'),
 'INDA': ('Große und mittelgroße indische Unternehmen.',
          'HDFC Bank, Reliance, Infosys und ICICI Bank. Das schnelle Wachstum Indiens hat seiner Börse eine der höchsten Bewertungen der Welt beschert, was weniger Spielraum für Fehler lässt.'),
 'ITA': ('US-Rüstungslieferanten und Flugzeughersteller.', 'Verteidigungsbudgets bringen lange Verträge und Planbarkeit; das zivile Geschäft folgt dem Luftverkehr.'),
 'IXUS': ('Alle Börsen der Welt außer der US-Börse in einem günstigen Fonds.',
          'Das iShares-Gegenstück zu VXUS und die übliche Ergänzung eines US-Fonds in einem Depot aus zwei Fonds.'),
 'JEPI': ('Defensive US-Aktien plus Optionsprämien: hohe Monatsausschüttung, dafür begrenztes Kursplus.',
          'Verkauft Kaufoptionen und verwandelt einen Teil künftiger Kursgewinne in monatliche Erträge. Fällt in Korrekturen weniger, bleibt in starken Aufwärtsphasen aber weit zurück: Ein Teil der hohen Ausschüttung ist das eigene Kursplus des Anlegers, das zurückgezahlt wird.'),
 'JEPQ': ('Nasdaq-100-Aktien plus Optionsprämien: zweistellige Ausschüttung bei weniger Kursplus als QQQ.',
          'Die Ausschüttung ist hoch, weil Nasdaq-Optionen teuer sind, doch in einer starken Tech-Rally behält der Fonds nur einen Teil des Gewinns.'),
 'JNK': ('Hochzinsanleihen von State Street, der große Rivale von HYG.', 'Folgt HYG sehr eng; die Unterschiede kommen aus kleinen Indexregeln und den Gebühren.'),
 'KRE': ('US-Regionalbanken mit gleichem Gewicht: eine Wette auf die US-Binnenwirtschaft und die Zinskurve.',
         'Sie verdienen an der Differenz zwischen Einlagen- und Kreditzinsen und halten Gewerbeimmobilienkredite, reagieren also stark auf Zinsen und Kreditschocks, wie 2023 zeigte.'),
 'LQD': ('Der meistgehandelte Fonds für US-Unternehmensanleihen, mit langen Laufzeiten.',
         'Verbindet Unternehmenskredit und lange Duration, schwankt also stärker als VCIT. Institutionelle nutzen ihn, um den Kreditmarkt schnell zu handeln.'),
 'MCHI': ('Chinesische Unternehmen mit Notierung in Hongkong, den USA und auf dem Festland.',
          'Tencent, Alibaba, PDD und Meituan. Hängt ebenso vom chinesischen Wachstum, von der Politik Pekings und vom Verhältnis zu den USA ab wie von den Geschäftszahlen.'),
 'MTUM': ('US-Aktien mit den stärksten jüngsten Kursgewinnen, zweimal jährlich angepasst.',
          'Kauft die Unternehmen, die in sechs bis zwölf Monaten am stärksten gestiegen sind. Nutzt Trends gut, leidet aber, wenn die Marktführerschaft plötzlich wechselt.'),
 'MUB': ('Steuerfreie Anleihen von US-Bundesstaaten und -Städten.',
         'Die Zinsen sind von der US-Bundessteuer befreit, ein Vorteil nur für US-Steuerzahler; für Anleger in Europa ergibt die niedrigere Rendite wenig Sinn.'),
 'SCHB': ('Rund 2.500 US-Unternehmen, groß und klein, fast kostenlos.', 'Die Antwort von Schwab auf VTI, mit praktisch gleicher Rendite.'),
 'SCHF': ('Große Unternehmen aus Industrieländern außerhalb der USA.', 'Europa, Japan, Großbritannien, Kanada und Australien zu sehr niedrigen Kosten; Alternative zu VEA und IEFA mit fast gleicher Rendite.'),
 'SCHG': ('Große US-Wachstumsunternehmen mit einigen der niedrigsten Kosten.',
          'Dominiert von Big Tech, verhält sich fast wie VUG und QQQ, mit etwas mehr Breite als QQQ.'),
 'SGOV': ('US-Schatzwechsel unter drei Monaten: ein Bargeldersatz, der die kurzfristigen Zinsen zahlt.',
          'Hält nur Wechsel mit weniger als drei Monaten Restlaufzeit, der Kurs bewegt sich also kaum, und die Rendite ist der Leitzins der Federal Reserve minus eine kleine Gebühr. Senkt die Fed die Zinsen, sinkt die Rendite fast sofort.'),
 'SHV': ('US-Staatsanleihen unter einem Jahr: Liquidität mit etwas mehr Rendite.',
         'Hält Wechsel und Notes mit weniger als zwölf Monaten Restlaufzeit. Reagiert etwas stärker auf Zinsen als ein Dreimonatsfonds, bleibt aber ein Platz für Geld, das keinen Wert verlieren darf.'),
 'SHY': ('US-Staatsanleihen mit einem bis drei Jahren: wenig Risiko und ein kleiner Gewinn, wenn die Zinsen fallen.',
         'Der Kurs bewegt sich um etwa 2 % je Prozentpunkt Zinsänderung, gewinnt also etwas, wenn die Fed senkt, und verliert etwas, wenn sie erhöht.'),
 'SLV': ('Physisches Silber in Tresoren.', 'Silber ist teils Edelmetall und teils Industriemetall für Solarmodule und Elektronik, das macht es schwankungsanfälliger als Gold.'),
 'TIP': ('Inflationsgeschützte US-Staatsanleihen: Der Nennwert steigt mit dem Verbraucherpreisindex.',
         'Schlagen normale Anleihen, wenn die Inflation nach oben überrascht, fallen aber trotzdem, wenn die Realzinsen steigen, was 2022 viele überrascht hat. Das europäische Gegenstück sind inflationsindexierte Anleihen wie die Bundesanleihen mit Inflationsschutz.'),
 'TLT': ('US-Staatsanleihen mit über zwanzig Jahren Laufzeit: eine gehebelte Wette auf fallende Zinsen, ohne Kreditrisiko.',
         'Ein Prozentpunkt weniger bei den langen Zinsen lässt ihn um etwa 16 % steigen, ein Prozentpunkt mehr kostet genauso viel; deshalb verlor er zwischen 2020 und 2023 fast die Hälfte seines Werts.'),
 'USMV': ('US-Aktien, so kombiniert, dass sie möglichst wenig schwanken.',
          'Neigt zu Versorgern, Basiskonsum und Gesundheit; fällt in Korrekturen meist weniger und bleibt in starken Aufschwüngen zurück.'),
 'VCIT': ('Fünf- bis zehnjährige Anleihen großer US-Unternehmen: mehr Rendite als Staatsanleihen, mit etwas Kreditrisiko.',
          'Man erhält einen Aufschlag auf Staatsanleihen dafür, Unternehmen Geld zu leihen; in einer Rezession weitet sich dieser Aufschlag, und der Fonds fällt, selbst wenn Staatsanleihen steigen.'),
 'VCSH': ('Kurze Anleihen großer US-Unternehmen: etwas mehr Rendite als Bargeld.',
          'Die kurzen Laufzeiten halten Zins- und Ausfallrisiko klein, in normalen Zeiten verhält er sich also wie ein Dollar-Geldmarktfonds mit etwas mehr Rendite.'),
 'VGIT': ('US-Staatsanleihen mit drei bis zehn Jahren, zu den niedrigen Kosten von Vanguard.',
          'Liegt in der Mitte der Zinskurve, zwischen SHY und IEF bei der Zinsempfindlichkeit, und ist ein üblicher Kern für alle, die Staatsanleihen ohne die Schwankungen langer Laufzeiten wollen.'),
 'VTEB': ('Der günstige Korb steuerfreier US-Kommunalanleihen von Vanguard.',
          'Wie MUB nur sinnvoll für US-Steuerzahler, für die steuerfreie Erträge mehr wert sind als die höhere Rendite einer steuerpflichtigen Anleihe.'),
 'XBI': ('US-Biotech-Unternehmen mit gleichem Gewicht: eine Wette auf die kleinen Werte und auf Übernahmen.',
         'Kleine Unternehmen in der klinischen Phase wiegen so viel wie die großen, deshalb kann er in einem Jahr je nach Zinsen, Studienergebnissen und Übernahmen um 50 % steigen oder fallen.'),
 'XLB': ('Chemie, Industriegase, Metalle und Verpackungen aus dem S&P 500.',
         'Die Gewinne folgen der Industrienachfrage und den Rohstoffpreisen, er ist also zyklisch und läuft meist zu Beginn einer Erholung besser.'),
 'XLC': ('Meta, Alphabet, Netflix und die Telekomkonzerne des S&P 500.', 'Meta und Alphabet machen fast die Hälfte des Fonds aus, die Rendite hängt also vor allem an der Onlinewerbung.'),
 'XLP': ('Lebensmittel, Getränke, Haushaltswaren und Supermärkte: was man kauft, wenn die Wirtschaft Sorgen macht.',
         'Die Nachfrage bleibt in der Rezession stabil, das macht ihn defensiv, obwohl geringes Wachstum und der Druck durch Handelsmarken und Abnehmspritzen ihn gebremst haben.'),
 'XLRE': ('Die Immobilienwerte des S&P 500: Funktürme, Lagerhallen, Rechenzentren und Wohnungen.',
          'REITs schütten fast ihren ganzen Gewinn aus und reagieren auf Zinsen, der Fonds steigt also meist, wenn die Anleiherenditen fallen.'),
 'XLU': ('Strom- und Gasversorger: Dividenden, Regulierung und jetzt der Strombedarf der KI.',
         'Früher ein Ertragssektor, ähnlich einer Anleihe; heute zum Teil eine Wette auf künstliche Intelligenz, weil Rechenzentren riesige Mengen Strom brauchen.'),
 'XLY': ('Der zyklische Konsum im S&P 500, dominiert von Amazon und Tesla.',
         'Enthält Händler, Autobauer, Restaurants und Hotels, doch Amazon und Tesla wiegen so schwer, dass er sich eher wie ein Big-Tech-Fonds verhält als wie eine Wette auf die Verbraucher.'),
 'XOP': ('US-Öl- und Gasförderer mit gleichem Gewicht: fast eine direkte Wette auf den Ölpreis.',
         'Die kleinen Schieferölfirmen wiegen so viel wie die großen, er bewegt sich also stärker mit dem Öl als XLE, der von Exxon und Chevron dominiert wird.')})
UCITS.update({'A UCITS 0-5 year USD corporate bond ETF': 'ein UCITS-ETF auf Dollar-Unternehmensanleihen mit 0 bis 5 Jahren',
 'A UCITS 1-3 year US Treasury ETF': 'ein UCITS-ETF auf US-Staatsanleihen mit 1 bis 3 Jahren',
 'A UCITS 20+ year US Treasury ETF': 'ein UCITS-ETF auf US-Staatsanleihen mit über 20 Jahren',
 'A UCITS 7-10 year US Treasury ETF': 'ein UCITS-ETF auf US-Staatsanleihen mit 7 bis 10 Jahren',
 'A UCITS ETF tracking the whole US market': 'ein UCITS-ETF auf den gesamten US-Markt',
 'A UCITS US TIPS ETF': 'ein UCITS-ETF auf inflationsgeschützte US-Staatsanleihen',
 'A UCITS US Treasury ETF': 'ein UCITS-ETF auf US-Staatsanleihen',
 'A UCITS US communication services sector ETF': 'ein UCITS-ETF auf den US-Kommunikationssektor',
 'A UCITS US consumer discretionary sector ETF': 'ein UCITS-ETF auf den zyklischen US-Konsum',
 'A UCITS US consumer staples sector ETF': 'ein UCITS-ETF auf den US-Basiskonsum',
 'A UCITS US materials sector ETF': 'ein UCITS-ETF auf den US-Grundstoffsektor',
 'A UCITS US property ETF': 'ein UCITS-ETF auf US-Immobilien',
 'A UCITS US utilities sector ETF': 'ein UCITS-ETF auf US-Versorger',
 'A UCITS USD corporate bond ETF': 'ein UCITS-ETF auf Dollar-Unternehmensanleihen',
 'A UCITS USD high yield bond ETF': 'ein UCITS-ETF auf Dollar-Hochzinsanleihen',
 'A UCITS aerospace and defence ETF': 'ein UCITS-ETF auf Luftfahrt und Rüstung',
 'A UCITS cybersecurity ETF': 'ein UCITS-ETF auf Cybersicherheit',
 'A UCITS developed-markets ex-US ETF': 'ein UCITS-ETF auf Industrieländer ohne USA',
 'A UCITS ex-US world ETF': 'ein UCITS-ETF auf die Welt ohne USA',
 'A UCITS short-term US aggregate bond ETF': 'ein UCITS-ETF auf kurzlaufende US-Anleihen',
 'A UCITS ultrashort US Treasury ETF': 'ein UCITS-ETF auf sehr kurz laufende US-Schatzwechsel',
 'Choose one matching the 3-10 year maturity range.': 'Wählen Sie einen mit Laufzeiten von 3 bis 10 Jahren.',
 'European bank ETFs hold European banks.': 'Europäische Banken-ETFs halten europäische Banken.',
 'European biotech ETFs are weighted by size.': 'Europäische Biotech-ETFs gewichten nach Größe.',
 'European energy ETFs are dominated by the integrated majors.': 'Europäische Energie-ETFs werden von den großen integrierten Ölkonzernen dominiert.',
 'European funds mix in European defence companies.': 'Europäische Fonds enthalten auch europäische Rüstungsunternehmen.',
 'European investors use physically backed gold ETCs': 'europäische Anleger nutzen physisch besicherte Gold-ETCs',
 'European investors use physically backed silver ETCs': 'europäische Anleger nutzen physisch besicherte Silber-ETCs',
 'Few European funds exclude the US; most investors use a world fund instead.': 'Wenige europäische Fonds schließen die USA aus; die meisten Anleger nehmen stattdessen einen Weltfonds.',
 'Few European funds hold small US companies; an S&P 500 fund is the usual substitute.': 'Wenige europäische Fonds halten kleine US-Unternehmen; ein S&P-500-Fonds ist der übliche Ersatz.',
 'No UCITS equivalent': 'kein UCITS-Gegenstück',
 'No exact UCITS equivalent': 'kein exaktes UCITS-Gegenstück',
 'Several providers offer 0-1 or 0-3 month Treasury funds in Europe.': 'Mehrere Anbieter haben in Europa Fonds auf Schatzwechsel mit 0 bis 1 oder 0 bis 3 Monaten.',
 'Several providers offer one.': 'Mehrere Anbieter haben einen.',
 'The tax exemption only benefits US taxpayers.': 'Die Steuerbefreiung nützt nur US-Steuerzahlern.',
 'UCITS rules do not permit a single-commodity fund.': 'Die UCITS-Regeln erlauben keinen Fonds auf einen einzelnen Rohstoff.',
 'iShares and others list one in Europe.': 'iShares und andere haben einen in Europa notiert.'})

# ---- Vergleiche und „Welche ETFs halten"
UI.update({
    'c_title': '%(a)s vs. %(b)s: Welcher ETF ist besser? Rendite, KGV und Überschneidung',
    'c_h1': '%(a)s vs. %(b)s', 'c_crumb': '%(a)s vs. %(b)s',
    'c_sub': 'Rendite, Bewertung der Bestände und wie stark sie sich überschneiden, direkt nebeneinander.',
    'c_what': 'Was jeder Fonds ist', 'c_side': 'Im direkten Vergleich', 'c_says': 'Was die Zahlen sagen',
    'c_shared': 'Die größten gemeinsamen Positionen', 'c_issuer': 'Anbieter', 'c_index': 'Index',
    'c_with': '%(t)s vergleichen mit',
    'v_ret': '%(w)s hat in den letzten 12 Monaten mehr gebracht: %(x)s gegenüber %(y)s.',
    'v_pe': '%(w)s hält nach unserem KGV günstigere Unternehmen: %(x)s gegenüber %(y)s.',
    'v_ov': '%(ov)s von %(a)s, gemessen am Gewicht der größten Positionen, steckt in Unternehmen, die auch %(b)s hält; beide zu besitzen streut also weniger, als es scheint.',
    'v_noov': '%(a)s und %(b)s haben keine der größten Positionen gemeinsam und erfüllen im Depot also unterschiedliche Aufgaben.',
    'hold_slug': 'welche-etfs-halten-%s',
    'h_title': 'Welche ETFs halten %(name)s (%(t)s)? Gewichte und Rendite',
    'h_h1': 'Welche ETFs halten Aktien von %(name)s?',
    'h_lead': '%(n)s der %(N)s ETFs, die wir abdecken, haben %(name)s unter ihren größten Positionen.',
    'h_top': 'Das höchste Gewicht hat sie in %(f)s, wo %(name)s %(w)s des Fonds ausmacht.',
    'h_stock': 'Unsere vollständige Analyse zu %(name)s lesen ›',
    'h_note': 'Laut dem von jedem Fonds veröffentlichten Bestand; geprüft werden nur die größten Positionen jedes Fonds, kleine erscheinen daher nicht.',
})

# ---- Fonds 101-150 (Nov. 2026)
UI['focus_labels'].update({'software': 'Software', 'leveraged': 'Gehebelt (3x täglich)', 'uranium': 'Uran', 'copper miners': 'Kupferminen', 'lithium and batteries': 'Lithium und Batterien', 'solar': 'Solar', 'infrastructure': 'Infrastruktur', 'robotics and AI': 'Robotik und KI', 'airlines': 'Fluggesellschaften', 'China internet': 'China-Internet', 'homebuilders': 'Hausbauer', 'metals and mining': 'Metalle und Bergbau', 'Germany': 'Deutschland', 'Taiwan': 'Taiwan', 'South Korea': 'Südkorea', 'United Kingdom': 'Großbritannien', 'emerging market bonds': 'Schwellenländeranleihen'})
_G = UI['groups']
_G[4][1].extend(['Germany', 'United Kingdom', 'Taiwan', 'South Korea'])
_G[5][1].extend(['software', 'robotics and AI', 'infrastructure', 'homebuilders', 'metals and mining', 'copper miners', 'uranium', 'lithium and batteries', 'solar', 'airlines', 'China internet', 'leveraged'])
_G[6][1].append('emerging market bonds')
UCITS.update({'A UCITS ETF on the same theme': 'ein UCITS-ETF zum selben Thema',
 'A UCITS ETF tracking the same country index': 'ein UCITS-ETF auf denselben Länderindex',
 'European leveraged products are ETPs, not UCITS funds.': 'In Europa sind gehebelte Produkte ETPs, keine UCITS-Fonds.',
 'A UCITS US Treasury ETF': 'ein UCITS-ETF auf US-Staatsanleihen',
 'A UCITS USD emerging-market bond ETF': 'ein UCITS-ETF auf Schwellenländeranleihen in Dollar'})
T.update({
 'DVY': ('Rund hundert US-Unternehmen mit hoher Dividende, gewichtet nach der gezahlten Dividende statt nach Größe.',
         'Wählt Unternehmen mit langer Dividendenhistorie und gewichtet sie nach der Dividende, was ihn zu Versorgern, Banken und Tabak neigen lässt. Bringt mehr Ertrag als der Markt, hat aber kaum Technologie und fällt daher weit zurück, wenn Wachstumswerte führen.'),
 'SDY': ('US-Unternehmen, die ihre Dividende seit mindestens zwanzig Jahren in Folge erhöhen, gewichtet nach Dividendenrendite.',
         'Sucht im gesamten S&P 1500, schließt also mittlere und kleine Werte ein, und gibt den renditestärksten mehr Gewicht. Die Zwanzig-Jahres-Regel lässt junge Unternehmen außen vor und jedes, das in einer Krise die Dividende gekürzt hat.'),
 'NOBL': ('Die S&P-500-Unternehmen, die ihre Dividende seit mindestens 25 Jahren in Folge erhöhen, gleich gewichtet.',
          'Hält die gut sechzig „Dividendenaristokraten" mit gleichem Gewicht und gleicht vierteljährlich aus. Das lässt ihn zu Industrie und Basiskonsum neigen und entfernt ihn von den Tech-Giganten, die den Index dominieren.'),
 'HDV': ('Fünfundsiebzig US-Unternehmen mit hoher Dividende, gefiltert nach finanzieller Stärke.',
         'Nimmt Aktien mit hoher Dividendenrendite und behält nur die, die Morningstar als finanziell solide mit dauerhafter Dividende einstuft. Konzentriert auf Energie, Gesundheit und Basiskonsum, mit wenigen Riesen wie Exxon und Johnson & Johnson, die schwer wiegen.'),
 'SPYD': ('Die achtzig S&P-500-Unternehmen mit der höchsten Dividendenrendite, gleich gewichtet.',
          'Sortiert den S&P 500 nur nach Dividendenrendite und hält die ersten achtzig zu gleichen Teilen. Einen Qualitätsfilter gibt es nicht, also wiegen REITs, Versorger und Unternehmen schwer, deren hohe Rendite aus einem gefallenen Kurs stammt.'),
 'DIVO': ('Rund 25 große Dividendenzahler, auf einige werden Kaufoptionen verkauft, um Ertrag hinzuzufügen.',
          'Die Fondsmanager wählen solide Dividendenwerte und verkaufen gezielt kurzlaufende Kaufoptionen, nicht auf den ganzen Fonds, er behält also mehr Kursplus als ein Fonds, der auf alles Optionen verkauft. Der Ertrag kommt aus Dividenden und Prämien.'),
 'QYLD': ('Der Nasdaq-100 mit monatlich verkauften Kaufoptionen „am Geld": hohe Monatsausschüttung gegen fast das ganze Kursplus.',
          'Hält den Nasdaq-100 und verkauft jeden Monat eine Kaufoption auf den ganzen Index zum aktuellen Kurs. Die Prämie finanziert eine große Ausschüttung, doch jeder Anstieg ist gedeckelt, während jeder Rückgang voll durchschlägt, deshalb ist der Kurs im Lauf der Zeit gesunken.'),
 'QQQM': ('Derselbe Nasdaq-100 wie QQQ, in einer günstigeren Variante zum langfristigen Halten.',
          'Hält genau dasselbe wie QQQ mit einer niedrigeren jährlichen Gebühr. QQQ bleibt wegen der enormen Liquidität die Wahl für Trading und Optionen; für Kaufen und Halten kostet QQQM weniger.'),
 'SPYG': ('Die Wachstumshälfte des S&P 500 zu sehr niedrigen Kosten.',
          'S&P teilt den Index nach Umsatz- und Gewinnwachstum und Momentum, und dieser Fonds hält die Wachstumsseite. In der Praxis dominieren dieselben Tech-Giganten wie im QQQ.'),
 'VONG': ('Der Russell 1000 Growth, derselbe Index wie IWF, mit niedrigerer Gebühr.',
          'Hält die Wachstumshälfte der tausend größten US-Unternehmen, ausgewählt nach Kurs-Buchwert und erwartetem Wachstum. Ein günstigerer Weg, das zu besitzen, was IWF hält.'),
 'IGV': ('Softwareunternehmen aus Nordamerika, von Microsoft und Oracle bis zu kleineren Cloud-Namen.',
         'Hält nur Softwarehersteller, keine Chips und keine Hardware, und begrenzt die größten auf ein Zehntel des Fonds. Er ist der Fonds, der am stärksten von der Frage abhängt, ob KI Softwareunternehmen hilft oder schadet.'),
 'FTEC': ('US-Technologieunternehmen aller Größen mit einer der niedrigsten Gebühren der Branche.',
          'Deckt dasselbe ab wie VGT, kleine Werte inklusive, mit Obergrenzen, die die größten Namen innerhalb der Grenzen eines diversifizierten Fonds halten. Der Unterschied zu VGT liegt vor allem in Kosten und Broker.'),
 'TQQQ': ('Die dreifache Tagesbewegung des Nasdaq-100: ein Werkzeug zum Handeln, nicht zum Halten.',
          'Nutzt Swaps und Futures, um das Dreifache der Tagesentwicklung des Nasdaq-100 zu liefern, und wird jede Nacht neu angepasst. Über Wochen kann das Ergebnis weit vom Dreifachen des Index abweichen, und in Seitwärts- oder Abwärtsmärkten vernichtet diese Anpassung Wert; ein Indexrückgang um 33 % an einem Tag würde ihn auslöschen.'),
 'SOXL': ('Die dreifache Tagesbewegung eines Halbleiterindex: einer der schwankungsstärksten Fonds überhaupt.',
          'Nutzt Swaps, um das Dreifache der Tagesrendite von dreißig großen Chipunternehmen zu liefern, und wird täglich angepasst. Chips schwanken schon stark, mit dem Dreifachen sind große Verluste häufig; gemacht ist er für Tage, nicht für Jahre.'),
 'SPYV': ('Die günstige Value-Hälfte des S&P 500: Banken, Gesundheit, Energie und Industrie.',
          'Hält die S&P-500-Unternehmen, die nach Buchwert, Gewinn und Umsatz günstig sind. Berkshire Hathaway, JPMorgan und Exxon sind typische Positionen, und er bleibt zurück, wenn wenige Tech-Giganten den Markt ziehen.'),
 'VOE': ('Mittelgroße US-Unternehmen mit niedriger Bewertung: Versicherer, Versorger, Industriezulieferer.',
         'Nimmt die Value-Hälfte des Midcap-Marktes nach CRSP. Diese Unternehmen tauchen selten in den Nachrichten auf, und deshalb waren sie historisch günstig.'),
 'VBR': ('Günstige kleine US-Unternehmen: die Ecke, in der die Value-Prämie zuerst gemessen wurde.',
         'Hält rund 850 kleine Unternehmen, die nach mehreren Maßstäben günstig sind. Breit und günstig, schließt aber Verlustbringer nicht aus, und das ist der große Unterschied zu AVUV.'),
 'AVUV': ('Günstige und profitable kleine US-Unternehmen, nach Regeln statt nach Wetten ausgewählt.',
          'Avantis filtert kleine Unternehmen nach niedrigem Kurs-Buchwert und hoher Profitabilität und handelt geduldig. Der Profitabilitätsfilter lässt die Werte außen vor, die aus gutem Grund billig sind und einfache Value-Fonds belasten.'),
 'IWR': ('Rund 800 mittelgroße US-Unternehmen, Nummer 201 bis 1.000 nach Größe.',
         'Hält den kleineren Teil des Russell 1000 ohne die zweihundert größten. Mittelgroße Werte haben die riskanteste Phase hinter sich, aber noch Raum zum Wachsen.'),
 'IWO': ('Die Wachstumshälfte des Russell 2000: Biotech, Software und junge Industrieunternehmen.',
         'Viele der Unternehmen schreiben noch keine Gewinne, das macht ihn sehr empfindlich für Zinsen und Risikobereitschaft. Anstiege kommen in Schüben, Rückgänge können tief sein.'),
 'IWN': ('Die Value-Hälfte des Russell 2000: Regionalbanken, Immobilien und Energie.',
         'Hält die günstigsten Nebenwerte des Russell 2000. Regionalbanken wiegen schwer, er leidet also bei Bankenstress und läuft gut, wenn die Wirtschaft anzieht.'),
 'MDY': ('Der S&P MidCap 400 im ältesten Midcap-ETF.',
         'Hält dieselben 400 Unternehmen wie IJH, der viel weniger kostet. MDY bleibt wegen Liquidität und Optionsmarkt bei Tradern beliebt.'),
 'SCHA': ('Rund 1.700 kleine US-Unternehmen mit sehr niedriger Gebühr.',
          'Hält den Nebenwerteteil des Dow-Jones-Gesamtmarktindex, breiter als der Russell 2000. Filtert nicht nach Gewinn, trägt also denselben schwachen Schwanz wie IWM.'),
 'VXF': ('Alle US-Aktien außer denen im S&P 500: die mittleren und kleinen Werte, die ein Depot vervollständigen.',
         'Hält rund 3.500 Unternehmen außerhalb des S&P 500, gewichtet nach Größe. Zusammen mit VOO im Verhältnis vier zu eins bildet er den ganzen Markt nach.'),
 'VDE': ('US-Öl- und Gasunternehmen aller Größen, günstig.',
         'Hält Exxon und Chevron mit begrenztem Gewicht und einen langen Schwanz aus Förderern, Raffinerien und Dienstleistern. Im Vergleich zu XLE mehr kleine Werte und weniger Gewicht auf den zwei Riesen.'),
 'VFH': ('US-Banken, Versicherer, Zahlungsnetzwerke und Vermögensverwalter aller Größen.',
         'Deckt dasselbe ab wie XLF, fügt aber Hunderte kleine Banken und Versicherer hinzu. Gewinnt, wenn Margen und Kredit gut laufen, und leidet bei Kreditschocks.'),
 'VIS': ('US-Industrie: Luftfahrt, Maschinen, Eisenbahnen, Baustoffe.',
         'Hält rund 400 Industrieunternehmen, viel mehr als XLI, hängt also weniger an wenigen Riesen wie GE Aerospace und Caterpillar. Folgt dem Konjunkturzyklus und den Investitionen der Unternehmen.'),
 'VCR': ('Was Amerikaner kaufen, wenn Geld übrig ist: Autos, Handel, Restaurants, Reisen.',
         'Amazon und Tesla wiegen schwer, mit Obergrenzen, gefolgt von Baumarktketten, Restaurants und Hotels. Eine Wette auf die Kaufkraft der US-Verbraucher.'),
 'VDC': ('Güter des täglichen Bedarfs: Lebensmittel, Haushalt, Getränke und Tabak.',
         'Walmart, Costco und Procter & Gamble führen einen Sektor an, dessen Umsätze sich in Rezessionen kaum bewegen. Fällt in Abschwüngen meist weniger als der Markt und bleibt in Euphoriephasen zurück.'),
 'VPU': ('US-Strom-, Gas- und Wasserversorger.',
         'Regulierte Unternehmen mit stabilen Dividenden, heute auch eine Wette auf den Strom, den Rechenzentren brauchen. Weil sie viel Schulden haben und viel ausschütten, bewegt sich der Kurs gegenläufig zu den Zinsen.'),
 'URA': ('Uranminen und Kernbrennstoffunternehmen aus aller Welt.',
         'Cameco und Kazatomprom führen, neben Trusts mit physischem Uran und Reaktorlieferanten. Folgt dem Uranpreis und der politischen Stimmung gegenüber der Kernkraft, die sich stark drehen kann.'),
 'COPX': ('Die Kupferminen der Welt.',
          'Hält Minen aus Kanada, Australien, China und den USA, etwa Freeport-McMoRan. Minenbetreiber verstärken den Kupferpreis, der vom Bau in China, von Stromnetzen und Elektroautos abhängt.'),
 'LIT': ('Lithiumförderer und Batteriehersteller, von Albemarle bis zu chinesischen Zellproduzenten.',
         'Umfasst die Batteriekette vom Rohlithium bis zur fertigen Zelle, mit viel Gewicht auf China. Folgt dem Lithiumpreis und der Nachfrage nach Elektroautos, die sehr tiefe Auf- und Abschwünge erlebt haben.'),
 'TAN': ('Hersteller von Solarmodulen, Installateure und Wechselrichterunternehmen.',
         'Hält First Solar, Enphase und andere Solarunternehmen der Welt. Der Sektor reagiert stark auf Zinsen, Subventionen und den Preis chinesischer Module, was ihn zu einem der schwankungsstärksten Aktienfonds gemacht hat.'),
 'PAVE': ('US-Unternehmen, die Straßen, Stromnetze und Fabriken bauen und beliefern.',
          'Hält Bauunternehmen, Maschinenbauer, Stahl- und Elektrozulieferer, die von öffentlichen Infrastrukturausgaben und neuen Fabriken profitieren. Verhält sich wie ein konzentrierter Industriefonds.'),
 'BOTZ': ('Unternehmen für Robotik, Automatisierung und KI-Hardware aus aller Welt.',
          'Nvidia steht neben japanischen Industrierobotern und Herstellern von Operationsrobotern. Ein engerer und globalerer Blick auf Automatisierung als ein gewöhnlicher Technologiefonds.'),
 'JETS': ('Fluggesellschaften aus den USA und dem Ausland, dazu Flugzeughersteller und Flughäfen.',
          'Die großen US-Airlines dominieren, ausländische Gesellschaften und Reiseunternehmen wiegen weniger. Airlines hängen am Kerosinpreis und an der Konjunktur und mussten schon mehrfach gerettet werden: ein zyklischer Fonds zum Handeln.'),
 'KWEB': ('Die Internetriesen Chinas: Tencent, Alibaba, PDD, Meituan und andere.',
          'Hält chinesische Internetunternehmen mit Notierung in Hongkong und New York. Verlor ab 2021 durch die Regulierungsoffensive Pekings den größten Teil seines Werts und bewegt sich stark mit der Politik zwischen China und den USA.'),
 'ITB': ('US-Hausbauer und ihre Zulieferer.',
         'D.R. Horton, Lennar und PulteGroup wiegen schwer, gefolgt von Baustoffherstellern und Baumärkten. Bewegt sich mehr mit den Hypothekenzinsen als mit allem anderen.'),
 'XME': ('US-Unternehmen für Stahl, Aluminium, Kohle, Gold und Kupfer, fast gleich gewichtet.',
         'Mit gleichen Gewichten zählen kleine Produzenten so viel wie große, er ist also eine breite Wette auf Metallpreise in den USA. Springt oft bei Zöllen und Infrastrukturausgaben und fällt in Abschwüngen stark.'),
 'EWG': ('Die großen Unternehmen Deutschlands: SAP, Siemens, Allianz, Deutsche Telekom.',
         'Hält rund sechzig deutsche Unternehmen mit viel Gewicht auf Industrie, Finanzwerten und Software. Für Anleger in Deutschland ist das der eigene Heimatmarkt; als US-Fonds ist er hier aber nicht kaufbar, ein DAX- oder MSCI-Germany-ETF aus Europa deckt dasselbe ab.'),
 'EWT': ('Die Börse Taiwans, die vor allem aus TSMC und seiner Lieferkette besteht.',
         'TSMC ist die größte Position, mit begrenztem Gewicht, gefolgt von MediaTek und Elektronikherstellern. Praktisch eine Wette auf den weltweiten Chipzyklus plus das geopolitische Risiko Taiwans.'),
 'EWY': ('Die großen Unternehmen Südkoreas, angeführt von Samsung Electronics und SK Hynix.',
         'Speicherchips wiegen schwer, gefolgt von Autobauern, Banken und Batterien. Koreanische Aktien werden seit Langem mit Abschlag gehandelt, wegen der Familienkonglomerate und der geringen Ausschüttungen an Aktionäre.'),
 'EWU': ('Die großen britischen Unternehmen: Shell, AstraZeneca, HSBC, Unilever.',
         'Die britische Börse ist schwer in Öl, Banken, Bergbau und Basiskonsum und leicht in Technologie, sie wird also günstig gehandelt und zahlt hohe Dividenden.'),
 'SPDW': ('Tausende Unternehmen aus Europa, Japan, Kanada und Australien mit sehr niedriger Gebühr.',
          'Deckt die Industrieländer außerhalb der USA ab, einschließlich kleiner Werte und Kanada. Eine günstige Alternative zu VEA und SCHF mit fast denselben Unternehmen.'),
 'VGLT': ('US-Staatsanleihen mit über zehn Jahren, mit niedrigerer Gebühr als TLT.',
          'Hält lange Staatsanleihen mit etwas kürzerer Durchschnittslaufzeit als TLT, ist also etwas weniger zinsempfindlich. Steigt, wenn die langen Zinsen fallen, und fällt, wenn sie steigen.'),
 'GOVT': ('Alle Laufzeiten von US-Staatsanleihen in einem Fonds.',
          'Hält den US-Staatsanleihenmarkt von einem bis dreißig Jahren, gewichtet nach Emissionsvolumen. Liegt beim Risiko zwischen kurzen und langen Fonds und ist ein einfacher Weg, die Zinskurve der USA zu besitzen.'),
 'EMB': ('Dollar-Anleihen von Schwellenländerstaaten und ihren Staatsunternehmen.',
         'Hält Anleihen von Ländern wie Mexiko, Saudi-Arabien, Indonesien und Brasilien, zahlbar in Dollar, also ohne Währungsrisiko gegenüber dem Dollar. Bringt wegen des Ausfallrisikos mehr als US-Staatsanleihen und leidet, wenn Dollar und US-Zinsen gemeinsam steigen.'),
 'SCHP': ('Inflationsgeschützte US-Staatsanleihen (TIPS) mit sehr niedriger Gebühr.',
          'Der Nennwert jeder Anleihe steigt mit den Verbraucherpreisen, er schützt also vor Inflationsüberraschungen. Trotzdem fällt er, wenn die Realzinsen steigen, wie 2022.'),
 'VGSH': ('US-Staatsanleihen mit einem bis drei Jahren, der günstige Zwilling von SHY.',
          'Hält kurze Staatsanleihen, der Kurs bewegt sich also kaum mit den Zinsen. Ein Schritt über Bargeld hinaus für Geld, das in ein oder zwei Jahren gebraucht werden könnte.'),
})
