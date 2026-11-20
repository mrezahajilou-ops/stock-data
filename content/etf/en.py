# -*- coding: utf-8 -*-
"""English labels for the ETF section. The per-fund text lives in etf_list.py, so T is empty here."""

UI = dict(
    home='Home', etfs='ETFs', other='Other',
    h1='The 50 biggest ETFs in the world',
    sub='Holdings, weights and valuations · updated',
    lead='The fifty largest exchange-traded funds in the world, with what each one is actually for, '
         'what it holds, and what the companies inside it are worth.',
    intro='The price/earnings ratio on these pages is not taken from the fund. Every holding is '
          'matched to our own page for that company and the figures are weighted by the fund’s own '
          'weights, so an ETF’s P/E here is built from the same SEC filings as every stock page on '
          'this site — and you can click any holding to read about the company.',
    idea='The idea', ret='Return', fund='What the companies inside it are worth',
    holds='Biggest holdings', made='What it is made of',
    where='Can you buy it where you live?', company='Company', weight='Weight',
    all50='All fifty funds, side by side', fundcol='Fund',
    y1='Past year', y3='Past 3 years', y5='Past 5 years', ytd='This year',
    m1='Past month', m3='Past 3 months',
    price='Price', pe='Price / earnings', ps='Price / sales',
    growth='Revenue growth, last year', margin='Net margin', score='Our average score',
    holdings='Holdings',
    chartcap='One-year price return, every fund on this page. Click a bar to open it.',
    linecap='Price since %(year)s. Dividends are not included.',
    note_ret='Price return only. A fund that pays dividends returned more than this; one that '
             'accumulates them did not.',
    note_pe='Not taken from the fund. Each holding is matched to our own page for that company and '
            'the figures are weighted by the fund’s own weights, so they are built from the same '
            'filings as the rest of this site. We cover %(cov)s of this fund by weight (%(n)s of %(total)s positions).',
    note_holds='Top %(n)d of %(total)s positions, from the fund’s own published holdings%(asof)s. Company names that '
               'link through have a full page on this site.',
    note_ctry='The general position, not advice about any particular broker or about tax. Where a '
              'fund cannot be bought it is the European document rule doing it, not the broker.',
    note_tbl='The price/earnings column is worked out from the companies each fund holds, weighted by '
             'the fund’s own weights, using the same figures as our stock pages. It is blank where '
             'the fund does not hold shares, and where the fund is mostly companies listed outside '
             'the United States, which we do not cover.',
    no_pe_h='Why there is no price/earnings ratio here',
    no_pe_bond='This fund does not own shares in companies, so there are no earnings to divide the '
               'price by. What matters for it instead is what it lends to and for how long: credit '
               'quality and duration for a bond fund, and the price of the thing itself for gold or '
               'bitcoin. It holds %(n)s positions.',
    no_pe_thin='Our company data covers companies listed in the United States. This fund holds %(n)s '
               'positions and only %(cov)s of its weight is in companies we cover, so a price/earnings '
               'ratio built from that part would describe a slice of the fund rather than the fund. '
               'We would rather leave it out than print a number that looks like an answer. The '
               'holdings and weights below are the fund’s own.',
    priips='%(fund)s is domiciled in the United States. US funds do not publish the key information '
           'document that European rules require, so a retail investor in the European Union or the '
           'United Kingdom cannot buy it — the order is simply refused, whatever broker they use. '
           'Investors in most of Latin America, the Middle East, Turkey and much of Asia can buy it '
           'through an international broker, subject to their own local rules.',
    in_europe='If you are in Europe:',
    vs_sp='The S&P 500 on the same measure is %(sp)s times, so this fund is %(diff)s %(dir)s.',
    more_exp='more expensive', cheaper='cheaper',
    shariah='Shariah-screened alternative',
    dis='Holdings from each fund’s own filings with the SEC; company figures from SEC filings, '
        'rebuilt every day. Educational information, not investment advice.',
    i_title='The 50 Biggest ETFs: Holdings, P/E and Returns',
    i_desc='The fifty largest ETFs in the world with their holdings, weights and one-year returns, '
           'and a price/earnings ratio worked out from the companies each one actually holds.',
    d_title='%(t)s ETF: holdings, P/E and returns',
    d_desc='%(name)s (%(t)s) holdings, weights and returns, with a price/earnings ratio built from '
           'the companies it actually holds. %(idea)s',
    groups=[
        ('Core US market', ['US large cap', 'US total market']),
        ('Growth and value', ['US large cap growth', 'US mega cap growth', 'US large cap value', 'US quality factor']),
        ('Dividends', ['US dividend', 'US dividend growth']),
        ('Smaller companies', ['US mid cap', 'US small cap']),
        ('Outside the United States', ['developed ex-US', 'global ex-US', 'global', 'emerging markets', 'Europe']),
        ('Sectors', ['technology', 'semiconductors', 'financials', 'healthcare', 'energy', 'industrials', 'real estate']),
        ('Bonds, gold and bitcoin', ['US investment grade bonds', 'international bonds', 'gold', 'bitcoin']),
    ],
)

T = {}   # English per-fund text comes from etf_list.py

# columns of the index box: the type tag, the localised name grammar and the P/E note
UI.update({
    'type': 'Type',
    'avg_yr': 'Average a year',
    'pe_avg': 'Average P/E',
    'name_pattern': '%(issuer)s %(index)s',
    'note_peavg': 'Nobody publishes a historical price/earnings ratio for a fund, because it depends on what the fund held at the time. So we started recording ours on %(since)s. The average column fills in once there is about a month of it.',
    'note_peavg_none': 'The average price/earnings column fills in as we record each day’s figure.',
    'focus_labels': {},
})

UI['pe_short'] = 'P/E'
UI['focus_labels'] = {'US large cap': 'US large cap', 'US total market': 'US total market', 'US large cap growth': 'US growth', 'US mega cap growth': 'US mega-cap growth', 'US large cap value': 'US value', 'US quality factor': 'US quality', 'US dividend': 'US dividend', 'US dividend growth': 'Dividend growth', 'US mid cap': 'US mid cap', 'US small cap': 'US small cap', 'developed ex-US': 'Developed ex-US', 'global ex-US': 'Global ex-US', 'global': 'Global', 'emerging markets': 'Emerging markets', 'Europe': 'Europe', 'technology': 'Technology', 'semiconductors': 'Semiconductors', 'financials': 'Financials', 'healthcare': 'Healthcare', 'energy': 'Energy', 'industrials': 'Industrials', 'real estate': 'Real estate', 'US investment grade bonds': 'US bonds', 'international bonds': 'International bonds', 'gold': 'Gold', 'bitcoin': 'Bitcoin'}
