"""Paquete en español para story.py (bolsacondor.com). Español neutro; tres redacciones por dato."""
import datetime

MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']


def _d(v, d):
    s = ('{:,.%df}' % d).format(v)
    return s.replace(',', '\x00').replace('.', ',').replace('\x00', '.')


class F:
    @staticmethod
    def money(v):
        a = abs(v)
        if a >= 1e12: return '%s billones de dólares' % _d(v / 1e12, 2)
        if a >= 1e9: return '%s mil millones de dólares' % _d(v / 1e9, 1)
        if a >= 1e6: return '%s millones de dólares' % _d(v / 1e6, 0)
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
        return '%s veces' % _d(v, 1 if v < 10 else 0)

    @staticmethod
    def price(v):
        return '%s dólares' % _d(v, 2)

    @staticmethod
    def years(ys):
        ys = [str(y) for y in ys]
        return ys[0] if len(ys) == 1 else ', '.join(ys[:-1]) + ' y ' + ys[-1]


def qdate(s):
    try:
        d = datetime.date.fromisoformat(str(s)[:10])
        return 'el trimestre cerrado en %s de %d' % (MES[d.month - 1], d.year)
    except Exception:
        return 'el último trimestre'


def month(m):
    return MES[m - 1]


T = {
    'eps_up': ['El beneficio por acción diluido subió de {e0} en el ejercicio {fy0} a {e1} en el ejercicio {fy1}, cerca de un {g} al año.',
               'El beneficio por acción pasó de {e0} a {e1} entre el ejercicio {fy0} y el ejercicio {fy1} (un {g} anual).', 'El beneficio por acción crece cerca de un {g} anual: de {e0} en el ejercicio {fy0} a {e1} en el ejercicio {fy1}.'],
    'eps_faster': ['El beneficio por acción creció más que las ventas, de {e0} en el ejercicio {fy0} a {e1} en el ejercicio {fy1} (un {g} anual): los márgenes se ampliaron por el camino.',
                   'El beneficio por acción corrió más que los ingresos: de {e0} a {e1} entre el ejercicio {fy0} y el ejercicio {fy1}, cerca de un {g} al año.',
                   'La última línea fue mejor que la primera: el beneficio por acción sube cerca de un {g} anual hasta {e1} (ejercicio {fy0}: {e0}).'],
    'eps_down': ['El beneficio por acción diluido bajó de {e0} en el ejercicio {fy0} a {e1} en el ejercicio {fy1}, cerca de un {g} al año.',
                 'El beneficio por acción se redujo de {e0} a {e1} entre el ejercicio {fy0} y el ejercicio {fy1}.', 'El beneficio por acción es menor que antes: {e1} en el ejercicio {fy1} frente a {e0} en el ejercicio {fy0}.'],
    'opm_up': ['El margen operativo, del {now} el último año, supera su media de cinco años ({avg}).', 'La rentabilidad operativa ha mejorado: {now} el último año frente a una media de cinco años del {avg}.',
               'El margen operativo del último año, {now}, batió la media de cinco años ({avg}).'],
    'opm_down': ['El margen operativo, del {now} el último año, está por debajo de su media de cinco años ({avg}).', 'La rentabilidad operativa ha retrocedido: {now} el último año frente a una media de cinco años del {avg}.',
                 'El margen operativo del último año, {now}, quedó por debajo de la media de cinco años ({avg}).'],
    'rnd': ['Gasta {v} al año en investigación y desarrollo, el {p} de los ingresos.', 'La investigación y el desarrollo se llevan el {p} de las ventas ({v} al año).', 'El gasto en I+D de {v} equivale al {p} de los ingresos.'],
    'capex': ['La inversión en activos es alta: {v} al año, el {p} de los ingresos.', 'Reinvierte el {p} de sus ventas en instalaciones y equipos ({v} al año).', 'La inversión en activo fijo ronda los {v}, el {p} de los ingresos.'],
    'int_tight': ['El beneficio operativo cubre solo {x} veces la factura de intereses de {ie}: un colchón fino.', 'Los intereses de {ie} al año se comen buena parte del beneficio operativo (cobertura de {x} veces).',
                  'Con una cobertura de intereses de {x} veces sobre {ie} de intereses, hay poco margen para un mal año.'],
    'int_easy': ['El beneficio operativo cubre los intereses {x} veces: la deuda no pesa.', 'Los intereses son casi irrelevantes, cubiertos {x} veces por el beneficio operativo.', 'La cobertura de intereses es holgada: {x} veces.'],
    'fy_end': ['Su ejercicio fiscal termina en {m}.', 'Ojo: el ejercicio fiscal cierra en {m}, no en diciembre.', 'Los ejercicios fiscales terminan en {m}.'],
    'head': ['{name} en cifras: lo que dice su historial', 'El historial de {name}, año a año', 'Cómo leer las cifras de {name}'],
    'size_top': ['{name} es la mayor de las {n} empresas de {ind} que cotizan en EE. UU. y que seguimos: vale {mcap}, unas {x} lo que vale la siguiente, {other}.',
                 'Con {mcap}, {name} encabeza el grupo de {ind} de nuestra lista: {n} empresas, y la segunda, {other}, es {x} más pequeña.',
                 'Ninguna empresa de {ind} cotizada en EE. UU. de nuestra lista es mayor: {name} vale {mcap}, {x} el valor de {other}, la segunda de {n}.'],
    'size_rank': ['{name} vale {mcap} y es la número {rank} por tamaño entre las {n} empresas de {ind} que cotizan en EE. UU. y que seguimos.',
                  'Con un valor de mercado de {mcap}, {name} ocupa el puesto {rank} de {n} en el sector de {ind} de nuestra lista.',
                  'Entre {n} empresas de {ind} cotizadas en EE. UU., {name} es la número {rank} por valor de mercado ({mcap}).'],
    'size_between': ['Justo por encima está {bigger}; justo por debajo, {smaller}.', 'Sus vecinas más cercanas por tamaño son {bigger} (mayor) y {smaller} (menor).',
                     'Por tamaño queda entre {bigger} y {smaller}.'],
    'size_last': ['Es la más pequeña del grupo; la siguiente es {bigger}.', 'No hay ninguna menor en el grupo; la más parecida en tamaño es {bigger}.',
                  'Cierra la lista por tamaño, justo detrás de {bigger}.'],
    'size_share': ['Por sí sola representa el {share} del valor conjunto del sector.', 'Eso equivale al {share} de lo que vale todo el grupo junto.',
                   'Su peso en el grupo es grande: el {share} del valor conjunto.'],
    'size_alone': ['{name} tiene un valor de mercado de {mcap}.', 'La bolsa valora {name} en {mcap}.', '{name} vale {mcap} en bolsa.'],
    'hist_cagr_up': ['Los ingresos pasaron de {r0} en el ejercicio {fy0} a {r1} en el ejercicio {fy1}, alrededor de un {g} anual durante {n} años.',
                     'En {n} años las ventas fueron de {r0} (ejercicio {fy0}) a {r1} (ejercicio {fy1}): cerca de un {g} anual compuesto.',
                     'Las ventas crecen a un ritmo de un {g} anual desde el ejercicio {fy0}, de {r0} a {r1} en el ejercicio {fy1}.'],
    'hist_cagr_flat': ['Los ingresos apenas se han movido en {n} años: {r0} en el ejercicio {fy0} y {r1} en el ejercicio {fy1}.',
                       'La facturación está donde estaba hace {n} años: {r1} en el ejercicio {fy1} frente a {r0} en el ejercicio {fy0}.',
                       'Las ventas de {r1} en el ejercicio {fy1} se parecen mucho a los {r0} del ejercicio {fy0}.'],
    'hist_cagr_down': ['Los ingresos han caído de {r0} en el ejercicio {fy0} a {r1} en el ejercicio {fy1}, cerca de un {g} al año.',
                       'El negocio es más pequeño que antes: {r1} de ingresos en el ejercicio {fy1}, frente a {r0} en el ejercicio {fy0} (alrededor de un {g} anual).',
                       'En {n} años las ventas bajaron cerca de un {g} al año, de {r0} a {r1}.'],
    'hist_no_down': ['Los ingresos subieron en cada uno de los últimos {n} años de nuestros datos, sin ningún año a la baja.',
                     'No hay ningún año de caída en los últimos {n}: los ingresos crecieron siempre.', 'El historial no registra ninguna caída de ingresos en {n} años seguidos.'],
    'hist_down_one': ['El único año en que bajaron los ingresos fue el ejercicio {fy}, un {g}.', 'El ejercicio {fy} es la única mancha: los ingresos cayeron un {g} ese año.',
                      'Los ingresos cayeron solo una vez, en el ejercicio {fy} (un {g} menos).'],
    'hist_down_many': ['Los ingresos cayeron en {n} años ({years}); el peor fue el ejercicio {worst}, con un descenso del {g}.',
                       'No es una línea recta: las ventas bajaron en {years}, sobre todo en el ejercicio {worst} (un {g}).',
                       'Hubo {n} años a la baja, {years}, y el ejercicio {worst} fue el más duro, con los ingresos un {g} por debajo.'],
    'hist_best': ['El mejor año fue el ejercicio {fy}, cuando los ingresos saltaron un {g}.', 'Su mejor año de crecimiento fue el ejercicio {fy}: un {g} más de ingresos.',
                  'Destaca el ejercicio {fy}, con los ingresos un {g} arriba.'],
    'hist_record': ['Los ingresos del ejercicio {fy} fueron los más altos de su historia en nuestros datos.', 'El último año, el ejercicio {fy}, marcó un récord de ingresos.',
                    'Los ingresos del ejercicio {fy} fueron un máximo histórico.'],
    'hist_below_peak': ['Los ingresos siguen un {g} por debajo de su máximo de {peak} en el ejercicio {fy}.',
                        'La facturación no ha vuelto a los {peak} del ejercicio {fy}; le falta un {g}.', 'Las ventas tocaron techo en {peak} en el ejercicio {fy} y hoy están un {g} más abajo.'],
    'prof_all': ['Ganó dinero en cada uno de los {n} años que tenemos.', 'Todos los últimos {n} años fueron rentables.', 'No hay ningún año de pérdidas en los {n} años registrados.'],
    'prof_never': ['No ha tenido beneficio anual en ninguno de los {n} años que tenemos.', 'Los {n} años registrados terminaron en pérdidas.',
                   'El beneficio todavía no ha llegado: {n} años, {n} pérdidas.'],
    'prof_turn': ['Tras las pérdidas de {years}, pasó a ganar dinero en el ejercicio {fy} y lo ha mantenido.',
                  'El ejercicio {fy} fue el punto de giro: rentable desde entonces, después de perder dinero en {years}.',
                  'Está en números negros desde el ejercicio {fy}; antes perdió dinero en {years}.'],
    'prof_slip': ['Volvió a las pérdidas en el ejercicio {fy}, con {loss} en rojo.', 'El ejercicio {fy} cortó la racha de beneficios con una pérdida de {loss}.',
                  'El último año, el ejercicio {fy}, cerró con una pérdida de {loss} tras un año con beneficio.'],
    'prof_mixed': ['Los beneficios van y vienen: {n} años con pérdidas de {span} ({years}).', 'Perdió dinero en {n} de {span} años ({years}).',
                   'Las ganancias son irregulares, con pérdidas en {years}.'],
    'prof_margin_off': ['El margen neto tocó máximos del {peak} en el ejercicio {fy} y hoy es del {now}.',
                        'La rentabilidad está por debajo de su mejor momento: margen neto del {now} hoy frente al {peak} del ejercicio {fy}.',
                        'Los márgenes han bajado del {peak} del ejercicio {fy} al {now}.'],
    'prof_margin_best': ['El último margen neto, del {m}, es el mejor en {n} años.', 'Con un {m}, el margen neto es el más alto de los {n} años registrados.',
                         'Nunca había sido tan rentable en nuestros datos: margen neto del {m}.'],
    'fcf_all': ['El flujo de caja libre fue positivo en los {n} años.', 'Generó caja libre en cada uno de los {n} años.', 'La caja tras inversiones fue positiva todos los años ({n} de {n}).'],
    'fcf_none': ['El flujo de caja libre fue negativo en los {n} años: el negocio consume caja.', 'No ha generado caja libre en ninguno de los {n} años.',
                 'Cada uno de los {n} años gastó más caja de la que ingresó.'],
    'fcf_one': ['El flujo de caja libre solo fue positivo en uno de {n} años.', 'Generó caja libre en un único año de {n}.', 'Solo un año de los {n} dejó flujo de caja libre positivo.'],
    'fcf_most': ['El flujo de caja libre fue positivo en {pos} de {n} años.', 'Generó caja libre en {pos} de los {n} años.', 'En {pos} de {n} años la caja libre fue positiva.'],
    'fcf_some': ['El flujo de caja libre fue positivo en {pos} de {n} años.', 'Generó caja libre en {pos} años de {n}.', 'La generación de caja es irregular: positiva en {pos} de {n} años.'],
    'q_up': ['En {q} los ingresos fueron de {rev}, un {g} más que un año antes.', 'Los ingresos de {q} sumaron {rev}, un {g} más que en el mismo trimestre del año anterior.',
             '{q} dejó {rev} de ingresos, un aumento interanual del {g}.'],
    'q_flat': ['Los ingresos de {q} fueron de {rev}, casi iguales a los de un año antes.', 'En {q} los ingresos de {rev} quedaron planos frente al año anterior.',
               '{q} dejó ventas de {rev}, al mismo nivel que un año antes.'],
    'q_down': ['En {q} los ingresos fueron de {rev}, un {g} menos que un año antes.', 'Los ingresos de {q} cayeron un {g} interanual, hasta {rev}.',
               '{q} dejó {rev} de ingresos, un {g} menos que un año antes.'],
    'q_streak': ['Son {n} trimestres seguidos de crecimiento interanual.', 'Ya suma {n} trimestres consecutivos creciendo frente al año anterior.', 'La racha de crecimiento llega a {n} trimestres.'],
    'q_profit': ['El beneficio neto del trimestre fue de {ni}.', 'Ganó {ni} en ese trimestre.', 'Resultado neto del trimestre: {ni} de beneficio.'],
    'q_loss': ['El trimestre cerró con una pérdida neta de {ni}.', 'Perdió {ni} en ese trimestre.', 'Resultado neto del trimestre: una pérdida de {ni}.'],
    'peer_margin_hi': ['Su margen neto del {m} supera con claridad la mediana del {med} de las empresas de {ind}.',
                       'Con un {m}, se queda con más de cada dólar de ventas que la empresa típica de {ind} ({med}).',
                       'La rentabilidad es un punto fuerte: margen neto del {m} frente a una mediana del sector del {med}.'],
    'peer_margin_lo': ['Su margen neto del {m} queda por debajo de la mediana del {med} de las empresas de {ind}.',
                       'Se queda con menos de sus ventas que la mayoría de sus pares: {m} frente a una mediana del {med}.',
                       'La rentabilidad va por detrás del grupo: margen neto del {m}, mediana del {med}.'],
    'peer_loss_hi': ['Pierde dinero (margen neto del {m}), pero menos que la empresa típica de {ind} ({med}).',
                     'Su margen neto del {m} es una pérdida, aunque menor que la mediana del sector ({med}).', 'Las pérdidas son más ligeras que en la mayoría del grupo: {m} frente a una mediana del {med}.'],
    'peer_loss_lo': ['Su margen neto del {m} es una pérdida mayor que la mediana del {med} de las empresas de {ind}.',
                     'Pierde más por cada dólar vendido que la mayoría de sus pares: {m} frente a {med}.', 'Las pérdidas son más pesadas que en el grupo, {m} frente a una mediana del {med}.'],
    'peer_margin_eq': ['Su margen neto del {m} está cerca de la mediana del sector, del {med}.', 'Con un {m}, la rentabilidad está en línea con el grupo ({med}).',
                       'Los márgenes son los típicos de las empresas de {ind}: {m} frente a {med}.'],
    'peer_growth_hi': ['El crecimiento de ingresos del último año, {g}, superó la mediana del sector ({med}).', 'Creció más rápido que la mayoría de sus pares el último año ({g} frente a una mediana de {med}).',
                       'El crecimiento superó al del grupo: {g} frente a {med}.'],
    'peer_growth_lo': ['El crecimiento de ingresos del último año, {g}, quedó por debajo de la mediana del sector ({med}).', 'Sus pares crecieron más el último año: mediana de {med}, frente a {g} aquí.',
                       'El crecimiento se quedó atrás del grupo, {g} frente a {med}.'],
    'peer_growth_eq': ['El crecimiento de ingresos del último año, {g}, igualó la mediana del sector ({med}).', 'Creció en línea con sus pares el último año: {g} frente a {med}.',
                       'El crecimiento del último año, {g}, estuvo cerca de la mediana del grupo, {med}.'],
    'peer_pe_hi': ['El mercado paga {pe} veces sus beneficios, {x} la mediana del sector ({med}): espera más de esta empresa que de sus pares.',
                   'Con un PER de {pe} frente a una mediana del sector de {med}, la acción cotiza con una prima de {x} el múltiplo del grupo.',
                   'La valoración es exigente frente a sus pares: PER de {pe}, mediana del sector de {med}.'],
    'peer_pe_lo': ['Su PER de {pe} está por debajo de la mediana del sector ({med}): el mercado es más prudente con ella que con sus pares.',
                   'A {pe} veces beneficios es más barata que el par típico ({med}); la pregunta es si ese descuento está justificado.',
                   'La acción cotiza con descuento frente al grupo: PER de {pe} frente a {med}.'],
    'peer_pe_eq': ['Su PER de {pe} está cerca de la mediana del sector, de {med}.', 'La valoración está en línea con sus pares: PER de {pe}, mediana de {med}.',
                   'A {pe} veces beneficios cotiza como el grupo ({med}).'],
    'peer_pe_none': ['No tiene PER porque no es rentable; sí lo son {n} de las {tot} empresas de su sector.',
                     'Sin beneficio no hay PER que comparar; {n} de sus {tot} pares sí ganan dinero.',
                     'La comparación del PER todavía no aplica: pierde dinero, mientras {n} de {tot} pares son rentables.'],
    'roic_hi': ['Un retorno sobre el capital invertido del {roic} es alto, señal de un negocio con poder de precios o con pocos activos.',
                'Gana un {roic} sobre el capital invertido en ella, muy por encima de lo que cuesta ese capital.', 'El retorno sobre el capital invertido es sólido: {roic}.'],
    'roic_lo': ['El retorno sobre el capital invertido es de solo un {roic}, bajo para una empresa rentable.', 'Gana apenas un {roic} sobre su capital invertido.',
                'El retorno del capital es escaso: un {roic} sobre el capital invertido.'],
    'bs_cash': ['Tiene {net} más en caja que en deuda, el {p} de su valor de mercado.', 'La caja neta de {net} cubre el {p} del valor de mercado.',
                'El balance tiene {net} de caja neta, el {p} de lo que vale la empresa.'],
    'bs_debt_x': ['La deuda neta es de {net}, unas {x} veces un año de beneficio operativo en caja (EBITDA).', 'Debe {net} más de lo que tiene en caja, {x} veces el EBITDA.',
                  'Una deuda neta de {net} equivale a {x} años de EBITDA.'],
    'bs_debt_p': ['La deuda neta es de {net}, el {p} de su valor de mercado.', 'Arrastra {net} de deuda neta, el {p} del valor de mercado.', 'Deuda neta de caja: {net} (el {p} del valor de mercado).'],
    'bs_runway': ['Consumió {burn} de caja en los últimos doce meses; la caja disponible cubre unos {x} años a ese ritmo.',
                  'Al ritmo reciente de {burn} al año, su caja dura unos {x} años.', 'El consumo de caja fue de {burn} en doce meses, unos {x} años de margen.'],
    'bs_runway_short': ['Consumió {burn} de caja en los últimos doce meses y la caja solo cubre unos {x} años: cabe esperar nuevas acciones o nueva deuda.',
                        'El margen es corto: {burn} de consumo al año frente a caja para unos {x} años, así que es probable que necesite más financiación.',
                        'Con {burn} de consumo de caja al año, la caja dura unos {x} años; una ampliación de capital no sorprendería.'],
    'sh_dilute': ['El número de acciones ha crecido cerca de un {p} anual en tres años, lo que diluye a los accionistas.', 'Los accionistas se han diluido cerca de un {p} al año durante tres años.',
                  'Las acciones nuevas suman cerca de un {p} al año.'],
    'sh_buyback': ['El número de acciones ha bajado cerca de un {p} anual en tres años gracias a las recompras.', 'Las recompras han reducido las acciones cerca de un {p} al año.',
                   'Cada año hay menos acciones: cerca de un {p} menos al año en tres años.'],
    'div_yes': ['Paga un dividendo con una rentabilidad del {y} y lo ha pagado en {n} de los años de nuestros datos.', 'El dividendo rinde un {y}; los pagos se remontan a {n} años en nuestros datos.',
                'Quien busca rentas obtiene un {y}, pagado durante {n} años registrados.'],
    'sbc_heavy': ['La retribución en acciones equivale al {p} del flujo de caja libre, un coste real que las cifras de caja no reflejan.',
                  'La retribución en acciones es grande: el {p} del flujo de caja libre.', 'El flujo de caja libre la favorece: la retribución en acciones es el {p} de esa cifra.'],
    'an_up': ['Los analistas han subido sus estimaciones: {up} al alza y {dn} a la baja en los últimos 30 días.', 'Las revisiones se inclinan al alza: {up} subidas frente a {dn} bajadas en 30 días.',
              'En el último mes {up} analistas subieron sus cifras y {dn} las bajaron.'],
    'an_down': ['Los analistas han recortado sus estimaciones: {dn} a la baja y {up} al alza en los últimos 30 días.', 'Las revisiones se inclinan a la baja: {dn} recortes frente a {up} subidas en 30 días.',
                'En el último mes {dn} analistas recortaron sus cifras y solo {up} las subieron.'],
    'an_mixed': ['Las revisiones de estimaciones son mixtas: {up} al alza y {dn} a la baja en 30 días.', 'Los analistas no coinciden en la dirección: {up} subidas y {dn} recortes en el último mes.',
                 'En 30 días subieron {up} estimaciones y bajaron {dn}.'],
    'an_range': ['Los precios objetivo de {n} analistas van de {lo} a {hi}.', 'Los {n} precios objetivo abarcan de {lo} a {hi}.',
                 'Los objetivos varían mucho: {lo} en el extremo bajo y {hi} en el alto ({n} analistas).'],
    'an_next': ['Para {q} el consenso espera un beneficio por acción de {eps} con unos ingresos de {rev}.', 'El próximo informe cubre {q}: consenso de {eps} por acción y {rev} de ingresos.',
                'Los analistas esperan {eps} por acción y {rev} de ingresos para {q}.'],
    'an_next_eps': ['Para {q} el consenso espera un beneficio por acción de {eps}.', 'El próximo informe cubre {q}; el consenso es de {eps} por acción.', 'Los analistas esperan {eps} por acción para {q}.'],
}
