# -*- coding: utf-8 -*-
"""Los 50 ETF más grandes del mundo, descritos en español para bolsacondor.com.

Escrito en español, no traducido: el lector está en Madrid, en Ciudad de México o en Buenos Aires, y
la pregunta que trae no es la misma. Al europeo le van a rechazar la orden y necesita saber por qué;
al mexicano no, porque los mismos fondos cotizan en el SIC de la Bolsa Mexicana; al argentino
tampoco, porque los grandes ETF estadounidenses tienen CEDEAR.

Las cifras no están aquí. Precio, rentabilidad, cartera y ratios se calculan cada día en etf_data.py.
"""

UI = dict(
    home='Inicio', etfs='ETF', other='Otros', fundcol='Fondo',
    ps='Precio / ventas', growth='Crecimiento de ventas, último año',
    margin='Margen neto', score='Nuestra puntuación media',
    no_pe_h='Por qué aquí no hay PER',
    in_europe='Si estás en Europa:',
    more_exp='más caro', cheaper='más barato',
    shariah='Alternativa conforme a la sharía',
    vs_sp='El S&P 500 en la misma medida está a %(sp)s veces, así que este fondo es un %(diff)s %(dir)s.',
    priips='%(fund)s está domiciliado en Estados Unidos. Los fondos estadounidenses no publican el '
           'documento de datos fundamentales que exige la norma europea, así que un inversor '
           'minorista de la Unión Europea o del Reino Unido no puede comprarlo: la orden se rechaza, '
           'con el bróker que sea. En buena parte de Latinoamérica, Oriente Medio, Turquía y Asia sí '
           'se puede comprar a través de un bróker internacional, con las reglas locales de cada país.',
    note_tbl='La columna del PER se calcula con las empresas que tiene cada fondo, ponderadas por los '
             'pesos del propio fondo y con las mismas cifras que nuestras fichas de acciones. Queda '
             'en blanco cuando el fondo no tiene acciones y cuando está formado sobre todo por '
             'empresas cotizadas fuera de Estados Unidos, que no cubrimos.',
    i_title='Los 50 ETF más grandes: cartera, PER y rentabilidad',
    i_desc='Los cincuenta ETF más grandes del mundo con su cartera, sus pesos y su rentabilidad a un '
           'año, y un PER calculado con las empresas que cada uno tiene realmente dentro.',
    d_title='ETF %(t)s: cartera, PER y rentabilidad',
    d_desc='%(name)s (%(t)s): cartera, pesos y rentabilidad, con un PER calculado a partir de las '
           'empresas que tiene dentro. %(idea)s',
    h1='Los 50 ETF más grandes del mundo',
    sub='Cartera, pesos y valoración · actualizado',
    lead='Los cincuenta fondos cotizados más grandes del mundo, con para qué sirve cada uno, qué '
         'tiene dentro y cuánto valen las empresas que lo componen.',
    intro='El PER de estas páginas no lo publica el fondo. Cada posición se cruza con nuestra propia '
          'ficha de esa empresa y las cifras se ponderan con los pesos del propio fondo, así que el '
          'PER de un ETF aquí sale de los mismos informes a la SEC que cualquier ficha de acción de '
          'esta web — y se puede pinchar en cualquier posición para leer sobre la empresa.',
    idea='La idea',
    ret='Rentabilidad',
    fund='Cuánto valen las empresas que tiene dentro',
    holds='Mayores posiciones',
    made='De qué está hecho',
    where='¿Puedes comprarlo donde vives?',
    faq='Preguntas frecuentes',
    company='Empresa',
    weight='Peso',
    all50='Los 50 fondos, uno al lado del otro',
    y1='1 año', y3='3 años', ytd='En el año', m1='Último mes', m3='3 meses', y5='5 años',
    price='Precio', pe='PER', holdings='Posiciones',
    chartcap='Rentabilidad del último año, todos los fondos de esta página. Pulsa una barra para abrirlo.',
    linecap='Precio desde %(year)s. No incluye dividendos.',
    note_ret='Solo rentabilidad por precio. Un fondo que reparte dividendos rindió más que esto; '
             'uno que los acumula, no.',
    note_pe='No lo tomamos del fondo. Cada posición se cruza con nuestra ficha de esa empresa y las '
            'cifras se ponderan con los pesos del propio fondo, de modo que salen de los mismos '
            'informes que el resto de la web. Cubrimos el %(cov)s del fondo por peso (%(n)s de %(total)s posiciones).',
    note_holds='Las %(n)d mayores de %(total)s posiciones, de la cartera publicada por el fondo%(asof)s. Los nombres '
               'que enlazan tienen ficha completa en esta web.',
    note_ctry='La situación general, no un consejo sobre un bróker concreto ni sobre impuestos. '
              'Cuando un fondo no se puede comprar, lo impide la norma europea del documento de '
              'datos fundamentales, no el bróker.',
    no_pe_bond='Este fondo no tiene acciones de empresas, así que no hay beneficios entre los que '
               'dividir el precio. Lo que importa en él es a quién presta y a qué plazo: calidad '
               'crediticia y duración en un fondo de bonos, y el precio del propio activo en el oro '
               'o el bitcoin. Tiene %(n)s posiciones.',
    no_pe_thin='Nuestros datos de empresas cubren compañías cotizadas en Estados Unidos. Este fondo '
               'tiene %(n)s posiciones y solo el %(cov)s de su peso está en empresas que cubrimos, así que un '
               'PER calculado con esa parte describiría un trozo del fondo y no el fondo. Preferimos '
               'omitirlo antes que publicar un número que parece una respuesta. La cartera y los '
               'pesos de abajo sí son los del propio fondo.',
    dis='Cartera según los informes del propio fondo; cifras de las empresas según sus informes a la '
        'SEC, recalculadas cada día. Información educativa, no es asesoramiento de inversión.',
    groups=[
        ('Mercado estadounidense', ['US large cap', 'US total market']),
        ('Crecimiento y valor', ['US large cap growth', 'US mega cap growth', 'US large cap value', 'US quality factor']),
        ('Dividendos', ['US dividend', 'US dividend growth']),
        ('Empresas más pequeñas', ['US mid cap', 'US small cap']),
        ('Fuera de Estados Unidos', ['developed ex-US', 'global ex-US', 'global', 'emerging markets', 'Europe']),
        ('Sectores', ['technology', 'semiconductors', 'financials', 'healthcare', 'energy', 'industrials', 'real estate']),
        ('Bonos, oro y bitcoin', ['US investment grade bonds', 'international bonds', 'gold', 'bitcoin']),
    ],
)

T = {
 'VOO': ('Las 500 mayores empresas de Estados Unidos, al coste más bajo del sector.',
         'Tiene todas las empresas del S&P 500 en proporción a su valor de mercado, así que las más '
         'grandes mandan. No hay criterio humano: una empresa entra cuando el comité del índice la '
         'añade y sale cuando la quita. Como los pesos siguen al valor de mercado, cerca de un tercio '
         'del fondo está en las diez mayores, bastante más concentrado de lo que casi nadie espera.'),
 'IVV': ('Las mismas 500 empresas que VOO, de otra gestora y al mismo coste.',
         'Replica el S&P 500 con todos sus componentes al peso del índice. Para quien va a mantenerlo '
         'años, elegir entre este y VOO depende del bróker que use y de cuál tenga mejor horquilla '
         'ese día, no de nada que distinga a los fondos.'),
 'SPY': ('El fondo original del S&P 500: el valor más negociado del mundo.',
         'Es el ETF más antiguo de Estados Unidos y está constituido como unit investment trust, no '
         'como fondo moderno, lo que significa que no puede prestar valores ni reinvertir los '
         'dividendos entre pagos. Eso le cuesta algo cada año frente a VOO e IVV a quien lo mantiene. '
         'A cambio tiene una liquidez y un mercado de opciones incomparables, que es por lo que lo '
         'usan los traders y por lo que el inversor de largo plazo normalmente no debería.'),
 'VTI': ('Todas las empresas cotizadas invertibles de Estados Unidos, en una sola posición.',
         'Tiene miles de empresas, de las mayores a las pequeñas, ponderadas por valor de mercado. En '
         'la práctica se comporta casi igual que un fondo del S&P 500, porque las pequeñas que lo '
         'diferencian son en conjunto un puñado de puntos porcentuales. La diferencia aparece en esos '
         'periodos poco frecuentes en que las pequeñas lideran.'),
 'QQQ': ('Las 100 mayores empresas no financieras del Nasdaq: en la práctica, una apuesta por la gran tecnología.',
         'Sigue al Nasdaq-100, que excluye por completo a las financieras y se define por dónde cotiza '
         'una empresa, no por lo que hace. Ese accidente de construcción explica por qué está tan '
         'concentrado en tecnología y por qué unas veces ha batido al S&P 500 y otras ha caído mucho '
         'más. Las diez primeras posiciones suelen rondar la mitad del fondo.'),
 'VUG': ('La mitad de mayor crecimiento de las grandes empresas estadounidenses, según una definición por reglas.',
         'Divide el mercado estadounidense de gran capitalización entre crecimiento y valor usando el '
         'crecimiento de beneficios, el de ventas y el valor contable, y se queda con el lado del '
         'crecimiento ponderado por valor de mercado. Como las mayores tecnológicas puntúan como '
         'crecimiento, el fondo acaba muy concentrado en ellas: se parece más a QQQ de lo que sugiere '
         'el nombre.'),
 'VTV': ('La mitad más barata de las grandes empresas estadounidenses: bancos, salud e industria.',
         'La otra mitad de la misma división que produce VUG. Tiene grandes empresas estadounidenses '
         'que puntúan como valor por precio sobre valor contable, PER y rentabilidad por dividendo, '
         'ponderadas por valor de mercado. El resultado es un fondo con mucha más banca, salud y '
         'energía, bastante menos tecnología que el S&P 500 y un dividendo más alto.'),
 'VIG': ('Empresas que llevan al menos diez años seguidos subiendo su dividendo.',
         'Filtra por un historial largo e ininterrumpido de subidas del dividendo y después descarta '
         'el cuarto de mayor rentabilidad entre las que pasan el filtro. Ese segundo paso es lo '
         'inteligente: una rentabilidad por dividendo muy alta suele ser síntoma de una cotización '
         'que ha caído, no de generosidad, así que quitarlas evita casi todos los recortes. Sale un '
         'fondo de calidad que además paga dividendo, no un fondo de renta alta.'),
 'SCHD': ('Cien pagadoras de dividendo filtradas por solidez del balance, no solo por rentabilidad.',
          'Exige diez años consecutivos pagando dividendo y después ordena lo que queda por flujo de '
          'caja sobre deuda, rentabilidad sobre fondos propios, rentabilidad por dividendo y '
          'crecimiento del dividendo. Esa combinación deja fuera a las empresas que pagan un '
          'dividendo que no pueden permitirse, que es el fallo habitual de los fondos de renta alta. '
          'Los pesos están limitados para que ninguna empresa ni sector domine.'),
 'VYM': ('La mitad de mayor rentabilidad por dividendo del mercado estadounidense, ponderada por tamaño.',
         'Ordena las empresas estadounidenses por rentabilidad por dividendo estimada y se queda con '
         'la mitad superior por valor de mercado, excluyendo las socimis. No aplica ningún filtro de '
         'calidad, lo que lo hace más simple y más amplio que SCHD pero deja dentro más empresas cuya '
         'rentabilidad es alta porque la acción ha caído.'),
 'DGRO': ('Empresas estadounidenses con cinco años subiendo el dividendo y margen para seguir.',
          'Exige cinco años seguidos de crecimiento del dividendo y un pay-out por debajo del 75%, lo '
          'que descarta a quien reparte más de lo que puede sostener. Excluye el decil de mayor '
          'rentabilidad por la misma razón que VIG. Más amplio que VIG y con algo más de dividendo.'),
 'IWF': ('La mitad de crecimiento de las mil mayores empresas estadounidenses, según Russell.',
         'Russell divide su universo de gran capitalización por valor contable sobre precio y '
         'crecimiento estimado, y permite que una empresa esté en parte en crecimiento y en parte en '
         'valor. El efecto práctico es mucho peso en tecnología, parecido a VUG pero con otro '
         'calendario de rebalanceo: la reconstitución anual de Russell en junio es uno de los mayores '
         'acontecimientos de negociación del año.'),
 'IWD': ('La mitad de valor de las mil mayores empresas estadounidenses.',
         'La imagen especular de IWF: las empresas que puntúan baratas por valor contable sobre precio '
         'y bajo crecimiento estimado. Dominan financieras, salud e industria. Junto con IWF '
         'reconstruye el Russell 1000 entero.'),
 'IWM': ('Dos mil pequeñas empresas estadounidenses: el indicador más usado de las small caps.',
         'Tiene desde la empresa número 1.001 hasta la 3.000 por valor de mercado. Una parte '
         'importante del índice no gana dinero, y por eso se comporta de forma muy distinta a los '
         'índices de grandes: es más sensible a los tipos de interés y a la economía doméstica, y '
         'mucho más volátil.'),
 'IJH': ('Las 400 medianas estadounidenses que están entre el S&P 500 y las pequeñas.',
         'El índice de medianas de S&P exige rentabilidad para entrar, cosa que los índices Russell no '
         'hacen. Esa única regla ha convertido históricamente a las medianas estadounidenses en un '
         'universo de mejor calidad que las pequeñas, y explica buena parte de la diferencia de '
         'rentabilidad a largo plazo entre ambas.'),
 'IJR': ('Seiscientas pequeñas empresas estadounidenses, filtradas por rentabilidad.',
         'Sigue al S&P SmallCap 600, que exige que la empresa gane dinero antes de entrar. Esa es la '
         'diferencia clave con el Russell 2000 y la razón de que los dos índices de pequeñas se hayan '
         'separado durante periodos largos pese a cubrir la misma parte del mercado.'),
 'VO': ('Medianas estadounidenses, definidas por dónde caen en el valor total del mercado.',
        'Se queda con el tramo del mercado estadounidense entre aproximadamente el percentil 70 y el '
        '85 del valor acumulado. Sin filtro de rentabilidad, a diferencia del índice de medianas de '
        'S&P, así que tiene un conjunto más amplio y de algo menos calidad, a menor coste.'),
 'VB': ('Pequeñas empresas estadounidenses, sin filtrar si ganan dinero.',
        'Cubre el tramo inferior del mercado estadounidense por valor acumulado, con más de mil '
        'empresas. Más amplio que IJR y más barato, pero incluye empresas en pérdidas que el índice '
        'de pequeñas de S&P deja fuera.'),
 'SPLG': ('El S&P 500 barato de State Street, pensado para mantener y no para operar.',
          'El mismo índice que SPY en una estructura de fondo moderna y a un coste mucho menor. State '
          'Street lo lanzó precisamente porque la estructura de trust de SPY lo hacía poco atractivo '
          'para el largo plazo. Menos volumen que SPY, lo que solo importa si se opera en tamaño.'),
 'RSP': ('Las mismas 500 empresas del S&P 500, pero todas con el mismo peso.',
         'Da a cada empresa en torno al 0,2% del fondo y rebalancea cada trimestre, lo que '
         'sistemáticamente vende lo que ha subido y compra lo que ha bajado. Elimina por completo la '
         'concentración en las mayores: el efecto práctico es una inclinación hacia medianas y valor. '
         'Bate al S&P 500 cuando el mercado se ensancha y se queda muy atrás cuando tiran unos pocos '
         'gigantes.'),
 'QUAL': ('Empresas estadounidenses con buena rentabilidad sobre fondos propios, beneficios estables y poca deuda.',
          'Ordena por tres medidas —rentabilidad sobre fondos propios, variabilidad de los beneficios '
          'y deuda sobre fondos propios— y se queda con las mejores dentro de cada sector, de modo '
          'que el fondo no se convierte en una apuesta sectorial por accidente. La calidad ha '
          'aguantado históricamente mejor en las caídas y se ha quedado atrás en las recuperaciones '
          'bruscas.'),
 'MGK': ('Solo las mayores empresas de crecimiento de Estados Unidos: la forma más concentrada de tenerlas.',
         'Se limita al extremo de megacapitalización del universo de crecimiento, lo que significa '
         'unas pocas decenas de posiciones y una concentración extrema en las mayores tecnológicas. '
         'Más concentrado que QQQ y mucho más que VUG. Solo tiene sentido para quien ha decidido '
         'deliberadamente que quiere esa exposición.'),
 'VV': ('La parte de gran capitalización del mercado estadounidense, definida por tamaño y no por un comité.',
        'Cubre el 85% superior del mercado estadounidense por valor acumulado, así que tiene más '
        'empresas que el S&P 500 y evita el comité que decide quién entra en él. En la práctica su '
        'rentabilidad sigue al S&P 500 muy de cerca.'),
 'ITOT': ('Todo el mercado estadounidense en un fondo, de BlackRock.',
          'Tiene el mercado estadounidense completo, de gran capitalización a microcaps, a peso de '
          'índice. Competidor directo de VTI, con prácticamente la misma exposición, el mismo coste y '
          'el mismo comportamiento.'),
 'SCHX': ('Las 750 mayores empresas estadounidenses, a uno de los costes más bajos que existen.',
          'Un fondo amplio de gran capitalización que cubre más empresas que el S&P 500 a un coste en '
          'el suelo del sector. Se comporta casi igual que VV y que el S&P 500 en cualquier periodo '
          'relevante.'),
 'VEA': ('Empresas de países desarrollados fuera de Estados Unidos: Europa, Japón, Canadá, Australia.',
         'Tiene miles de empresas de mercados desarrollados excluyendo Estados Unidos, ponderadas por '
         'valor de mercado, lo que convierte a Japón y el Reino Unido en posiciones grandes. A '
         'diferencia de la versión de MSCI incluye Canadá y Corea del Sur. La rentabilidad depende '
         'mucho del dólar: uno débil la favorece y uno fuerte la perjudica.'),
 'VXUS': ('Todas las empresas invertibles del mundo fuera de Estados Unidos.',
          'Junta mercados desarrollados y emergentes fuera de Estados Unidos en un solo fondo, a pesos '
          'de mercado y con varios miles de empresas. Combinado con VTI construye una cartera global '
          'completa con dos posiciones.'),
 'IEFA': ('Europa, Australasia y Lejano Oriente desarrollados: el índice internacional de referencia.',
          'Sigue el universo EAFE de MSCI, que excluye Estados Unidos y Canadá y cubre grandes, '
          'medianas y pequeñas. Es la asignación internacional más usada en las carteras '
          'estadounidenses y la referencia contra la que se mide a los gestores internacionales.'),
 'VWO': ('Empresas de economías en desarrollo, dominadas por China, India y Taiwán.',
         'Tiene empresas de mercados emergentes a peso de mercado, lo que concentra el fondo en un '
         'puñado de países y en unas pocas tecnológicas y de internet muy grandes. FTSE clasifica a '
         'Corea del Sur como desarrollada, así que, a diferencia de la versión de MSCI, este fondo no '
         'tiene empresas coreanas.'),
 'IEMG': ('Emergentes según la definición de MSCI, que sí incluye Corea del Sur.',
          'La diferencia principal con VWO es la clasificación de países: MSCI trata a Corea del Sur '
          'como emergente, así que este fondo tiene grandes empresas coreanas que VWO no tiene. '
          'También baja más hacia las pequeñas. Por lo demás se comportan de forma parecida.'),
 'EFA': ('El fondo internacional de desarrollados original, solo grandes y medianas.',
         'Más antiguo y más caro que IEFA, cubre los mismos mercados pero sin pequeñas. Sigue vivo por '
         'su mercado de opciones y por su papel como índice de referencia en mandatos '
         'institucionales, no porque sea el mejor fondo para mantener.'),
 'VT': ('Todo el mercado de acciones invertible del planeta, en una sola posición.',
        'Tiene alrededor de diez mil empresas de mercados desarrollados y emergentes a peso de '
        'mercado, lo que hoy significa en torno a dos tercios Estados Unidos. Es lo más parecido que '
        'existe a poseer la cartera global de mercado y no exige decidir cuánto asignar a ningún '
        'país.'),
 'VGK': ('Empresas europeas, del Reino Unido y Suiza a los países nórdicos.',
         'Exposición a Europa desarrollada ponderada por mercado, lo que concentra el fondo en unas '
         'pocas empresas muy grandes de farmacia, lujo, equipos para semiconductores y banca. Los '
         'movimientos entre el euro, la libra y el dólar explican buena parte de la rentabilidad de '
         'cualquier año.'),
 'VEU': ('El mundo fuera de Estados Unidos, solo grandes y medianas.',
         'Muy parecido a VXUS pero sin pequeñas, lo que lo deja algo más concentrado en las grandes '
         'multinacionales que dominan los índices no estadounidenses. Cualquiera de los dos cumple la '
         'misma función en una cartera.'),
 'VGT': ('Tecnológicas estadounidenses, incluidos los fabricantes de hardware y semiconductores.',
         'Cubre el sector tecnológico según la definición de MSCI, que incluye software, hardware y '
         'semiconductores pero deja fuera a las grandes de internet y medios, clasificadas como '
         'servicios de comunicación, y también a Amazon y Tesla, que son consumo. Esas exclusiones '
         'importan más de lo que la gente cree y son la diferencia principal con QQQ.'),
 'XLK': ('Las tecnológicas que están dentro del S&P 500, y solo esas.',
         'Limitado a los miembros del S&P 500 clasificados como tecnología, lo que lo hace mucho más '
         'concentrado que VGT: suele tener menos de 70 posiciones y las dos primeras se acercan al '
         '40% del fondo. Las definiciones sectoriales se revisan cada cierto tiempo y esas revisiones '
         'pueden cambiar el fondo de un día para otro.'),
 'SMH': ('Las 25 mayores empresas de semiconductores cotizadas: la forma más concentrada de jugar el ciclo del chip.',
         'Solo tiene 25 empresas, lo que lo hace extremadamente concentrado: las dos o tres primeras '
         'pueden ser un tercio del fondo. Incluye fabricantes extranjeros a través de sus cotizaciones '
         'en Estados Unidos, cosa que SOXX históricamente no hacía. La demanda de semiconductores es '
         'cíclica y este fondo se mueve mucho más que el mercado en ambas direcciones.'),
 'SOXX': ('Treinta empresas de semiconductores cotizadas en Estados Unidos, algo más repartidas que SMH.',
          'Sigue un índice de semiconductores cotizados en Estados Unidos con topes que limitan cuánto '
          'puede pesar una sola posición, así que está menos cargado arriba que SMH. La metodología '
          'del índice ha cambiado más de una vez, cosa que conviene saber antes de comparar su '
          'historial con nada.'),
 'XLF': ('Los bancos, aseguradoras y empresas de pagos que están dentro del S&P 500.',
         'Tiene las financieras del S&P 500 a pesos de mercado con topes. Desde que el inmobiliario se '
         'separó en su propio sector, el fondo es una apuesta más limpia por banca, seguros y mercados '
         'de capitales. Es muy sensible a los tipos de interés y a las condiciones de crédito, que es '
         'exactamente la razón para tenerlo o para evitarlo.'),
 'XLV': ('La gran salud estadounidense: farmacéuticas, dispositivos, aseguradoras y distribuidoras.',
         'Cubre las empresas de salud del S&P 500, lo que mezcla negocios muy distintos: farmacéuticas '
         'que dependen de patentes, fabricantes de dispositivos estables y aseguradoras cuya economía '
         'la decide la política pública. El precio de los medicamentos y la política sanitaria en '
         'Estados Unidos afectan a todas, y por eso el sector se mueve con las noticias políticas más '
         'que la mayoría.'),
 'XLE': ('El petróleo y el gas estadounidenses, dominados por dos supergrandes.',
         'Tiene las energéticas del S&P 500 y, como el sector está tan cargado arriba, las dos mayores '
         'petroleras integradas suelen rondar el 40% del fondo. Es una apuesta directa por el precio '
         'del crudo con el apalancamiento operativo de las productoras encima.'),
 'XLI': ('La industria estadounidense: aeroespacial, ferrocarriles, maquinaria y los grandes conglomerados.',
         'Tiene las industriales del S&P 500, un grupo realmente diverso que va de contratistas de '
         'defensa con cartera de pedidos a varios años a fabricantes de maquinaria atados al ciclo. '
         'Se usa a menudo como forma directa de expresar una opinión sobre la industria y la '
         'inversión en infraestructuras en Estados Unidos.'),
 'VNQ': ('Inmobiliario estadounidense, a través de socimis cotizadas.',
         'Tiene REIT estadounidenses de centros de datos, naves logísticas, torres de '
         'telecomunicaciones, viviendas, comercios y oficinas. Como los REIT están obligados a '
         'repartir casi todo su beneficio, el fondo paga un dividendo alto y es especialmente sensible '
         'a los tipos: tipos más altos encarecen la deuda con la que se financia el ladrillo y a la '
         'vez hacen menos atractivo ese dividendo.'),
 'VHT': ('Todo el sector sanitario estadounidense, incluidas las biotecnológicas pequeñas.',
         'Más amplio que XLV porque va más allá del S&P 500 hasta medianas y pequeñas, lo que le da '
         'una cola larga de biotecnológicas. Esa cola añade volatilidad y la posibilidad de '
         'rentabilidades extraordinarias que un fondo sanitario solo de grandes no tiene.'),
 'BND': ('El mercado de bonos estadounidense con grado de inversión: deuda pública, hipotecaria y corporativa.',
         'Tiene miles de bonos con grado de inversión a peso de índice, lo que significa en torno a dos '
         'tercios deuda pública y deuda hipotecaria con respaldo público. Su precio cae cuando suben '
         'los tipos y sube cuando bajan; la duración de unos seis años dice aproximadamente cuánto. Es '
         'el lastre estándar de una cartera, no una fuente de rentabilidad.'),
 'AGG': ('El mismo mercado de bonos estadounidense que BND, de BlackRock.',
         'Sigue el índice Bloomberg US Aggregate sin ajuste de capital flotante. La diferencia práctica '
         'con BND es despreciable: un ajuste distinto y un coste marginalmente distinto. Se elige por '
         'cuál negocie más barato el bróker.'),
 'BNDX': ('Bonos con grado de inversión de fuera de Estados Unidos, con la divisa cubierta.',
          'Tiene deuda con grado de inversión no estadounidense, sobre todo pública europea y japonesa, '
          'y cubre la exposición a divisa contra el dólar. La cobertura es lo importante: sin ella, un '
          'bono extranjero es sobre todo una apuesta de divisas, y cubrirla lo convierte en un '
          'diversificador real frente a los tipos estadounidenses.'),
 'GLD': ('Oro físico, guardado en una cámara en Londres y dividido en participaciones.',
         'Cada participación representa una fracción de onza de oro en custodia asignada. No hay renta '
         'ni beneficios: la rentabilidad es el precio del oro menos el coste de custodia, que se '
         'descuenta vendiendo una pequeña cantidad de oro cada año, de modo que el oro por '
         'participación baja poco a poco. En Estados Unidos su fiscalidad difiere de la de las '
         'acciones, cosa que importa en cuentas sujetas a impuestos.'),
 'IAU': ('El mismo oro físico que GLD, con un coste anual menor.',
         'Idéntico en sustancia a GLD —oro físico asignado, sin renta, coste descontado en metal— pero '
         'cobra menos, lo que compuesto a diez años es una diferencia apreciable. GLD conserva más '
         'volumen y un mercado de opciones más profundo.'),
 'IBIT': ('Bitcoin en manos de un custodio, que se compra y se vende como una acción.',
          'Tiene bitcoin directamente con un custodio institucional, así que la cotización sigue al '
          'precio del bitcoin menos la comisión. Quita la necesidad de gestionar claves privadas o de '
          'usar un exchange, que es exactamente la razón por la que captó dinero más rápido que '
          'ningún lanzamiento de ETF de la historia. El activo subyacente no genera flujo de caja, así '
          'que no hay nada contra lo que valorarlo.'),
}

# Los países por los que pregunta este lector, con la respuesta en español. La norma europea no es
# una prohibición al fondo: es que falta un documento, y por eso el bróker rechaza la orden. En
# México y Argentina la respuesta es otra, porque los mismos fondos cotizan localmente.
UI.update({
    's_blocked': 'No se puede comprar',
    's_open': 'Se puede comprar',
    's_local': 'Se puede comprar, y además cotiza localmente',
    's_hard': 'Permitido, pero difícil en la práctica',
    's_sanctions': 'No accesible',
    'c_Spain': 'España', 'c_Mexico': 'México', 'c_Argentina': 'Argentina', 'c_Chile': 'Chile',
    'c_Colombia': 'Colombia', 'c_Peru': 'Perú', 'c_Uruguay': 'Uruguay', 'c_Ecuador': 'Ecuador',
    'c_Costa Rica': 'Costa Rica', 'c_Panama': 'Panamá',
    'c_Dominican Republic': 'República Dominicana', 'c_Guatemala': 'Guatemala',
    'c_Bolivia': 'Bolivia', 'c_Venezuela': 'Venezuela',
    'w_Spain': 'La norma europea exige un documento de datos fundamentales en una lengua oficial de '
               'la UE antes de vender un producto empaquetado a un minorista. Las gestoras '
               'estadounidenses no lo elaboran, así que la orden se rechaza: con cualquier bróker, '
               'no solo con el tuyo. El fondo europeo que se indica arriba sigue el mismo índice y sí '
               'se vende con ese documento.',
    'w_Mexico': 'Los ETF estadounidenses cotizan en el Sistema Internacional de Cotizaciones de la '
                'Bolsa Mexicana, así que se compran en pesos con una casa de bolsa mexicana y sin '
                'abrir cuenta en el extranjero. También se llega a ellos en dólares con un bróker '
                'internacional.',
    'w_Argentina': 'Los grandes ETF estadounidenses cotizan en Buenos Aires como CEDEAR —'
                   'certificados locales que representan al valor extranjero— y se compran en pesos. '
                   'Comprar el fondo en sí exige una cuenta en dólares en el exterior, y ahí entran '
                   'las reglas locales sobre la compra de divisa.',
    'w_Chile': 'No se aplica ninguna restricción europea. Las corredoras locales dan acceso al '
               'mercado estadounidense y los brókeres internacionales aceptan residentes, así que el '
               'fondo se compra en dólares.',
    'w_Colombia': 'Accesible con comisionistas locales que ofrecen mercado global y con brókeres '
                  'internacionales. El obstáculo es el coste de convertir y sacar los pesos, no el '
                  'fondo.',
    'w_Peru': 'Accesible con sociedades agentes de bolsa que ofrecen mercados extranjeros y con '
              'brókeres internacionales. No se aplica ninguna restricción al estilo europeo.',
    'w_Uruguay': 'No se aplica ninguna restricción europea; los brókeres internacionales aceptan residentes.',
    'w_Ecuador': 'La economía está dolarizada, lo que elimina el paso de la divisa; accesible con brókeres internacionales.',
    'w_Costa Rica': 'No se aplica ninguna restricción europea; accesible con brókeres internacionales.',
    'w_Panama': 'No se aplica ninguna restricción europea; accesible con brókeres internacionales.',
    'w_Dominican Republic': 'No se aplica ninguna restricción europea; accesible con brókeres internacionales.',
    'w_Guatemala': 'No se aplica ninguna restricción europea; accesible con brókeres internacionales.',
    'w_Bolivia': 'El acceso a divisa extranjera está restringido, y ese es el obstáculo, no el fondo.',
    'w_Venezuela': 'Los controles de cambio y las sanciones hacen muy difícil abrir y fondear una '
                   'cuenta de inversión en el exterior.',
})
