/* Stock screener v2 (shared by every language site).
   - "Add filters" opens a searchable, grouped list of every available filter
   - every chosen filter gets its own control: ready-made conditions plus a custom over / under / between / exactly rule
   - result table with ready-made column views, a view made of the active filters, and a custom column picker
   Data: core.json (default views, loaded first) + more.json (everything else) from the "scrx" branch of stock-data.
   Language: window.SCR2_CFG = {lang, stockUrl}; labels come from window.SCR2_I18N[lang] (English text is the key). */
(function () {
  'use strict';
  var CFG = window.SCR2_CFG || {}, LANG = CFG.lang || 'en', W = (window.SCR2_I18N || {})[LANG] || {};
  var RTL = LANG === 'fa' || LANG === 'ar';
  var BASE = CFG.data || 'https://raw.githubusercontent.com/mrezahajilou-ops/stock-data/scrx';
  var QUOTES = CFG.quotes || 'https://raw.githubusercontent.com/mrezahajilou-ops/stock-data/quotes/quotes.json';
  var STOCK = CFG.stockUrl || '/stock/#';
  var PAGE = 50, LS = 'scr2_' + LANG + '_';
  var ACCESS = CFG.access !== false, FREE = CFG.freeRows || 10;   /* members-only sites show the first rows and a subscribe box */
  function L(s) { var a = arguments, t = W[s] != null ? W[s] : s; if (a.length < 2) return t; return t.replace(/%([12])/g, function (m, i) { var v = a[+i]; if (v == null) return m; if (LANG === 'fa' && /^[\d,]+$/.test(String(v))) v = String(v).replace(/\d/g, function (d) { return String.fromCharCode(0x06F0 + +d) }).replace(/,/g, '\u066C'); return v }) }
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c] }) }
  function $(s, r) { return (r || document).querySelector(s) }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)) }
  function ltr(s) { return RTL ? '<bdi dir="ltr">' + s + '</bdi>' : s }

  /* ------------------------------------------------------------------ filter catalogue
     [key, label, type, description]
     types: m money ($M) · p percent · y yield percent · x multiple · n number · pr price · s score 0-5 · i whole number
            v volume · sh shares (M) · d days from today · c category */
  var CATS = [
    ['Most popular', [
      ['mcap', 'Market cap', 'm', 'Share price times shares outstanding.'],
      ['sector', 'Sector', 'c', 'Broad group of the economy the company belongs to.'],
      ['industry', 'Industry', 'c', 'The specific line of business.'],
      ['price', 'Stock price', 'pr', 'Latest share price.'],
      ['pe', 'P/E ratio', 'x', 'Price divided by earnings per share of the last twelve months.'],
      ['divy', 'Dividend yield', 'y', 'Yearly dividend per share divided by the share price.'],
      ['chg1d', 'Price change 1D', 'p', 'Price change on the latest trading day.'],
      ['revg1', 'Revenue growth', 'p', 'Revenue growth in the last fiscal year.'],
      ['rec', 'Analyst rating', 'c', 'Consensus recommendation of Wall Street analysts.'],
      ['s_total', 'Overall score', 's', 'Our 0 to 5 score: average of value, future, past, health and shareholder returns.'],
      ['country', 'Country', 'c', 'Country of the company headquarters.']]],
    ['Company', [
      ['ipo', 'IPO year', 'i', 'Year the stock started trading.'],
      ['years', 'Years of data', 'i', 'Fiscal years of financial statements available.'],
      ['cur', 'Reporting currency', 'c', 'Currency of the financial statements (all amounts here are shown in US dollars).'],
      ['fy_month', 'Fiscal year end (month)', 'c', 'Month in which the fiscal year ends.'],
      ['earn_in', 'Next earnings date', 'd', 'Date of the next earnings report.'],
      ['exdiv_in', 'Ex-dividend date', 'd', 'Latest or next ex-dividend date.']]],
    ['Price & volume', [
      ['r1w', 'Price change 1W', 'p', 'Price change over one week.'],
      ['r1m', 'Price change 1M', 'p', 'Price change over one month.'],
      ['r3m', 'Price change 3M', 'p', 'Price change over three months.'],
      ['r6m', 'Price change 6M', 'p', 'Price change over six months.'],
      ['rytd', 'Price change YTD', 'p', 'Price change since the start of the year.'],
      ['r1y', 'Price change 1Y', 'p', 'Price change over one year.'],
      ['r3y', 'Price change 3Y', 'p', 'Total price change over three years.'],
      ['r5y', 'Price change 5Y', 'p', 'Total price change over five years.'],
      ['r10y', 'Price change 10Y', 'p', 'Total price change over ten years.'],
      ['cagr3', 'Annual return 3Y', 'p', 'Average yearly price return over three years.'],
      ['cagr5', 'Annual return 5Y', 'p', 'Average yearly price return over five years.'],
      ['cagr10', 'Annual return 10Y', 'p', 'Average yearly price return over ten years.'],
      ['hi52', '52-week high', 'pr', 'Highest price of the last 52 weeks.'],
      ['lo52', '52-week low', 'pr', 'Lowest price of the last 52 weeks.'],
      ['off_hi', 'From 52-week high', 'p', 'How far the price is below its 52-week high.'],
      ['off_lo', 'From 52-week low', 'p', 'How far the price is above its 52-week low.'],
      ['range_pos', 'Position in 52-week range', 'p', '0% is the 52-week low, 100% is the 52-week high.'],
      ['off_ath', 'From 10-year high', 'p', 'How far the price is below its highest weekly close of the last ten years.'],
      ['vol', 'Average volume', 'v', 'Average number of shares traded per day (3 months).'],
      ['dvol', 'Dollar volume', 'm', 'Average daily volume times the share price.'],
      ['relvol', 'Relative volume', 'x', '10-day average volume divided by the 3-month average.'],
      ['beta', 'Beta', 'n', 'Sensitivity to market moves (1 = moves with the market).'],
      ['volat', 'Volatility (1Y)', 'p', 'Annualised volatility of weekly returns over one year.']]],
    ['Technicals', [
      ['rsi', 'RSI (14)', 'n', 'Relative strength index: under 30 is oversold, over 70 is overbought.'],
      ['ma50', 'Price vs 50-day average', 'p', 'Distance of the price from its 50-day moving average.'],
      ['ma200', 'Price vs 200-day average', 'p', 'Distance of the price from its 200-day moving average.'],
      ['ma_cross', '50-day vs 200-day average', 'p', 'Above 0 means the 50-day average is above the 200-day average (golden cross side).']]],
    ['Valuation', [
      ['ev', 'Enterprise value', 'm', 'Market cap plus debt minus cash.'],
      ['fwd_pe', 'Forward P/E', 'x', 'Price divided by expected earnings per share of the next twelve months.'],
      ['peg', 'PEG ratio', 'x', 'P/E divided by expected earnings growth.'],
      ['ps', 'P/S ratio', 'x', 'Market cap divided by revenue of the last twelve months.'],
      ['fwd_ps', 'Forward P/S', 'x', 'Market cap divided by expected revenue.'],
      ['pb', 'P/B ratio', 'x', 'Market cap divided by shareholders’ equity.'],
      ['ptbv', 'P/TBV ratio', 'x', 'Market cap divided by tangible book value (equity minus goodwill and intangibles).'],
      ['pfcf', 'P/FCF ratio', 'x', 'Market cap divided by free cash flow.'],
      ['fwd_pfcf', 'Forward P/FCF', 'x', 'Market cap divided by expected free cash flow.'],
      ['ev_sales', 'EV/Sales', 'x', 'Enterprise value divided by revenue.'],
      ['ev_ebitda', 'EV/EBITDA', 'x', 'Enterprise value divided by EBITDA.'],
      ['ev_ebit', 'EV/EBIT', 'x', 'Enterprise value divided by operating income.'],
      ['ev_fcf', 'EV/FCF', 'x', 'Enterprise value divided by free cash flow.'],
      ['earn_yield', 'Earnings yield', 'y', 'Earnings divided by market cap (the inverse of P/E).'],
      ['fcf_yield', 'FCF yield', 'y', 'Free cash flow divided by market cap.'],
      ['fair_up', 'Upside to fair value (DCF)', 'p', 'Gap between the price and our discounted cash flow fair value.']]],
    ['Income', [
      ['rev', 'Revenue', 'm', 'Revenue of the last twelve months.'],
      ['gp', 'Gross profit', 'm', 'Revenue minus cost of revenue.'],
      ['opi', 'Operating income', 'm', 'Profit from operations before interest and taxes.'],
      ['ni', 'Net income', 'm', 'Profit of the last twelve months.'],
      ['ebitda', 'EBITDA', 'm', 'Earnings before interest, taxes, depreciation and amortisation.'],
      ['eps', 'EPS', 'pr', 'Diluted earnings per share of the last twelve months.'],
      ['revps', 'Revenue per share', 'pr', 'Revenue divided by diluted shares.'],
      ['rnd', 'Research & development', 'm', 'R&D spending in the last fiscal year.'],
      ['rnd_pct', 'R&D / revenue', 'p', 'Share of revenue spent on research and development.'],
      ['sbc', 'Stock-based compensation', 'm', 'Pay given to employees in shares in the last fiscal year.'],
      ['sbc_pct', 'SBC / revenue', 'p', 'Stock-based compensation as a share of revenue.'],
      ['intexp', 'Interest expense', 'm', 'Interest paid on debt in the last fiscal year.']]],
    ['Growth', [
      ['revg_q', 'Revenue growth (quarter, YoY)', 'p', 'Latest quarter revenue against the same quarter a year earlier.'],
      ['revg_qoq', 'Revenue growth (QoQ)', 'p', 'Latest quarter revenue against the previous quarter.'],
      ['revg3', 'Revenue growth 3Y', 'p', 'Average yearly revenue growth over three years.'],
      ['revg5', 'Revenue growth 5Y', 'p', 'Average yearly revenue growth over five years.'],
      ['revg10', 'Revenue growth 10Y', 'p', 'Average yearly revenue growth over ten years.'],
      ['revg_fy1', 'Revenue growth next year (est.)', 'p', 'Analyst estimate: next fiscal year revenue against this fiscal year.'],
      ['nig1', 'Net income growth', 'p', 'Net income growth in the last fiscal year.'],
      ['nig_q', 'Net income growth (quarter, YoY)', 'p', 'Latest quarter net income against the same quarter a year earlier.'],
      ['nig3', 'Net income growth 3Y', 'p', 'Average yearly net income growth over three years.'],
      ['nig5', 'Net income growth 5Y', 'p', 'Average yearly net income growth over five years.'],
      ['epsg1', 'EPS growth', 'p', 'Earnings per share growth in the last fiscal year.'],
      ['epsg3', 'EPS growth 3Y', 'p', 'Average yearly EPS growth over three years.'],
      ['epsg5', 'EPS growth 5Y', 'p', 'Average yearly EPS growth over five years.'],
      ['epsg10', 'EPS growth 10Y', 'p', 'Average yearly EPS growth over ten years.'],
      ['epsg_q0', 'EPS growth this quarter (est.)', 'p', 'Analyst estimate for the current quarter against a year earlier.'],
      ['epsg_fy0', 'EPS growth this year (est.)', 'p', 'Analyst estimate for the current fiscal year.'],
      ['epsg_fy1', 'EPS growth next year (est.)', 'p', 'Analyst estimate for the next fiscal year.'],
      ['fcfg1', 'FCF growth', 'p', 'Free cash flow growth in the last fiscal year.'],
      ['fcfg3', 'FCF growth 3Y', 'p', 'Average yearly free cash flow growth over three years.'],
      ['fcfg5', 'FCF growth 5Y', 'p', 'Average yearly free cash flow growth over five years.'],
      ['rule40', 'Rule of 40', 'p', 'Revenue growth plus free cash flow margin.']]],
    ['Margins', [
      ['gm', 'Gross margin', 'p', 'Gross profit divided by revenue.'],
      ['om', 'Operating margin', 'p', 'Operating income divided by revenue.'],
      ['ptm', 'Pretax margin', 'p', 'Pretax income divided by revenue.'],
      ['nm', 'Profit margin', 'p', 'Net income divided by revenue.'],
      ['fm', 'FCF margin', 'p', 'Free cash flow divided by revenue.'],
      ['ebitda_m', 'EBITDA margin', 'p', 'EBITDA divided by revenue.'],
      ['gm5', 'Gross margin (5Y avg.)', 'p', 'Five-year average gross margin.'],
      ['om5', 'Operating margin (5Y avg.)', 'p', 'Five-year average operating margin.'],
      ['nm5', 'Profit margin (5Y avg.)', 'p', 'Five-year average net margin.'],
      ['fm5', 'FCF margin (5Y avg.)', 'p', 'Five-year average free cash flow margin.'],
      ['nm_trend', 'Profit margin trend', 'p', 'Last year’s net margin minus the average of the three years before (in points).'],
      ['om_trend', 'Operating margin trend', 'p', 'Last year’s operating margin minus the average of the three years before (in points).']]],
    ['Returns & efficiency', [
      ['roic', 'Return on invested capital', 'p', 'After-tax operating profit divided by invested capital.'],
      ['roic5', 'ROIC (5Y avg.)', 'p', 'Five-year average return on invested capital.'],
      ['roe', 'Return on equity', 'p', 'Net income divided by shareholders’ equity.'],
      ['roa', 'Return on assets', 'p', 'Net income divided by total assets.'],
      ['roce', 'Return on capital employed', 'p', 'Operating income divided by assets minus current liabilities.'],
      ['asset_turn', 'Asset turnover', 'x', 'Revenue divided by total assets.'],
      ['fcf_conv', 'Cash conversion', 'x', 'Free cash flow divided by net income.']]],
    ['Cash flow', [
      ['ocf', 'Operating cash flow', 'm', 'Cash generated by operations in the last twelve months.'],
      ['capex', 'Capital expenditures', 'm', 'Spending on property and equipment.'],
      ['fcf', 'Free cash flow', 'm', 'Operating cash flow minus capital expenditures.'],
      ['fcf_sbc', 'Free cash flow minus SBC', 'm', 'Free cash flow after subtracting stock-based compensation.'],
      ['fcfps', 'FCF per share', 'pr', 'Free cash flow divided by diluted shares.'],
      ['da', 'Depreciation & amortisation', 'm', 'Non-cash depreciation and amortisation in the last fiscal year.']]],
    ['Balance sheet', [
      ['cash', 'Cash', 'm', 'Cash and short-term investments.'],
      ['debt', 'Total debt', 'm', 'Short-term plus long-term debt.'],
      ['netcash', 'Net cash', 'm', 'Cash minus debt (negative means net debt).'],
      ['netcash_mc', 'Net cash / market cap', 'p', 'Net cash as a share of market cap.'],
      ['cash_mc', 'Cash / market cap', 'p', 'Cash as a share of market cap.'],
      ['assets', 'Total assets', 'm', 'Everything the company owns.'],
      ['liab', 'Total liabilities', 'm', 'Everything the company owes.'],
      ['equity', 'Shareholders’ equity', 'm', 'Assets minus liabilities.'],
      ['wc', 'Working capital', 'm', 'Current assets minus current liabilities.'],
      ['tbv', 'Tangible book value', 'm', 'Equity minus goodwill and intangibles.'],
      ['bvps', 'Book value per share', 'pr', 'Equity divided by shares outstanding.'],
      ['goodwill', 'Goodwill', 'm', 'Premium paid for past acquisitions.'],
      ['ppe', 'Property & equipment', 'm', 'Net property, plant and equipment.'],
      ['inventory', 'Inventory', 'm', 'Goods held for sale.'],
      ['recv', 'Receivables', 'm', 'Money owed by customers.']]],
    ['Financial health', [
      ['de', 'Debt / equity', 'x', 'Total debt divided by shareholders’ equity.'],
      ['debt_assets', 'Debt / assets', 'p', 'Total debt as a share of total assets.'],
      ['debt_ebitda', 'Debt / EBITDA', 'x', 'Total debt divided by EBITDA.'],
      ['nd_ebitda', 'Net debt / EBITDA', 'x', 'Debt minus cash, divided by EBITDA (negative means net cash).'],
      ['cur_ratio', 'Current ratio', 'x', 'Current assets divided by current liabilities.'],
      ['quick', 'Quick ratio', 'x', 'Current assets minus inventory, divided by current liabilities.'],
      ['int_cov', 'Interest coverage', 'x', 'Operating income divided by interest expense.'],
      ['altman', 'Altman Z-score', 'n', 'Bankruptcy risk gauge: above 3 is safe, below 1.8 is distress (not used for banks).'],
      ['fscore', 'Piotroski F-score', 'i', '0 to 9 points for improving profitability, leverage and efficiency.'],
      ['profit_yrs', 'Profitable years (of 10)', 'i', 'Years with positive net income in the last ten.'],
      ['fcf_yrs', 'Positive FCF years (of 10)', 'i', 'Years with positive free cash flow in the last ten.']]],
    ['Dividends & buybacks', [
      ['dps', 'Dividend per share', 'pr', 'Dividends paid per share over the last twelve months.'],
      ['payout', 'Payout ratio', 'p', 'Dividends as a share of net income.'],
      ['divg1', 'Dividend growth', 'p', 'Dividend growth in the last fiscal year.'],
      ['divg3', 'Dividend growth 3Y', 'p', 'Average yearly growth of the dividend per share over three years.'],
      ['divg5', 'Dividend growth 5Y', 'p', 'Average yearly growth of the dividend per share over five years.'],
      ['div_yrs', 'Years paying dividends (of 10)', 'i', 'Years with a dividend in the last ten.'],
      ['div_paid', 'Dividends paid', 'm', 'Total cash paid as dividends in the last fiscal year.'],
      ['buybacks', 'Share buybacks', 'm', 'Cash spent buying back shares in the last fiscal year.'],
      ['bby', 'Buyback yield', 'y', 'Buybacks divided by market cap.'],
      ['shy', 'Shareholder yield', 'y', 'Dividend yield plus buyback yield.'],
      ['sh_chg1', 'Share count change 1Y', 'p', 'Change in diluted shares in the last fiscal year (negative = buybacks).'],
      ['sh_chg3', 'Share count change 3Y', 'p', 'Average yearly change in diluted shares over three years.'],
      ['sh_chg5', 'Share count change 5Y', 'p', 'Average yearly change in diluted shares over five years.']]],
    ['Analysts', [
      ['tgt_up', 'Price target upside', 'p', 'Gap between the price and the average analyst target.'],
      ['tgt_lo_up', 'Lowest target vs price', 'p', 'Gap between the price and the lowest analyst target.'],
      ['tgt_hi_up', 'Highest target vs price', 'p', 'Gap between the price and the highest analyst target.'],
      ['n_an', 'Number of analysts', 'i', 'Analysts covering the stock.'],
      ['rm', 'Rating score', 'n', '1 = strong buy, 3 = hold, 5 = sell.'],
      ['buy_pct', 'Buy ratings', 'p', 'Share of analysts rating the stock buy or strong buy.'],
      ['rev30', 'EPS revisions (30 days)', 'i', 'Upward minus downward revisions of the EPS estimate in the last 30 days.']]],
    ['Ownership & short interest', [
      ['shares', 'Shares outstanding', 'sh', 'Total shares in existence.'],
      ['float', 'Float', 'sh', 'Shares available for public trading.'],
      ['float_pct', 'Float / shares', 'p', 'Share of the company that trades freely.'],
      ['insiders', 'Insider ownership', 'p', 'Share of the company held by insiders.'],
      ['inst', 'Institutional ownership', 'p', 'Share of the company held by institutions.'],
      ['short_float', 'Short % of float', 'p', 'Shares sold short as a share of the float.'],
      ['short_ratio', 'Short ratio (days to cover)', 'n', 'Shares sold short divided by average daily volume.']]],
    ['Scores', [
      ['s_value', 'Value score', 's', 'Our 0 to 5 score for valuation.'],
      ['s_future', 'Future score', 's', 'Our 0 to 5 score for expected growth.'],
      ['s_past', 'Past score', 's', 'Our 0 to 5 score for the track record.'],
      ['s_health', 'Health score', 's', 'Our 0 to 5 score for the balance sheet.'],
      ['s_capital', 'Shareholder returns score', 's', 'Our 0 to 5 score for dividends and buybacks.']]]
  ];
  var F = {}; CATS.forEach(function (c) { c[1].forEach(function (f) { F[f[0]] = { k: f[0], label: f[1], type: f[2], desc: f[3], cat: c[0] } }) });
  var LOWER = { pe: 1, fwd_pe: 1, peg: 1, ps: 1, fwd_ps: 1, pb: 1, ptbv: 1, pfcf: 1, fwd_pfcf: 1, ev_sales: 1, ev_ebitda: 1, ev_ebit: 1, ev_fcf: 1, de: 1, debt_ebitda: 1, nd_ebitda: 1, debt_assets: 1, sbc_pct: 1, payout: 1, rm: 1, short_float: 1, volat: 1, beta: 1 };
  var REC = { strong_buy: 'Strong buy', buy: 'Buy', hold: 'Hold', underperform: 'Underperform', sell: 'Sell' };
  var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

  /* ------------------------------------------------------------------ ready-made conditions per filter */
  function R(op, a, b, label) { return { op: op, a: a, b: b, label: label } }
  function ready(f) {
    var k = f.k, t = f.type, o = [];
    function over(arr) { arr.forEach(function (v) { o.push(R('gt', v)) }) } function under(arr) { arr.forEach(function (v) { o.push(R('lt', v)) }) }
    if (k === 'mcap') return [R('ge', 200000, null, 'Mega cap: $200B and more'), R('bt', 10000, 200000, 'Large cap: $10B to $200B'), R('bt', 2000, 10000, 'Mid cap: $2B to $10B'), R('bt', 300, 2000, 'Small cap: $300M to $2B'), R('bt', 50, 300, 'Micro cap: $50M to $300M'), R('lt', 50, null, 'Nano cap: under $50M'), R('gt', 1000), R('gt', 10000), R('gt', 50000), R('lt', 1000), R('lt', 300)];
    if (k === 'rsi') return [R('lt', 30, null, 'Oversold: under 30'), R('gt', 70, null, 'Overbought: over 70'), R('lt', 40), R('gt', 50), R('gt', 60)];
    if (k === 'beta') return [R('lt', 0.5), R('lt', 1), R('bt', 0.8, 1.2, 'Close to the market: 0.8 to 1.2'), R('gt', 1), R('gt', 1.5), R('gt', 2)];
    if (k === 'altman') return [R('gt', 3, null, 'Safe zone: over 3'), R('bt', 1.8, 3, 'Grey zone: 1.8 to 3'), R('lt', 1.8, null, 'Distress zone: under 1.8')];
    if (k === 'rm') return [R('lt', 1.5, null, 'Strong buy: under 1.5'), R('lt', 2.5, null, 'Buy or better: under 2.5'), R('gt', 3.5, null, 'Sell side: over 3.5')];
    if (k === 'range_pos') return [R('gt', 90, null, 'Near the high: top 10%'), R('gt', 70), R('lt', 30), R('lt', 10, null, 'Near the low: bottom 10%')];
    if (k === 'off_hi' || k === 'off_ath') return [R('gt', -5, null, 'Within 5% of the high'), R('gt', -10, null, 'Within 10% of the high'), R('lt', -20, null, '20% or more below'), R('lt', -30, null, '30% or more below'), R('lt', -50, null, '50% or more below'), R('lt', -70, null, '70% or more below')];
    if (k === 'off_lo') return [R('lt', 5, null, 'Within 5% of the low'), R('lt', 10, null, 'Within 10% of the low'), R('gt', 25), R('gt', 50), R('gt', 100)];
    if (k === 'ma50' || k === 'ma200' || k === 'ma_cross') return [R('gt', 0, null, 'Above'), R('lt', 0, null, 'Below'), R('gt', 10), R('gt', 20), R('lt', -10), R('lt', -20)];
    if (k === 'relvol') return [R('gt', 1), R('gt', 1.5), R('gt', 2), R('gt', 3), R('lt', 0.75)];
    if (k === 'earn_in') return [R('bt', 0, 7, 'In the next 7 days'), R('bt', 0, 14, 'In the next 14 days'), R('bt', 0, 30, 'In the next 30 days'), R('bt', 0, 90, 'In the next 90 days'), R('bt', -3, -1, 'Reported in the last 3 days')];
    if (k === 'exdiv_in') return [R('bt', 0, 7, 'In the next 7 days'), R('bt', 0, 30, 'In the next 30 days'), R('bt', -30, -1, 'In the last 30 days'), R('bt', -90, -1, 'In the last 90 days')];
    if (k === 'ipo') { var y = new Date().getFullYear(); return [R('ge', y, null, 'This year'), R('ge', y - 1, null, 'Last 2 years'), R('ge', y - 4, null, 'Last 5 years'), R('lt', y - 9, null, 'More than 10 years ago'), R('lt', 2000, null, 'Before 2000')] }
    if (k === 'years') return [R('ge', 10), R('ge', 5), R('lt', 5)];
    if (k === 'fscore') return [R('ge', 8, null, 'Strong: 8 or 9'), R('ge', 7), R('ge', 5), R('le', 3, null, 'Weak: 3 or less')];
    if (k === 'profit_yrs' || k === 'fcf_yrs' || k === 'div_yrs') return [R('ge', 10, null, 'All 10 years'), R('ge', 8), R('ge', 5), R('ge', 1), R('le', 0, null, 'None')];
    if (k === 'n_an') return [R('ge', 1), R('ge', 5), R('ge', 10), R('ge', 20), R('le', 3)];
    if (k === 'rev30') return [R('gt', 0, null, 'More upgrades than downgrades'), R('ge', 5), R('lt', 0, null, 'More downgrades than upgrades')];
    if (k === 'short_float') return [R('gt', 5), R('gt', 10), R('gt', 20), R('gt', 30), R('lt', 5), R('lt', 2)];
    if (k === 'short_ratio') return [R('gt', 5), R('gt', 10), R('lt', 2)];
    if (k === 'payout') return [R('lt', 30), R('lt', 60), R('lt', 80), R('gt', 0), R('gt', 100)];
    if (k === 'divy') return [R('gt', 0, null, 'Pays a dividend'), R('gt', 1), R('gt', 2), R('gt', 3), R('gt', 4), R('gt', 5), R('gt', 7), R('le', 0, null, 'No dividend')];
    if (k === 'price' || k === 'hi52' || k === 'lo52') return [R('lt', 1), R('lt', 5), R('lt', 10), R('lt', 20), R('gt', 5), R('gt', 10), R('gt', 50), R('gt', 100), R('gt', 500)];
    if (k === 'vol') return [R('gt', 50000), R('gt', 200000), R('gt', 500000), R('gt', 1000000), R('gt', 5000000), R('lt', 50000)];
    if (k === 'dvol') return [R('gt', 1), R('gt', 5), R('gt', 20), R('gt', 100), R('lt', 1)];
    if (k === 'shares' || k === 'float') return [R('lt', 10), R('lt', 50), R('gt', 100), R('gt', 500), R('gt', 1000)];
    if (k === 'insiders' || k === 'inst' || k === 'float_pct' || k === 'buy_pct') return [R('gt', 10), R('gt', 30), R('gt', 50), R('gt', 80), R('lt', 10), R('lt', 50)];
    if (k === 'sh_chg1' || k === 'sh_chg3' || k === 'sh_chg5') return [R('lt', 0, null, 'Shrinking (buybacks)'), R('lt', -2), R('lt', -5), R('gt', 0, null, 'Growing (dilution)'), R('gt', 5), R('gt', 10)];
    if (k === 'nm_trend' || k === 'om_trend') return [R('gt', 0, null, 'Improving'), R('gt', 3), R('gt', 5), R('lt', 0, null, 'Declining'), R('lt', -3)];
    if (k === 'netcash') return [R('gt', 0, null, 'Net cash (more cash than debt)'), R('lt', 0, null, 'Net debt'), R('gt', 1000), R('gt', 10000)];
    if (k === 'nd_ebitda') return [R('lt', 0, null, 'Net cash'), R('lt', 1), R('lt', 2), R('lt', 3), R('gt', 4)];
    if (k === 'de') return [R('le', 0, null, 'No debt'), R('lt', 0.3), R('lt', 0.5), R('lt', 1), R('gt', 1), R('gt', 2)];
    if (k === 'cur_ratio' || k === 'quick') return [R('gt', 1), R('gt', 1.5), R('gt', 2), R('gt', 3), R('lt', 1)];
    if (k === 'int_cov') return [R('gt', 3), R('gt', 5), R('gt', 10), R('gt', 20), R('lt', 2)];
    if (k === 'debt_ebitda') return [R('lt', 1), R('lt', 2), R('lt', 3), R('gt', 4), R('gt', 6)];
    if (k === 'asset_turn' || k === 'fcf_conv') return [R('gt', 0.5), R('gt', 0.8), R('gt', 1), R('gt', 1.5), R('lt', 0.5)];
    if (k === 'rule40') return [R('gt', 40, null, 'Passes: over 40%'), R('gt', 50), R('gt', 60), R('lt', 40)];
    if (k === 'peg') return [R('lt', 1), R('lt', 1.5), R('lt', 2), R('gt', 2), R('gt', 3)];
    if (k === 'fair_up' || k === 'tgt_up' || k === 'tgt_lo_up' || k === 'tgt_hi_up') return [R('gt', 0, null, 'Upside (price below it)'), R('gt', 10), R('gt', 20), R('gt', 30), R('gt', 50), R('lt', 0, null, 'Downside (price above it)'), R('lt', -20)];
    if (t === 's') return [R('ge', 5, null, '5'), R('ge', 4, null, '4 or more'), R('ge', 3, null, '3 or more'), R('ge', 2, null, '2 or more'), R('le', 1, null, '1 or less')];
    if (t === 'm') { if (k === 'ni' || k === 'fcf' || k === 'ocf' || k === 'opi' || k === 'ebitda' || k === 'fcf_sbc' || k === 'wc' || k === 'equity' || k === 'tbv') o.push(R('gt', 0, null, 'Positive'), R('lt', 0, null, 'Negative')); over([10, 100, 1000, 10000]); under([100]); return o }
    if (t === 'y') { over([0, 1, 2, 3, 4, 5, 7, 10]); return o }
    if (t === 'x') { if (LOWER[k]) { under([5, 10, 15, 20, 30, 50]); over([50]) } else { over([0.5, 1, 2, 5]); under([1]) } return o }
    if (t === 'p') { if (/^(r\d|rytd|cagr|chg1d)/.test(k)) { over([0, 5, 10, 20, 50, 100]); under([0, -5, -10, -20, -50]) } else if (LOWER[k]) { under([2, 5, 10, 20, 50]); over([20, 50]) } else { over([0, 5, 10, 15, 20, 30, 50]); under([0, -10]) } return o }
    if (t === 'pr') { over([0, 1, 5, 10]); under([0]); return o }
    return o
  }

  /* ------------------------------------------------------------------ units: stored value <-> the number a person types */
  function unit(f) { return f.type === 'p' || f.type === 'y' ? 100 : 1 }      /* typed 20 (%) = stored 0.20 */
  function big(v) { if (v == null || !isFinite(v)) return '—'; var a = Math.abs(v), s = v < 0 ? '-' : ''; return ltr(s + '$' + (a >= 1e6 ? (a / 1e6).toFixed(2) + 'T' : a >= 1e3 ? (a / 1e3).toFixed(a >= 1e5 ? 0 : a >= 1e4 ? 1 : 2) + 'B' : a >= 1 ? (a >= 100 ? a.toFixed(0) : a.toFixed(1)) + 'M' : (a * 1e3).toFixed(0) + 'K')) }
  function cnt(v) { if (v == null || !isFinite(v)) return '—'; var a = Math.abs(v); return ltr(a >= 1e9 ? (v / 1e9).toFixed(2) + 'B' : a >= 1e6 ? (v / 1e6).toFixed(a >= 1e8 ? 0 : 1) + 'M' : a >= 1e3 ? (v / 1e3).toFixed(a >= 1e5 ? 0 : 1) + 'K' : String(Math.round(v))) }
  function nf(v, d) { return v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }) }
  function dateIn(days) { var d = new Date(TODAY.getTime() + days * 864e5); return ltr(d.toLocaleDateString(LANG === 'en' ? 'en-US' : LANG === 'fa' ? 'en-GB' : LANG === 'ar' ? 'en-GB' : LANG, { month: RTL ? 'numeric' : 'short', day: 'numeric', year: 'numeric' })) }
  function fmt(f, v, color) {
    if (v == null || (typeof v === 'number' && !isFinite(v))) return '—';
    switch (f.type) {
      case 'm': return big(v);
      case 'p': case 'y': { var x = v * 100; if (Math.abs(x) >= 10000) return ltr((x < 0 ? '<-' : '>') + '9,999%'); var s = nf(x, Math.abs(x) >= 100 ? 0 : Math.abs(x) >= 10 ? 1 : 2) + '%'; return color ? '<span class="' + (x < 0 ? 'neg' : x > 0 ? 'pos' : '') + '">' + ltr(s) + '</span>' : ltr(s) }
      case 'x': case 'n': return ltr(nf(v, Math.abs(v) >= 100 ? 0 : Math.abs(v) >= 10 ? 1 : 2));
      case 'pr': return ltr((v < 0 ? '-$' : '$') + nf(Math.abs(v), Math.abs(v) >= 1000 ? 0 : 2));
      case 's': return '<span class="sc" style="background:' + (v >= 4 ? '#4FA37A' : v >= 3 ? '#8FB07A' : v >= 2 ? '#C9A961' : '#C8534F') + '">' + (Math.round(v * 10) / 10) + '</span>';
      case 'i': return ltr(String(v));
      case 'v': return cnt(v);
      case 'sh': return cnt(v * 1e6);
      case 'd': return dateIn(v);
      case 'c': return f.k === 'rec' ? '<span class="rec rec-' + esc(v) + '">' + esc(L(REC[v] || v)) + '</span>' : f.k === 'fy_month' ? esc(L(MONTHS[v - 1] || '')) : esc(v);
    }
    return esc(v)
  }
  var COLORED = /^(chg1d|r\d|rytd|cagr|revg|nig|epsg|fcfg|divg|fair_up|tgt_|off_|ma|nm_trend|om_trend|sh_chg|rule40)/;
  /* a condition written out: "Over 20%", "$2B to $10B" */
  function trim0(s) { return s.replace(/\.0+(?=[TBMK%]|$|<)/, '').replace(/(\.\d*[1-9])0+(?=[TBMK%]|$|<)/, '$1') }
  function pv(f, v) {
    if (f.type === 'm') return trim0(big(v)); if (f.type === 'p' || f.type === 'y') return ltr(String(+(+v).toFixed(2)) + '%');
    if (f.type === 'pr') return ltr((v < 0 ? '-$' : '$') + Math.abs(v)); if (f.type === 'v') return trim0(cnt(v)); if (f.type === 'sh') return trim0(cnt(v * 1e6)); if (f.type === 'd') return dateIn(v); return ltr(String(v))
  }
  function condText(f, c) {
    if (!c) return L('Any');
    if (c.op === 'in') return c.set.length === 1 ? esc(catLabel(f, c.set[0])) : L('%1 selected', c.set.length);
    if (c.label) return esc(L(c.label));
    var a = pv(f, c.a);
    return c.op === 'gt' ? L('Over %1', a) : c.op === 'ge' ? L('%1 or more', a) : c.op === 'lt' ? L('Under %1', a) : c.op === 'le' ? L('%1 or less', a) : c.op === 'eq' ? L('Exactly %1', a) : L('%1 to %2', a, pv(f, c.b))
  }
  function catLabel(f, v) { return f.k === 'rec' ? L(REC[v] || v) : f.k === 'fy_month' ? L(MONTHS[v - 1] || v) : v }

  /* ------------------------------------------------------------------ state */
  var C = {}, ROWS = [], DICT = {}, HAVE_MORE = false, AS_OF = '', TODAY = new Date(new Date().toISOString().slice(0, 10) + 'T12:00:00Z'), view = [];
  var active = [], cond = {}, sortKey = 'mcap', asc = false, shown = PAGE, tab = 'general', find = '', customCols = null, preset = '';
  var VIEWS = {
    general: ['General', ['mcap', 'price', 'chg1d', 'industry', 'vol', 'pe', 's_total']],
    filters: ['Filters', null],
    performance: ['Performance', ['mcap', 'price', 'chg1d', 'r1w', 'r1m', 'r3m', 'r6m', 'rytd', 'r1y', 'r3y', 'r5y']],
    analysts: ['Analysts', ['mcap', 'price', 'rec', 'n_an', 'tgt_up', 'tgt_lo_up', 'tgt_hi_up', 'epsg_fy1', 'revg_fy1']],
    dividends: ['Dividends', ['mcap', 'divy', 'dps', 'payout', 'divg1', 'divg5', 'div_yrs', 'shy', 'exdiv_in']],
    financials: ['Financials', ['mcap', 'rev', 'opi', 'ni', 'fcf', 'eps', 'cash', 'debt', 'netcash']],
    valuation: ['Valuation', ['mcap', 'ev', 'pe', 'fwd_pe', 'ps', 'pb', 'pfcf', 'peg', 'ev_ebitda', 'fcf_yield', 'fair_up']],
    growth: ['Growth', ['mcap', 'revg1', 'revg_q', 'revg3', 'revg5', 'epsg1', 'epsg5', 'fcfg3', 'revg_fy1', 'epsg_fy1']],
    quality: ['Quality', ['mcap', 'gm', 'om', 'nm', 'fm', 'roic', 'roe', 'fcf_conv', 'profit_yrs', 'fscore']],
    health: ['Health', ['mcap', 'de', 'nd_ebitda', 'cur_ratio', 'int_cov', 'altman', 'netcash', 's_health']],
    scores: ['Scores', ['mcap', 's_total', 's_value', 's_future', 's_past', 's_health', 's_capital']],
    custom: ['My columns', null]
  };
  var PRESETS = [
    ['quality', 'Quality + growth', 'ROIC above 20%, 5-year revenue growth above 15%, improving margins and bigger than $1B.', { roic: R('gt', 20), revg5: R('gt', 15), nm_trend: R('gt', 0, null, 'Improving'), mcap: R('gt', 1000) }],
    ['compounder', 'Debt-free compounders', 'More cash than debt, ROIC above 15%, 5-year revenue growth above 10% and profitable in all of the last 10 years.', { nd_ebitda: R('lt', 0, null, 'Net cash'), roic: R('gt', 15), revg5: R('gt', 10), profit_yrs: R('ge', 10, null, 'All 10 years'), mcap: R('gt', 300) }],
    ['value', 'Cheap and profitable', 'P/E under 20, value score 4 or more and profitable in at least 5 of the last 10 years.', { pe: R('lt', 20), s_value: R('ge', 4, null, '4 or more'), profit_yrs: R('ge', 5), mcap: R('gt', 300) }],
    ['growth', 'Fast growers', 'Revenue growth above 20% last year and a future score of 4 or more.', { revg1: R('gt', 20), s_future: R('ge', 4, null, '4 or more') }],
    ['rule40', 'Rule of 40 (software)', 'Technology companies where revenue growth plus free cash flow margin is above 40%.', { sector: { op: 'in', set: ['Technology'] }, rule40: R('gt', 40, null, 'Passes: over 40%'), mcap: R('gt', 1000) }],
    ['dividend', 'Reliable dividends', 'A dividend in all of the last 10 years, shareholder returns score 4 or more and health score 3 or more.', { div_yrs: R('ge', 10, null, 'All 10 years'), s_capital: R('ge', 4, null, '4 or more'), s_health: R('ge', 3, null, '3 or more') }],
    ['buyback', 'Buyback kings', 'Share count falling more than 3% a year and a free cash flow yield above 4%.', { sh_chg3: R('lt', -3), fcf_yield: R('gt', 4), mcap: R('gt', 1000) }],
    ['health', 'Fortress balance sheet', 'Health score 5 out of 5 and bigger than $300M.', { s_health: R('ge', 5, null, '5'), mcap: R('gt', 300) }],
    ['cheapfcf', 'Below intrinsic value', 'Price at least 30% below our DCF fair value, free cash flow yield above 5% and health score 3 or more.', { fair_up: R('gt', 30), fcf_yield: R('gt', 5), s_health: R('ge', 3, null, '3 or more'), mcap: R('gt', 1000) }],
    ['turnaround', 'Expanding margins', 'Net margin at least 3 points above the average of the three years before, with growing revenue.', { nm_trend: R('gt', 3), revg1: R('gt', 0), mcap: R('gt', 300) }],
    ['oversold', 'Oversold quality', 'RSI under 30, overall score 3.5 or more and bigger than $1B.', { rsi: R('lt', 30, null, 'Oversold: under 30'), s_total: R('ge', 3.5), mcap: R('gt', 1000) }],
    ['smallcap', 'Small-cap growth', 'Market cap $300M to $2B, revenue growth above 20% and profitable.', { mcap: R('bt', 300, 2000, 'Small cap: $300M to $2B'), revg1: R('gt', 20), ni: R('gt', 0, null, 'Positive') }],
    ['highs', 'Near 52-week high', 'Within 5% of the 52-week high and up more than 20% in a year.', { off_hi: R('gt', -5, null, 'Within 5% of the high'), r1y: R('gt', 20), mcap: R('gt', 1000) }],
    ['analyst', 'Analyst favourites', 'Rated strong buy by at least 10 analysts, with 20% or more upside to the average target.', { rec: { op: 'in', set: ['strong_buy'] }, n_an: R('ge', 10), tgt_up: R('gt', 20) }]
  ];
  var DEFAULT = ['mcap', 'sector', 'pe', 'divy', 'revg1', 'roic'];

  /* ------------------------------------------------------------------ data */
  function getJSON(u) { return fetch(u).then(function (r) { if (!r.ok) throw new Error(u + ' ' + r.status); return r.json() }) }
  function g(r, k) { var i = C[k]; return i == null ? null : r[i] == null ? null : r[i] }
  function merge(j) {
    var base = ROWS.length ? ROWS[0].length : 0, by = {}, n = 0;
    j.cols.forEach(function (c, i) { if (C[c] == null) { C[c] = base + n++; j.cols[i] = [c, C[c]] } else j.cols[i] = [c, -1] });
    for (var d in j.dict) DICT[d] = j.dict[d];
    if (!ROWS.length) { ROWS = j.rows.map(function (r) { return decode(j, r, []) }); return }
    ROWS.forEach(function (r) { by[r[C.t]] = r });
    j.rows.forEach(function (r) { var t = r[0], row = by[t]; if (row) decode(j, r, row) })
  }
  function decode(j, r, row) {
    for (var i = 0; i < j.cols.length; i++) { var c = j.cols[i]; if (c[1] < 0) continue; var v = r[i]; if (v == null) { row[c[1]] = null; continue } row[c[1]] = j.dict[c[0]] ? j.dict[c[0]][v] : v }
    return row
  }
  function live(q) {
    if (!q || !q.q || C.price == null) return 0; var n = 0;
    var mul = ['mcap', 'dvol', 'pe', 'fwd_pe', 'ps', 'fwd_ps', 'pb', 'ptbv', 'pfcf', 'fwd_pfcf', 'peg'], dv = ['divy', 'fcf_yield', 'earn_yield', 'bby', 'shy'], up = ['tgt_up', 'fair_up', 'tgt_lo_up', 'tgt_hi_up'], rel = ['off_hi', 'off_lo', 'off_ath', 'ma50', 'ma200', 'r1w', 'r1m', 'r3m', 'r6m', 'rytd', 'r1y', 'r3y', 'r5y', 'r10y'];
    ROWS.forEach(function (r) {
      var Q = q.q[r[C.t]], p0 = r[C.price]; if (!Q || !(Q[0] > 0) || !(p0 > 0) || r._l) return; var f = Q[0] / p0; if (!(f > 0.5 && f < 2)) return; r._l = 1; n++;
      r[C.price] = Q[0]; if (typeof Q[1] === 'number' && C.chg1d != null) r[C.chg1d] = Q[1] / 100;
      mul.forEach(function (k) { var i = C[k]; if (i != null && r[i] != null) r[i] *= f }); dv.forEach(function (k) { var i = C[k]; if (i != null && r[i] != null) r[i] /= f });
      up.forEach(function (k) { var i = C[k]; if (i != null && r[i] != null) r[i] = (1 + r[i]) / f - 1 }); rel.forEach(function (k) { var i = C[k]; if (i != null && r[i] != null) r[i] = (1 + r[i]) * f - 1 })
    }); return n
  }

  /* ------------------------------------------------------------------ filtering */
  function test(f, c, v) {
    if (c.op === 'in') return v != null && c.set.indexOf(v) >= 0;
    if (v == null) return false; var u = unit(f), a = c.a / u, b = c.b != null ? c.b / u : null, e = 1e-9;
    switch (c.op) { case 'gt': return v > a + e; case 'ge': return v >= a - e; case 'lt': return v < a - e; case 'le': return v <= a + e; case 'eq': return Math.abs(v - a) <= Math.max(Math.abs(a) * 0.005, e); case 'bt': return v >= Math.min(a, b) - e && v <= Math.max(a, b) + e }
    return true
  }
  function need() { var ks = active.concat(cols().map(function (c) { return c })).concat([sortKey]); return ks.some(function (k) { return F[k] && C[k] == null }) }
  function apply() {
    var fs = active.filter(function (k) { return cond[k] && C[k] != null }).map(function (k) { return [C[k], F[k], cond[k]] }), q = find.trim().toUpperCase();
    view = ROWS.filter(function (r) {
      if (q && !(String(r[C.t]).indexOf(q) === 0 || String(r[C.n]).toUpperCase().indexOf(q) >= 0)) return false;
      for (var i = 0; i < fs.length; i++) if (!test(fs[i][1], fs[i][2], r[fs[i][0]])) return false;
      return true
    });
    var si = C[sortKey];
    view.sort(function (x, y) { var a = si == null ? null : x[si], b = si == null ? null : y[si]; if (sortKey === 'n' || sortKey === 't' || (F[sortKey] && F[sortKey].type === 'c')) { a = a == null ? '' : String(a); b = b == null ? '' : String(b); if (!a && b) return 1; if (!b && a) return -1; return asc ? a.localeCompare(b) : b.localeCompare(a) } if (a == null && b == null) return 0; if (a == null) return 1; if (b == null) return -1; return asc ? a - b : b - a });
    shown = PAGE; draw(); save()
  }

  /* ------------------------------------------------------------------ rendering */
  var root;
  function cols() {
    if (tab === 'filters') { var c = ['mcap']; active.forEach(function (k) { if (c.indexOf(k) < 0) c.push(k) }); if (c.length < 4) ['price', 'chg1d', 'pe'].forEach(function (k) { if (c.indexOf(k) < 0) c.push(k) }); return c }
    if (tab === 'custom') return customCols && customCols.length ? customCols : VIEWS.general[1];
    return VIEWS[tab][1]
  }
  function shell() {
    root.innerHTML =
      '<div class="s2-card"><div class="s2-pre" id="s2-pre">' + PRESETS.map(function (p) { return '<button type="button" data-p="' + p[0] + '">' + esc(L(p[1])) + '</button>' }).join('') + '</div><div class="s2-pdesc" id="s2-pdesc"></div></div>' +
      '<div class="s2-card s2-fcard"><div class="s2-fhead"><h2>' + esc(L('Filters')) + ' <span id="s2-fn"></span></h2><button type="button" class="s2-link" id="s2-reset">' + esc(L('Reset filters')) + '</button></div>' +
      '<div class="s2-fbar"><button type="button" class="s2-btn" id="s2-add">+ ' + esc(L('Add filters')) + '</button><div class="s2-quick"><input id="s2-q" type="search" autocomplete="off" placeholder="' + esc(L('Search %1 filters…', Object.keys(F).length)) + '"><div class="s2-qlist" id="s2-qlist"></div></div>' +
      '<button type="button" class="s2-btn ghost" id="s2-save">' + esc(L('Save screen')) + '</button></div><div class="s2-saved" id="s2-saved"></div><div class="s2-flist" id="s2-flist"></div></div>' +
      '<div class="s2-bar"><div class="s2-count"><b id="s2-count">' + esc(L('Loading…')) + '</b><span id="s2-asof"></span></div><div class="s2-tools"><input id="s2-find" type="search" autocomplete="off" placeholder="' + esc(L('Find a ticker or name…')) + '"><button type="button" class="s2-btn ghost" id="s2-cols">' + esc(L('Edit columns')) + '</button><button type="button" class="s2-btn ghost" id="s2-csv">' + esc(L('Download CSV')) + '</button></div></div>' +
      '<div class="s2-tabs" id="s2-tabs"></div><div class="s2-tw"><table><thead><tr id="s2-head"></tr></thead><tbody id="s2-body"></tbody></table></div><div class="s2-more" id="s2-more"></div>' +
      '<div class="s2-modal" id="s2-modal" hidden></div><div class="s2-pop" id="s2-pop" hidden></div>'
  }
  function tabs() { $('#s2-tabs').innerHTML = Object.keys(VIEWS).filter(function (k) { return k !== 'custom' || (customCols && customCols.length) }).map(function (k) { var n = k === 'filters' ? ' <i>' + active.filter(function (x) { return cond[x] }).length + '</i>' : ''; return '<button type="button" data-t="' + k + '"' + (k === tab ? ' class="on"' : '') + '>' + esc(L(VIEWS[k][0])) + n + '</button>' }).join('') }
  function head() { $('#s2-head').innerHTML = '<th data-k="t" class="nm">' + esc(L('Company')) + '</th>' + cols().map(function (k) { var f = F[k]; return '<th data-k="' + k + '" title="' + esc(L(f.desc)) + '"' + (f.type === 'c' ? ' class="tx"' : '') + '>' + esc(L(f.label)) + '</th>' }).join(''); mark() }
  function mark() { $$('#s2-head th').forEach(function (th) { th.classList.toggle('s', th.dataset.k === sortKey); th.classList.toggle('asc', th.dataset.k === sortKey && asc) }) }
  function draw() {
    var CL = cols(), h = '';
    view.slice(0, ACCESS ? shown : FREE + 5).forEach(function (r, ri) {
      var t = r[C.t];
      h += '<tr' + (!ACCESS && ri >= FREE ? ' class="s2-lockrow"' : '') + '><td class="nm"><a href="' + STOCK + esc(t) + '" title="' + esc(r[C.n]) + '"><small>' + esc(t) + '</small><span>' + esc(r[C.n]) + '</span></a></td>' + CL.map(function (k) { var f = F[k], v = g(r, k); return '<td' + (f.type === 'c' ? ' class="tx"' : '') + '>' + (C[k] == null ? '…' : fmt(f, v, COLORED.test(k))) + '</td>' }).join('') + '</tr>'
    });
    $('#s2-body').innerHTML = h || '<tr><td class="s2-none" colspan="' + (CL.length + 1) + '">' + esc(L('No stock matches all of these filters. Loosen or remove one.')) + '</td></tr>';
    $('#s2-count').textContent = L(view.length === 1 ? '%1 stock' : '%1 stocks', view.length.toLocaleString('en-US'));
    if (!ACCESS) $('#s2-more').innerHTML = view.length > FREE ? '<div class="s2-wall"><b>' + esc(L('%1 more stocks match these filters', (view.length - FREE).toLocaleString('en-US'))) + '</b><p>' + esc(L('WALL_TEXT')) + '</p><a class="s2-btn" href="' + esc(CFG.subUrl || '#') + '">' + esc(L('WALL_MONTHLY')) + '</a> <a class="s2-btn alt" href="' + esc(CFG.subYearUrl || CFG.subUrl || '#') + '">' + esc(L('WALL_YEARLY')) + '</a>' + (CFG.logged ? '' : ' <a class="s2-btn ghost" href="' + esc(CFG.loginUrl || '#') + '">' + esc(L('WALL_LOGIN')) + '</a>') + '</div>' : '';
    else $('#s2-more').innerHTML = view.length > shown ? '<button type="button" class="s2-btn ghost" id="s2-mb">' + esc(L('Show %1 more', Math.min(PAGE, view.length - shown))) + '</button> <button type="button" class="s2-btn ghost" id="s2-ma">' + esc(L('Show all %1', view.length.toLocaleString('en-US'))) + '</button>' : '';
    mark(); fn(); tabs()
  }
  function fn() { var n = active.filter(function (k) { return cond[k] }).length; $('#s2-fn').textContent = n ? '(' + n + ')' : '' }
  function flist() {
    $('#s2-flist').innerHTML = active.map(function (k) {
      var f = F[k], c = cond[k];
      return '<div class="s2-f' + (c ? ' on' : '') + '" data-k="' + k + '"><span class="s2-fl" title="' + esc(L(f.desc)) + '">' + esc(L(f.label)) + '<i class="s2-i" tabindex="0" data-tip="' + esc(L(f.desc)) + '">i</i></span><button type="button" class="s2-x" aria-label="' + esc(L('Remove')) + '" data-x="' + k + '">×</button><button type="button" class="s2-sel" data-o="' + k + '"><span>' + condText(f, c) + '</span><b>▾</b></button></div>'
    }).join('') || '<p class="s2-empty">' + esc(L('No filters yet. Press “Add filters” to choose from %1 filters.', Object.keys(F).length)) + '</p>';
    fn()
  }
  function refresh() { flist(); head(); apply() }

  /* ------------------------------------------------------------------ one filter's control (popover) */
  var popKey = null;
  function closePop() { $('#s2-pop').hidden = true; popKey = null }
  function openPop(k, anchor) {
    var f = F[k], c = cond[k], pop = $('#s2-pop'), h = ''; popKey = k;
    if (f.type === 'c') {
      var vals = f.k === 'rec' ? Object.keys(REC) : f.k === 'fy_month' ? [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] : (DICT[k] || []).slice().sort(), cntBy = {}, i = C[k];
      if (i != null) ROWS.forEach(function (r) { var v = r[i]; if (v != null) cntBy[v] = (cntBy[v] || 0) + 1 });
      var set = c ? c.set : [];
      h = (vals.length > 10 ? '<input class="s2-ps" type="search" placeholder="' + esc(L('Search…')) + '">' : '') + '<div class="s2-pl"><label class="any"><input type="checkbox" data-any' + (set.length ? '' : ' checked') + '> ' + esc(L('Any')) + '</label>' + vals.filter(function (v) { return cntBy[v] }).map(function (v) { return '<label><input type="checkbox" value="' + esc(v) + '"' + (set.indexOf(v) >= 0 ? ' checked' : '') + '> <span>' + esc(catLabel(f, v)) + '</span><em>' + cntBy[v] + '</em></label>' }).join('') + '</div>'
    } else {
      var op = c && !c.label ? c.op : (LOWER[k] ? 'lt' : 'gt'), u = f.type === 'm' ? unitOf(c) : null, a = c && !c.label ? shownNum(f, c.a, u) : '', b = c && !c.label && c.op === 'bt' ? shownNum(f, c.b, u) : '';
      if (f.type === 'd') h = '';
      else h = '<div class="s2-cu"><select class="s2-op">' + [['gt', 'Over'], ['ge', 'At least'], ['lt', 'Under'], ['le', 'At most'], ['bt', 'Between'], ['eq', 'Exactly']].map(function (o) { return '<option value="' + o[0] + '"' + (o[0] === op ? ' selected' : '') + '>' + esc(L(o[1])) + '</option>' }).join('') + '</select><span class="s2-in"><input class="s2-a" inputmode="decimal" placeholder="' + esc(L('Value')) + '" value="' + a + '"><span class="s2-and"' + (op === 'bt' ? '' : ' hidden') + '>' + esc(L('and')) + '</span><input class="s2-b" inputmode="decimal" placeholder="' + esc(L('Value')) + '" value="' + b + '"' + (op === 'bt' ? '' : ' hidden') + '></span>' +
        (f.type === 'm' ? '<select class="s2-u">' + [['1', L('$ million')], ['1000', L('$ billion')], ['1000000', L('$ trillion')]].map(function (o) { return '<option value="' + o[0] + '"' + (+o[0] === u ? ' selected' : '') + '>' + esc(o[1]) + '</option>' }).join('') + '</select>' : '<span class="s2-un">' + (f.type === 'p' || f.type === 'y' ? '%' : f.type === 'pr' ? '$' : f.type === 'sh' ? esc(L('million')) : '') + '</span>') + '</div>';
      h += '<div class="s2-pl"><button type="button" data-r="-1"' + (c ? '' : ' class="on"') + '>' + esc(L('Any')) + '</button>' + ready(f).map(function (r, i) { var on = c && c.op === r.op && c.a === r.a && (c.b == null ? r.b == null : c.b === r.b); return '<button type="button" data-r="' + i + '"' + (on ? ' class="on"' : '') + '>' + condText(f, r) + '</button>' }).join('') + '</div>'
    }
    pop.innerHTML = '<div class="s2-pt"><b>' + esc(L(f.label)) + '</b><button type="button" class="s2-x" data-close>×</button></div><p class="s2-pd">' + esc(L(f.desc)) + '</p>' + h; pop.hidden = false; place(pop, anchor);
    var first = $('.s2-a', pop) || $('.s2-ps', pop); if (first && window.innerWidth > 760) first.focus()
  }
  function unitOf(c) { if (!c || c.label) return 1000; var m = Math.max(Math.abs(c.a || 0), Math.abs(c.b || 0)); return m >= 1e6 ? 1e6 : m >= 1000 ? 1000 : 1 }
  function shownNum(f, v, u) { if (v == null) return ''; return String(+((f.type === 'm' ? v / u : v)).toFixed(4)) }
  function place(pop, anchor) {
    var r = anchor.getBoundingClientRect(), rr = root.getBoundingClientRect(); pop.style.top = (r.bottom - rr.top + 6) + 'px';
    if (window.innerWidth <= 760) { pop.style.left = '0px'; pop.style.right = '0px'; pop.style.width = 'auto'; return }
    pop.style.width = '320px'; pop.style.right = 'auto'; var left = Math.min(r.left - rr.left, rr.width - 320); pop.style.left = Math.max(0, left) + 'px'
  }
  function readCustom() {
    if (!popKey || !$('#s2-pop .s2-op')) return;
    var pop = $('#s2-pop'), f = F[popKey], op = $('.s2-op', pop).value, pa = function (s) { var v = parseFloat(String(s).replace(/,/g, '').replace(/[\u06F0-\u06F9]/g, function (d) { return d.charCodeAt(0) - 0x06F0 }).replace(/[\u0660-\u0669]/g, function (d) { return d.charCodeAt(0) - 0x0660 }).replace(/\u066B/g, '.')); return isFinite(v) ? v : null };
    var u = f.type === 'm' ? +$('.s2-u', pop).value : 1, a = pa($('.s2-a', pop).value), b = pa($('.s2-b', pop).value);
    $('.s2-b', pop).hidden = $('.s2-and', pop).hidden = op !== 'bt';
    if (a == null || (op === 'bt' && b == null)) return;
    cond[popKey] = op === 'bt' ? { op: op, a: Math.min(a, b) * u, b: Math.max(a, b) * u } : { op: op, a: a * u };
    $$('.s2-pl button', pop).forEach(function (x) { x.classList.remove('on') }); preset = ''; afterCond()
  }
  function afterCond() { var k = popKey, el = $('.s2-f[data-k="' + k + '"]'); if (el) { el.classList.toggle('on', !!cond[k]); $('.s2-sel span', el).innerHTML = condText(F[k], cond[k]) } markPreset(); if (tab === 'filters') head(); apply() }

  /* ------------------------------------------------------------------ the "add filters" / "edit columns" dialog */
  var modalMode = 'f';
  function openModal(mode) {
    modalMode = mode; var m = $('#s2-modal'), sel = mode === 'f' ? active : (customCols || cols()).slice();
    m._sel = sel.slice();
    m.innerHTML = '<div class="s2-mbox" role="dialog" aria-modal="true"><div class="s2-mh"><div><b>' + esc(mode === 'f' ? L('Select screener filters (%1 total)', Object.keys(F).length) : L('Choose the columns of the table')) + '</b><span id="s2-msel"></span><button type="button" class="s2-link" id="s2-mclr">' + esc(L('Clear all')) + '</button></div><button type="button" class="s2-x" data-mclose aria-label="' + esc(L('Close')) + '">×</button></div>' +
      '<div class="s2-ms"><input id="s2-mq" type="search" autocomplete="off" placeholder="' + esc(L('Search')) + '"></div><div class="s2-mb" id="s2-mbody"></div><div class="s2-mf"><button type="button" class="s2-btn" data-mclose>' + esc(L('Done')) + '</button></div></div>';
    m.hidden = false; document.documentElement.classList.add('s2-lock'); mbody(''); if (window.innerWidth > 760) $('#s2-mq').focus()
  }
  function mbody(q) {
    var m = $('#s2-modal'), sel = m._sel; q = q.trim().toLowerCase();
    $('#s2-mbody').innerHTML = CATS.map(function (c) {
      var items = c[1].filter(function (f) { return !q || L(f[1]).toLowerCase().indexOf(q) >= 0 || f[1].toLowerCase().indexOf(q) >= 0 || L(f[3]).toLowerCase().indexOf(q) >= 0 });
      if (c[0] === 'Most popular' && q) items = [];
      return items.length ? '<h3>' + esc(L(c[0])) + '</h3><div class="s2-mg">' + items.map(function (f) { return '<label title="' + esc(L(f[3])) + '"><input type="checkbox" value="' + f[0] + '"' + (sel.indexOf(f[0]) >= 0 ? ' checked' : '') + '> <span>' + esc(L(f[1])) + '</span></label>' }).join('') + '</div>' : ''
    }).join('') || '<p class="s2-empty">' + esc(L('No filter matches this search.')) + '</p>';
    $('#s2-msel').textContent = L('%1 selected', sel.length)
  }
  function closeModal() {
    var m = $('#s2-modal'); if (m.hidden) return; m.hidden = true; document.documentElement.classList.remove('s2-lock');
    if (modalMode === 'f') { active = m._sel.slice(); Object.keys(cond).forEach(function (k) { if (active.indexOf(k) < 0) delete cond[k] }); markPreset(); refresh() }
    else { customCols = m._sel.slice(); try { localStorage.setItem(LS + 'cols', JSON.stringify(customCols)) } catch (e) { } tab = customCols.length ? 'custom' : 'general'; if (!F[sortKey] || cols().indexOf(sortKey) < 0) { sortKey = 'mcap'; asc = false } head(); apply() }
  }

  /* ------------------------------------------------------------------ presets, saved screens, address */
  function setPreset(id) {
    var p = PRESETS.filter(function (x) { return x[0] === id })[0]; if (!p) return; preset = id; active = Object.keys(p[3]); cond = {};
    active.forEach(function (k) { var c = p[3][k]; cond[k] = c.op === 'in' ? { op: 'in', set: c.set.slice() } : { op: c.op, a: c.a, b: c.b, label: c.label } }); tab = 'filters'; markPreset(); refresh()
  }
  function markPreset() { $$('#s2-pre button').forEach(function (b) { b.classList.toggle('on', b.dataset.p === preset) }); var p = PRESETS.filter(function (x) { return x[0] === preset })[0]; $('#s2-pdesc').textContent = p ? L(p[2]) : '' }
  function enc() { return active.map(function (k) { var c = cond[k]; return !c ? k : c.op === 'in' ? k + '~in~' + c.set.map(encodeURIComponent).join('|') : k + '~' + c.op + '~' + c.a + (c.b != null ? '~' + c.b : '') }).join(';') }
  function dec(s) {
    var a = [], cd = {};
    String(s || '').split(';').forEach(function (p) {
      var x = p.split('~'), k = x[0], f = F[k]; if (!f || a.indexOf(k) >= 0) return; a.push(k);
      if (x[1] === 'in' && x[2]) cd[k] = { op: 'in', set: x[2].split('|').map(function (v) { v = decodeURIComponent(v); return f.k === 'fy_month' ? +v : v }) };
      else if (x[1] && isFinite(+x[2]) && /^(gt|ge|lt|le|eq|bt)$/.test(x[1])) { cd[k] = { op: x[1], a: +x[2] }; if (x[1] === 'bt') { if (!isFinite(+x[3])) { delete cd[k]; return } cd[k].b = +x[3] } var rd = ready(f).filter(function (r) { return r.op === cd[k].op && r.a === cd[k].a && (r.b == null ? cd[k].b == null : r.b === cd[k].b) })[0]; if (rd && rd.label) cd[k].label = rd.label }
    });
    return { a: a, c: cd }
  }
  function save() {
    var st = { f: enc(), t: tab, s: sortKey, d: asc ? 1 : 0, p: preset };
    try { localStorage.setItem(LS + 'state', JSON.stringify(st)) } catch (e) { }
    var h = '#f=' + st.f + '&v=' + tab + '&s=' + sortKey + (asc ? '&asc=1' : ''); try { history.replaceState(null, '', h) } catch (e) { }
  }
  function load() {
    var h = (location.hash || '').slice(1), st = null;
    if (h && h.indexOf('=') < 0) { if (PRESETS.some(function (p) { return p[0] === h })) return { preset: h } }
    if (h.indexOf('f=') >= 0) { st = {}; h.split('&').forEach(function (p) { var i = p.indexOf('='); st[p.slice(0, i)] = p.slice(i + 1) }); st = { f: st.f, t: st.v, s: st.s, d: st.asc ? 1 : 0 } }
    else try { st = JSON.parse(localStorage.getItem(LS + 'state') || 'null') } catch (e) { }
    return st
  }
  function savedList() { try { return JSON.parse(localStorage.getItem(LS + 'saved') || '{}') } catch (e) { return {} } }
  function drawSaved() { var S = savedList(), ks = Object.keys(S); $('#s2-saved').innerHTML = ks.length ? '<span>' + esc(L('Saved screens')) + ':</span>' + ks.map(function (n) { return '<span class="s2-sv"><button type="button" data-sv="' + esc(n) + '">★ ' + esc(n) + '</button><button type="button" class="s2-x" data-svx="' + esc(n) + '" aria-label="' + esc(L('Remove')) + '">×</button></span>' }).join('') : '' }
  function csv() {
    var CL = ['t', 'n'].concat(cols()), rows = [CL.map(function (k) { return k === 't' ? L('Symbol') : k === 'n' ? L('Company') : L(F[k].label) })];
    view.forEach(function (r) { rows.push(CL.map(function (k) { var v = g(r, k), f = F[k]; if (v == null) return ''; if (!f) return v; if (f.type === 'm' || f.type === 'sh') return Math.round(v * 1e6); if (f.type === 'p' || f.type === 'y') return +(v * 100).toFixed(2); if (f.type === 'd') return new Date(TODAY.getTime() + v * 864e5).toISOString().slice(0, 10); if (f.type === 'c') return catLabel(f, v); return typeof v === 'number' ? +v.toFixed(4) : v })) });
    var s = '﻿' + rows.map(function (r) { return r.map(function (v) { return '"' + String(v).replace(/"/g, '""') + '"' }).join(',') }).join('\n'), b = new Blob([s], { type: 'text/csv' }), u = URL.createObjectURL(b), l = document.createElement('a');
    l.href = u; l.download = 'screener_' + new Date().toISOString().slice(0, 10) + '.csv'; document.body.appendChild(l); l.click(); l.remove(); URL.revokeObjectURL(u)
  }

  /* ------------------------------------------------------------------ events */
  function bind() {
    root.addEventListener('click', function (e) {
      var t = e.target, b;
      if ((b = t.closest('[data-mclose]'))) return closeModal();
      if (t.id === 's2-modal') return closeModal();
      if (t.closest('#s2-modal')) { if (t.id === 's2-mclr') { $('#s2-modal')._sel = []; mbody($('#s2-mq').value) } return }
      if ((b = t.closest('[data-close]'))) return closePop();
      if ((b = t.closest('#s2-pop'))) { var r = t.closest('[data-r]'); if (r) { var i = +r.dataset.r, f = F[popKey]; if (i < 0) delete cond[popKey]; else { var rd = ready(f)[i]; cond[popKey] = { op: rd.op, a: rd.a, b: rd.b, label: rd.label } } preset = ''; afterCond(); closePop() } return }
      if ((b = t.closest('[data-o]'))) { if (popKey === b.dataset.o) return closePop(); return openPop(b.dataset.o, b) }
      closePop();
      if ((b = t.closest('[data-x]'))) { var k = b.dataset.x; active = active.filter(function (x) { return x !== k }); delete cond[k]; preset = ''; markPreset(); return refresh() }
      if ((b = t.closest('#s2-pre button'))) return setPreset(b.dataset.p);
      if (t.id === 's2-add') return openModal('f');
      if (t.id === 's2-cols') return openModal('c');
      if (t.id === 's2-reset') { active = DEFAULT.slice(); cond = {}; preset = ''; find = ''; $('#s2-find').value = ''; tab = 'general'; sortKey = 'mcap'; asc = false; markPreset(); return refresh() }
      if (t.id === 's2-csv') { if (!ACCESS) { location.href = CFG.subUrl || '#'; return } return csv() }
      if (t.id === 's2-save') { if (!ACCESS) { location.href = CFG.subUrl || '#'; return } var n = prompt(L('Name this screen')); if (!n) return; var S = savedList(); S[n.slice(0, 40)] = enc(); try { localStorage.setItem(LS + 'saved', JSON.stringify(S)) } catch (e2) { } return drawSaved() }
      if ((b = t.closest('[data-svx]'))) { var S2 = savedList(); delete S2[b.dataset.svx]; try { localStorage.setItem(LS + 'saved', JSON.stringify(S2)) } catch (e3) { } return drawSaved() }
      if ((b = t.closest('[data-sv]'))) { var d = dec(savedList()[b.dataset.sv]); active = d.a; cond = d.c; preset = ''; tab = 'filters'; markPreset(); return refresh() }
      if ((b = t.closest('#s2-tabs button'))) { tab = b.dataset.t; if (sortKey !== 't' && cols().indexOf(sortKey) < 0) { sortKey = 'mcap'; asc = false } head(); return apply() }
      if ((b = t.closest('#s2-head th'))) { var sk = b.dataset.k; if (sk === sortKey) asc = !asc; else { sortKey = sk; asc = sk === 't' || !!LOWER[sk] || (F[sk] && F[sk].type === 'c') } return apply() }
      if (t.id === 's2-mb') { shown += PAGE; return draw() }
      if (t.id === 's2-ma') { shown = view.length; return draw() }
      if ((b = t.closest('#s2-qlist button'))) { var qk = b.dataset.k; if (active.indexOf(qk) < 0) active.push(qk); $('#s2-q').value = ''; $('#s2-qlist').innerHTML = ''; refresh(); var el = $('.s2-f[data-k="' + qk + '"] .s2-sel'); if (el) openPop(qk, el); return }
    });
    root.addEventListener('input', function (e) {
      var t = e.target;
      if (t.id === 's2-find') { find = t.value; return apply() }
      if (t.id === 's2-mq') return mbody(t.value);
      if (t.id === 's2-q') { var q = t.value.trim().toLowerCase(), out = []; if (q) Object.keys(F).forEach(function (k) { var f = F[k]; if (out.length < 12 && (L(f.label).toLowerCase().indexOf(q) >= 0 || f.label.toLowerCase().indexOf(q) >= 0)) out.push(f) }); $('#s2-qlist').innerHTML = out.map(function (f) { return '<button type="button" data-k="' + f.k + '">' + esc(L(f.label)) + '<em>' + esc(L(f.cat)) + '</em></button>' }).join(''); return }
      if (t.classList.contains('s2-ps')) { var s = t.value.trim().toLowerCase(); $$('#s2-pop .s2-pl label:not(.any)').forEach(function (l) { l.hidden = !!s && l.textContent.toLowerCase().indexOf(s) < 0 }); return }
      if (t.closest('.s2-cu')) return readCustom()
    });
    root.addEventListener('change', function (e) {
      var t = e.target, m = $('#s2-modal');
      if (t.closest('#s2-mbody') && t.type === 'checkbox') { var i = m._sel.indexOf(t.value); if (t.checked && i < 0) m._sel.push(t.value); if (!t.checked && i >= 0) m._sel.splice(i, 1); $$('#s2-mbody input[value="' + t.value + '"]').forEach(function (x) { x.checked = t.checked }); $('#s2-msel').textContent = L('%1 selected', m._sel.length); return }
      if (t.closest('#s2-pop .s2-pl') && t.type === 'checkbox') {
        if (!popKey) return; var f = F[popKey]; if (t.hasAttribute('data-any')) { $$('#s2-pop .s2-pl input[value]').forEach(function (x) { x.checked = false }); delete cond[popKey] }
        else { var set = $$('#s2-pop .s2-pl input[value]').filter(function (x) { return x.checked }).map(function (x) { return f.k === 'fy_month' ? +x.value : x.value }); if (set.length) cond[popKey] = { op: 'in', set: set }; else delete cond[popKey]; $('#s2-pop [data-any]').checked = !set.length }
        preset = ''; return afterCond()
      }
      if (t.closest('.s2-cu')) return readCustom()
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closePop(); closeModal() } });
    document.addEventListener('click', function (e) { if (e.target.isConnected && !root.contains(e.target)) closePop() });
    window.addEventListener('resize', closePop)
  }

  /* ------------------------------------------------------------------ start */
  function start() {
    var host = document.getElementById('scr2'); if (!host) return; root = host; root.classList.toggle('s2-rtl', RTL); root.setAttribute('dir', RTL ? 'rtl' : 'ltr');
    try { customCols = JSON.parse(localStorage.getItem(LS + 'cols') || 'null') } catch (e) { }
    if (customCols) customCols = customCols.filter(function (k) { return F[k] });
    shell(); bind(); drawSaved();
    var sub = CFG.subSel && document.querySelector(CFG.subSel); if (sub && W.SUB) sub.textContent = L('SUB', Object.keys(F).length);
    var st = load(), pre = st && st.preset;
    if (st && st.f != null) { var d = dec(st.f); active = d.a; cond = d.c; if (VIEWS[st.t] && (st.t !== 'custom' || customCols)) tab = st.t; if (st.s === 't' || F[st.s]) sortKey = st.s; asc = !!st.d; preset = st.p || '' }
    if (!active.length && !pre) active = DEFAULT.slice();
    flist(); head(); tabs(); markPreset();
    var core = getJSON(BASE + '/core.json?v=' + Math.floor(Date.now() / 3e5)), more = getJSON(BASE + '/more.json?v=' + Math.floor(Date.now() / 3e5)), quotes = getJSON(QUOTES + '?v=' + Math.floor(Date.now() / 12e4)).catch(function () { return null });
    core.then(function (j) {
      merge(j); AS_OF = j.as_of || '';
      $('#s2-asof').textContent = AS_OF ? L('Data as of %1', AS_OF) : '';
      if (pre) setPreset(pre); else if (!need()) apply(); else $('#s2-count').textContent = L('Loading…');
      return more
    }).then(function (j) {
      merge(j); HAVE_MORE = true;
      /* dates are stored as days from the build day: shift them to days from today */
      var off = j.built ? Math.round((new Date(new Date().toISOString().slice(0, 10)) - new Date(j.built)) / 864e5) : 0;
      if (off > 0) ['earn_in', 'exdiv_in'].forEach(function (k) { var i = C[k]; if (i != null) ROWS.forEach(function (r) { if (r[i] != null) { r[i] -= off; if (k === 'earn_in' && r[i] < -3) r[i] = null } }) });
      return quotes
    }).then(function (q) { live(q); head(); apply() })
      .catch(function (err) { if (ROWS.length) { head(); apply() } else $('#s2-count').textContent = L('The data could not be loaded. Please reload the page.'); if (window.console) console.warn('screener', err) })
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
  window.SCR2 = { F: F, CATS: CATS, PRESETS: PRESETS, VIEWS: VIEWS, DEFAULT: DEFAULT, ready: ready, test: test };
})();
