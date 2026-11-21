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
    i_title='Los {N} ETF más grandes: cartera, PER y rentabilidad',
    i_desc='Los {N} ETF más grandes del mundo con su cartera, sus pesos y su rentabilidad a un '
           'año, y un PER calculado con las empresas que cada uno tiene realmente dentro.',
    d_title='ETF %(t)s: cartera, PER y rentabilidad',
    d_desc='%(name)s (%(t)s): cartera, pesos y rentabilidad, con un PER calculado a partir de las '
           'empresas que tiene dentro. %(idea)s',
    h1='Los {N} ETF más grandes del mundo',
    sub='Cartera, pesos y valoración · actualizado',
    lead='Los {N} fondos cotizados más grandes del mundo, con para qué sirve cada uno, qué '
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
    all50='Los {N} fondos, uno al lado del otro',
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
 'SPYM': ('El S&P 500 barato de State Street, pensado para mantener y no para operar.',
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

# columns of the index box: the type tag, the localised name grammar and the P/E note
UI.update({
    'type': 'Tipo',
    'avg_yr': 'Media anual',
    'pe_avg': 'PER medio',
    'name_pattern': '%(index)s de %(issuer)s',
    'note_peavg': 'Nadie publica un PER histórico de un fondo, porque depende de lo que el fondo tuviera dentro en cada momento. Por eso empezamos a registrar el nuestro el %(since)s. La columna de la media se rellena cuando haya alrededor de un mes de datos.',
    'note_peavg_none': 'La columna del PER medio se rellena a medida que registramos la cifra de cada día.',
    'focus_labels': {'US large cap': 'Grandes EE. UU.', 'US total market': 'Todo el mercado EE. UU.', 'US large cap growth': 'Crecimiento EE. UU.', 'US mega cap growth': 'Megacaps crecimiento', 'US large cap value': 'Valor EE. UU.', 'US quality factor': 'Calidad EE. UU.', 'US dividend': 'Dividendo EE. UU.', 'US dividend growth': 'Dividendo creciente', 'US mid cap': 'Medianas EE. UU.', 'US small cap': 'Pequeñas EE. UU.', 'developed ex-US': 'Desarrollados sin EE. UU.', 'global ex-US': 'Global sin EE. UU.', 'global': 'Global', 'emerging markets': 'Emergentes', 'Europe': 'Europa', 'technology': 'Tecnología', 'semiconductors': 'Semiconductores', 'financials': 'Financieras', 'healthcare': 'Salud', 'energy': 'Energía', 'industrials': 'Industria', 'real estate': 'Inmobiliario', 'US investment grade bonds': 'Bonos EE. UU.', 'international bonds': 'Bonos internacionales', 'gold': 'Oro', 'bitcoin': 'Bitcoin'},
})

UI['pe_short'] = 'PER'

# the European-alternative wording from etf_list.py, in this edition's language
UCITS = {'VUAA accumulates dividends, VUSA pays them out.': 'VUAA acumula los dividendos; VUSA los reparte.', 'The same index from the same manager, in a European wrapper.': 'El mismo índice y la misma gestora, en formato europeo.', 'No European fund replicates SPY’s trust structure, and none needs to.': 'Ningún fondo europeo reproduce la estructura de trust de SPY, y ninguno necesita hacerlo.', 'Closest European equivalent; it includes Canada, which VTI does not.': 'El equivalente europeo más cercano; incluye Canadá, cosa que VTI no hace.', 'Both track the same index; CNDX accumulates, EQQQ distributes.': 'Ambos siguen el mismo índice; CNDX acumula y EQQQ reparte.', 'Several providers offer one; there is no single obvious equivalent.': 'Lo ofrecen varias gestoras; no hay un equivalente único evidente.', 'Available from several providers; check which value definition it uses.': 'Disponible en varias gestoras; mira qué definición de valor usa.', 'The ten-year increase screen is uncommon in European wrappers.': 'El filtro de diez años subiendo el dividendo es poco común en formato europeo.', 'Nothing in Europe replicates the Dow Jones 100 methodology exactly.': 'En Europa no hay nada que reproduzca exactamente la metodología del Dow Jones 100.', 'Global rather than US-only, but the same family and methodology.': 'Global en vez de solo Estados Unidos, pero la misma familia y metodología.', 'IWDA includes the US; VEVE ex-US variants differ by provider.': 'IWDA incluye Estados Unidos; las variantes sin EE. UU. cambian según la gestora.', 'VWRL includes the US as well; there is no exact ex-US twin in the range.': 'VWRL también incluye Estados Unidos; en la gama no hay un gemelo exacto sin EE. UU.', 'World includes the US; EAFE-only UCITS versions exist but are less traded.': 'El índice mundial incluye Estados Unidos; existen versiones UCITS solo de EAFE, pero se negocian menos.', 'VWCE accumulates dividends, VWRL distributes them.': 'VWCE acumula los dividendos; VWRL los reparte.', 'European equivalents are exchange-traded commodities, not UCITS funds.': 'Los equivalentes europeos son materias primas cotizadas (ETC), no fondos UCITS.', 'UCITS rules do not permit a single-asset crypto fund.': 'Las normas UCITS no permiten un fondo cripto de un solo activo.', 'A UCITS ETF tracking a US large-cap growth index': 'un ETF UCITS que siga un índice de crecimiento de grandes empresas de EE. UU.', 'A UCITS ETF tracking a US large-cap value index': 'un ETF UCITS que siga un índice de valor de grandes empresas de EE. UU.', 'A UCITS ETF tracking a US dividend growth index': 'un ETF UCITS que siga un índice de dividendo creciente de EE. UU.', 'A UCITS ETF tracking a quality US dividend index': 'un ETF UCITS que siga un índice de dividendo de calidad de EE. UU.', 'A UCITS ETF tracking the Russell 1000 Growth index': 'un ETF UCITS que siga el índice Russell 1000 Growth', 'A UCITS ETF tracking the Russell 1000 Value index': 'un ETF UCITS que siga el índice Russell 1000 Value', 'A UCITS ETF tracking the Russell 2000': 'un ETF UCITS que siga el Russell 2000', 'A UCITS ETF tracking the S&P MidCap 400': 'un ETF UCITS que siga el S&P MidCap 400', 'A UCITS ETF tracking the S&P SmallCap 600': 'un ETF UCITS que siga el S&P SmallCap 600', 'A UCITS ETF tracking a US mid-cap index': 'un ETF UCITS que siga un índice de medianas de EE. UU.', 'A UCITS ETF tracking a US small-cap index': 'un ETF UCITS que siga un índice de pequeñas de EE. UU.', 'A UCITS ETF tracking the S&P 500 Equal Weight index': 'un ETF UCITS que siga el S&P 500 Equal Weight', 'A UCITS ETF tracking a US mega-cap growth index': 'un ETF UCITS que siga un índice de megacaps de crecimiento de EE. UU.', 'A UCITS ETF tracking US or world information technology': 'un ETF UCITS de tecnología de la información, estadounidense o mundial', 'A UCITS ETF tracking global semiconductors': 'un ETF UCITS de semiconductores globales', 'A UCITS ETF tracking US or developed-market property': 'un ETF UCITS inmobiliario, estadounidense o de mercados desarrollados', 'A UCITS ETF tracking US health care': 'un ETF UCITS de salud estadounidense', 'European investors use exchange-traded products rather than UCITS funds': 'los inversores europeos usan productos cotizados (ETP) en vez de fondos UCITS', 'A EUR-hedged global aggregate bond UCITS ETF': 'un ETF UCITS de bonos globales con la divisa cubierta a euros', 'A USD-hedged global or US aggregate bond UCITS ETF': 'un ETF UCITS de bonos globales o estadounidenses cubierto a dólares', 'Screened US dividend UCITS funds': 'fondos UCITS de dividendo estadounidense filtrados'}

UCITS.update({'Invesco EQQQ Nasdaq-100 UCITS ETF, or iShares Nasdaq 100 UCITS ETF': 'Invesco EQQQ Nasdaq-100 UCITS ETF o iShares Nasdaq 100 UCITS ETF', 'Vanguard FTSE Developed World UCITS ETF, or iShares Core MSCI World': 'Vanguard FTSE Developed World UCITS ETF o iShares Core MSCI World', 'Vanguard FTSE Emerging Markets UCITS ETF, or iShares Core MSCI EM IMI': 'Vanguard FTSE Emerging Markets UCITS ETF o iShares Core MSCI EM IMI'})

# phone layout: return ranking, fund finder, quick keys (etf_pages.py, web_src/etfm.*)
UI.update({'rank_h': 'Ranking de rentabilidad', 'rank_all': 'Ver los %(n)s fondos ▾', 'rank_less': 'Ver solo los 10 primeros ▴', 'rank_note': 'Rentabilidad del precio, sin dividendos. Toca un fondo para abrir su página.', 'find_ph': 'Busca entre los {N} fondos: ticker, nombre o tipo', 'sort_big': 'Más grandes', 'sort_pe': 'PER más bajo', 'n_funds': '%n fondos', 'no_fund': 'Ningún fondo coincide con la búsqueda.', 'more': 'Leer más ▾', 'less': 'Ver menos ▴', 'holds_all': 'Ver las %(n)s posiciones ▾', 'holds_less': 'Ver solo las 10 primeras ▴', 'k_idea': 'Idea', 'k_val': 'Valoración', 'k_ret': 'Rentabilidad', 'k_hold': 'Cartera', 'k_sec': 'Secciones de la página', 'k_find': 'Buscar', 'k_ph': 'Busca cualquier acción o ETF', 'k_none': 'Sin resultados', 'l_y1': 'Último año', 'l_avg': 'Media anual', 'l_hold': 'Posiciones', 'l_pe': 'PER'})

# ---- funds 51-100 (Nov 2026)
UI['focus_labels'].update({'US treasury bonds': 'Bonos del Tesoro EE. UU.', 'US corporate bonds': 'Bonos corporativos EE. UU.', 'high yield bonds': 'Alto rendimiento', 'municipal bonds': 'Bonos municipales', 'US covered call': 'Rentas con opciones', 'consumer discretionary': 'Consumo discrecional', 'consumer staples': 'Consumo básico', 'utilities': 'Servicios públicos', 'materials': 'Materiales', 'communication services': 'Comunicaciones', 'biotech': 'Biotecnología', 'aerospace and defense': 'Aeroespacial y defensa', 'banks': 'Bancos', 'gold miners': 'Mineras de oro', 'oil and gas': 'Petróleo y gas', 'cybersecurity': 'Ciberseguridad', 'clean energy': 'Energía limpia', 'innovation': 'Innovación', 'US momentum': 'Momentum EE. UU.', 'US low volatility': 'Baja volatilidad EE. UU.', 'Japan': 'Japón', 'China': 'China', 'India': 'India', 'Brazil': 'Brasil', 'silver': 'Plata', 'ether': 'Ether'})

_G = UI['groups']
_G[1][1].extend(['US momentum', 'US low volatility'])
_G[2][1].append('US covered call')
_G[4][1].extend(['Japan', 'China', 'India', 'Brazil'])
_G[5][1].extend(['consumer discretionary', 'consumer staples', 'utilities', 'materials', 'communication services', 'biotech', 'aerospace and defense', 'banks', 'gold miners', 'oil and gas', 'cybersecurity', 'clean energy', 'innovation'])
_G[6][1].extend(['US treasury bonds', 'US corporate bonds', 'high yield bonds', 'municipal bonds', 'silver', 'ether'])
T.update({'ACWI': ('Unas 2.500 grandes y medianas empresas de mercados desarrollados y emergentes.',
          'Es la bolsa mundial por tamaño, con cerca de dos tercios en EE. UU.: una cartera global en un fondo, parecida a VT pero sin pequeñas.'),
 'ARKK': ('La apuesta activa y concentrada de Cathie Wood por la tecnología disruptiva.',
          'Tiene unas pocas decenas de empresas elegidas por la gestora; subió más de un 150% en 2020 y cayó cerca de un 75% desde su máximo.'),
 'BIL': ('Letras del Tesoro a uno a tres meses: el ETF de liquidez más antiguo.',
         'Hace lo mismo que SGOV con una comisión algo mayor y reparte los intereses cada mes. Su largo historial lo convierte en la referencia de la rentabilidad del efectivo.'),
 'BSV': ('Bonos cortos del Estado y de grandes empresas de EE. UU. en un solo fondo barato.',
         'Bonos a uno a cinco años, dos tercios públicos y un tercio corporativos de calidad: un paso conservador más allá de la liquidez.'),
 'CIBR': ('Empresas de ciberseguridad, del software a los equipos de red.',
          'Incluye CrowdStrike, Palo Alto Networks y Cisco con topes a las mayores. El gasto en seguridad ha resistido incluso con presupuestos de TI débiles.'),
 'EEM': ('El ETF original de emergentes, más usado por operadores que por inversores a largo plazo.',
         'Cuesta más que IEMG y VWO, que tienen casi las mismas empresas, pero es el más líquido para operar y para opciones.'),
 'ETHA': ('Ether al contado, la moneda de la red Ethereum, desde una cuenta de bolsa normal.', 'El ether es más volátil que el bitcoin y su valor depende de la actividad en la red Ethereum.'),
 'EWJ': ('Grandes y medianas empresas japonesas.',
         'Toyota, Sony y Mitsubishi UFJ, entre otras. Para un inversor en dólares la rentabilidad depende de la bolsa japonesa y del yen, que lleva años débil.'),
 'EWZ': ('Las mayores empresas de Brasil: materias primas, bancos y un dividendo alto.', 'Dominado por Petrobras, Vale e Itaú; oscila con las materias primas, el real y la política brasileña.'),
 'FBTC': ('Bitcoin al contado custodiado por la propia Fidelity, el segundo mayor ETF de bitcoin.',
          'Fidelity actúa como su propio custodio en lugar de depender de un exchange; el precio sigue al bitcoin menos la comisión.'),
 'FXI': ('Las 50 mayores empresas chinas que cotizan en Hong Kong.',
         'Más concentrado que MCHI, con mucho peso en bancos, plataformas de internet y empresas estatales; se usa para apostar por estímulos o noticias arancelarias.'),
 'GDX': ('Mineras de oro: una forma apalancada de tener oro.', 'Como sus costes son en gran parte fijos, sus beneficios suben más deprisa que el oro, y también bajan más deprisa.'),
 'GLDM': ('Oro físico con una comisión y un precio por participación menores que GLD.',
          'Guarda lingotes en Londres como GLD pero cobra mucho menos, algo que importa a largo plazo; GLD sigue siendo el preferido de los grandes operadores por su liquidez.'),
 'HYG': ('Bonos basura: más rentas por prestar a empresas estadounidenses más arriesgadas.',
         'El rendimiento es alto porque algunos emisores quiebran; en una recesión puede caer casi tanto como la bolsa, así que es más un híbrido entre acción y bono que un activo seguro.'),
 'IBB': ('Biotecnológicas estadounidenses ponderadas por tamaño, lideradas por las grandes con productos en el mercado.', 'Amgen, Gilead y Vertex pesan mucho, lo que lo hace más estable que XBI.'),
 'ICLN': ('Empresas solares, eólicas y de energía renovable de todo el mundo.',
          'Depende mucho de los tipos y de las subvenciones: se disparó en 2020 y luego perdió casi todo lo ganado al subir los tipos.'),
 'IEF': ('Bonos del Tesoro a diez años: la cobertura clásica de una cartera ante una recesión.',
         'Su precio cambia un 7-8% por cada punto que se mueven los tipos largos. Suele subir cuando la bolsa cae por miedo al crecimiento y baja cuando la inflación empuja los tipos, como en 2022.'),
 'INDA': ('Grandes y medianas empresas indias.',
          'HDFC Bank, Reliance, Infosys e ICICI Bank. El rápido crecimiento de la India ha dado a su bolsa una de las valoraciones más altas del mundo, lo que deja menos margen de error.'),
 'ITA': ('Contratistas de defensa y fabricantes de aviones de EE. UU.', 'Los presupuestos de defensa dan contratos largos y visibilidad; la parte comercial sigue al tráfico aéreo.'),
 'IXUS': ('Todas las bolsas del mundo salvo la de EE. UU., en un fondo barato.',
          'Es el equivalente de iShares a VXUS y el complemento habitual de un fondo estadounidense en una cartera de dos fondos.'),
 'JEPI': ('Acciones estadounidenses defensivas más ingresos por opciones: un pago mensual alto a cambio de limitar las subidas.',
          'Vende opciones de compra y convierte parte de las ganancias futuras en renta mensual. Cae menos en las correcciones, pero se queda muy atrás en las subidas fuertes: parte del alto '
          'rendimiento es la propia subida del inversor devuelta.'),
 'JEPQ': ('Acciones del Nasdaq-100 más ingresos por opciones: rendimiento de dos dígitos con menos subida que QQQ.',
          'El pago es alto porque las opciones del Nasdaq son caras, pero en un rally tecnológico fuerte el fondo solo se queda con parte de la ganancia.'),
 'JNK': ('Bonos de alto rendimiento de State Street, el gran rival de HYG.', 'Sigue a HYG muy de cerca; las diferencias vienen de pequeñas reglas del índice y de las comisiones.'),
 'KRE': ('Bancos regionales estadounidenses con el mismo peso: una apuesta por la economía interna y la curva de tipos.',
         'Ganan con la diferencia entre lo que pagan por los depósitos y cobran por los préstamos y tienen préstamos inmobiliarios comerciales, así que son muy sensibles a los tipos y al miedo al '
         'crédito, como mostró 2023.'),
 'LQD': ('El fondo de bonos corporativos estadounidenses más negociado, con vencimientos largos.',
         'Combina crédito corporativo y duración larga, así que oscila más que VCIT. Los institucionales lo usan para operar el mercado de crédito con rapidez.'),
 'MCHI': ('Empresas chinas que cotizan en Hong Kong, EE. UU. y China continental.',
          'Tencent, Alibaba, PDD y Meituan. Depende del crecimiento chino, de la política de Pekín y de la relación con EE. UU. tanto como de los resultados.'),
 'MTUM': ('Acciones estadounidenses con las mayores subidas recientes, revisadas dos veces al año.',
          'Compra las empresas que más han subido en seis a doce meses. Aprovecha bien las tendencias, pero sufre cuando el liderazgo del mercado cambia de golpe.'),
 'MUB': ('Bonos exentos de impuestos de estados y ciudades de EE. UU.',
         'El interés está libre del impuesto federal estadounidense, una ventaja que solo tiene quien paga impuestos en EE. UU.; para un inversor extranjero el menor rendimiento tiene poco sentido.'),
 'SCHB': ('Unas 2.500 empresas estadounidenses, grandes y pequeñas, casi gratis.', 'Es la respuesta de Schwab a VTI y rinde prácticamente igual.'),
 'SCHF': ('Grandes empresas de países desarrollados fuera de EE. UU.', 'Europa, Japón, Reino Unido, Canadá y Australia a muy bajo coste; alternativa a VEA e IEFA con casi la misma rentabilidad.'),
 'SCHG': ('Grandes empresas de crecimiento de EE. UU. a uno de los costes más bajos.',
          'Dominado por las grandes tecnológicas, se comporta casi igual que VUG y QQQ, con algo más de amplitud que QQQ.'),
 'SGOV': ('Letras del Tesoro de EE. UU. a menos de tres meses: un sustituto de la liquidez que paga el tipo de interés a corto plazo.',
          'Solo tiene letras con menos de tres meses de vida, así que su precio apenas se mueve y su rentabilidad es el tipo oficial de la Reserva Federal menos una pequeña comisión. Cuando la Fed '
          'baja tipos, su rendimiento cae casi de inmediato.'),
 'SHV': ('Bonos del Tesoro a menos de un año: liquidez con algo más de rendimiento.',
         'Tiene letras y notas con menos de doce meses de vida. Reacciona un poco más a los tipos que un fondo a tres meses, pero sigue siendo un lugar para dinero que no debe perder valor.'),
 'SHY': ('Bonos del Tesoro a uno a tres años: poco riesgo y una pequeña ganancia si bajan los tipos.',
         'Su precio se mueve en torno a un 2% por cada punto que cambian los tipos, así que gana algo cuando la Fed recorta y pierde algo cuando sube.'),
 'SLV': ('Plata física guardada en cámaras.', 'La plata es en parte metal precioso y en parte metal industrial para paneles solares y electrónica, lo que la hace más volátil que el oro.'),
 'TIP': ('Bonos del Tesoro protegidos contra la inflación: el principal sube con el IPC.',
         'Ganan a los bonos normales cuando la inflación sorprende al alza, pero siguen cayendo cuando suben los tipos reales, algo que sorprendió a muchos en 2022.'),
 'TLT': ('Bonos del Tesoro a más de veinte años: una apuesta apalancada a la bajada de tipos, sin riesgo de crédito.',
         'Un punto menos en los tipos largos lo sube cerca de un 16%, y un punto más le cuesta lo mismo; por eso perdió casi la mitad de su valor entre 2020 y 2023.'),
 'USMV': ('Acciones estadounidenses combinadas para oscilar lo menos posible.',
          'Se inclina hacia eléctricas, consumo básico y salud; suele caer menos en las correcciones y quedarse atrás en las subidas fuertes.'),
 'VCIT': ('Bonos a cinco a diez años de grandes empresas de EE. UU.: más rendimiento que el Tesoro, con algo de riesgo de crédito.',
          'Se cobra un diferencial sobre el Tesoro por prestar a empresas; en una recesión ese diferencial se amplía y el fondo cae aunque los bonos públicos suban.'),
 'VCSH': ('Bonos cortos de grandes empresas estadounidenses: un poco más de rendimiento que la liquidez.',
          'Los vencimientos cortos mantienen pequeños el riesgo de tipos y las pérdidas por impagos, así que en tiempos normales se comporta como un fondo monetario con más rentabilidad.'),
 'VGIT': ('Bonos del Tesoro a tres a diez años al bajo coste de Vanguard.',
          'Ocupa el tramo medio de la curva, entre SHY e IEF en sensibilidad a los tipos, y es un núcleo habitual para quien quiere bonos públicos sin los vaivenes de los largos.'),
 'VTEB': ('La cesta barata de Vanguard de bonos municipales exentos de impuestos.',
          'Como MUB, solo tiene sentido para quien tributa en EE. UU., para quien la renta exenta vale más que el mayor rendimiento de un bono con impuestos.'),
 'XBI': ('Biotecnológicas estadounidenses con el mismo peso cada una: una apuesta por las pequeñas y por las compras.',
         'Las pequeñas en fase clínica pesan tanto como las grandes, así que puede subir o bajar un 50% en un año según los tipos, los ensayos y las adquisiciones.'),
 'XLB': ('Químicas, gases industriales, metales y envases del S&P 500.',
         'Sus beneficios siguen a la demanda industrial y a las materias primas, así que es cíclico y suele ir mejor al principio de una recuperación.'),
 'XLC': ('Meta, Alphabet, Netflix y las telecos del S&P 500.', 'Meta y Alphabet son casi la mitad del fondo, así que su rentabilidad depende sobre todo de la publicidad digital.'),
 'XLP': ('Alimentación, bebidas, productos del hogar y supermercados: lo que se compra cuando preocupa la economía.',
         'La demanda es estable en recesión, lo que lo hace defensivo, aunque el bajo crecimiento y la presión de las marcas blancas y los fármacos para adelgazar lo han frenado.'),
 'XLRE': ('Las inmobiliarias del S&P 500: torres, almacenes, centros de datos y viviendas.',
          'Las socimis reparten casi todo su beneficio y son sensibles a los tipos, así que el fondo suele subir cuando bajan los rendimientos de los bonos.'),
 'XLU': ('Eléctricas y gasistas: dividendos, regulación y ahora la demanda de energía de la IA.',
         'Era un sector de rentas parecido a un bono; ahora es en parte una apuesta por la inteligencia artificial, porque los centros de datos necesitan enormes cantidades de electricidad.'),
 'XLY': ('El consumo discrecional del S&P 500, dominado por Amazon y Tesla.',
         'Tiene minoristas, fabricantes de coches, restaurantes y hoteles, pero Amazon y Tesla pesan tanto que se comporta más como un fondo de gran tecnología que como una apuesta por el '
         'consumidor.'),
 'XOP': ('Productoras de petróleo y gas de EE. UU. con el mismo peso: casi una apuesta directa al precio del crudo.',
         'Las pequeñas del esquisto pesan tanto como las grandes, así que se mueve más con el petróleo que XLE, dominado por Exxon y Chevron.')})
UCITS.update({'A UCITS 0-5 year USD corporate bond ETF': 'un ETF UCITS de bonos corporativos en dólares a 0-5 años',
 'A UCITS 1-3 year US Treasury ETF': 'un ETF UCITS de bonos del Tesoro de EE. UU. a 1-3 años',
 'A UCITS 20+ year US Treasury ETF': 'un ETF UCITS de bonos del Tesoro de EE. UU. a más de 20 años',
 'A UCITS 7-10 year US Treasury ETF': 'un ETF UCITS de bonos del Tesoro de EE. UU. a 7-10 años',
 'A UCITS ETF tracking the whole US market': 'un ETF UCITS de todo el mercado estadounidense',
 'A UCITS US TIPS ETF': 'un ETF UCITS de bonos ligados a la inflación de EE. UU.',
 'A UCITS US Treasury ETF': 'un ETF UCITS de bonos del Tesoro de EE. UU.',
 'A UCITS US communication services sector ETF': 'un ETF UCITS del sector de comunicaciones de EE. UU.',
 'A UCITS US consumer discretionary sector ETF': 'un ETF UCITS de consumo discrecional de EE. UU.',
 'A UCITS US consumer staples sector ETF': 'un ETF UCITS de consumo básico de EE. UU.',
 'A UCITS US materials sector ETF': 'un ETF UCITS de materiales de EE. UU.',
 'A UCITS US property ETF': 'un ETF UCITS inmobiliario de EE. UU.',
 'A UCITS US utilities sector ETF': 'un ETF UCITS de servicios públicos de EE. UU.',
 'A UCITS USD corporate bond ETF': 'un ETF UCITS de bonos corporativos en dólares',
 'A UCITS USD high yield bond ETF': 'un ETF UCITS de bonos de alto rendimiento en dólares',
 'A UCITS aerospace and defence ETF': 'un ETF UCITS de aeroespacial y defensa',
 'A UCITS cybersecurity ETF': 'un ETF UCITS de ciberseguridad',
 'A UCITS developed-markets ex-US ETF': 'un ETF UCITS de mercados desarrollados sin EE. UU.',
 'A UCITS ex-US world ETF': 'un ETF UCITS mundial sin EE. UU.',
 'A UCITS short-term US aggregate bond ETF': 'un ETF UCITS de bonos agregados de EE. UU. a corto plazo',
 'A UCITS ultrashort US Treasury ETF': 'un ETF UCITS de letras del Tesoro de EE. UU. a muy corto plazo',
 'Choose one matching the 3-10 year maturity range.': 'Elige uno con vencimientos de 3 a 10 años.',
 'European bank ETFs hold European banks.': 'Los ETF europeos de bancos tienen bancos europeos.',
 'European biotech ETFs are weighted by size.': 'Los ETF europeos de biotecnología ponderan por tamaño.',
 'European energy ETFs are dominated by the integrated majors.': 'Los ETF europeos de energía están dominados por las grandes petroleras integradas.',
 'European funds mix in European defence companies.': 'Los fondos europeos incluyen también empresas de defensa europeas.',
 'European investors use physically backed gold ETCs': 'los inversores europeos usan ETC de oro físico',
 'European investors use physically backed silver ETCs': 'los inversores europeos usan ETC de plata física',
 'Few European funds exclude the US; most investors use a world fund instead.': 'Pocos fondos europeos excluyen EE. UU.; la mayoría usa un fondo mundial.',
 'Few European funds hold small US companies; an S&P 500 fund is the usual substitute.': 'Pocos fondos europeos tienen pequeñas empresas de EE. UU.; lo habitual es un fondo del S&P 500.',
 'No UCITS equivalent': 'no hay equivalente UCITS',
 'No exact UCITS equivalent': 'no hay un equivalente UCITS exacto',
 'Several providers offer 0-1 or 0-3 month Treasury funds in Europe.': 'Varias gestoras ofrecen en Europa fondos de letras a 0-1 o 0-3 meses.',
 'Several providers offer one.': 'Lo ofrecen varias gestoras.',
 'The tax exemption only benefits US taxpayers.': 'La exención fiscal solo beneficia a quien tributa en EE. UU.',
 'UCITS rules do not permit a single-commodity fund.': 'Las normas UCITS no permiten un fondo de una sola materia prima.',
 'iShares and others list one in Europe.': 'iShares y otras gestoras cotizan uno en Europa.'})
