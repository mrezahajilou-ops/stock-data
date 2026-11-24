# -*- coding: utf-8 -*-
"""Os maiores ETFs do mundo, descritos em português para bolsagaviao.com.

Escrito em português, não traduzido: o leitor está em São Paulo, em Lisboa ou em Luanda, e a
pergunta que ele traz não é a mesma. O europeu vai ter a ordem recusada e precisa saber por quê; o
brasileiro não, porque os grandes ETFs americanos têm BDR na B3 e também podem ser comprados numa
conta no exterior.

Os números não estão aqui. Preço, rentabilidade, carteira e múltiplos são calculados todo dia em
etf_data.py.
"""

UI = dict(
    home='Início', etfs='ETFs', other='Outros', fundcol='Fundo',
    ps='Preço / receita', growth='Crescimento da receita, último ano',
    margin='Margem líquida', score='Nossa nota média',
    no_pe_h='Por que aqui não há P/L',
    in_europe='Se você está na Europa:',
    more_exp='mais caro', cheaper='mais barato',
    shariah='Alternativa compatível com a sharia',
    vs_sp='O S&P 500 pela mesma medida está em %(sp)s vezes, então este fundo está %(diff)s %(dir)s.',
    priips='%(fund)s é domiciliado nos Estados Unidos. Fundos americanos não publicam o documento de '
           'informações fundamentais exigido pela regra europeia, então um investidor de varejo da '
           'União Europeia ou do Reino Unido não consegue comprá-lo: a ordem é recusada, em qualquer '
           'corretora. No Brasil e em boa parte da América Latina, do Oriente Médio e da Ásia, ele pode '
           'ser comprado por meio de uma corretora internacional, seguindo as regras locais de cada país.',
    note_tbl='A coluna do P/L é calculada com as empresas que cada fundo tem, ponderadas pelos pesos '
             'do próprio fundo e com os mesmos números das nossas páginas de ações. Fica em branco '
             'quando o fundo não tem ações e quando é formado sobretudo por empresas listadas fora dos '
             'Estados Unidos, que não cobrimos.',
    i_title='Os {N} maiores ETFs: carteira, P/L e rentabilidade',
    i_desc='Os {N} maiores ETFs do mundo com carteira, pesos e rentabilidade em 12 meses, e um P/L '
           'calculado com as empresas que cada um realmente tem dentro.',
    d_title='ETF %(t)s: carteira, P/L e rentabilidade',
    d_desc='%(name)s (%(t)s): carteira, pesos e rentabilidade, com um P/L calculado a partir das '
           'empresas que ele tem dentro. %(idea)s',
    h1='Os {N} maiores ETFs do mundo',
    sub='Carteira, pesos e valuation · atualizado',
    lead='Os {N} maiores fundos de índice negociados em bolsa do mundo: para que serve cada um, o '
         'que ele tem dentro e quanto valem as empresas que o compõem.',
    intro='O P/L destas páginas não é publicado pelo fundo. Cada posição é cruzada com a nossa própria '
          'página daquela empresa e os números são ponderados pelos pesos do próprio fundo, então o '
          'P/L de um ETF aqui sai dos mesmos relatórios à SEC que qualquer página de ação deste site '
          '— e dá para clicar em qualquer posição para ler sobre a empresa.',
    idea='A ideia',
    ret='Rentabilidade',
    fund='Quanto valem as empresas que ele tem dentro',
    holds='Maiores posições',
    made='Do que ele é feito',
    where='Dá para comprar onde você mora?',
    faq='Perguntas frequentes',
    company='Empresa',
    weight='Peso',
    all50='Os {N} fundos, lado a lado',
    y1='1 ano', y3='3 anos', ytd='No ano', m1='Último mês', m3='3 meses', y5='5 anos',
    price='Preço', pe='P/L', holdings='Posições',
    chartcap='Rentabilidade dos últimos 12 meses, todos os fundos desta página. Toque numa barra para abri-lo.',
    linecap='Preço desde %(year)s. Não inclui dividendos.',
    note_ret='Somente a variação do preço. Um fundo que distribui dividendos rendeu mais do que isso; '
             'um que os reinveste, não.',
    note_pe='Não tiramos esse número do fundo. Cada posição é cruzada com a nossa página daquela '
            'empresa e os números são ponderados pelos pesos do próprio fundo, então eles saem dos '
            'mesmos relatórios que o resto do site. Cobrimos %(cov)s do fundo por peso (%(n)s de %(total)s posições).',
    note_holds='As %(n)d maiores de %(total)s posições, segundo a carteira publicada pelo fundo%(asof)s. Os nomes '
               'com link têm página completa neste site.',
    note_ctry='A situação geral, não uma recomendação sobre uma corretora específica nem sobre impostos. '
              'Quando um fundo não pode ser comprado, quem impede é a regra europeia do documento de '
              'informações fundamentais, não a corretora.',
    no_pe_bond='Este fundo não tem ações de empresas, então não há lucro pelo qual dividir o preço. O '
               'que importa nele é para quem ele empresta e por quanto tempo: qualidade de crédito e '
               'duration num fundo de títulos, e o preço do próprio ativo no ouro ou no bitcoin. Ele '
               'tem %(n)s posições.',
    no_pe_thin='Nossos dados de empresas cobrem companhias listadas nos Estados Unidos. Este fundo tem '
               '%(n)s posições e só %(cov)s do seu peso está em empresas que cobrimos, então um P/L '
               'calculado com essa parte descreveria um pedaço do fundo, e não o fundo. Preferimos '
               'omiti-lo a publicar um número que parece uma resposta. A carteira e os pesos abaixo, '
               'esses sim, são os do próprio fundo.',
    dis='Carteira segundo os relatórios do próprio fundo; números das empresas segundo os relatórios '
        'delas à SEC, recalculados todo dia. Conteúdo educativo, não é recomendação de investimento.',
    groups=[
        ('Mercado americano', ['US large cap', 'US total market']),
        ('Crescimento e valor', ['US large cap growth', 'US mega cap growth', 'US large cap value', 'US quality factor']),
        ('Dividendos', ['US dividend', 'US dividend growth']),
        ('Empresas menores', ['US mid cap', 'US small cap']),
        ('Fora dos Estados Unidos', ['developed ex-US', 'global ex-US', 'global', 'emerging markets', 'Europe']),
        ('Setores', ['technology', 'semiconductors', 'financials', 'healthcare', 'energy', 'industrials', 'real estate']),
        ('Títulos, ouro e bitcoin', ['US investment grade bonds', 'international bonds', 'gold', 'bitcoin']),
    ],
)

T = {
 'VOO': ('As 500 maiores empresas dos Estados Unidos, com o menor custo do mercado.',
         'Tem todas as empresas do S&P 500 na proporção do seu valor de mercado, então as maiores '
         'mandam. Não há julgamento humano: uma empresa entra quando o comitê do índice a inclui e sai '
         'quando ele a retira. Como os pesos seguem o valor de mercado, perto de um terço do fundo está '
         'nas dez maiores — bem mais concentrado do que quase todo mundo imagina.'),
 'IVV': ('As mesmas 500 empresas do VOO, de outra gestora e com o mesmo custo.',
         'Replica o S&P 500 com todos os componentes no peso do índice. Para quem vai manter por anos, '
         'escolher entre ele e o VOO depende da corretora que você usa e de qual tem o melhor spread '
         'naquele dia, não de alguma coisa que diferencie os fundos.'),
 'SPY': ('O fundo original do S&P 500: o papel mais negociado do mundo.',
         'É o ETF mais antigo dos Estados Unidos e foi constituído como unit investment trust, não como '
         'fundo moderno, o que significa que não pode emprestar ativos nem reinvestir os dividendos '
         'entre um pagamento e outro. Isso custa um pouco por ano a quem o mantém, em comparação com '
         'VOO e IVV. Em troca, tem uma liquidez e um mercado de opções incomparáveis, e é por isso que '
         'os traders o usam — e por isso o investidor de longo prazo normalmente não deveria.'),
 'VTI': ('Todas as empresas listadas investíveis dos Estados Unidos, numa única posição.',
         'Tem milhares de empresas, das maiores às pequenas, ponderadas pelo valor de mercado. Na '
         'prática se comporta quase igual a um fundo do S&P 500, porque as pequenas que fazem a '
         'diferença somam, juntas, poucos pontos percentuais. A diferença aparece naqueles períodos '
         'raros em que as small caps lideram.'),
 'QQQ': ('As 100 maiores empresas não financeiras da Nasdaq: na prática, uma aposta na grande tecnologia.',
         'Segue o Nasdaq-100, que exclui completamente as financeiras e se define pela bolsa onde a '
         'empresa é listada, não pelo que ela faz. Esse acidente de construção explica por que ele é '
         'tão concentrado em tecnologia e por que às vezes bateu o S&P 500 e outras vezes caiu muito '
         'mais. As dez primeiras posições costumam somar cerca de metade do fundo.'),
 'VUG': ('A metade de maior crescimento das grandes empresas americanas, segundo uma definição por regras.',
         'Divide o mercado americano de grandes empresas entre crescimento e valor usando o crescimento '
         'do lucro, o da receita e o valor patrimonial, e fica com o lado do crescimento ponderado pelo '
         'valor de mercado. Como as maiores empresas de tecnologia pontuam como crescimento, o fundo '
         'acaba muito concentrado nelas: parece mais com o QQQ do que o nome sugere.'),
 'VTV': ('A metade mais barata das grandes empresas americanas: bancos, saúde e indústria.',
         'A outra metade da mesma divisão que produz o VUG. Tem grandes empresas americanas que pontuam '
         'como valor por preço sobre valor patrimonial, P/L e dividend yield, ponderadas pelo valor de '
         'mercado. O resultado é um fundo com muito mais bancos, saúde e energia, bem menos tecnologia '
         'que o S&P 500 e um dividendo mais alto.'),
 'VIG': ('Empresas que aumentam o dividendo há pelo menos dez anos seguidos.',
         'Filtra por um histórico longo e ininterrupto de aumentos do dividendo e depois descarta o '
         'quarto de maior dividend yield entre as que passaram no filtro. Esse segundo passo é o mais '
         'inteligente: um dividend yield muito alto costuma ser sintoma de uma cotação que caiu, não de '
         'generosidade, e tirá-las evita quase todos os cortes. Sai um fundo de qualidade que também '
         'paga dividendo, não um fundo de renda alta.'),
 'SCHD': ('Cem pagadoras de dividendos filtradas pela solidez do balanço, não só pelo dividend yield.',
          'Exige dez anos consecutivos pagando dividendos e depois ordena o que sobra por fluxo de caixa '
          'sobre dívida, retorno sobre o patrimônio, dividend yield e crescimento do dividendo. Essa '
          'combinação deixa de fora as empresas que pagam um dividendo que não conseguem bancar, que é '
          'a falha típica dos fundos de renda alta. Os pesos têm teto para que nenhuma empresa ou '
          'setor domine.'),
 'VYM': ('A metade de maior dividend yield do mercado americano, ponderada pelo tamanho.',
         'Ordena as empresas americanas pelo dividend yield estimado e fica com a metade de cima por '
         'valor de mercado, excluindo os REITs. Não aplica nenhum filtro de qualidade, o que o torna '
         'mais simples e mais amplo que o SCHD, mas deixa dentro mais empresas cujo yield é alto porque '
         'a ação caiu.'),
 'DGRO': ('Empresas americanas que aumentam o dividendo há cinco anos e têm espaço para continuar.',
          'Exige cinco anos seguidos de crescimento do dividendo e um payout abaixo de 75%, o que descarta '
          'quem distribui mais do que consegue sustentar. Exclui o décimo de maior dividend yield pelo '
          'mesmo motivo do VIG. Mais amplo que o VIG e com um pouco mais de dividendo.'),
 'IWF': ('A metade de crescimento das mil maiores empresas americanas, segundo a Russell.',
         'A Russell divide seu universo de grandes empresas por valor patrimonial sobre preço e '
         'crescimento estimado, e permite que uma empresa fique parte em crescimento e parte em valor. '
         'O efeito prático é muito peso em tecnologia, parecido com o VUG, mas com outro calendário de '
         'rebalanceamento: a reconstituição anual da Russell, em junho, é um dos maiores eventos de '
         'negociação do ano.'),
 'IWD': ('A metade de valor das mil maiores empresas americanas.',
         'O espelho do IWF: as empresas que saem baratas por valor patrimonial sobre preço e têm baixo '
         'crescimento estimado. Dominam financeiras, saúde e indústria. Junto com o IWF, reconstrói o '
         'Russell 1000 inteiro.'),
 'IWM': ('Duas mil pequenas empresas americanas: o indicador mais usado das small caps.',
         'Vai da empresa número 1.001 até a 3.000 por valor de mercado. Uma parte importante do índice '
         'não dá lucro, e por isso ele se comporta de um jeito muito diferente dos índices de grandes: '
         'é mais sensível aos juros e à economia doméstica, e muito mais volátil.'),
 'IJH': ('As 400 empresas médias americanas que ficam entre o S&P 500 e as pequenas.',
         'O índice de mid caps da S&P exige lucro para entrar, coisa que os índices Russell não fazem. '
         'Essa única regra transformou historicamente as médias americanas num universo de qualidade '
         'melhor que o das pequenas, e explica boa parte da diferença de retorno de longo prazo entre '
         'as duas.'),
 'IJR': ('Seiscentas pequenas empresas americanas, filtradas por lucratividade.',
         'Segue o S&P SmallCap 600, que exige que a empresa dê lucro antes de entrar. Essa é a diferença '
         'principal em relação ao Russell 2000 e a razão de os dois índices de small caps terem se '
         'distanciado por longos períodos, apesar de cobrirem a mesma parte do mercado.'),
 'VO': ('Empresas médias americanas, definidas por onde caem no valor total do mercado.',
        'Fica com a faixa do mercado americano entre, aproximadamente, o percentil 70 e o 85 do valor '
        'acumulado. Sem filtro de lucratividade, ao contrário do índice de mid caps da S&P, então tem '
        'um conjunto mais amplo e de qualidade um pouco menor, a um custo menor.'),
 'VB': ('Pequenas empresas americanas, sem filtrar se dão lucro.',
        'Cobre a faixa de baixo do mercado americano por valor acumulado, com mais de mil empresas. Mais '
        'amplo e mais barato que o IJR, mas inclui empresas com prejuízo que o índice de small caps da '
        'S&P deixa de fora.'),
 'SPYM': ('O S&P 500 barato da State Street, feito para manter, não para operar.',
          'O mesmo índice do SPY numa estrutura de fundo moderna e com um custo muito menor. A State '
          'Street o lançou justamente porque a estrutura de trust do SPY o tornava pouco atraente para o '
          'longo prazo. Menos volume que o SPY, o que só importa para quem opera em tamanho grande.'),
 'RSP': ('As mesmas 500 empresas do S&P 500, mas todas com o mesmo peso.',
         'Dá a cada empresa cerca de 0,2% do fundo e rebalanceia a cada trimestre, o que vende '
         'sistematicamente o que subiu e compra o que caiu. Elimina por completo a concentração nas '
         'maiores: o efeito prático é uma inclinação para empresas médias e para valor. Bate o S&P 500 '
         'quando a alta se espalha pelo mercado e fica muito para trás quando poucos gigantes puxam.'),
 'QUAL': ('Empresas americanas com bom retorno sobre o patrimônio, lucros estáveis e pouca dívida.',
          'Ordena por três medidas — retorno sobre o patrimônio, variabilidade do lucro e dívida sobre '
          'patrimônio — e fica com as melhores dentro de cada setor, para que o fundo não vire uma '
          'aposta setorial por acidente. Historicamente, a qualidade aguentou melhor as quedas e ficou '
          'para trás nas recuperações bruscas.'),
 'MGK': ('Só as maiores empresas de crescimento dos Estados Unidos: o jeito mais concentrado de tê-las.',
         'Fica restrito ao extremo das mega caps do universo de crescimento, o que significa poucas '
         'dezenas de posições e uma concentração extrema nas maiores empresas de tecnologia. Mais '
         'concentrado que o QQQ e muito mais que o VUG. Só faz sentido para quem decidiu '
         'deliberadamente que quer essa exposição.'),
 'VV': ('A parte de grandes empresas do mercado americano, definida pelo tamanho e não por um comitê.',
        'Cobre os 85% de cima do mercado americano por valor acumulado, então tem mais empresas que o '
        'S&P 500 e dispensa o comitê que decide quem entra nele. Na prática, o retorno segue o S&P 500 '
        'muito de perto.'),
 'ITOT': ('O mercado americano inteiro num fundo, da BlackRock.',
          'Tem o mercado americano completo, das grandes às micro caps, no peso do índice. Concorrente '
          'direto do VTI, com praticamente a mesma exposição, o mesmo custo e o mesmo comportamento.'),
 'SCHX': ('As 750 maiores empresas americanas, com um dos menores custos que existem.',
          'Um fundo amplo de grandes empresas que cobre mais nomes que o S&P 500, com um custo no piso '
          'do mercado. Se comporta quase igual ao VV e ao S&P 500 em qualquer período relevante.'),
 'VEA': ('Empresas de países desenvolvidos fora dos Estados Unidos: Europa, Japão, Canadá, Austrália.',
         'Tem milhares de empresas de mercados desenvolvidos, excluindo os Estados Unidos, ponderadas '
         'pelo valor de mercado, o que faz do Japão e do Reino Unido posições grandes. Ao contrário da '
         'versão da MSCI, inclui o Canadá e a Coreia do Sul. O retorno depende muito do dólar: um dólar '
         'fraco ajuda e um dólar forte atrapalha.'),
 'VXUS': ('Todas as empresas investíveis do mundo fora dos Estados Unidos.',
          'Junta mercados desenvolvidos e emergentes fora dos Estados Unidos num único fundo, com pesos '
          'de mercado e vários milhares de empresas. Combinado com o VTI, monta uma carteira global '
          'completa com duas posições.'),
 'IEFA': ('Europa, Australásia e Extremo Oriente desenvolvidos: o índice internacional de referência.',
          'Segue o universo EAFE da MSCI, que exclui Estados Unidos e Canadá e cobre grandes, médias e '
          'pequenas. É a alocação internacional mais usada nas carteiras americanas e a referência '
          'contra a qual se mede os gestores internacionais.'),
 'VWO': ('Empresas de economias em desenvolvimento, dominadas por China, Índia e Taiwan.',
         'Tem empresas de mercados emergentes com peso de mercado, o que concentra o fundo num punhado '
         'de países e em poucas empresas muito grandes de tecnologia e internet. A FTSE classifica a '
         'Coreia do Sul como desenvolvida, então, ao contrário da versão da MSCI, este fundo não tem '
         'empresas coreanas. O Brasil é uma das posições de país relevantes.'),
 'IEMG': ('Emergentes segundo a definição da MSCI, que inclui a Coreia do Sul.',
          'A principal diferença em relação ao VWO é a classificação dos países: a MSCI trata a Coreia do '
          'Sul como emergente, então este fundo tem grandes empresas coreanas que o VWO não tem. Também '
          'desce mais até as small caps. No resto, os dois se comportam de forma parecida.'),
 'EFA': ('O fundo internacional original de desenvolvidos, só grandes e médias.',
         'Mais antigo e mais caro que o IEFA, cobre os mesmos mercados, mas sem as pequenas. Continua '
         'vivo pelo seu mercado de opções e pelo papel de índice de referência em mandatos '
         'institucionais, não porque seja o melhor fundo para manter.'),
 'VT': ('Todo o mercado de ações investível do planeta, numa única posição.',
        'Tem cerca de dez mil empresas de mercados desenvolvidos e emergentes com peso de mercado, o '
        'que hoje significa uns dois terços de Estados Unidos. É o mais perto que existe de ter a '
        'carteira global de mercado, e não exige decidir quanto alocar em país nenhum.'),
 'VGK': ('Empresas europeias, do Reino Unido e da Suíça aos países nórdicos.',
         'Exposição à Europa desenvolvida ponderada pelo mercado, o que concentra o fundo em poucas '
         'empresas muito grandes de farmácia, luxo, equipamentos para semicondutores e bancos. Os '
         'movimentos entre euro, libra e dólar explicam boa parte do retorno de qualquer ano.'),
 'VEU': ('O mundo fora dos Estados Unidos, só grandes e médias.',
         'Muito parecido com o VXUS, mas sem as pequenas, o que o deixa um pouco mais concentrado nas '
         'grandes multinacionais que dominam os índices fora dos Estados Unidos. Qualquer um dos dois '
         'cumpre a mesma função numa carteira.'),
 'VGT': ('Empresas americanas de tecnologia, incluindo fabricantes de hardware e semicondutores.',
         'Cobre o setor de tecnologia segundo a definição da MSCI, que inclui software, hardware e '
         'semicondutores, mas deixa de fora as grandes de internet e mídia, classificadas como serviços '
         'de comunicação, e também Amazon e Tesla, que são consumo. Essas exclusões importam mais do que '
         'as pessoas pensam e são a principal diferença em relação ao QQQ.'),
 'XLK': ('As empresas de tecnologia que estão no S&P 500, e só elas.',
         'Restrito aos membros do S&P 500 classificados como tecnologia, o que o torna muito mais '
         'concentrado que o VGT: costuma ter menos de 70 posições e as duas primeiras chegam perto de '
         '40% do fundo. As definições setoriais são revisadas de tempos em tempos, e essas revisões '
         'podem mudar o fundo de um dia para o outro.'),
 'SMH': ('As 25 maiores empresas de semicondutores listadas: o jeito mais concentrado de jogar o ciclo dos chips.',
         'Tem só 25 empresas, o que o torna extremamente concentrado: as duas ou três primeiras podem ser '
         'um terço do fundo. Inclui fabricantes estrangeiros por meio das suas listagens nos Estados '
         'Unidos, coisa que o SOXX historicamente não fazia. A demanda por semicondutores é cíclica, e '
         'este fundo se move muito mais que o mercado nas duas direções.'),
 'SOXX': ('Trinta empresas de semicondutores listadas nos Estados Unidos, um pouco mais distribuídas que o SMH.',
          'Segue um índice de semicondutores listados nos Estados Unidos com tetos que limitam quanto '
          'uma única posição pode pesar, então é menos carregado no topo que o SMH. A metodologia do '
          'índice mudou mais de uma vez, algo que vale saber antes de comparar o histórico dele com '
          'qualquer coisa.'),
 'XLF': ('Os bancos, seguradoras e empresas de pagamento que estão no S&P 500.',
         'Tem as financeiras do S&P 500 com pesos de mercado e tetos. Desde que o setor imobiliário foi '
         'separado num setor próprio, o fundo é uma aposta mais limpa em bancos, seguros e mercado de '
         'capitais. É muito sensível aos juros e às condições de crédito, que é exatamente o motivo para '
         'tê-lo ou para evitá-lo.'),
 'XLV': ('A grande saúde americana: farmacêuticas, equipamentos médicos, planos de saúde e distribuidoras.',
         'Cobre as empresas de saúde do S&P 500, o que mistura negócios muito diferentes: farmacêuticas '
         'que dependem de patentes, fabricantes de equipamentos estáveis e operadoras de planos de saúde '
         'cuja economia é decidida pela política pública. O preço dos remédios e a política de saúde '
         'nos Estados Unidos afetam todas, e por isso o setor se move com o noticiário político mais '
         'que a maioria.'),
 'XLE': ('O petróleo e o gás americanos, dominados por duas supergigantes.',
         'Tem as empresas de energia do S&P 500 e, como o setor é muito carregado no topo, as duas '
         'maiores petroleiras integradas costumam somar perto de 40% do fundo. É uma aposta direta no '
         'preço do petróleo, com a alavancagem operacional das produtoras por cima.'),
 'XLI': ('A indústria americana: aeroespacial, ferrovias, máquinas e os grandes conglomerados.',
         'Tem as industriais do S&P 500, um grupo realmente diverso, que vai de fornecedores de defesa '
         'com carteira de pedidos para vários anos a fabricantes de máquinas presos ao ciclo. É usado '
         'com frequência como forma direta de expressar uma visão sobre a indústria e o investimento em '
         'infraestrutura nos Estados Unidos.'),
 'VNQ': ('Imóveis americanos, por meio de REITs listados.',
         'Tem REITs americanos de data centers, galpões logísticos, torres de telecomunicações, '
         'residências, lojas e escritórios — o equivalente americano dos fundos imobiliários (FIIs). '
         'Como os REITs são obrigados a distribuir quase todo o lucro, o fundo paga um dividendo alto e '
         'é especialmente sensível aos juros: juros mais altos encarecem a dívida que financia os '
         'imóveis e, ao mesmo tempo, tornam esse dividendo menos atraente.'),
 'VHT': ('Todo o setor de saúde americano, incluindo as pequenas de biotecnologia.',
         'Mais amplo que o XLV porque vai além do S&P 500 até médias e pequenas, o que lhe dá uma cauda '
         'longa de empresas de biotecnologia. Essa cauda acrescenta volatilidade e a chance de retornos '
         'extraordinários que um fundo de saúde só de grandes não tem.'),
 'BND': ('O mercado americano de títulos com grau de investimento: dívida pública, hipotecária e corporativa.',
         'Tem milhares de títulos com grau de investimento no peso do índice, o que significa uns dois '
         'terços de dívida pública e de dívida hipotecária com garantia do governo. O preço cai quando '
         'os juros sobem e sobe quando caem; a duration de uns seis anos diz aproximadamente quanto. É '
         'o lastro padrão de uma carteira, não uma fonte de retorno.'),
 'AGG': ('O mesmo mercado de títulos americano do BND, da BlackRock.',
         'Segue o índice Bloomberg US Aggregate sem ajuste por free float. A diferença prática em '
         'relação ao BND é desprezível: um ajuste diferente e um custo marginalmente diferente. A '
         'escolha é por qual dos dois a sua corretora negocia mais barato.'),
 'BNDX': ('Títulos com grau de investimento de fora dos Estados Unidos, com hedge cambial.',
          'Tem dívida com grau de investimento não americana, sobretudo pública europeia e japonesa, e '
          'protege a exposição cambial contra o dólar. O hedge é o que importa: sem ele, um título '
          'estrangeiro é sobretudo uma aposta em moeda; com ele, vira um diversificador real frente aos '
          'juros americanos.'),
 'GLD': ('Ouro físico, guardado num cofre em Londres e dividido em cotas.',
         'Cada cota representa uma fração de onça de ouro em custódia alocada. Não há renda nem lucro: '
         'o retorno é o preço do ouro menos o custo de custódia, que é pago vendendo uma pequena '
         'quantidade de ouro todo ano, de modo que o ouro por cota diminui pouco a pouco. Nos Estados '
         'Unidos a tributação é diferente da das ações, o que importa em contas tributáveis.'),
 'IAU': ('O mesmo ouro físico do GLD, com um custo anual menor.',
         'Idêntico em substância ao GLD — ouro físico alocado, sem renda, custo pago em metal —, mas '
         'cobra menos, o que, composto ao longo de dez anos, dá uma diferença considerável. O GLD '
         'mantém mais volume e um mercado de opções mais profundo.'),
 'IBIT': ('Bitcoin nas mãos de um custodiante, comprado e vendido como uma ação.',
          'Tem bitcoin diretamente com um custodiante institucional, então a cotação segue o preço do '
          'bitcoin menos a taxa. Tira a necessidade de cuidar de chaves privadas ou de usar uma '
          'exchange, que é exatamente o motivo de ter captado dinheiro mais rápido que qualquer outro '
          'lançamento de ETF da história. O ativo por trás não gera fluxo de caixa, então não há nada '
          'contra o que avaliá-lo.'),
}

# Os países de quem lê esta edição, com a resposta em português. A regra europeia não é uma proibição
# ao fundo: falta um documento, e por isso a corretora recusa a ordem. No Brasil a resposta é outra,
# porque os grandes ETFs americanos têm BDR na B3.
UI.update({
    's_blocked': 'Não pode ser comprado',
    's_open': 'Pode ser comprado',
    's_local': 'Pode ser comprado, e também é negociado localmente',
    's_hard': 'Permitido, mas difícil na prática',
    's_sanctions': 'Inacessível',
    'c_Brazil': 'Brasil', 'c_Portugal': 'Portugal', 'c_United States': 'Estados Unidos',
    'c_Angola': 'Angola', 'c_Mozambique': 'Moçambique', 'c_Cape Verde': 'Cabo Verde',
    'w_Brazil': 'Os grandes ETFs americanos são negociados na B3 como BDR — certificados locais que '
                'representam o fundo no exterior — e podem ser comprados em reais em qualquer '
                'corretora brasileira. O próprio fundo pode ser comprado em dólares numa conta no '
                'exterior (Avenue, Nomad, Inter, XP e outras); aí entram o IOF e o spread do câmbio, e '
                'os dividendos sofrem retenção de 30% nos Estados Unidos, porque não há acordo '
                'tributário entre os dois países.',
    'w_Portugal': 'A regra europeia exige um documento de informações fundamentais numa língua oficial '
                  'da UE antes de vender um produto empacotado a um investidor de retalho. As gestoras '
                  'americanas não o produzem, então a ordem é recusada: em qualquer corretora, não só '
                  'na sua. O fundo europeu indicado acima segue o mesmo índice e é vendido com esse '
                  'documento.',
    'w_United States': 'O fundo é domiciliado aqui; compra-se como qualquer ação.',
    'w_Angola': 'Enviar kwanzas para o exterior é o obstáculo, não o fundo.',
    'w_Mozambique': 'As regras cambiais para mandar dinheiro para o exterior são o obstáculo, não o fundo.',
    'w_Cape Verde': 'Não se aplica nenhuma restrição europeia; acessível por corretoras internacionais.',
})

# colunas da caixa do índice: o tipo, a gramática do nome e a nota do P/L
UI.update({
    'type': 'Tipo',
    'avg_yr': 'Média anual',
    'pe_avg': 'P/L médio',
    'name_pattern': '%(index)s da %(issuer)s',
    'note_peavg': 'Ninguém publica um P/L histórico de um fundo, porque ele depende do que o fundo tinha dentro em cada momento. Por isso começamos a registrar o nosso em %(since)s. A coluna da média é preenchida quando houver cerca de um mês de dados.',
    'note_peavg_none': 'A coluna do P/L médio é preenchida à medida que registramos o número de cada dia.',
    'focus_labels': {'US large cap': 'Grandes EUA', 'US total market': 'Mercado total EUA', 'US large cap growth': 'Crescimento EUA', 'US mega cap growth': 'Mega caps de crescimento', 'US large cap value': 'Valor EUA', 'US quality factor': 'Qualidade EUA', 'US dividend': 'Dividendos EUA', 'US dividend growth': 'Dividendo crescente', 'US mid cap': 'Médias EUA', 'US small cap': 'Small caps EUA', 'developed ex-US': 'Desenvolvidos sem EUA', 'global ex-US': 'Global sem EUA', 'global': 'Global', 'emerging markets': 'Emergentes', 'Europe': 'Europa', 'technology': 'Tecnologia', 'semiconductors': 'Semicondutores', 'financials': 'Financeiras', 'healthcare': 'Saúde', 'energy': 'Energia', 'industrials': 'Indústria', 'real estate': 'Imobiliário', 'US investment grade bonds': 'Títulos EUA', 'international bonds': 'Títulos internacionais', 'gold': 'Ouro', 'bitcoin': 'Bitcoin'},
})

UI['pe_short'] = 'P/L'

# o texto da alternativa europeia de etf_list.py, no idioma desta edição
UCITS = {'VUAA accumulates dividends, VUSA pays them out.': 'O VUAA reinveste os dividendos; o VUSA os distribui.', 'The same index from the same manager, in a European wrapper.': 'O mesmo índice e a mesma gestora, em formato europeu.', 'No European fund replicates SPY’s trust structure, and none needs to.': 'Nenhum fundo europeu reproduz a estrutura de trust do SPY, e nenhum precisa.', 'Closest European equivalent; it includes Canada, which VTI does not.': 'O equivalente europeu mais próximo; inclui o Canadá, que o VTI não tem.', 'Both track the same index; CNDX accumulates, EQQQ distributes.': 'Os dois seguem o mesmo índice; o CNDX reinveste e o EQQQ distribui.', 'Several providers offer one; there is no single obvious equivalent.': 'Várias gestoras oferecem um; não há um único equivalente óbvio.', 'Available from several providers; check which value definition it uses.': 'Disponível em várias gestoras; veja qual definição de valor ele usa.', 'The ten-year increase screen is uncommon in European wrappers.': 'O filtro de dez anos de aumento do dividendo é raro em formato europeu.', 'Nothing in Europe replicates the Dow Jones 100 methodology exactly.': 'Na Europa não há nada que reproduza exatamente a metodologia do Dow Jones 100.', 'Global rather than US-only, but the same family and methodology.': 'Global em vez de só Estados Unidos, mas a mesma família e a mesma metodologia.', 'IWDA includes the US; VEVE ex-US variants differ by provider.': 'O IWDA inclui os Estados Unidos; as variantes sem EUA mudam conforme a gestora.', 'VWRL includes the US as well; there is no exact ex-US twin in the range.': 'O VWRL também inclui os Estados Unidos; na linha não há um gêmeo exato sem EUA.', 'World includes the US; EAFE-only UCITS versions exist but are less traded.': 'O índice mundial inclui os Estados Unidos; existem versões UCITS só de EAFE, mas são menos negociadas.', 'VWCE accumulates dividends, VWRL distributes them.': 'O VWCE reinveste os dividendos; o VWRL os distribui.', 'European equivalents are exchange-traded commodities, not UCITS funds.': 'Os equivalentes europeus são commodities negociadas em bolsa (ETC), não fundos UCITS.', 'UCITS rules do not permit a single-asset crypto fund.': 'As regras UCITS não permitem um fundo cripto de um único ativo.', 'A UCITS ETF tracking a US large-cap growth index': 'um ETF UCITS que siga um índice de crescimento de grandes empresas dos EUA', 'A UCITS ETF tracking a US large-cap value index': 'um ETF UCITS que siga um índice de valor de grandes empresas dos EUA', 'A UCITS ETF tracking a US dividend growth index': 'um ETF UCITS que siga um índice de dividendo crescente dos EUA', 'A UCITS ETF tracking a quality US dividend index': 'um ETF UCITS que siga um índice de dividendos de qualidade dos EUA', 'A UCITS ETF tracking the Russell 1000 Growth index': 'um ETF UCITS que siga o índice Russell 1000 Growth', 'A UCITS ETF tracking the Russell 1000 Value index': 'um ETF UCITS que siga o índice Russell 1000 Value', 'A UCITS ETF tracking the Russell 2000': 'um ETF UCITS que siga o Russell 2000', 'A UCITS ETF tracking the S&P MidCap 400': 'um ETF UCITS que siga o S&P MidCap 400', 'A UCITS ETF tracking the S&P SmallCap 600': 'um ETF UCITS que siga o S&P SmallCap 600', 'A UCITS ETF tracking a US mid-cap index': 'um ETF UCITS que siga um índice de empresas médias dos EUA', 'A UCITS ETF tracking a US small-cap index': 'um ETF UCITS que siga um índice de small caps dos EUA', 'A UCITS ETF tracking the S&P 500 Equal Weight index': 'um ETF UCITS que siga o S&P 500 Equal Weight', 'A UCITS ETF tracking a US mega-cap growth index': 'um ETF UCITS que siga um índice de mega caps de crescimento dos EUA', 'A UCITS ETF tracking US or world information technology': 'um ETF UCITS de tecnologia da informação, americana ou mundial', 'A UCITS ETF tracking global semiconductors': 'um ETF UCITS de semicondutores globais', 'A UCITS ETF tracking US or developed-market property': 'um ETF UCITS imobiliário, americano ou de mercados desenvolvidos', 'A UCITS ETF tracking US health care': 'um ETF UCITS de saúde americana', 'European investors use exchange-traded products rather than UCITS funds': 'os investidores europeus usam produtos negociados em bolsa (ETP) em vez de fundos UCITS', 'A EUR-hedged global aggregate bond UCITS ETF': 'um ETF UCITS de títulos globais com hedge para o euro', 'A USD-hedged global or US aggregate bond UCITS ETF': 'um ETF UCITS de títulos globais ou americanos com hedge para o dólar', 'Screened US dividend UCITS funds': 'fundos UCITS filtrados de dividendos americanos'}

UCITS.update({'Invesco EQQQ Nasdaq-100 UCITS ETF, or iShares Nasdaq 100 UCITS ETF': 'Invesco EQQQ Nasdaq-100 UCITS ETF ou iShares Nasdaq 100 UCITS ETF', 'Vanguard FTSE Developed World UCITS ETF, or iShares Core MSCI World': 'Vanguard FTSE Developed World UCITS ETF ou iShares Core MSCI World', 'Vanguard FTSE Emerging Markets UCITS ETF, or iShares Core MSCI EM IMI': 'Vanguard FTSE Emerging Markets UCITS ETF ou iShares Core MSCI EM IMI'})

# layout do celular: ranking de rentabilidade, busca de fundos, atalhos (etf_pages.py, web_src/etfm.*)
UI.update({'rank_h': 'Ranking de rentabilidade', 'rank_all': 'Ver os %(n)s fundos ▾', 'rank_less': 'Ver só os 10 primeiros ▴', 'rank_note': 'Rentabilidade do preço, sem dividendos. Toque num fundo para abrir a página dele.', 'find_ph': 'Busque entre os {N} fundos: ticker, nome ou tipo', 'sort_big': 'Maiores', 'sort_pe': 'Menor P/L', 'n_funds': '%n fundos', 'no_fund': 'Nenhum fundo corresponde à busca.', 'more': 'Ler mais ▾', 'less': 'Ver menos ▴', 'holds_all': 'Ver as %(n)s posições ▾', 'holds_less': 'Ver só as 10 primeiras ▴', 'k_idea': 'Ideia', 'k_val': 'Valuation', 'k_ret': 'Rentabilidade', 'k_hold': 'Carteira', 'k_sec': 'Seções da página', 'k_find': 'Buscar', 'k_ph': 'Busque qualquer ação ou ETF', 'k_none': 'Nenhum resultado', 'l_y1': 'Último ano', 'l_avg': 'Média anual', 'l_hold': 'Posições', 'l_pe': 'P/L'})

# ---- fundos 51-100 (nov 2026)
UI['focus_labels'].update({'US treasury bonds': 'Treasuries EUA', 'US corporate bonds': 'Títulos corporativos EUA', 'high yield bonds': 'High yield', 'municipal bonds': 'Títulos municipais', 'US covered call': 'Renda com opções', 'consumer discretionary': 'Consumo discricionário', 'consumer staples': 'Consumo básico', 'utilities': 'Utilidades públicas', 'materials': 'Materiais', 'communication services': 'Comunicações', 'biotech': 'Biotecnologia', 'aerospace and defense': 'Aeroespacial e defesa', 'banks': 'Bancos', 'gold miners': 'Mineradoras de ouro', 'oil and gas': 'Petróleo e gás', 'cybersecurity': 'Cibersegurança', 'clean energy': 'Energia limpa', 'innovation': 'Inovação', 'US momentum': 'Momentum EUA', 'US low volatility': 'Baixa volatilidade EUA', 'Japan': 'Japão', 'China': 'China', 'India': 'Índia', 'Brazil': 'Brasil', 'silver': 'Prata', 'ether': 'Ether'})
_G = UI['groups']
_G[1][1].extend(['US momentum', 'US low volatility'])
_G[2][1].append('US covered call')
_G[4][1].extend(['Japan', 'China', 'India', 'Brazil'])
_G[5][1].extend(['consumer discretionary', 'consumer staples', 'utilities', 'materials', 'communication services', 'biotech', 'aerospace and defense', 'banks', 'gold miners', 'oil and gas', 'cybersecurity', 'clean energy', 'innovation'])
_G[6][1].extend(['US treasury bonds', 'US corporate bonds', 'high yield bonds', 'municipal bonds', 'silver', 'ether'])
T.update({'ACWI': ('Cerca de 2.500 empresas grandes e médias de mercados desenvolvidos e emergentes.',
          'É a bolsa mundial por tamanho, com perto de dois terços nos EUA: uma carteira global num fundo, parecida com o VT, mas sem as pequenas.'),
 'ARKK': ('A aposta ativa e concentrada de Cathie Wood em tecnologia disruptiva.',
          'Tem poucas dezenas de empresas escolhidas pela gestora; subiu mais de 150% em 2020 e caiu cerca de 75% a partir do pico.'),
 'BIL': ('Letras do Tesouro americano de um a três meses: o ETF de caixa mais antigo.',
         'Faz o mesmo que o SGOV com uma taxa um pouco maior e distribui os juros todo mês. O histórico longo o torna a referência do rendimento do caixa em dólar.'),
 'BSV': ('Títulos curtos do governo e de grandes empresas dos EUA num único fundo barato.',
         'Títulos de um a cinco anos, dois terços públicos e um terço corporativos de qualidade: um passo conservador além do caixa.'),
 'CIBR': ('Empresas de cibersegurança, do software aos equipamentos de rede.',
          'Inclui CrowdStrike, Palo Alto Networks e Cisco, com teto para as maiores. O gasto com segurança resistiu mesmo com orçamentos de TI fracos.'),
 'EEM': ('O ETF original de emergentes, mais usado por traders que por investidores de longo prazo.',
         'Custa mais que IEMG e VWO, que têm quase as mesmas empresas, mas é o mais líquido para operar e para opções.'),
 'ETHA': ('Ether à vista, a moeda da rede Ethereum, numa conta de corretora comum.', 'O ether é mais volátil que o bitcoin e seu valor depende da atividade na rede Ethereum.'),
 'EWJ': ('Empresas japonesas grandes e médias.',
         'Toyota, Sony e Mitsubishi UFJ, entre outras. Para quem investe em dólar, o retorno depende da bolsa japonesa e do iene, que está fraco há anos.'),
 'EWZ': ('As maiores empresas do Brasil: commodities, bancos e dividendo alto.', 'Dominado por Petrobras, Vale e Itaú; oscila com as commodities, o real e a política brasileira. Para quem já tem ações na B3, é exposição repetida, não diversificação.'),
 'FBTC': ('Bitcoin à vista custodiado pela própria Fidelity, o segundo maior ETF de bitcoin.',
          'A Fidelity atua como sua própria custodiante, em vez de depender de uma exchange; o preço segue o bitcoin menos a taxa.'),
 'FXI': ('As 50 maiores empresas chinesas listadas em Hong Kong.',
         'Mais concentrado que o MCHI, com muito peso em bancos, plataformas de internet e estatais; é usado para apostar em estímulos ou em notícias de tarifas.'),
 'GDX': ('Mineradoras de ouro: um jeito alavancado de ter ouro.', 'Como os custos são em boa parte fixos, o lucro delas sobe mais rápido que o ouro — e também cai mais rápido.'),
 'GLDM': ('Ouro físico com taxa e preço por cota menores que os do GLD.',
          'Guarda barras em Londres como o GLD, mas cobra muito menos, o que pesa no longo prazo; o GLD continua sendo o preferido dos grandes operadores pela liquidez.'),
 'HYG': ('Títulos high yield: mais renda por emprestar a empresas americanas mais arriscadas.',
         'O rendimento é alto porque alguns emissores quebram; numa recessão ele pode cair quase tanto quanto a bolsa, então é mais um híbrido de ação e título que um ativo seguro.'),
 'IBB': ('Empresas americanas de biotecnologia ponderadas pelo tamanho, lideradas pelas grandes com produtos no mercado.', 'Amgen, Gilead e Vertex pesam muito, o que o torna mais estável que o XBI.'),
 'ICLN': ('Empresas de energia solar, eólica e renovável do mundo todo.',
          'Depende muito dos juros e dos subsídios: disparou em 2020 e depois perdeu quase todo o ganho quando os juros subiram.'),
 'IEF': ('Treasuries de dez anos: o hedge clássico de uma carteira contra a recessão.',
         'O preço muda 7% a 8% para cada ponto percentual que os juros longos se movem. Costuma subir quando a bolsa cai por medo de crescimento e cair quando a inflação empurra os juros, como em 2022.'),
 'INDA': ('Empresas indianas grandes e médias.',
          'HDFC Bank, Reliance, Infosys e ICICI Bank. O crescimento rápido da Índia deu à sua bolsa um dos valuations mais altos do mundo, o que deixa menos margem para erro.'),
 'ITA': ('Fornecedores de defesa e fabricantes de aviões dos EUA.', 'Os orçamentos de defesa trazem contratos longos e visibilidade; a parte comercial segue o tráfego aéreo.'),
 'IXUS': ('Todas as bolsas do mundo, menos a americana, num fundo barato.',
          'É o equivalente da iShares ao VXUS e o complemento habitual de um fundo americano numa carteira de dois fundos.'),
 'JEPI': ('Ações americanas defensivas mais renda com opções: um pagamento mensal alto em troca de limitar a alta.',
          'Vende opções de compra e transforma parte dos ganhos futuros em renda mensal. Cai menos nas correções, mas fica muito para trás nas altas fortes: parte do rendimento alto é a própria alta do investidor sendo devolvida.'),
 'JEPQ': ('Ações do Nasdaq-100 mais renda com opções: rendimento de dois dígitos com menos alta que o QQQ.',
          'O pagamento é alto porque as opções da Nasdaq são caras, mas num rali forte de tecnologia o fundo fica só com parte do ganho.'),
 'JNK': ('Títulos high yield da State Street, o grande rival do HYG.', 'Acompanha o HYG muito de perto; as diferenças vêm de pequenas regras do índice e das taxas.'),
 'KRE': ('Bancos regionais americanos com o mesmo peso: uma aposta na economia interna e na curva de juros.',
         'Ganham com a diferença entre o que pagam pelos depósitos e o que cobram nos empréstimos, e têm crédito imobiliário comercial, então são muito sensíveis aos juros e aos sustos de crédito, como mostrou 2023.'),
 'LQD': ('O fundo de títulos corporativos americanos mais negociado, com vencimentos longos.',
         'Combina crédito corporativo e duration longa, então oscila mais que o VCIT. Os institucionais o usam para operar o mercado de crédito com rapidez.'),
 'MCHI': ('Empresas chinesas listadas em Hong Kong, nos EUA e na China continental.',
          'Tencent, Alibaba, PDD e Meituan. Depende do crescimento chinês, da política de Pequim e da relação com os EUA tanto quanto dos resultados.'),
 'MTUM': ('Ações americanas com as maiores altas recentes, revisadas duas vezes por ano.',
          'Compra as empresas que mais subiram em seis a doze meses. Aproveita bem as tendências, mas sofre quando a liderança do mercado muda de repente.'),
 'MUB': ('Títulos isentos de impostos de estados e cidades americanos.',
         'Os juros são isentos do imposto federal americano, uma vantagem que só tem quem paga imposto nos EUA; para um investidor estrangeiro, o rendimento menor faz pouco sentido.'),
 'SCHB': ('Cerca de 2.500 empresas americanas, grandes e pequenas, quase de graça.', 'É a resposta da Schwab ao VTI e rende praticamente igual.'),
 'SCHF': ('Grandes empresas de países desenvolvidos fora dos EUA.', 'Europa, Japão, Reino Unido, Canadá e Austrália a custo muito baixo; alternativa ao VEA e ao IEFA com quase o mesmo retorno.'),
 'SCHG': ('Grandes empresas americanas de crescimento com um dos menores custos.',
          'Dominado pelas grandes de tecnologia, se comporta quase igual ao VUG e ao QQQ, com um pouco mais de amplitude que o QQQ.'),
 'SGOV': ('Letras do Tesouro americano de menos de três meses: um substituto do caixa que paga os juros de curto prazo.',
          'Só tem letras com menos de três meses até o vencimento, então o preço quase não se move e o rendimento é a taxa básica do Federal Reserve menos uma pequena taxa. Quando o Fed corta juros, o rendimento cai quase na hora.'),
 'SHV': ('Treasuries de menos de um ano: caixa com um pouco mais de rendimento.',
         'Tem letras e notas com menos de doze meses até o vencimento. Reage um pouco mais aos juros que um fundo de três meses, mas continua sendo lugar para dinheiro que não pode perder valor.'),
 'SHY': ('Treasuries de um a três anos: pouco risco e um pequeno ganho se os juros caírem.',
         'O preço se move cerca de 2% para cada ponto que os juros mudam, então ganha um pouco quando o Fed corta e perde um pouco quando sobe.'),
 'SLV': ('Prata física guardada em cofres.', 'A prata é em parte metal precioso e em parte metal industrial para painéis solares e eletrônicos, o que a torna mais volátil que o ouro.'),
 'TIP': ('Treasuries protegidos contra a inflação: o principal sobe com o índice de preços ao consumidor.',
         'Ganham dos títulos comuns quando a inflação surpreende para cima, mas continuam caindo quando os juros reais sobem, algo que surpreendeu muita gente em 2022. É o primo americano do Tesouro IPCA+.'),
 'TLT': ('Treasuries de mais de vinte anos: uma aposta alavancada na queda dos juros, sem risco de crédito.',
         'Um ponto a menos nos juros longos o faz subir cerca de 16%, e um ponto a mais custa o mesmo; por isso perdeu quase metade do valor entre 2020 e 2023.'),
 'USMV': ('Ações americanas combinadas para oscilar o mínimo possível.',
          'Se inclina para elétricas, consumo básico e saúde; costuma cair menos nas correções e ficar para trás nas altas fortes.'),
 'VCIT': ('Títulos de cinco a dez anos de grandes empresas americanas: mais rendimento que os Treasuries, com algum risco de crédito.',
          'Cobra-se um spread sobre os Treasuries por emprestar a empresas; numa recessão esse spread se abre e o fundo cai mesmo que os títulos públicos subam.'),
 'VCSH': ('Títulos curtos de grandes empresas americanas: um pouco mais de rendimento que o caixa.',
          'Os vencimentos curtos mantêm pequenos o risco de juros e as perdas com calotes, então em tempos normais se comporta como um fundo DI em dólar com mais rendimento.'),
 'VGIT': ('Treasuries de três a dez anos, com o custo baixo da Vanguard.',
          'Ocupa o meio da curva, entre o SHY e o IEF em sensibilidade aos juros, e é um núcleo comum para quem quer títulos públicos sem as oscilações dos longos.'),
 'VTEB': ('A cesta barata da Vanguard de títulos municipais isentos de impostos.',
          'Como o MUB, só faz sentido para quem paga imposto nos EUA, para quem a renda isenta vale mais que o rendimento maior de um título tributado.'),
 'XBI': ('Empresas americanas de biotecnologia com o mesmo peso cada uma: uma aposta nas pequenas e nas aquisições.',
         'As pequenas em fase clínica pesam tanto quanto as grandes, então ele pode subir ou cair 50% num ano conforme os juros, os estudos clínicos e as aquisições.'),
 'XLB': ('Químicas, gases industriais, metais e embalagens do S&P 500.',
         'O lucro segue a demanda industrial e as commodities, então é cíclico e costuma ir melhor no começo de uma recuperação.'),
 'XLC': ('Meta, Alphabet, Netflix e as teles do S&P 500.', 'Meta e Alphabet são quase metade do fundo, então o retorno depende sobretudo da publicidade digital.'),
 'XLP': ('Alimentos, bebidas, produtos de casa e supermercados: o que se compra quando a economia preocupa.',
         'A demanda é estável na recessão, o que o torna defensivo, embora o baixo crescimento e a pressão das marcas próprias e dos remédios para emagrecer o tenham freado.'),
 'XLRE': ('As imobiliárias do S&P 500: torres, galpões, data centers e residências.',
          'Os REITs distribuem quase todo o lucro e são sensíveis aos juros, então o fundo costuma subir quando o rendimento dos títulos cai.'),
 'XLU': ('Elétricas e distribuidoras de gás: dividendos, regulação e agora a demanda de energia da IA.',
         'Era um setor de renda parecido com um título; agora é em parte uma aposta em inteligência artificial, porque os data centers precisam de quantidades enormes de eletricidade.'),
 'XLY': ('O consumo discricionário do S&P 500, dominado por Amazon e Tesla.',
         'Tem varejistas, montadoras, restaurantes e hotéis, mas Amazon e Tesla pesam tanto que ele se comporta mais como um fundo de grande tecnologia que como uma aposta no consumidor.'),
 'XOP': ('Produtoras americanas de petróleo e gás com o mesmo peso: quase uma aposta direta no preço do petróleo.',
         'As pequenas do xisto pesam tanto quanto as grandes, então ele se move mais com o petróleo que o XLE, dominado por Exxon e Chevron.')})
UCITS.update({'A UCITS 0-5 year USD corporate bond ETF': 'um ETF UCITS de títulos corporativos em dólar de 0 a 5 anos',
 'A UCITS 1-3 year US Treasury ETF': 'um ETF UCITS de Treasuries de 1 a 3 anos',
 'A UCITS 20+ year US Treasury ETF': 'um ETF UCITS de Treasuries de mais de 20 anos',
 'A UCITS 7-10 year US Treasury ETF': 'um ETF UCITS de Treasuries de 7 a 10 anos',
 'A UCITS ETF tracking the whole US market': 'um ETF UCITS de todo o mercado americano',
 'A UCITS US TIPS ETF': 'um ETF UCITS de títulos americanos atrelados à inflação',
 'A UCITS US Treasury ETF': 'um ETF UCITS de Treasuries',
 'A UCITS US communication services sector ETF': 'um ETF UCITS do setor de comunicações dos EUA',
 'A UCITS US consumer discretionary sector ETF': 'um ETF UCITS de consumo discricionário dos EUA',
 'A UCITS US consumer staples sector ETF': 'um ETF UCITS de consumo básico dos EUA',
 'A UCITS US materials sector ETF': 'um ETF UCITS de materiais dos EUA',
 'A UCITS US property ETF': 'um ETF UCITS imobiliário dos EUA',
 'A UCITS US utilities sector ETF': 'um ETF UCITS de utilidades públicas dos EUA',
 'A UCITS USD corporate bond ETF': 'um ETF UCITS de títulos corporativos em dólar',
 'A UCITS USD high yield bond ETF': 'um ETF UCITS de títulos high yield em dólar',
 'A UCITS aerospace and defence ETF': 'um ETF UCITS de aeroespacial e defesa',
 'A UCITS cybersecurity ETF': 'um ETF UCITS de cibersegurança',
 'A UCITS developed-markets ex-US ETF': 'um ETF UCITS de mercados desenvolvidos sem os EUA',
 'A UCITS ex-US world ETF': 'um ETF UCITS mundial sem os EUA',
 'A UCITS short-term US aggregate bond ETF': 'um ETF UCITS de títulos americanos agregados de curto prazo',
 'A UCITS ultrashort US Treasury ETF': 'um ETF UCITS de letras do Tesouro americano de prazo muito curto',
 'Choose one matching the 3-10 year maturity range.': 'Escolha um com vencimentos de 3 a 10 anos.',
 'European bank ETFs hold European banks.': 'Os ETFs europeus de bancos têm bancos europeus.',
 'European biotech ETFs are weighted by size.': 'Os ETFs europeus de biotecnologia ponderam pelo tamanho.',
 'European energy ETFs are dominated by the integrated majors.': 'Os ETFs europeus de energia são dominados pelas grandes petroleiras integradas.',
 'European funds mix in European defence companies.': 'Os fundos europeus incluem também empresas de defesa europeias.',
 'European investors use physically backed gold ETCs': 'os investidores europeus usam ETCs de ouro físico',
 'European investors use physically backed silver ETCs': 'os investidores europeus usam ETCs de prata física',
 'Few European funds exclude the US; most investors use a world fund instead.': 'Poucos fundos europeus excluem os EUA; a maioria usa um fundo mundial.',
 'Few European funds hold small US companies; an S&P 500 fund is the usual substitute.': 'Poucos fundos europeus têm small caps americanas; o substituto habitual é um fundo do S&P 500.',
 'No UCITS equivalent': 'não há equivalente UCITS',
 'No exact UCITS equivalent': 'não há um equivalente UCITS exato',
 'Several providers offer 0-1 or 0-3 month Treasury funds in Europe.': 'Várias gestoras oferecem na Europa fundos de letras de 0 a 1 ou de 0 a 3 meses.',
 'Several providers offer one.': 'Várias gestoras oferecem um.',
 'The tax exemption only benefits US taxpayers.': 'A isenção só beneficia quem paga imposto nos EUA.',
 'UCITS rules do not permit a single-commodity fund.': 'As regras UCITS não permitem um fundo de uma única commodity.',
 'iShares and others list one in Europe.': 'A iShares e outras gestoras listam um na Europa.'})

# ---- comparações e "quais ETFs têm"
UI.update({
    'c_title': '%(a)s vs %(b)s: qual ETF é melhor? Rentabilidade, P/L e sobreposição',
    'c_h1': '%(a)s vs %(b)s', 'c_crumb': '%(a)s vs %(b)s',
    'c_sub': 'Rentabilidade, valuation do que eles têm e quanto se sobrepõem, lado a lado.',
    'c_what': 'O que é cada um', 'c_side': 'Frente a frente', 'c_says': 'O que os números dizem',
    'c_shared': 'As maiores posições em comum', 'c_issuer': 'Gestora', 'c_index': 'Índice',
    'c_with': 'Comparar %(t)s com',
    'v_ret': '%(w)s rendeu mais nos últimos 12 meses: %(x)s contra %(y)s.',
    'v_pe': '%(w)s tem empresas mais baratas pelo nosso P/L: %(x)s contra %(y)s.',
    'v_ov': '%(ov)s de %(a)s, pelo peso das maiores posições, está em empresas que %(b)s também tem, então ter os dois diversifica menos do que parece.',
    'v_noov': '%(a)s e %(b)s não têm nenhuma das maiores posições em comum, então cumprem funções diferentes numa carteira.',
    'hold_slug': 'quais-etfs-tem-%s',
    'h_title': 'Quais ETFs têm %(name)s (%(t)s)? Pesos e rentabilidade',
    'h_h1': 'Quais ETFs têm ações da %(name)s?',
    'h_lead': '%(n)s dos %(N)s ETFs que cobrimos têm %(name)s entre as maiores posições.',
    'h_top': 'O maior peso está no %(f)s, onde %(name)s representa %(w)s do fundo.',
    'h_stock': 'Leia nossa análise completa de %(name)s ›',
    'h_note': 'Segundo a carteira publicada por cada fundo; só as maiores posições de cada um são verificadas, então as pequenas não aparecem.',
})

# ---- fundos 101-150 (nov 2026)
UI['focus_labels'].update({'software': 'Software', 'leveraged': 'Alavancado (3x diário)', 'uranium': 'Urânio', 'copper miners': 'Mineradoras de cobre', 'lithium and batteries': 'Lítio e baterias', 'solar': 'Solar', 'infrastructure': 'Infraestrutura', 'robotics and AI': 'Robótica e IA', 'airlines': 'Companhias aéreas', 'China internet': 'Internet na China', 'homebuilders': 'Construtoras', 'metals and mining': 'Metais e mineração', 'Germany': 'Alemanha', 'Taiwan': 'Taiwan', 'South Korea': 'Coreia do Sul', 'United Kingdom': 'Reino Unido', 'emerging market bonds': 'Títulos emergentes'})
_G = UI['groups']
_G[4][1].extend(['Germany', 'United Kingdom', 'Taiwan', 'South Korea'])
_G[5][1].extend(['software', 'robotics and AI', 'infrastructure', 'homebuilders', 'metals and mining', 'copper miners', 'uranium', 'lithium and batteries', 'solar', 'airlines', 'China internet', 'leveraged'])
_G[6][1].append('emerging market bonds')
UCITS.update({'A UCITS ETF on the same theme': 'um ETF UCITS do mesmo tema',
 'A UCITS ETF tracking the same country index': 'um ETF UCITS que siga o mesmo índice do país',
 'European leveraged products are ETPs, not UCITS funds.': 'Na Europa os produtos alavancados são ETPs, não fundos UCITS.',
 'A UCITS US Treasury ETF': 'um ETF UCITS de Treasuries',
 'A UCITS USD emerging-market bond ETF': 'um ETF UCITS de títulos emergentes em dólar'})
T.update({
 'DVY': ('Cerca de cem empresas americanas de dividendo alto, ponderadas pelo dividendo que pagam e não pelo tamanho.',
         'Escolhe empresas com longo histórico de dividendos e as pondera pelo dividendo, o que o inclina para elétricas, bancos e tabaco. Rende mais que o mercado, mas quase não tem tecnologia, então fica muito para trás quando as de crescimento lideram.'),
 'SDY': ('Empresas dos EUA que aumentam o dividendo há pelo menos vinte anos seguidos, ponderadas pelo dividend yield.',
         'Procura em todo o S&P 1500, então inclui médias e pequenas, e dá mais peso às que mais rendem. A regra dos vinte anos deixa de fora as empresas jovens e qualquer uma que tenha cortado o dividendo numa crise.'),
 'NOBL': ('As empresas do S&P 500 que aumentam o dividendo há pelo menos 25 anos seguidos, com pesos iguais.',
          'Tem os sessenta e poucos "aristocratas do dividendo" com o mesmo peso e rebalanceia a cada trimestre. Isso o inclina para industriais e consumo básico e o afasta dos gigantes de tecnologia que dominam o índice.'),
 'HDV': ('Setenta e cinco empresas americanas de dividendo alto filtradas pela solidez financeira.',
         'Pega ações de alto dividend yield e fica só com as que a Morningstar considera financeiramente sólidas e com dividendo duradouro. Fica concentrado em energia, saúde e consumo básico, com poucos gigantes como Exxon e Johnson & Johnson pesando muito.'),
 'SPYD': ('As oitenta empresas do S&P 500 com maior dividend yield, com pesos iguais.',
          'Ordena o S&P 500 só pelo dividend yield e tem as oitenta primeiras em partes iguais. Não há filtro de qualidade, então pesam muito os REITs, as elétricas e empresas cujo yield alto vem de uma cotação que caiu.'),
 'DIVO': ('Cerca de 25 grandes pagadoras de dividendos, com calls vendidas sobre algumas para somar renda.',
          'Os gestores escolhem empresas sólidas de dividendos e vendem calls de curto prazo de forma seletiva, não sobre o fundo todo, então ele preserva mais alta que um fundo que vende calls sobre tudo. A renda vem de dividendos e prêmios.'),
 'QYLD': ('O Nasdaq-100 com calls "no dinheiro" vendidas todo mês: uma distribuição mensal alta em troca de quase toda a alta.',
          'Tem o Nasdaq-100 e vende todo mês uma call sobre o índice inteiro ao preço atual. O prêmio paga uma grande distribuição, mas cada alta fica limitada enquanto cada queda é sentida por inteiro, e por isso a cotação foi caindo com o tempo.'),
 'QQQM': ('O mesmo Nasdaq-100 do QQQ, numa classe mais barata feita para manter no longo prazo.',
          'Tem exatamente o mesmo que o QQQ com uma taxa anual menor. O QQQ continua sendo a opção para operar e para opções, pela liquidez enorme; para quem compra e mantém, o QQQM custa menos.'),
 'SPYG': ('A metade de crescimento do S&P 500 a um custo muito baixo.',
          'A S&P divide o índice por crescimento de receita e lucro e por momentum, e este fundo tem o lado do crescimento. Na prática é dominado pelos mesmos gigantes de tecnologia do QQQ.'),
 'VONG': ('O índice Russell 1000 Growth, o mesmo do IWF, com uma taxa menor.',
          'Tem a metade de crescimento das mil maiores empresas dos EUA, escolhidas por preço sobre valor patrimonial e crescimento esperado. É um jeito mais barato de ter o que o IWF tem.'),
 'IGV': ('Empresas de software da América do Norte, de Microsoft e Oracle a nomes menores da nuvem.',
         'Só tem fabricantes de software, sem chips nem hardware, e limita as maiores a um décimo do fundo. É o fundo mais exposto à dúvida sobre se a IA ajuda ou atrapalha as empresas de software.'),
 'FTEC': ('Empresas americanas de tecnologia de todos os tamanhos com uma das menores taxas do setor.',
          'Cobre o mesmo que o VGT, pequenas incluídas, com tetos que impedem os maiores nomes de passar dos limites de um fundo diversificado. A diferença em relação ao VGT é sobretudo o custo e a corretora.'),
 'TQQQ': ('Três vezes o movimento diário do Nasdaq-100: uma ferramenta para operar, não para manter.',
          'Usa swaps e futuros para entregar três vezes o que o Nasdaq-100 faz em cada dia e é reajustado toda noite. Em semanas, o resultado pode se afastar muito do triplo do índice, e em mercados laterais ou de queda esse reajuste destrói valor; uma queda de 33% do índice o zeraria num único dia.'),
 'SOXL': ('Três vezes o movimento diário de um índice de semicondutores: um dos fundos mais voláteis que existem.',
          'Usa swaps para entregar três vezes o retorno diário de trinta grandes empresas de chips e é reajustado todo dia. Os chips já se movem muito, então com o triplo as grandes perdas são comuns; ele foi feito para dias, não para anos.'),
 'SPYV': ('A metade de valor do S&P 500, barata: bancos, saúde, energia e industriais.',
          'Tem as empresas do S&P 500 que saem baratas por valor patrimonial, lucro e receita. Berkshire Hathaway, JPMorgan e Exxon são posições típicas, e ele fica para trás quando poucos gigantes de tecnologia puxam o mercado.'),
 'VOE': ('Empresas médias americanas com valuation baixo: seguradoras, elétricas, fornecedores industriais.',
         'Pega a metade de valor do mercado de médias segundo a CRSP. Essas empresas raramente aparecem no noticiário, e por isso historicamente ficaram baratas.'),
 'VBR': ('Pequenas empresas americanas baratas: o canto onde o prêmio de valor foi medido pela primeira vez.',
         'Tem umas 850 pequenas empresas baratas segundo várias medidas. É amplo e barato, mas não exclui as que dão prejuízo, e essa é a grande diferença em relação ao AVUV.'),
 'AVUV': ('Pequenas empresas americanas baratas e lucrativas, escolhidas com regras e não com apostas.',
          'A Avantis filtra pequenas empresas por preço baixo sobre valor patrimonial e alta lucratividade, e negocia com paciência. O filtro de lucratividade deixa de fora as baratas por um bom motivo, que pesam nos fundos de valor simples.'),
 'IWR': ('Cerca de 800 empresas médias dos EUA, da 201ª à milésima por tamanho.',
         'Tem a parte menor do Russell 1000, sem as duzentas maiores. As médias já passaram da fase mais arriscada, mas ainda têm espaço para crescer.'),
 'IWO': ('A metade de crescimento do Russell 2000: biotecnologia, software e industriais jovens.',
         'Muitas das empresas ainda não dão lucro, o que o torna muito sensível aos juros e ao apetite por risco. As altas vêm em arrancadas e as quedas podem ser profundas.'),
 'IWN': ('A metade de valor do Russell 2000: bancos regionais, imobiliário e energia.',
         'Tem as small caps mais baratas do Russell 2000. Os bancos regionais pesam muito, então ele sofre quando há estresse bancário e vai bem quando a economia acelera.'),
 'MDY': ('O S&P MidCap 400 no ETF de empresas médias mais antigo.',
         'Tem as mesmas 400 empresas do IJH, que cobra muito menos. O MDY continua popular entre traders pela liquidez e pelo mercado de opções.'),
 'SCHA': ('Cerca de 1.700 pequenas empresas americanas com uma taxa muito baixa.',
          'Tem a parte de small caps do índice total da Dow Jones, mais ampla que o Russell 2000. Não filtra por lucro, então carrega a mesma cauda fraca do IWM.'),
 'VXF': ('Todas as ações americanas, menos as do S&P 500: as médias e pequenas que completam uma carteira.',
         'Tem umas 3.500 empresas fora do S&P 500, ponderadas pelo tamanho. Junto com o VOO, na proporção de quatro para um, reproduz o mercado inteiro.'),
 'VDE': ('Petroleiras e empresas de gás dos EUA de todos os tamanhos, barato.',
         'Tem Exxon e Chevron com peso limitado e uma longa cauda de produtoras, refinarias e empresas de serviços. Em relação ao XLE, tem mais pequenas e menos peso nos dois gigantes.'),
 'VFH': ('Bancos, seguradoras, redes de pagamento e gestoras dos EUA de todos os tamanhos.',
         'Cobre o mesmo que o XLF, mas acrescenta centenas de bancos e seguradoras pequenos. Ganha quando margens e crédito vão bem e sofre nos sustos de crédito.'),
 'VIS': ('Industriais dos EUA: aeroespacial, máquinas, ferrovias, materiais de construção.',
         'Tem umas 400 empresas industriais, muito mais que o XLI, então depende menos de poucos gigantes como GE Aerospace e Caterpillar. Segue o ciclo econômico e o investimento das empresas.'),
 'VCR': ('O que os americanos compram quando sobra dinheiro: carros, varejo, restaurantes, viagens.',
         'Amazon e Tesla pesam muito, com tetos, seguidas de redes de material de construção, restaurantes e hotéis. É uma aposta na capacidade de gasto do consumidor americano.'),
 'VDC': ('Produtos de primeira necessidade: alimentos, casa, bebidas e tabaco.',
         'Walmart, Costco e Procter & Gamble lideram um setor cujas vendas quase não se mexem nas recessões. Costuma cair menos que o mercado nas quedas e ficar para trás nas euforias.'),
 'VPU': ('Elétricas, distribuidoras de gás e de água dos EUA.',
         'Empresas reguladas com dividendos estáveis, agora também uma aposta na eletricidade de que os data centers precisam. Como se endividam muito e distribuem muito, a cotação anda na direção oposta à dos juros.'),
 'URA': ('Mineradoras de urânio e empresas de combustível nuclear do mundo todo.',
         'Cameco e Kazatomprom lideram, ao lado de trusts de urânio físico e fornecedores de reatores. Segue o preço do urânio e o clima político em relação à energia nuclear, que podem mudar com força.'),
 'COPX': ('As mineradoras de cobre do mundo.',
          'Tem mineradoras do Canadá, da Austrália, da China e dos EUA, como a Freeport-McMoRan. As mineradoras amplificam o preço do cobre, que depende da construção na China, das redes elétricas e dos carros elétricos.'),
 'LIT': ('Mineradoras de lítio e fabricantes de baterias, da Albemarle a produtores chineses de células.',
         'Abrange a cadeia da bateria, do lítio bruto à célula pronta, com muito peso na China. Segue o preço do lítio e a demanda por carros elétricos, que tiveram ciclos de alta e queda muito profundos.'),
 'TAN': ('Fabricantes de painéis solares, instaladores e empresas de inversores.',
         'Tem First Solar, Enphase e outras empresas solares do mundo. O setor é muito sensível aos juros, aos subsídios e ao preço dos painéis chineses, o que o tornou um dos fundos de ações mais voláteis.'),
 'PAVE': ('Empresas dos EUA que constroem e abastecem estradas, redes elétricas e fábricas.',
          'Tem construtoras, fabricantes de máquinas, aço e fornecedores elétricos que se beneficiam do gasto público em infraestrutura e das novas fábricas. Se comporta como um fundo industrial concentrado.'),
 'BOTZ': ('Empresas de robótica, automação e hardware de IA do mundo todo.',
          'A Nvidia convive com fabricantes japoneses de robôs industriais e empresas de robôs cirúrgicos. É uma visão mais estreita e mais global da automação que um fundo de tecnologia comum.'),
 'JETS': ('Companhias aéreas dos EUA e do exterior, mais fabricantes de aviões e aeroportos.',
          'Dominam as grandes companhias aéreas americanas, com menos peso nas estrangeiras e em empresas de viagem. As aéreas dependem do combustível e da economia e já precisaram de socorro várias vezes: é um fundo cíclico para operar.'),
 'KWEB': ('Os gigantes da internet da China: Tencent, Alibaba, PDD, Meituan e outros.',
          'Tem empresas chinesas de internet listadas em Hong Kong e Nova York. Perdeu a maior parte do valor com a ofensiva regulatória de Pequim a partir de 2021 e se move com força com o noticiário político entre China e EUA.'),
 'ITB': ('Construtoras de casas dos EUA e seus fornecedores.',
         'D.R. Horton, Lennar e PulteGroup pesam muito, seguidas de fabricantes de materiais e lojas de material de construção. Se move com os juros das hipotecas mais do que com qualquer outra coisa.'),
 'XME': ('Empresas de aço, alumínio, carvão, ouro e cobre dos EUA, com pesos quase iguais.',
         'Com pesos iguais, as produtoras pequenas contam tanto quanto as grandes, então é uma aposta ampla nos preços dos metais nos EUA. Costuma saltar com tarifas e gasto em infraestrutura e cair com força nas desacelerações.'),
 'EWG': ('As grandes empresas da Alemanha: SAP, Siemens, Allianz, Deutsche Telekom.',
         'Tem umas sessenta empresas alemãs, com muito peso em industriais, financeiras e software. Para quem investe em dólar, o retorno também depende do euro.'),
 'EWT': ('A bolsa de Taiwan, que é sobretudo a TSMC e a sua cadeia de fornecedores.',
         'A TSMC é a maior posição, com peso limitado, seguida de MediaTek e fabricantes de eletrônicos. Na prática é uma aposta no ciclo mundial dos chips mais o risco geopolítico de Taiwan.'),
 'EWY': ('As grandes empresas da Coreia do Sul, lideradas por Samsung Electronics e SK Hynix.',
         'Os chips de memória pesam muito, seguidos de montadoras, bancos e baterias. As ações coreanas são negociadas há muito tempo com desconto por causa dos conglomerados familiares e da baixa remuneração ao acionista.'),
 'EWU': ('As grandes empresas britânicas: Shell, AstraZeneca, HSBC, Unilever.',
         'A bolsa britânica pesa muito em petróleo, bancos, mineração e consumo básico e pouco em tecnologia, então é negociada barata e paga dividendo alto.'),
 'SPDW': ('Milhares de empresas da Europa, do Japão, do Canadá e da Austrália com uma taxa muito baixa.',
          'Cobre os mercados desenvolvidos fora dos EUA, incluindo pequenas e o Canadá. É uma alternativa barata ao VEA e ao SCHF com quase as mesmas empresas.'),
 'VGLT': ('Treasuries de mais de dez anos, com uma taxa menor que a do TLT.',
          'Tem títulos públicos longos com vencimento médio um pouco mais curto que o do TLT, então é um pouco menos sensível aos juros. Sobe quando os juros longos caem e cai quando sobem.'),
 'GOVT': ('Todos os prazos de Treasuries num fundo.',
          'Tem o mercado do Tesouro americano de um a trinta anos, ponderado pelo que foi emitido. Fica entre os fundos curtos e os longos em risco e é um jeito simples de ter a curva do governo americano.'),
 'EMB': ('Títulos em dólar de governos emergentes e suas estatais.',
         'Tem títulos de países como México, Arábia Saudita, Indonésia e Brasil, pagos em dólar, então não há risco cambial. Rende mais que os Treasuries pelo risco de calote e sofre quando o dólar e os juros americanos sobem juntos.'),
 'SCHP': ('Treasuries protegidos contra a inflação (TIPS) com uma taxa muito baixa.',
          'O principal de cada título sobe com os preços ao consumidor, então ele protege contra surpresas de inflação. Mesmo assim cai quando os juros reais sobem, como em 2022.'),
 'VGSH': ('Treasuries de um a três anos, o gêmeo barato do SHY.',
          'Tem títulos públicos curtos, então o preço quase não se mexe com os juros. É um passo além do caixa para dinheiro que pode ser necessário em um ou dois anos.'),
})
