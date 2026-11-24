"""Pacote em português do Brasil para story.py (bolsagaviao.com). Três redações por dado."""
import datetime

MES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']


def _d(v, d):
    s = ('{:,.%df}' % d).format(v)
    return s.replace(',', '\x00').replace('.', ',').replace('\x00', '.')


class F:
    @staticmethod
    def money(v):
        a = abs(v)
        if a >= 1e12: return '%s trilhões de dólares' % _d(v / 1e12, 2)
        if a >= 1e9: return '%s bilhões de dólares' % _d(v / 1e9, 1)
        if a >= 1e6: return '%s milhões de dólares' % _d(v / 1e6, 0)
        return '%s mil dólares' % _d(v / 1e3, 0)

    @staticmethod
    def pct(v, d=0):
        return _d(v * 100, d) + '%'

    @staticmethod
    def mpct(v):
        return _d(v * 100, 1 if abs(v) < 0.1 else 0) + '%'

    @staticmethod
    def spct(v):
        if abs(v) < 0.005:
            v = 0.0
        return ('' if v == 0 else '+' if v > 0 else '−') + _d(abs(v) * 100, 0) + '%'

    @staticmethod
    def num(v):
        return _d(v, 1)

    @staticmethod
    def times(v):
        return '%s vezes' % _d(v, 1 if v < 10 else 0)

    @staticmethod
    def price(v):
        a = abs(v); d = 2
        if 0 < a < 0.005:
            d = 3 if a >= 0.0005 else 4
        return '%sUS$ %s' % ('−' if v < 0 and round(a, d) else '', _d(a, d))

    @staticmethod
    def years(ys):
        ys = [str(y) for y in ys]
        return ys[0] if len(ys) == 1 else ', '.join(ys[:-1]) + ' e ' + ys[-1]


def qdate(s):
    try:
        d = datetime.date.fromisoformat(str(s)[:10])
        return 'o trimestre encerrado em %s de %d' % (MES[d.month - 1], d.year)
    except Exception:
        return 'o último trimestre'


def month(m):
    return MES[m - 1]


T = {
    'eps_up': ['O lucro por ação diluído subiu de {e0} no exercício {fy0} para {e1} no exercício {fy1}, cerca de {g} ao ano.',
               'O lucro por ação passou de {e0} para {e1} entre o exercício {fy0} e o exercício {fy1} ({g} ao ano).', 'O lucro por ação cresce cerca de {g} ao ano: de {e0} no exercício {fy0} para {e1} no exercício {fy1}.'],
    'eps_faster': ['O lucro por ação cresceu mais que as vendas, de {e0} no exercício {fy0} para {e1} no exercício {fy1} ({g} ao ano): as margens se ampliaram no caminho.',
                   'O lucro por ação correu mais que a receita: de {e0} para {e1} entre o exercício {fy0} e o exercício {fy1}, cerca de {g} ao ano.',
                   'A última linha foi melhor que a primeira: o lucro por ação sobe cerca de {g} ao ano, até {e1} (exercício {fy0}: {e0}).'],
    'eps_down': ['O lucro por ação diluído caiu de {e0} no exercício {fy0} para {e1} no exercício {fy1}, cerca de {g} ao ano.',
                 'O lucro por ação diminuiu de {e0} para {e1} entre o exercício {fy0} e o exercício {fy1}.', 'O lucro por ação é menor que antes: {e1} no exercício {fy1} contra {e0} no exercício {fy0}.'],
    'opm_up': ['A margem operacional, de {now} no último ano, supera a média de cinco anos ({avg}).', 'A rentabilidade operacional melhorou: {now} no último ano contra uma média de cinco anos de {avg}.',
               'A margem operacional do último ano, {now}, bateu a média de cinco anos ({avg}).'],
    'opm_down': ['A margem operacional, de {now} no último ano, está abaixo da média de cinco anos ({avg}).', 'A rentabilidade operacional recuou: {now} no último ano contra uma média de cinco anos de {avg}.',
                 'A margem operacional do último ano, {now}, ficou abaixo da média de cinco anos ({avg}).'],
    'rnd': ['Gasta {v} por ano em pesquisa e desenvolvimento, {p} da receita.', 'A pesquisa e o desenvolvimento levam {p} das vendas ({v} por ano).', 'O gasto com P&D de {v} equivale a {p} da receita.'],
    'capex': ['O investimento em ativos é alto: {v} por ano, {p} da receita.', 'Reinveste {p} das vendas em instalações e equipamentos ({v} por ano).', 'O investimento em ativo imobilizado fica em torno de {v}, {p} da receita.'],
    'int_tight': ['O lucro operacional cobre só {x} vezes a conta de juros de {ie}: um colchão fino.', 'Os juros de {ie} por ano comem boa parte do lucro operacional (cobertura de {x} vezes).',
                  'Com uma cobertura de juros de {x} vezes sobre {ie} de juros, há pouca margem para um ano ruim.'],
    'int_easy': ['O lucro operacional cobre os juros {x} vezes: a dívida não pesa.', 'Os juros são quase irrelevantes, cobertos {x} vezes pelo lucro operacional.', 'A cobertura de juros é folgada: {x} vezes.'],
    'fy_end': ['O exercício fiscal dela termina em {m}.', 'Atenção: o exercício fiscal termina em {m}, não em dezembro.', 'Os exercícios fiscais terminam em {m}.'],
    'head': ['{name} em números: o que diz o histórico', 'O histórico de {name}, ano a ano', 'Como ler os números de {name}'],
    'size_top': ['{name} é a maior das {n} empresas de {ind} listadas nos EUA que acompanhamos: vale {mcap}, cerca de {x} o valor da segunda, {other}.',
                 'Com {mcap}, {name} lidera o grupo de {ind} da nossa lista: {n} empresas, e a segunda, {other}, é {x} menor.',
                 'Nenhuma empresa de {ind} listada nos EUA da nossa lista é maior: {name} vale {mcap}, {x} o valor de {other}, a segunda de {n}.'],
    'size_rank': ['{name} vale {mcap} e é a número {rank} em tamanho entre as {n} empresas de {ind} listadas nos EUA que acompanhamos.',
                  'Com valor de mercado de {mcap}, {name} ocupa a posição {rank} de {n} no setor de {ind} da nossa lista.',
                  'Entre {n} empresas de {ind} listadas nos EUA, {name} é a número {rank} em valor de mercado ({mcap}).'],
    'size_between': ['Logo acima está {bigger}; logo abaixo, {smaller}.', 'As vizinhas mais próximas em tamanho são {bigger} (maior) e {smaller} (menor).',
                     'Em tamanho, fica entre {bigger} e {smaller}.'],
    'size_last': ['É a menor do grupo; a seguinte é {bigger}.', 'Não há nenhuma menor no grupo; a mais parecida em tamanho é {bigger}.',
                  'Fecha a lista em tamanho, logo atrás de {bigger}.'],
    'size_share': ['Sozinha, representa {share} do valor conjunto do setor.', 'Isso equivale a {share} do que vale o grupo inteiro junto.',
                   'O peso dela no grupo é grande: {share} do valor conjunto.'],
    'size_alone': ['{name} tem valor de mercado de {mcap}.', 'A bolsa avalia {name} em {mcap}.', '{name} vale {mcap} na bolsa.'],
    'hist_cagr_up': ['A receita passou de {r0} no exercício {fy0} para {r1} no exercício {fy1}, cerca de {g} ao ano durante {n} anos.',
                     'Em {n} anos as vendas foram de {r0} (exercício {fy0}) para {r1} (exercício {fy1}): cerca de {g} ao ano, de forma composta.',
                     'As vendas crescem num ritmo de {g} ao ano desde o exercício {fy0}, de {r0} para {r1} no exercício {fy1}.'],
    'hist_cagr_flat': ['A receita quase não se mexeu em {n} anos: {r0} no exercício {fy0} e {r1} no exercício {fy1}.',
                       'O faturamento está onde estava há {n} anos: {r1} no exercício {fy1} contra {r0} no exercício {fy0}.',
                       'As vendas de {r1} no exercício {fy1} são muito parecidas com os {r0} do exercício {fy0}.'],
    'hist_cagr_down': ['A receita caiu de {r0} no exercício {fy0} para {r1} no exercício {fy1}, cerca de {g} ao ano.',
                       'O negócio é menor que antes: {r1} de receita no exercício {fy1}, contra {r0} no exercício {fy0} (cerca de {g} ao ano).',
                       'Em {n} anos as vendas caíram cerca de {g} ao ano, de {r0} para {r1}.'],
    'hist_no_down': ['A receita subiu em cada um dos últimos {n} anos dos nossos dados, sem nenhum ano de queda.',
                     'Não há nenhum ano de queda nos últimos {n}: a receita sempre cresceu.', 'O histórico não registra nenhuma queda de receita em {n} anos seguidos.'],
    'hist_down_one': ['O único ano em que a receita caiu foi o exercício {fy}, {g}.', 'O exercício {fy} é a única mancha: a receita caiu {g} naquele ano.',
                      'A receita caiu só uma vez, no exercício {fy} ({g} a menos).'],
    'hist_down_many': ['A receita caiu em {n} anos ({years}); o pior foi o exercício {worst}, com queda de {g}.',
                       'Não é uma linha reta: as vendas caíram em {years}, sobretudo no exercício {worst} ({g}).',
                       'Houve {n} anos de queda, {years}, e o exercício {worst} foi o mais duro, com a receita {g} abaixo.'],
    'hist_best': ['O melhor ano foi o exercício {fy}, quando a receita saltou {g}.', 'O melhor ano de crescimento foi o exercício {fy}: {g} a mais de receita.',
                  'Destaca-se o exercício {fy}, com a receita {g} acima.'],
    'hist_record': ['A receita do exercício {fy} foi a mais alta da história nos nossos dados.', 'O último ano, o exercício {fy}, marcou um recorde de receita.',
                    'A receita do exercício {fy} foi uma máxima histórica.'],
    'hist_below_peak': ['A receita continua {g} abaixo da máxima de {peak} no exercício {fy}.',
                        'O faturamento não voltou aos {peak} do exercício {fy}; faltam {g}.', 'As vendas chegaram ao teto de {peak} no exercício {fy} e hoje estão {g} abaixo.'],
    'prof_all': ['Teve lucro em cada um dos {n} anos que temos.', 'Todos os últimos {n} anos foram lucrativos.', 'Não há nenhum ano de prejuízo nos {n} anos registrados.'],
    'prof_never': ['Não teve lucro anual em nenhum dos {n} anos que temos.', 'Os {n} anos registrados terminaram com prejuízo.',
                   'O lucro ainda não chegou: {n} anos, {n} prejuízos.'],
    'prof_turn': ['Depois dos prejuízos de {years}, passou a dar lucro no exercício {fy} e manteve isso.',
                  'O exercício {fy} foi a virada: lucrativa desde então, depois de perder dinheiro em {years}.',
                  'Está no azul desde o exercício {fy}; antes, perdeu dinheiro em {years}.'],
    'prof_slip': ['Voltou ao prejuízo no exercício {fy}, com {loss} no vermelho.', 'O exercício {fy} interrompeu a sequência de lucros com um prejuízo de {loss}.',
                  'O último ano, o exercício {fy}, fechou com prejuízo de {loss} depois de um ano de lucro.'],
    'prof_mixed': ['Os lucros vêm e vão: {n} anos com prejuízo em {span} ({years}).', 'Perdeu dinheiro em {n} de {span} anos ({years}).',
                   'Os ganhos são irregulares, com prejuízo em {years}.'],
    'prof_margin_off': ['A margem líquida chegou a {peak} no exercício {fy} e hoje é de {now}.',
                        'A rentabilidade está abaixo do melhor momento: margem líquida de {now} hoje contra {peak} no exercício {fy}.',
                        'As margens caíram de {peak} no exercício {fy} para {now}.'],
    'prof_margin_best': ['A última margem líquida, de {m}, é a melhor em {n} anos.', 'Com {m}, a margem líquida é a mais alta dos {n} anos registrados.',
                         'Nunca tinha sido tão lucrativa nos nossos dados: margem líquida de {m}.'],
    'fcf_all': ['O fluxo de caixa livre foi positivo nos {n} anos.', 'Gerou caixa livre em cada um dos {n} anos.', 'O caixa depois dos investimentos foi positivo todos os anos ({n} de {n}).'],
    'fcf_none': ['O fluxo de caixa livre foi negativo nos {n} anos: o negócio consome caixa.', 'Não gerou caixa livre em nenhum dos {n} anos.',
                 'Em cada um dos {n} anos, gastou mais caixa do que entrou.'],
    'fcf_one': ['O fluxo de caixa livre só foi positivo em um de {n} anos.', 'Gerou caixa livre num único ano de {n}.', 'Só um ano dos {n} deixou fluxo de caixa livre positivo.'],
    'fcf_most': ['O fluxo de caixa livre foi positivo em {pos} de {n} anos.', 'Gerou caixa livre em {pos} dos {n} anos.', 'Em {pos} de {n} anos o caixa livre foi positivo.'],
    'fcf_some': ['O fluxo de caixa livre foi positivo em {pos} de {n} anos.', 'Gerou caixa livre em {pos} anos de {n}.', 'A geração de caixa é irregular: positiva em {pos} de {n} anos.'],
    'q_up': ['Em {q} a receita foi de {rev}, {g} a mais que um ano antes.', 'A receita de {q} somou {rev}, {g} a mais que no mesmo trimestre do ano anterior.',
             '{q} trouxe {rev} de receita, uma alta de {g} em 12 meses.'],
    'q_flat': ['A receita de {q} foi de {rev}, quase igual à de um ano antes.', 'Em {q} a receita de {rev} ficou estável em relação ao ano anterior.',
               '{q} trouxe vendas de {rev}, no mesmo nível de um ano antes.'],
    'q_down': ['Em {q} a receita foi de {rev}, {g} a menos que um ano antes.', 'A receita de {q} caiu {g} em 12 meses, para {rev}.',
               '{q} trouxe {rev} de receita, {g} a menos que um ano antes.'],
    'q_streak': ['São {n} trimestres seguidos de crescimento em relação ao ano anterior.', 'Já soma {n} trimestres consecutivos crescendo em relação ao ano anterior.', 'A sequência de crescimento chega a {n} trimestres.'],
    'q_profit': ['O lucro líquido do trimestre foi de {ni}.', 'Lucrou {ni} naquele trimestre.', 'Resultado líquido do trimestre: {ni} de lucro.'],
    'q_loss': ['O trimestre fechou com prejuízo líquido de {ni}.', 'Perdeu {ni} naquele trimestre.', 'Resultado líquido do trimestre: um prejuízo de {ni}.'],
    'peer_margin_hi': ['A margem líquida de {m} supera com folga a mediana de {med} das empresas de {ind}.',
                       'Com {m}, fica com mais de cada dólar de vendas do que a empresa típica de {ind} ({med}).',
                       'A rentabilidade é um ponto forte: margem líquida de {m} contra uma mediana do setor de {med}.'],
    'peer_margin_lo': ['A margem líquida de {m} fica abaixo da mediana de {med} das empresas de {ind}.',
                       'Fica com menos das vendas do que a maioria dos pares: {m} contra uma mediana de {med}.',
                       'A rentabilidade está atrás do grupo: margem líquida de {m}, mediana de {med}.'],
    'peer_loss_hi': ['Perde dinheiro (margem líquida de {m}), mas menos que a empresa típica de {ind} ({med}).',
                     'A margem líquida de {m} é um prejuízo, embora menor que a mediana do setor ({med}).', 'Os prejuízos são mais leves que na maioria do grupo: {m} contra uma mediana de {med}.'],
    'peer_loss_lo': ['A margem líquida de {m} é um prejuízo maior que a mediana de {med} das empresas de {ind}.',
                     'Perde mais por dólar vendido do que a maioria dos pares: {m} contra {med}.', 'Os prejuízos são mais pesados que no grupo, {m} contra uma mediana de {med}.'],
    'peer_margin_eq': ['A margem líquida de {m} está perto da mediana do setor, de {med}.', 'Com {m}, a rentabilidade está em linha com o grupo ({med}).',
                       'As margens são as típicas das empresas de {ind}: {m} contra {med}.'],
    'peer_growth_hi_ttm': ["O crescimento da receita dos últimos doze meses, {g}, superou a mediana do setor ({med}).", "Nos últimos doze meses cresceu mais rápido que a maioria dos pares ({g} contra uma mediana de {med}).", "Nos últimos doze meses o crescimento superou o do grupo: {g} contra {med}."],
    'peer_growth_lo_ttm': ["O crescimento da receita dos últimos doze meses, {g}, ficou abaixo da mediana do setor ({med}).", "Os pares cresceram mais nos últimos doze meses: mediana de {med}, contra {g} aqui.", "Nos últimos doze meses o crescimento ficou atrás do grupo, {g} contra {med}."],
    'peer_growth_eq_ttm': ["O crescimento da receita dos últimos doze meses, {g}, igualou a mediana do setor ({med}).", "Nos últimos doze meses cresceu em linha com os pares: {g} contra {med}.", "O crescimento dos últimos doze meses, {g}, ficou perto da mediana do grupo, {med}."],
    'opm_up_ttm': ["A margem operacional, {now} nos últimos doze meses, está acima da média de cinco anos ({avg}).", "A rentabilidade operacional melhorou: {now} nos últimos doze meses contra uma média de cinco anos de {avg}."],
    'opm_down_ttm': ["A margem operacional, {now} nos últimos doze meses, está abaixo da média de cinco anos ({avg}).", "A rentabilidade operacional caiu: {now} nos últimos doze meses contra uma média de cinco anos de {avg}."],
    'peer_growth_hi': ['O crescimento da receita do último ano, {g}, superou a mediana do setor ({med}).', 'Cresceu mais rápido que a maioria dos pares no último ano ({g} contra uma mediana de {med}).',
                       'O crescimento superou o do grupo: {g} contra {med}.'],
    'peer_growth_lo': ['O crescimento da receita do último ano, {g}, ficou abaixo da mediana do setor ({med}).', 'Os pares cresceram mais no último ano: mediana de {med}, contra {g} aqui.',
                       'O crescimento ficou atrás do grupo, {g} contra {med}.'],
    'peer_growth_eq': ['O crescimento da receita do último ano, {g}, igualou a mediana do setor ({med}).', 'Cresceu em linha com os pares no último ano: {g} contra {med}.',
                       'O crescimento do último ano, {g}, ficou perto da mediana do grupo, {med}.'],
    'peer_pe_hi': ['O mercado paga {pe} vezes o lucro, {x} a mediana do setor ({med}): espera mais desta empresa do que dos pares.',
                   'Com P/L de {pe} contra uma mediana do setor de {med}, a ação é negociada com um prêmio de {x} o múltiplo do grupo.',
                   'O valuation é exigente em relação aos pares: P/L de {pe}, mediana do setor de {med}.'],
    'peer_pe_lo': ['O P/L de {pe} está abaixo da mediana do setor ({med}): o mercado é mais cauteloso com ela do que com os pares.',
                   'A {pe} vezes o lucro, é mais barata que o par típico ({med}); a pergunta é se esse desconto se justifica.',
                   'A ação é negociada com desconto em relação ao grupo: P/L de {pe} contra {med}.'],
    'peer_pe_eq': ['O P/L de {pe} está perto da mediana do setor, de {med}.', 'O valuation está em linha com os pares: P/L de {pe}, mediana de {med}.',
                   'A {pe} vezes o lucro, é negociada como o grupo ({med}).'],
    'peer_pe_none': ['Não tem P/L porque não é lucrativa; {n} das {tot} empresas do setor são.',
                     'Sem lucro não há P/L para comparar; {n} dos {tot} pares ganham dinheiro.',
                     'A comparação de P/L ainda não se aplica: perde dinheiro, enquanto {n} de {tot} pares são lucrativos.'],
    'roic_hi': ['Um retorno sobre o capital investido de {roic} é alto, sinal de um negócio com poder de preço ou com poucos ativos.',
                'Ganha {roic} sobre o capital investido nela, bem acima do que esse capital custa.', 'O retorno sobre o capital investido é sólido: {roic}.'],
    'roic_lo': ['O retorno sobre o capital investido é de só {roic}, baixo para uma empresa lucrativa.', 'Ganha apenas {roic} sobre o capital investido.',
                'O retorno do capital é fraco: {roic} sobre o capital investido.'],
    'bs_cash': ['Tem {net} a mais em caixa do que em dívida, {p} do valor de mercado.', 'O caixa líquido de {net} cobre {p} do valor de mercado.',
                'O balanço tem {net} de caixa líquido, {p} do que a empresa vale.'],
    'bs_debt_x': ['A dívida líquida é de {net}, cerca de {x} vezes um ano de lucro operacional em caixa (EBITDA).', 'Deve {net} a mais do que tem em caixa, {x} vezes o EBITDA.',
                  'Uma dívida líquida de {net} equivale a {x} anos de EBITDA.'],
    'bs_debt_p': ['A dívida líquida é de {net}, {p} do valor de mercado.', 'Carrega {net} de dívida líquida, {p} do valor de mercado.', 'Dívida líquida de caixa: {net} ({p} do valor de mercado).'],
    'bs_runway': ['Consumiu {burn} de caixa nos últimos doze meses; o caixa disponível cobre cerca de {x} anos nesse ritmo.',
                  'No ritmo recente de {burn} por ano, o caixa dura cerca de {x} anos.', 'A queima de caixa foi de {burn} em doze meses, cerca de {x} anos de fôlego.'],
    'bs_runway_short': ['Consumiu {burn} de caixa nos últimos doze meses e o caixa só cobre cerca de {x} anos: é de esperar novas ações ou nova dívida.',
                        'O fôlego é curto: {burn} de queima por ano contra caixa para cerca de {x} anos, então é provável que precise de mais financiamento.',
                        'Com {burn} de queima de caixa por ano, o caixa dura cerca de {x} anos; um aumento de capital não surpreenderia.'],
    'sh_dilute': ['O número de ações cresceu cerca de {p} ao ano em três anos, o que dilui os acionistas.', 'Os acionistas foram diluídos em cerca de {p} ao ano durante três anos.',
                  'As ações novas somam cerca de {p} ao ano.'],
    'sh_buyback': ['O número de ações caiu cerca de {p} ao ano em três anos graças às recompras.', 'As recompras reduziram as ações em cerca de {p} ao ano.',
                   'Todo ano há menos ações: cerca de {p} a menos por ano em três anos.'],
    'div_yes': ['Paga um dividendo com yield de {y} e pagou em {n} dos anos dos nossos dados.', 'O dividendo rende {y}; os pagamentos remontam a {n} anos nos nossos dados.',
                'Quem busca renda recebe {y}, pago durante {n} anos registrados.'],
    'sbc_heavy': ['A remuneração em ações equivale a {p} do fluxo de caixa livre, um custo real que os números de caixa não mostram.',
                  'A remuneração em ações é grande: {p} do fluxo de caixa livre.', 'O fluxo de caixa livre a favorece: a remuneração em ações é {p} desse número.'],
    'an_up': ['Os analistas elevaram as estimativas: {up} para cima e {dn} para baixo nos últimos 30 dias.', 'As revisões pendem para cima: {up} elevações contra {dn} reduções em 30 dias.',
              'No último mês, {up} analistas elevaram os números e {dn} os reduziram.'],
    'an_down': ['Os analistas cortaram as estimativas: {dn} para baixo e {up} para cima nos últimos 30 dias.', 'As revisões pendem para baixo: {dn} cortes contra {up} elevações em 30 dias.',
                'No último mês, {dn} analistas cortaram os números e só {up} os elevaram.'],
    'an_mixed': ['As revisões das estimativas são mistas: {up} para cima e {dn} para baixo em 30 dias.', 'Os analistas não concordam na direção: {up} elevações e {dn} cortes no último mês.',
                 'Em 30 dias, {up} estimativas subiram e {dn} caíram.'],
    'an_range': ['Os preços-alvo de {n} analistas vão de {lo} a {hi}.', 'Os {n} preços-alvo vão de {lo} a {hi}.',
                 'Os alvos variam muito: {lo} na ponta baixa e {hi} na alta ({n} analistas).'],
    'an_next': ['Para {q}, o consenso espera um lucro por ação de {eps} com receita de {rev}.', 'O próximo relatório cobre {q}: consenso de {eps} por ação e {rev} de receita.',
                'Os analistas esperam {eps} por ação e {rev} de receita para {q}.'],
    'an_next_eps': ['Para {q}, o consenso espera um lucro por ação de {eps}.', 'O próximo relatório cobre {q}; o consenso é de {eps} por ação.', 'Os analistas esperam {eps} por ação para {q}.'],
}
