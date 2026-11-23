"""English pack for story.py (stockanaliz.com). Three phrasings per fact; the engine fixes one per company."""
import datetime


class F:
    @staticmethod
    def money(v):
        a = abs(v)
        if a >= 1e12: return '$%.2f trillion' % (v / 1e12)
        if a >= 1e9: return '$%.1f billion' % (v / 1e9)
        if a >= 1e6: return '$%.0f million' % (v / 1e6)
        return '$%.0f thousand' % (v / 1e3)

    @staticmethod
    def pct(v, d=0):
        return ('%.' + str(d) + 'f%%') % (v * 100)

    @staticmethod
    def mpct(v):   # margins: one decimal below 10%
        return ('%.1f%%' if abs(v) < 0.1 else '%.0f%%') % (v * 100)

    @staticmethod
    def spct(v):
        if abs(v) < 0.005:
            v = 0.0
        return '%s%.0f%%' % ('' if v == 0 else '+' if v > 0 else '−', abs(v) * 100)

    @staticmethod
    def num(v):
        return '%.1f' % v

    @staticmethod
    def times(v):
        return '%.1f times' % v if v < 10 else '%.0f times' % v

    @staticmethod
    def price(v):
        a = abs(v); d = 2
        if 0 < a < 0.005:   # sub-cent EPS: show it, not "$0.00" (23 Nov 2026)
            d = 3 if a >= 0.0005 else 4
        s = format(a, ',.%df' % d)
        return ('−' if v < 0 and float(s.replace(',', '')) else '') + '$' + s

    @staticmethod
    def years(ys):
        ys = [str(y) for y in ys]
        return ys[0] if len(ys) == 1 else ', '.join(ys[:-1]) + ' and ' + ys[-1]


def qdate(s):
    try:
        d = datetime.date.fromisoformat(str(s)[:10])
        return 'the quarter to %s %d' % (d.strftime('%B'), d.year)
    except Exception:
        return 'the latest quarter'


def month(m):
    return ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][m - 1]


T = {
    'eps_up': ['Diluted earnings per share rose from {e0} in fiscal {fy0} to {e1} in fiscal {fy1}, about {g} a year.', 'Per-share earnings went from {e0} to {e1} between fiscal {fy0} and fiscal {fy1} ({g} a year).',
               'Earnings per share have compounded at about {g} a year, {e0} in fiscal {fy0} to {e1} in fiscal {fy1}.'],
    'eps_faster': ['Earnings per share grew faster than sales, from {e0} in fiscal {fy0} to {e1} in fiscal {fy1} ({g} a year): margins widened along the way.',
                   'Per-share profit outran revenue: {e0} to {e1} from fiscal {fy0} to fiscal {fy1}, about {g} a year.',
                   'The bottom line did better than the top line, with earnings per share up about {g} a year to {e1} (fiscal {fy0}: {e0}).'],
    'eps_down': ['Diluted earnings per share fell from {e0} in fiscal {fy0} to {e1} in fiscal {fy1}, about {g} a year.', 'Per-share earnings shrank from {e0} to {e1} between fiscal {fy0} and fiscal {fy1}.',
                 'Earnings per share are lower than they were: {e1} in fiscal {fy1} against {e0} in fiscal {fy0}.'],
    'opm_up': ['The operating margin, {now} last year, is above its five-year average of {avg}.', 'Operating profitability has improved: {now} last year against a five-year average of {avg}.',
               'Last year’s operating margin of {now} beat the five-year average ({avg}).'],
    'opm_down': ['The operating margin, {now} last year, is below its five-year average of {avg}.', 'Operating profitability has slipped: {now} last year against a five-year average of {avg}.',
                 'Last year’s operating margin of {now} fell short of the five-year average ({avg}).'],
    'rnd': ['It spends {v} a year on research and development, {p} of revenue.', 'Research and development takes {p} of sales ({v} a year).', 'R&D spending of {v} equals {p} of revenue.'],
    'capex': ['Capital spending is heavy at {v} a year, {p} of revenue.', 'It reinvests {p} of its sales in plant and equipment ({v} a year).', 'Investment in fixed assets runs at {v}, {p} of revenue.'],
    'int_tight': ['Operating profit covers its {ie} interest bill only {x} times, a thin cushion.', 'Interest of {ie} a year eats most of operating profit (cover {x} times).',
                  'With interest cover of {x} times on a {ie} interest bill, there is little room for a bad year.'],
    'int_easy': ['Operating profit covers interest {x} times over: debt is not a burden.', 'Interest is a rounding error, covered {x} times by operating profit.', 'Interest cover is comfortable at {x} times.'],
    'fy_end': ['Its fiscal year ends in {m}.', 'Note that the fiscal year closes in {m}, not December.', 'Fiscal years end in {m}.'],
    'head': ['{name} in numbers: what the record shows', 'The {name} record, year by year', 'Reading {name}’s numbers'],
    # size
    'size_top': ['{name} is the largest of the {n} US-listed {ind} companies we track, worth {mcap}, about {x} the size of the next one, {other}.',
                 'At {mcap}, {name} leads the {ind} group on our list: {n} companies, and the runner-up, {other}, is {x} smaller.',
                 'No US-listed {ind} company on our list is bigger: {name} is valued at {mcap}, {x} the market value of {other}, the second largest of {n}.'],
    'size_rank': ['{name} is valued at {mcap}, number {rank} by size among the {n} US-listed {ind} companies we track.',
                  'With a market value of {mcap}, {name} ranks {rank} of {n} in the {ind} industry on our list.',
                  'Among {n} {ind} companies listed in the US, {name} comes in at number {rank} by market value ({mcap}).'],
    'size_between': ['Just above it sits {bigger}; just below, {smaller}.', 'Its nearest neighbours by size are {bigger} (larger) and {smaller} (smaller).',
                     'In size it falls between {bigger} and {smaller}.'],
    'size_last': ['It is the smallest of the group; the next one up is {bigger}.', 'Nothing in the group is smaller; {bigger} is the closest in size.',
                  'It closes the list by size, right behind {bigger}.'],
    'size_share': ['On its own it accounts for {share} of the industry’s combined market value.', 'That is {share} of what the whole group is worth together.',
                   'Its weight in the group is large: {share} of the combined value.'],
    'size_alone': ['{name} has a market value of {mcap}.', 'The market values {name} at {mcap}.', '{name} is worth {mcap} on the stock market.'],
    # long record
    'hist_cagr_up': ['Revenue grew from {r0} in fiscal {fy0} to {r1} in fiscal {fy1}, about {g} a year over {n} years.',
                     'Over {n} years the top line went from {r0} (fiscal {fy0}) to {r1} (fiscal {fy1}): roughly {g} a year compounded.',
                     'Sales have compounded at about {g} a year since fiscal {fy0}, from {r0} to {r1} in fiscal {fy1}.'],
    'hist_cagr_flat': ['Revenue has barely moved in {n} years: {r0} in fiscal {fy0}, {r1} in fiscal {fy1}.',
                       'The top line is about where it was {n} years ago, {r1} in fiscal {fy1} against {r0} in fiscal {fy0}.',
                       'Sales of {r1} in fiscal {fy1} are close to the {r0} of fiscal {fy0}: a flat decade-scale record.'],
    'hist_cagr_down': ['Revenue has shrunk from {r0} in fiscal {fy0} to {r1} in fiscal {fy1}, about {g} a year.',
                       'The business is smaller than it was: {r1} of revenue in fiscal {fy1}, down from {r0} in fiscal {fy0} (about {g} a year).',
                       'Over {n} years sales fell about {g} a year, from {r0} to {r1}.'],
    'hist_no_down': ['Revenue rose in every one of the last {n} years in our data, with no down year.', 'There is no down year in the last {n}: revenue grew each time.',
                     'The record has no revenue decline in {n} consecutive years.'],
    'hist_down_one': ['The only year revenue fell was fiscal {fy}, by {g}.', 'Fiscal {fy} is the one blemish: revenue dropped {g} that year.',
                      'Revenue fell just once, in fiscal {fy} ({g} lower).'],
    'hist_down_many': ['Revenue fell in {n} years ({years}); the worst was fiscal {worst}, down {g}.',
                       'It is not a straight line: sales declined in {years}, most sharply in fiscal {worst} ({g}).',
                       'There were {n} down years, {years}, and fiscal {worst} was the hardest, with revenue {g} lower.'],
    'hist_best': ['The strongest year was fiscal {fy}, when revenue jumped {g}.', 'Its best year for growth was fiscal {fy}: {g} more revenue.',
                  'Fiscal {fy} stands out, with revenue up {g}.'],
    'hist_record': ['Fiscal {fy} revenue was the highest in its history in our data.', 'The latest year, fiscal {fy}, set a revenue record.',
                    'Revenue in fiscal {fy} was a new high.'],
    'hist_below_peak': ['Revenue is still {g} below its peak of {peak} in fiscal {fy}.', 'The top line has not recovered to the {peak} of fiscal {fy}; it is {g} short.',
                        'Sales peaked at {peak} in fiscal {fy} and are now {g} lower.'],
    # profits
    'prof_all': ['It made a profit in each of the {n} years we have.', 'Every one of the last {n} years was profitable.',
                 'There is no loss year in the {n} years on record.'],
    'prof_never': ['It has not made an annual profit in any of the {n} years we have.', 'All {n} years on record were loss years.',
                   'Profit is still ahead of it: {n} years, {n} losses.'],
    'prof_turn': ['After losses in {years}, it turned profitable in fiscal {fy} and has stayed there.',
                  'Fiscal {fy} was the turn: profitable since then, after losing money in {years}.',
                  'It has been in the black since fiscal {fy}; before that it lost money in {years}.'],
    'prof_slip': ['It slipped back into a loss in fiscal {fy}, losing {loss}.', 'Fiscal {fy} broke the profit run with a {loss} loss.',
                  'The latest year, fiscal {fy}, ended with a loss of {loss} after a profitable year before.'],
    'prof_mixed': ['Profits have come and gone: {n} loss years out of {span} ({years}).', 'It lost money in {n} of {span} years ({years}).',
                   'Earnings are uneven, with losses in {years}.'],
    'prof_margin_off': ['The net margin peaked at {peak} in fiscal {fy} and is {now} now.', 'Profitability is below its best: {now} net margin today against {peak} in fiscal {fy}.',
                        'Margins have come down from the {peak} of fiscal {fy} to {now}.'],
    'prof_margin_best': ['The latest net margin, {m}, is the best in {n} years.', 'At {m}, the net margin is the highest in the {n} years on record.',
                         'It has never been more profitable in our data: a {m} net margin.'],
    'fcf_all': ['Free cash flow was positive in all {n} years.', 'It generated free cash in each of the {n} years.', 'Cash flow after investment was positive every year ({n} of {n}).'],
    'fcf_none': ['Free cash flow was negative in all {n} years: the business consumes cash.', 'It has not generated free cash in any of {n} years.',
                 'Every year of the {n} used more cash than it brought in.'],
    'fcf_one': ['Free cash flow was positive in only one of {n} years.', 'It produced free cash in just one year out of {n}.', 'Only one year of the {n} brought positive free cash flow.'],
    'fcf_most': ['Free cash flow was positive in {pos} of {n} years.', 'It generated free cash in {pos} of the {n} years.', 'Only {n_minus} of the {n} years used more cash than came in.'.replace('{n_minus}', 'a few')],
    'fcf_some': ['Free cash flow was positive in {pos} of {n} years.', 'It produced free cash in {pos} years out of {n}.', 'Cash generation is patchy: positive in {pos} of {n} years.'],
    # quarters
    'q_up': ['In {q} revenue was {rev}, {g} more than a year earlier.', 'Revenue for {q} came to {rev}, up {g} on the same quarter a year before.',
             '{q} brought {rev} of revenue, a {g} increase year on year.'],
    'q_flat': ['Revenue for {q} was {rev}, about the same as a year earlier.', '{q} revenue of {rev} was flat on the year.', 'In {q} sales were {rev}, level with a year ago.'],
    'q_down': ['In {q} revenue was {rev}, {g} less than a year earlier.', 'Revenue for {q} fell {g} year on year to {rev}.', '{q} brought {rev} of revenue, down {g} on a year before.'],
    'q_streak': ['That is {n} quarters in a row of year-on-year growth.', 'It has now grown on the year for {n} straight quarters.', 'The growth streak runs to {n} quarters.'],
    'q_profit': ['The quarter’s net profit was {ni}.', 'It earned {ni} in that quarter.', 'Net income for the quarter: {ni}.'],
    'q_loss': ['The quarter ended with a net loss of {ni}.', 'It lost {ni} in that quarter.', 'Net result for the quarter: a {ni} loss.'],
    # peers
    'peer_margin_hi': ['Its net margin of {m} is well above the {med} median for {ind} companies.', 'At {m}, it keeps more of each dollar of sales than the typical {ind} company ({med}).',
                       'Profitability is a strength: {m} net margin against an industry median of {med}.'],
    'peer_margin_lo': ['Its net margin of {m} trails the {med} median for {ind} companies.', 'It keeps less of its sales than most peers: {m} against a {med} median.',
                       'Profitability lags the group: {m} net margin, median {med}.'],
    'peer_loss_hi': ['It loses money ({m} net margin), but less than the typical {ind} company ({med}).', 'Its {m} net margin is a loss, though a smaller one than the {med} industry median.',
                     'Losses are lighter than in most of the group: {m} against a {med} median.'],
    'peer_loss_lo': ['Its net margin of {m} is a deeper loss than the {med} median for {ind} companies.', 'It loses more per dollar of sales than most peers: {m} against {med}.',
                     'Losses run heavier than in the group, {m} against a {med} median.'],
    'peer_margin_eq': ['Its net margin of {m} is close to the {med} industry median.', 'At {m}, profitability is in line with the group ({med}).',
                       'Margins are typical for {ind} companies: {m} against {med}.'],
    'peer_growth_hi': ['Last year’s revenue growth of {g} beat the industry median of {med}.', 'It grew faster than most peers last year ({g} against a median {med}).',
                       'Growth outpaced the group: {g} versus {med}.'],
    'peer_growth_lo': ['Last year’s revenue growth of {g} was below the industry median of {med}.', 'Peers grew faster last year: median {med}, against {g} here.',
                       'Growth lagged the group, {g} against {med}.'],
    'peer_growth_eq': ['Revenue growth of {g} last year matched the industry median ({med}).', 'It grew in line with peers last year: {g} against {med}.',
                       'Last year’s growth, {g}, was close to the group median of {med}.'],
    'peer_pe_hi': ['The market pays {pe} times earnings for it, {x} the industry median of {med}: it expects more from this company than from its peers.',
                   'At a P/E of {pe} against an industry median of {med}, the shares carry a premium of {x} the group multiple.',
                   'Valuation is demanding next to peers: P/E {pe}, industry median {med}.'],
    'peer_pe_lo': ['Its P/E of {pe} is below the industry median of {med}: the market is more cautious about it than about its peers.',
                   'At {pe} times earnings it is cheaper than the typical peer ({med}); the question is whether that discount is deserved.',
                   'The shares trade at a discount to the group, P/E {pe} against {med}.'],
    'peer_pe_eq': ['Its P/E of {pe} is close to the industry median of {med}.', 'Valuation is in line with peers: P/E {pe}, median {med}.',
                   'At {pe} times earnings it is priced like the group ({med}).'],
    'peer_pe_none': ['It has no P/E because it is not profitable; {n} of the {tot} companies in its industry are.',
                     'With no profit there is no P/E to compare; {n} of {tot} peers do earn money.',
                     'The P/E comparison does not apply yet: it loses money, while {n} of {tot} peers are profitable.'],
    'roic_hi': ['A return on invested capital of {roic} is high, the mark of a business with pricing power or a light asset base.',
                'It earns {roic} on the capital invested in it, well above what that capital costs.', 'Return on invested capital is strong at {roic}.'],
    'roic_lo': ['Return on invested capital is only {roic}, low for a profitable company.', 'It earns just {roic} on its invested capital.',
                'Capital returns are thin: {roic} on invested capital.'],
    # balance sheet
    'bs_cash': ['It holds {net} more cash than debt, {p} of its market value.', 'Net cash of {net} covers {p} of the market value.',
                'The balance sheet carries {net} of net cash, equal to {p} of what the company is worth.'],
    'bs_debt_x': ['Net debt is {net}, about {x} times a year of operating cash earnings (EBITDA).', 'It owes {net} more than it holds in cash, {x} times EBITDA.',
                  'Net debt of {net} equals {x} years of EBITDA.'],
    'bs_debt_p': ['Net debt is {net}, {p} of its market value.', 'It carries {net} of net debt, equal to {p} of the market value.', 'Debt net of cash: {net} ({p} of market value).'],
    'bs_runway': ['It used {burn} of cash over the last twelve months; cash on hand covers about {x} years at that rate.',
                  'At the recent burn of {burn} a year, its cash lasts about {x} years.', 'Cash burn was {burn} over twelve months, about {x} years of runway.'],
    'bs_runway_short': ['It used {burn} of cash over the last twelve months and cash covers only about {x} years: expect new shares or new debt.',
                        'Runway is short: {burn} of burn a year against cash for about {x} years, so more funding is likely.',
                        'At {burn} of cash burn a year, the cash pile lasts about {x} years; a capital raise would not surprise.'],
    'sh_dilute': ['The share count has grown about {p} a year over three years, diluting existing holders.', 'Shareholders have been diluted by about {p} a year for three years.',
                  'New shares add about {p} a year to the count.'],
    'sh_buyback': ['The share count has fallen about {p} a year over three years as it buys back stock.', 'Buybacks have cut the share count by about {p} a year.',
                   'There are fewer shares each year: about {p} fewer a year over three years.'],
    'div_yes': ['It pays a dividend yielding {y} and has paid one in {n} of the years in our data.', 'The dividend yields {y}; payments go back {n} years in our data.',
                'Income investors get a {y} yield, paid for {n} years on record.'],
    'sbc_heavy': ['Stock-based pay equals {p} of free cash flow, a real cost that cash flow figures leave out.', 'Share-based compensation is large: {p} of free cash flow.',
                  'Free cash flow flatters it: stock pay is {p} of it.'],
    # analysts
    'an_up': ['Analysts have been raising estimates: {up} up and {dn} down in the last 30 days.', 'Estimate revisions lean positive, {up} up against {dn} down over 30 days.',
              'In the last month {up} analysts raised their numbers and {dn} cut them.'],
    'an_down': ['Analysts have been cutting estimates: {dn} down and {up} up in the last 30 days.', 'Revisions lean negative, {dn} cuts against {up} raises in 30 days.',
                'In the last month {dn} analysts cut their numbers and only {up} raised them.'],
    'an_mixed': ['Estimate revisions are mixed: {up} up, {dn} down in 30 days.', 'Analysts are split on direction, {up} raises and {dn} cuts in the past month.',
                 'Over 30 days {up} estimates went up and {dn} went down.'],
    'an_range': ['Price targets from {n} analysts run from {lo} to {hi}.', 'The {n} price targets span {lo} to {hi}.', 'Targets range widely, {lo} at the low end and {hi} at the top ({n} analysts).'],
    'an_next': ['For {q} the consensus expects earnings of {eps} a share on revenue of {rev}.', 'The next report covers {q}: consensus {eps} a share, {rev} of revenue.',
                'Analysts look for {eps} a share and {rev} of revenue for {q}.'],
    'an_next_eps': ['For {q} the consensus expects earnings of {eps} a share.', 'The next report covers {q}; consensus is {eps} a share.', 'Analysts look for {eps} a share for {q}.'],
}
