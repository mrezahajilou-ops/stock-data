# -*- coding: utf-8 -*-
"""English labels for the ETF section. The per-fund text lives in etf_list.py, so T is empty here."""

UI = dict(
    home='Home', etfs='ETFs', other='Other',
    h1='The {N} biggest ETFs in the world',
    sub='Holdings, weights and valuations · updated',
    lead='The {N} largest exchange-traded funds in the world, with what each one is actually for, '
         'what it holds, and what the companies inside it are worth.',
    intro='The price/earnings ratio on these pages is not taken from the fund. Every holding is '
          'matched to our own page for that company and the figures are weighted by the fund’s own '
          'weights, so an ETF’s P/E here is built from the same SEC filings as every stock page on '
          'this site — and you can click any holding to read about the company.',
    idea='The idea', ret='Return', fund='What the companies inside it are worth',
    holds='Biggest holdings', made='What it is made of',
    where='Can you buy it where you live?', company='Company', weight='Weight',
    all50='All {N} funds, side by side', fundcol='Fund',
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
    i_title='The {N} Biggest ETFs: Holdings, P/E and Returns',
    i_desc='The {N} largest ETFs in the world with their holdings, weights and one-year returns, '
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

UCITS = {}   # already English

# phone layout: return ranking, fund finder, quick keys (etf_pages.py, web_src/etfm.*)
UI.update({'rank_h': 'Return ranking', 'rank_all': 'Show all %(n)s funds ▾', 'rank_less': 'Show the top 10 ▴', 'rank_note': 'Price return without dividends. Tap a fund to open its page.', 'find_ph': 'Search the {N} funds: ticker, name or type', 'sort_big': 'Largest', 'sort_pe': 'Lowest P/E', 'n_funds': '%n funds', 'no_fund': 'No fund matches that search.', 'more': 'Read more ▾', 'less': 'Show less ▴', 'holds_all': 'Show all %(n)s holdings ▾', 'holds_less': 'Show the top 10 ▴', 'k_idea': 'Idea', 'k_val': 'Valuation', 'k_ret': 'Return', 'k_hold': 'Holdings', 'k_sec': 'Page sections', 'k_find': 'Search', 'k_ph': 'Search any stock or ETF', 'k_none': 'No match', 'l_y1': 'Past year', 'l_avg': 'Avg a year', 'l_hold': 'Holdings', 'l_pe': 'P/E'})

# ---- funds 51-100 (Nov 2026)
UI['focus_labels'].update({'US treasury bonds': 'US Treasuries', 'US corporate bonds': 'US corporate bonds', 'high yield bonds': 'High-yield bonds', 'municipal bonds': 'Municipal bonds', 'US covered call': 'Covered-call income', 'consumer discretionary': 'Consumer discretionary', 'consumer staples': 'Consumer staples', 'utilities': 'Utilities', 'materials': 'Materials', 'communication services': 'Communication services', 'biotech': 'Biotech', 'aerospace and defense': 'Aerospace & defense', 'banks': 'Banks', 'gold miners': 'Gold miners', 'oil and gas': 'Oil & gas', 'cybersecurity': 'Cybersecurity', 'clean energy': 'Clean energy', 'innovation': 'Innovation', 'US momentum': 'US momentum', 'US low volatility': 'US low volatility', 'Japan': 'Japan', 'China': 'China', 'India': 'India', 'Brazil': 'Brazil', 'silver': 'Silver', 'ether': 'Ether'})

_G = UI['groups']
_G[1][1].extend(['US momentum', 'US low volatility'])
_G[2][1].append('US covered call')
_G[4][1].extend(['Japan', 'China', 'India', 'Brazil'])
_G[5][1].extend(['consumer discretionary', 'consumer staples', 'utilities', 'materials', 'communication services', 'biotech', 'aerospace and defense', 'banks', 'gold miners', 'oil and gas', 'cybersecurity', 'clean energy', 'innovation'])
_G[6][1].extend(['US treasury bonds', 'US corporate bonds', 'high yield bonds', 'municipal bonds', 'silver', 'ether'])

# ---- comparison and "which ETFs hold" pages
UI.update({
    'c_title': '%(a)s vs %(b)s: Which ETF Is Better? Returns, P/E, Overlap',
    'c_h1': '%(a)s vs %(b)s', 'c_crumb': '%(a)s vs %(b)s',
    'c_sub': 'Returns, valuation, cost of what they hold and how much they overlap, side by side.',
    'c_what': 'What each one is', 'c_side': 'Side by side', 'c_says': 'What the numbers say',
    'c_shared': 'Biggest holdings they share', 'c_issuer': 'Manager', 'c_index': 'Index',
    'c_with': 'Compare %(t)s with',
    'v_ret': '%(w)s returned more over the past year: %(x)s against %(y)s.',
    'v_pe': '%(w)s holds cheaper companies on our price/earnings measure: %(x)s against %(y)s.',
    'v_ov': '%(ov)s of %(a)s, by weight of its biggest holdings, is in companies %(b)s also owns, so owning both adds less diversification than it seems.',
    'v_noov': '%(a)s and %(b)s share none of their biggest holdings, so they do different jobs in a portfolio.',
    'hold_slug': 'which-etfs-hold-%s',
    'h_title': 'Which ETFs Hold %(name)s (%(t)s)? Weights and Returns',
    'h_h1': 'Which ETFs hold %(name)s?',
    'h_lead': '%(n)s of the %(N)s ETFs we cover hold %(name)s among their biggest positions.',
    'h_top': 'The biggest weight is in %(f)s, where %(name)s makes up %(w)s of the fund.',
    'h_stock': 'Read our full analysis of %(name)s ›',
    'h_note': 'From each fund’s own published holdings; only the largest positions of each fund are checked, so smaller holdings across the %(N)s funds are not listed.',
})

# ---- funds 101-150 (Nov 2026)
UI['focus_labels'].update({'software': 'Software', 'leveraged': 'Leveraged (3x daily)', 'uranium': 'Uranium', 'copper miners': 'Copper miners', 'lithium and batteries': 'Lithium & batteries', 'solar': 'Solar', 'infrastructure': 'Infrastructure', 'robotics and AI': 'Robotics & AI', 'airlines': 'Airlines', 'China internet': 'China internet', 'homebuilders': 'Homebuilders', 'metals and mining': 'Metals & mining', 'Germany': 'Germany', 'Taiwan': 'Taiwan', 'South Korea': 'South Korea', 'United Kingdom': 'United Kingdom', 'emerging market bonds': 'Emerging-market bonds'})
_G = UI['groups']
_G[4][1].extend(['Germany', 'United Kingdom', 'Taiwan', 'South Korea'])
_G[5][1].extend(['software', 'robotics and AI', 'infrastructure', 'homebuilders', 'metals and mining', 'copper miners', 'uranium', 'lithium and batteries', 'solar', 'airlines', 'China internet', 'leveraged'])
_G[6][1].append('emerging market bonds')
