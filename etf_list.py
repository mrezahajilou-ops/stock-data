#!/usr/bin/env python3
"""The 50 ETFs the site covers, and the durable facts about each one.

Only things that do not change live here: the issuer, the index tracked, the year it launched, what
the fund is for, and which UCITS fund a European investor can buy instead. Anything that moves —
price, assets, expense ratio, returns, holdings — is fetched daily by etf_data.py, because a stale
number on a page is worse than no number.

`ucits` names a specific replacement only where the replacement is unambiguous. Where several funds
track the same index and none is the obvious answer, it names the index to look for instead of
inventing a ticker.
"""

# idea:      one sentence, what you are actually buying
# strategy:  how the fund picks what it holds, and what that means in practice
# focus:     short tag used for grouping and filtering
ETFS = [
    dict(t='VOO', name='Vanguard S&P 500 ETF', issuer='Vanguard', index='S&P 500', since=2010,
         cls='equity', focus='US large cap',
         idea='The 500 biggest American companies, at the lowest cost in the industry.',
         strategy='Holds every company in the S&P 500 in proportion to its market value, so the '
                  'biggest companies dominate the fund. There is no judgement involved: a company '
                  'joins when the index committee adds it and leaves when it is removed. Because '
                  'the weights follow market value, roughly a third of the fund sits in the ten '
                  'largest companies, which is far more concentrated than most buyers expect.',
         ucits=dict(ticker='VUAA / VUSA', name='Vanguard S&P 500 UCITS ETF',
                    note='VUAA accumulates dividends, VUSA pays them out.')),
    dict(t='IVV', name='iShares Core S&P 500 ETF', issuer='BlackRock', index='S&P 500', since=2000,
         cls='equity', focus='US large cap',
         idea='The same 500 companies as VOO, from a different manager, at the same cost.',
         strategy='Tracks the S&P 500 by holding every constituent at its index weight. For a '
                  'long-term holder the choice between this and VOO comes down to which brokerage '
                  'you use and which trades at a tighter spread on the day, not to anything about '
                  'the funds themselves.',
         ucits=dict(ticker='CSPX / SXR8', name='iShares Core S&P 500 UCITS ETF (Acc)',
                    note='The same index from the same manager, in a European wrapper.')),
    dict(t='SPY', name='SPDR S&P 500 ETF Trust', issuer='State Street', index='S&P 500', since=1993,
         cls='equity', focus='US large cap',
         idea='The original S&P 500 fund: the most heavily traded security in the world.',
         strategy='The oldest US ETF, and structured as a unit investment trust rather than a '
                  'modern fund, which means it cannot lend out securities or reinvest dividends '
                  'between payments. That costs long-term holders a little each year against VOO '
                  'and IVV. In exchange it has by far the deepest liquidity and options market, '
                  'which is why traders use it and buy-and-hold investors usually should not.',
         ucits=dict(ticker='CSPX / VUAA', name='iShares Core S&P 500 UCITS ETF',
                    note='No European fund replicates SPY’s trust structure, and none needs to.')),
    dict(t='VTI', name='Vanguard Total Stock Market ETF', issuer='Vanguard',
         index='CRSP US Total Market', since=2001, cls='equity', focus='US total market',
         idea='Every investable public company in America, in one holding.',
         strategy='Holds thousands of companies, from the largest down to small caps, weighted by '
                  'market value. In practice it behaves almost identically to an S&P 500 fund, '
                  'because the small companies that make it different are collectively a few '
                  'percent of the weight. The difference shows up in the rare periods when small '
                  'caps lead.',
         ucits=dict(ticker='VNRT', name='Vanguard FTSE North America UCITS ETF',
                    note='Closest European equivalent; it includes Canada, which VTI does not.')),
    dict(t='QQQ', name='Invesco QQQ Trust', issuer='Invesco', index='Nasdaq-100', since=1999,
         cls='equity', focus='US large cap growth',
         idea='The 100 largest non-financial companies on the Nasdaq — in practice, a bet on big technology.',
         strategy='Tracks the Nasdaq-100, which excludes financial companies entirely and is '
                  'defined by where a company is listed rather than what it does. That accident of '
                  'construction is why the fund is so concentrated in technology and why it has '
                  'both outperformed and fallen harder than the S&P 500 at different times. The '
                  'top ten holdings are typically close to half the fund.',
         ucits=dict(ticker='EQQQ / CNDX', name='Invesco EQQQ Nasdaq-100 UCITS ETF, or iShares Nasdaq 100 UCITS ETF',
                    note='Both track the same index; CNDX accumulates, EQQQ distributes.')),
    dict(t='VUG', name='Vanguard Growth ETF', issuer='Vanguard', index='CRSP US Large Cap Growth',
         since=2004, cls='equity', focus='US large cap growth',
         idea='The faster-growing half of large American companies, by a rules-based definition of growth.',
         strategy='Splits the large-cap US market into growth and value using measures such as '
                  'earnings growth, sales growth and book value, then holds the growth side by '
                  'market value. Because the biggest technology companies score as growth, the '
                  'fund ends up heavily concentrated in them — closer to QQQ in behaviour than the '
                  'name suggests.',
         ucits=dict(name='A UCITS ETF tracking a US large-cap growth index',
                    note='Several providers offer one; there is no single obvious equivalent.')),
    dict(t='VTV', name='Vanguard Value ETF', issuer='Vanguard', index='CRSP US Large Cap Value',
         since=2004, cls='equity', focus='US large cap value',
         idea='The cheaper half of large American companies, which means banks, healthcare and industrials.',
         strategy='The other half of the same split that produces VUG. It holds large US companies '
                  'that score as value on price to book, price to earnings and dividend yield, '
                  'weighted by market value. The result is a fund with far more financials, '
                  'healthcare and energy and far less technology than the S&P 500, and a higher '
                  'dividend yield.',
         ucits=dict(name='A UCITS ETF tracking a US large-cap value index',
                    note='Available from several providers; check which value definition it uses.')),
    dict(t='VIG', name='Vanguard Dividend Appreciation ETF', issuer='Vanguard',
         index='S&P U.S. Dividend Growers', since=2006, cls='equity', focus='US dividend growth',
         idea='Companies that have raised their dividend for at least ten years running.',
         strategy='Screens for a long unbroken record of dividend increases, then excludes the '
                  'highest-yielding quarter of those that qualify. That second step is the clever '
                  'part: a very high yield is usually a sign of a falling share price rather than '
                  'generosity, so removing those names avoids most dividend cuts. The result is a '
                  'quality fund that happens to pay a dividend, not a high-income fund.',
         ucits=dict(name='A UCITS ETF tracking a US dividend growth index',
                    note='The ten-year increase screen is uncommon in European wrappers.')),
    dict(t='SCHD', name='Schwab U.S. Dividend Equity ETF', issuer='Charles Schwab',
         index='Dow Jones U.S. Dividend 100', since=2011, cls='equity', focus='US dividend',
         idea='A hundred dividend payers filtered for balance-sheet strength, not just yield.',
         strategy='Requires ten consecutive years of dividends, then ranks what is left on cash '
                  'flow to debt, return on equity, dividend yield and dividend growth. That '
                  'combination keeps out companies paying a dividend they cannot afford, which is '
                  'the usual failure of high-yield funds. Holdings are capped so no single company '
                  'or sector dominates.',
         ucits=dict(ticker='Screened US dividend UCITS funds', name='A UCITS ETF tracking a quality US dividend index',
                    note='Nothing in Europe replicates the Dow Jones 100 methodology exactly.')),
    dict(t='VYM', name='Vanguard High Dividend Yield ETF', issuer='Vanguard',
         index='FTSE High Dividend Yield', since=2006, cls='equity', focus='US dividend',
         idea='The higher-yielding half of the US market, weighted by size.',
         strategy='Ranks US companies by forecast dividend yield and takes the top half by market '
                  'value, excluding real estate trusts. It applies no quality screen at all, which '
                  'makes it simpler and broader than SCHD but leaves it holding more companies '
                  'whose yield is high because the share price has fallen.',
         ucits=dict(ticker='VHYL', name='Vanguard FTSE All-World High Dividend Yield UCITS ETF',
                    note='Global rather than US-only, but the same family and methodology.')),
    dict(t='DGRO', name='iShares Core Dividend Growth ETF', issuer='BlackRock',
         index='Morningstar US Dividend Growth', since=2014, cls='equity', focus='US dividend growth',
         idea='US companies with five years of dividend increases and room to keep raising them.',
         strategy='Requires five years of uninterrupted dividend growth and a payout ratio below '
                  '75%, which screens out companies paying out more than they can sustain. It '
                  'excludes the top decile by yield for the same reason VIG does. Broader than VIG '
                  'with a slightly higher yield.',
         ucits=dict(name='A UCITS ETF tracking a US dividend growth index')),
    dict(t='IWF', name='iShares Russell 1000 Growth ETF', issuer='BlackRock',
         index='Russell 1000 Growth', since=2000, cls='equity', focus='US large cap growth',
         idea='The growth half of the thousand largest US companies, on Russell’s definition.',
         strategy='Russell splits its large-cap universe using book-to-price and forecast growth, '
                  'and allows companies to sit partly in growth and partly in value. The practical '
                  'effect is heavy technology weighting, similar to VUG but with a different '
                  'rebalancing calendar — the annual Russell reconstitution in June is one of the '
                  'largest single trading events of the year.',
         ucits=dict(name='A UCITS ETF tracking the Russell 1000 Growth index')),
    dict(t='IWD', name='iShares Russell 1000 Value ETF', issuer='BlackRock',
         index='Russell 1000 Value', since=2000, cls='equity', focus='US large cap value',
         idea='The value half of the thousand largest US companies.',
         strategy='The mirror image of IWF, holding the companies that score cheap on book-to-price '
                  'and low forecast growth. Dominated by financials, healthcare and industrials. '
                  'Pairs with IWF to reconstruct the whole Russell 1000.',
         ucits=dict(name='A UCITS ETF tracking the Russell 1000 Value index')),
    dict(t='IWM', name='iShares Russell 2000 ETF', issuer='BlackRock', index='Russell 2000',
         since=2000, cls='equity', focus='US small cap',
         idea='Two thousand small American companies — the most-used proxy for US small caps.',
         strategy='Holds the 1,001st to 3,000th largest US companies by market value. A meaningful '
                  'share of the index is unprofitable, which is why it behaves very differently '
                  'from large-cap indices: it is more sensitive to interest rates and to the '
                  'domestic economy, and far more volatile.',
         ucits=dict(ticker='IDP6 / RTWO', name='A UCITS ETF tracking the Russell 2000')),
    dict(t='IJH', name='iShares Core S&P Mid-Cap ETF', issuer='BlackRock', index='S&P MidCap 400',
         since=2000, cls='equity', focus='US mid cap',
         idea='The 400 mid-sized American companies that sit between the S&P 500 and small caps.',
         strategy='The S&P mid-cap index applies a profitability requirement for entry, which the '
                  'Russell indices do not. That single rule has historically made US mid caps a '
                  'better-quality universe than small caps, and explains much of the long-run '
                  'return difference between the two.',
         ucits=dict(name='A UCITS ETF tracking the S&P MidCap 400')),
    dict(t='IJR', name='iShares Core S&P Small-Cap ETF', issuer='BlackRock', index='S&P SmallCap 600',
         since=2000, cls='equity', focus='US small cap',
         idea='Six hundred small American companies, screened for profitability.',
         strategy='Tracks the S&P SmallCap 600, which requires companies to be profitable before '
                  'they can join. That is the key difference from the Russell 2000 and the reason '
                  'the two small-cap indices have diverged over long periods despite covering the '
                  'same part of the market.',
         ucits=dict(name='A UCITS ETF tracking the S&P SmallCap 600')),
    dict(t='VO', name='Vanguard Mid-Cap ETF', issuer='Vanguard', index='CRSP US Mid Cap',
         since=2004, cls='equity', focus='US mid cap',
         idea='Mid-sized American companies, defined by where they fall in total market value.',
         strategy='Takes the slice of the US market between roughly the 70th and 85th percentile of '
                  'cumulative market value. No profitability screen, unlike the S&P mid-cap index, '
                  'so it holds a broader and slightly lower-quality set of companies at a lower cost.',
         ucits=dict(name='A UCITS ETF tracking a US mid-cap index')),
    dict(t='VB', name='Vanguard Small-Cap ETF', issuer='Vanguard', index='CRSP US Small Cap',
         since=2004, cls='equity', focus='US small cap',
         idea='Small American companies, with no screen on whether they make money.',
         strategy='Covers the bottom slice of the US market by cumulative value, holding well over '
                  'a thousand companies. Broader than IJR and cheaper, but it includes '
                  'loss-making companies that the S&P small-cap index excludes.',
         ucits=dict(name='A UCITS ETF tracking a US small-cap index')),
    dict(t='SPYM', name='State Street SPDR Portfolio S&P 500 ETF', issuer='State Street', index='S&P 500',
         since=2005, cls='equity', focus='US large cap',
         idea='State Street’s cheap S&P 500 fund, built for holding rather than trading.',
         strategy='The same index as SPY in a modern fund structure at a far lower cost. State '
                  'Street launched it precisely because SPY’s trust structure made it unattractive '
                  'to long-term investors. Lower trading volume than SPY, which only matters if '
                  'you are dealing in size.',
         ucits=dict(ticker='CSPX / VUAA', name='iShares or Vanguard S&P 500 UCITS ETF')),
    dict(t='RSP', name='Invesco S&P 500 Equal Weight ETF', issuer='Invesco',
         index='S&P 500 Equal Weight', since=2003, cls='equity', focus='US large cap',
         idea='The same 500 companies as the S&P 500, but each one holding the same weight.',
         strategy='Gives every company roughly 0.2% of the fund and rebalances quarterly, which '
                  'systematically sells what has risen and buys what has fallen. That removes the '
                  'concentration in the largest companies entirely — the practical effect is a '
                  'tilt toward mid-sized and value companies. It beats the standard S&P 500 when '
                  'the market broadens and lags badly when a few giants lead.',
         ucits=dict(ticker='XDEW / EWSP', name='A UCITS ETF tracking the S&P 500 Equal Weight index')),
    dict(t='QUAL', name='iShares MSCI USA Quality Factor ETF', issuer='BlackRock',
         index='MSCI USA Sector Neutral Quality', since=2013, cls='equity', focus='US quality factor',
         idea='American companies that score well on return on equity, stable earnings and low debt.',
         strategy='Ranks companies on three measures — return on equity, earnings variability and '
                  'debt to equity — and holds the best within each sector, so the fund does not '
                  'become an accidental sector bet. Quality has historically held up better than '
                  'the market in downturns and lagged in sharp recoveries.',
         ucits=dict(ticker='IS3Q / QDVB', name='iShares Edge MSCI USA Quality Factor UCITS ETF')),
    dict(t='MGK', name='Vanguard Mega Cap Growth ETF', issuer='Vanguard',
         index='CRSP US Mega Cap Growth', since=2007, cls='equity', focus='US mega cap growth',
         idea='Only the very largest American growth companies — the most concentrated way to own them.',
         strategy='Restricts itself to the mega-cap end of the growth universe, which means a few '
                  'dozen holdings and extreme concentration in the largest technology companies. '
                  'More concentrated than QQQ and far more than VUG. Suitable only for someone who '
                  'has deliberately decided they want that exposure.',
         ucits=dict(name='A UCITS ETF tracking a US mega-cap growth index')),
    dict(t='VV', name='Vanguard Large-Cap ETF', issuer='Vanguard', index='CRSP US Large Cap',
         since=2004, cls='equity', focus='US large cap',
         idea='The large-cap part of the US market, defined by size rather than by a committee.',
         strategy='Covers the top 85% of the US market by cumulative value, so it holds more '
                  'companies than the S&P 500 and avoids the index committee that decides S&P '
                  'membership. In practice its returns track the S&P 500 very closely.',
         ucits=dict(ticker='CSPX / VUAA', name='An S&P 500 or MSCI USA UCITS ETF')),
    dict(t='ITOT', name='iShares Core S&P Total U.S. Stock Market ETF', issuer='BlackRock',
         index='S&P Total Market', since=2004, cls='equity', focus='US total market',
         idea='The whole US stock market in one fund, from BlackRock.',
         strategy='Holds the full breadth of the US market, large through micro cap, at index '
                  'weights. The direct competitor to VTI, with essentially the same exposure, the '
                  'same cost and the same practical behaviour.',
         ucits=dict(ticker='VNRT', name='Vanguard FTSE North America UCITS ETF')),
    dict(t='SCHX', name='Schwab U.S. Large-Cap ETF', issuer='Charles Schwab',
         index='Dow Jones U.S. Large-Cap Total Stock Market', since=2009, cls='equity',
         focus='US large cap',
         idea='The largest 750 US companies, at one of the lowest costs available.',
         strategy='A broad large-cap fund covering more companies than the S&P 500 at a cost at the '
                  'very bottom of the industry. Behaves almost identically to VV and the S&P 500 '
                  'over any meaningful period.',
         ucits=dict(ticker='CSPX / VUAA', name='An S&P 500 or MSCI USA UCITS ETF')),
    dict(t='VEA', name='Vanguard FTSE Developed Markets ETF', issuer='Vanguard',
         index='FTSE Developed All Cap ex US', since=2007, cls='equity', focus='developed ex-US',
         idea='Developed-market companies outside the United States: Europe, Japan, Canada, Australia.',
         strategy='Holds thousands of companies across developed markets excluding the US, '
                  'weighted by market value, which means Japan and the United Kingdom are large '
                  'positions. Unlike the MSCI version it includes Canada and South Korea. Returns '
                  'depend heavily on the dollar: a weaker dollar flatters them, a stronger one '
                  'does the opposite.',
         ucits=dict(ticker='VEVE / IWDA', name='Vanguard FTSE Developed World UCITS ETF, or iShares Core MSCI World',
                    note='IWDA includes the US; VEVE ex-US variants differ by provider.')),
    dict(t='VXUS', name='Vanguard Total International Stock ETF', issuer='Vanguard',
         index='FTSE Global All Cap ex US', since=2011, cls='equity', focus='global ex-US',
         idea='Every investable company in the world outside the United States.',
         strategy='Combines developed and emerging markets outside the US in one fund, at market '
                  'weights, holding several thousand companies. Pairs with VTI to build a complete '
                  'global portfolio with two holdings.',
         ucits=dict(ticker='VWRL / VWCE', name='Vanguard FTSE All-World UCITS ETF',
                    note='VWRL includes the US as well; there is no exact ex-US twin in the range.')),
    dict(t='IEFA', name='iShares Core MSCI EAFE ETF', issuer='BlackRock', index='MSCI EAFE IMI',
         since=2012, cls='equity', focus='developed ex-US',
         idea='Developed Europe, Australasia and the Far East — the standard international benchmark.',
         strategy='Tracks MSCI’s EAFE universe, which excludes the US and Canada and covers large, '
                  'mid and small companies. The most widely used international allocation in US '
                  'portfolios, and the reference point against which international managers are '
                  'measured.',
         ucits=dict(ticker='IWDA / SWDA', name='iShares Core MSCI World UCITS ETF',
                    note='World includes the US; EAFE-only UCITS versions exist but are less traded.')),
    dict(t='VWO', name='Vanguard FTSE Emerging Markets ETF', issuer='Vanguard',
         index='FTSE Emerging Markets All Cap', since=2005, cls='equity', focus='emerging markets',
         idea='Companies in developing economies, dominated by China, India and Taiwan.',
         strategy='Holds emerging-market companies at market weight, which concentrates the fund in '
                  'a handful of countries and in a small number of very large technology and '
                  'internet companies. FTSE classifies South Korea as developed, so unlike the '
                  'MSCI version this fund does not hold Korean companies.',
         ucits=dict(ticker='VFEM / EIMI', name='Vanguard FTSE Emerging Markets UCITS ETF, or iShares Core MSCI EM IMI')),
    dict(t='IEMG', name='iShares Core MSCI Emerging Markets ETF', issuer='BlackRock',
         index='MSCI Emerging Markets IMI', since=2012, cls='equity', focus='emerging markets',
         idea='Emerging markets on MSCI’s definition, which includes South Korea.',
         strategy='The main difference from VWO is country classification: MSCI treats South Korea '
                  'as emerging, so this fund holds large Korean companies that VWO does not. It '
                  'also reaches further down into small caps. Otherwise the two behave similarly.',
         ucits=dict(ticker='EIMI', name='iShares Core MSCI EM IMI UCITS ETF')),
    dict(t='EFA', name='iShares MSCI EAFE ETF', issuer='BlackRock', index='MSCI EAFE', since=2001,
         cls='equity', focus='developed ex-US',
         idea='The original international developed-markets fund, large and mid caps only.',
         strategy='Older and more expensive than IEFA, covering the same markets but without small '
                  'caps. It persists because of its deep options market and its role as the '
                  'benchmark in institutional mandates rather than because it is the better fund '
                  'to hold.',
         ucits=dict(ticker='IWDA / SWDA', name='iShares Core MSCI World UCITS ETF')),
    dict(t='VT', name='Vanguard Total World Stock ETF', issuer='Vanguard',
         index='FTSE Global All Cap', since=2008, cls='equity', focus='global',
         idea='The entire investable stock market on earth, in a single holding.',
         strategy='Holds roughly ten thousand companies across developed and emerging markets at '
                  'market weight, which currently means about two-thirds United States. It is the '
                  'closest thing available to owning the global market portfolio, and requires no '
                  'decision about how much to allocate to any country.',
         ucits=dict(ticker='VWCE / VWRL', name='Vanguard FTSE All-World UCITS ETF',
                    note='VWCE accumulates dividends, VWRL distributes them.')),
    dict(t='VGK', name='Vanguard FTSE Europe ETF', issuer='Vanguard', index='FTSE Developed Europe All Cap',
         since=2005, cls='equity', focus='Europe',
         idea='European companies, from the UK and Switzerland through to the Nordics.',
         strategy='Market-weighted exposure to developed Europe, which concentrates the fund in a '
                  'few very large companies in pharmaceuticals, luxury goods, semiconductor '
                  'equipment and banking. Currency moves between the euro, the pound and the '
                  'dollar account for a large share of the return in any given year.',
         ucits=dict(ticker='VEUR / IMEU', name='Vanguard FTSE Developed Europe UCITS ETF')),
    dict(t='VEU', name='Vanguard FTSE All-World ex-US ETF', issuer='Vanguard',
         index='FTSE All-World ex US', since=2007, cls='equity', focus='global ex-US',
         idea='The world outside America, large and mid caps only.',
         strategy='Very close to VXUS but without small caps, which makes it slightly more '
                  'concentrated in the large multinationals that dominate non-US indices. Either '
                  'fund serves the same role in a portfolio.',
         ucits=dict(ticker='VWRL / VWCE', name='Vanguard FTSE All-World UCITS ETF')),
    dict(t='VGT', name='Vanguard Information Technology ETF', issuer='Vanguard',
         index='MSCI US IMI Information Technology', since=2004, cls='equity', focus='technology',
         idea='American technology companies, including the hardware and semiconductor makers.',
         strategy='Covers the technology sector on MSCI’s definition, which includes software, '
                  'hardware and semiconductors but excludes the large internet and media companies '
                  'that are classified as communication services, and excludes Amazon and Tesla, '
                  'which are consumer companies. Those exclusions matter more than most buyers '
                  'realise, and are the main difference from QQQ.',
         ucits=dict(ticker='IITU / XLKQ', name='A UCITS ETF tracking US or world information technology')),
    dict(t='XLK', name='Technology Select Sector SPDR Fund', issuer='State Street',
         index='Technology Select Sector', since=1998, cls='equity', focus='technology',
         idea='The technology companies inside the S&P 500, and only those.',
         strategy='Restricted to S&P 500 members classified as technology, which makes it far more '
                  'concentrated than VGT — typically fewer than 70 holdings, with the top two '
                  'approaching 40% of the fund. Sector definitions are revised periodically and '
                  'those revisions can change the fund materially overnight.',
         ucits=dict(ticker='IITU', name='iShares S&P 500 Information Technology Sector UCITS ETF')),
    dict(t='SMH', name='VanEck Semiconductor ETF', issuer='VanEck', index='MVIS US Listed Semiconductor 25',
         since=2011, cls='equity', focus='semiconductors',
         idea='The 25 largest listed semiconductor companies — the most concentrated way to own the chip cycle.',
         strategy='Holds only 25 companies, which makes it extremely concentrated: the largest two '
                  'or three positions can be a third of the fund. It includes foreign-listed chip '
                  'makers through their US listings, which SOXX historically did not. Semiconductor '
                  'demand is cyclical and this fund moves far more than the market in both '
                  'directions.',
         ucits=dict(ticker='SMGB / SMH LN', name='VanEck Semiconductor UCITS ETF')),
    dict(t='SOXX', name='iShares Semiconductor ETF', issuer='BlackRock',
         index='NYSE Semiconductor', since=2001, cls='equity', focus='semiconductors',
         idea='Thirty US-listed semiconductor companies, slightly more spread out than SMH.',
         strategy='Tracks a US-listed semiconductor index with caps that limit how large any single '
                  'holding can become, so it is less top-heavy than SMH. The index methodology has '
                  'changed more than once, which is worth knowing before comparing its long-run '
                  'record with anything else.',
         ucits=dict(ticker='SEMI / CHIP', name='A UCITS ETF tracking global semiconductors')),
    dict(t='XLF', name='Financial Select Sector SPDR Fund', issuer='State Street',
         index='Financial Select Sector', since=1998, cls='equity', focus='financials',
         idea='The banks, insurers and payment companies inside the S&P 500.',
         strategy='Holds S&P 500 financial companies at capped market weights. Since real estate '
                  'was split out into its own sector the fund is a cleaner bet on banking, '
                  'insurance and capital markets. It is highly sensitive to interest rates and to '
                  'credit conditions, which is the whole reason to own or avoid it.',
         ucits=dict(ticker='IUFS', name='iShares S&P 500 Financials Sector UCITS ETF')),
    dict(t='XLV', name='Health Care Select Sector SPDR Fund', issuer='State Street',
         index='Health Care Select Sector', since=1998, cls='equity', focus='healthcare',
         idea='Large American healthcare: drug makers, device companies, insurers and distributors.',
         strategy='Covers S&P 500 healthcare companies, which blends very different businesses — '
                  'patent-dependent pharmaceutical makers, steady device manufacturers and '
                  'insurers whose economics are driven by government policy. US drug pricing and '
                  'health policy affect all of them, which is why the sector moves on political '
                  'news more than most.',
         ucits=dict(ticker='IUHC', name='iShares S&P 500 Health Care Sector UCITS ETF')),
    dict(t='XLE', name='Energy Select Sector SPDR Fund', issuer='State Street',
         index='Energy Select Sector', since=1998, cls='equity', focus='energy',
         idea='American oil and gas, dominated by two supermajors.',
         strategy='Holds S&P 500 energy companies, and because the sector is so top-heavy the two '
                  'largest integrated oil companies are typically around 40% of the fund. It is a '
                  'direct bet on the oil price with the operating leverage of the producers on top.',
         ucits=dict(ticker='IUES', name='iShares S&P 500 Energy Sector UCITS ETF')),
    dict(t='XLI', name='Industrial Select Sector SPDR Fund', issuer='State Street',
         index='Industrial Select Sector', since=1998, cls='equity', focus='industrials',
         idea='American industry: aerospace, railroads, machinery and the big conglomerates.',
         strategy='Holds the S&P 500 industrials, a genuinely diverse group ranging from defence '
                  'contractors with multi-year backlogs to machinery makers tied to the economic '
                  'cycle. Often used as a direct way to express a view on US manufacturing and '
                  'infrastructure spending.',
         ucits=dict(ticker='IUIS', name='iShares S&P 500 Industrials Sector UCITS ETF')),
    dict(t='VNQ', name='Vanguard Real Estate ETF', issuer='Vanguard',
         index='MSCI US Investable Market Real Estate 25/50', since=2004, cls='equity',
         focus='real estate',
         idea='American property, owned through listed real estate investment trusts.',
         strategy='Holds US REITs across data centres, warehouses, towers, apartments, shops and '
                  'offices. Because REITs must distribute most of their income, the fund pays a '
                  'high dividend and is unusually sensitive to interest rates: higher rates raise '
                  'the cost of the debt that property is financed with and make the yield less '
                  'attractive at the same time.',
         ucits=dict(ticker='IUSP / EPRA', name='A UCITS ETF tracking US or developed-market property')),
    dict(t='VHT', name='Vanguard Health Care ETF', issuer='Vanguard',
         index='MSCI US IMI Health Care', since=2004, cls='equity', focus='healthcare',
         idea='The whole US healthcare sector, including the smaller biotechnology companies.',
         strategy='Broader than XLV because it reaches beyond the S&P 500 into mid and small caps, '
                  'which means it holds a long tail of biotechnology companies. That tail adds '
                  'volatility and the possibility of outsized returns that a large-cap-only '
                  'healthcare fund does not have.',
         ucits=dict(ticker='IUHC', name='A UCITS ETF tracking US health care')),
    dict(t='BND', name='Vanguard Total Bond Market ETF', issuer='Vanguard',
         index='Bloomberg U.S. Aggregate Float Adjusted', since=2007, cls='bond',
         focus='US investment grade bonds',
         idea='The US investment-grade bond market: government, mortgage and corporate debt together.',
         strategy='Holds thousands of investment-grade bonds at index weight, which means roughly '
                  'two-thirds government and government-backed mortgage debt. Its price falls when '
                  'interest rates rise and rises when they fall; the duration of around six years '
                  'tells you roughly how much. It is the standard ballast holding in a portfolio '
                  'rather than a source of return.',
         ucits=dict(ticker='AGGU / VAGU', name='A USD-hedged global or US aggregate bond UCITS ETF')),
    dict(t='AGG', name='iShares Core U.S. Aggregate Bond ETF', issuer='BlackRock',
         index='Bloomberg U.S. Aggregate', since=2003, cls='bond',
         focus='US investment grade bonds',
         idea='The same US bond market as BND, from BlackRock.',
         strategy='Tracks the unadjusted Bloomberg US Aggregate index. The practical difference '
                  'from BND is negligible — a slightly different float adjustment and a marginally '
                  'different cost. Choose on which your broker trades more cheaply.',
         ucits=dict(ticker='AGGU', name='iShares Core Global Aggregate Bond UCITS ETF')),
    dict(t='BNDX', name='Vanguard Total International Bond ETF', issuer='Vanguard',
         index='Bloomberg Global Aggregate ex-USD (hedged)', since=2013, cls='bond',
         focus='international bonds',
         idea='Investment-grade bonds from outside the United States, with the currency risk hedged away.',
         strategy='Holds non-US investment-grade debt, mostly European and Japanese government '
                  'bonds, and hedges the currency exposure back to dollars. The hedging is the '
                  'point: unhedged foreign bonds are mostly a currency bet, and hedging turns this '
                  'into a genuine diversifier against US interest rates.',
         ucits=dict(name='A EUR-hedged global aggregate bond UCITS ETF')),
    dict(t='GLD', name='SPDR Gold Shares', issuer='State Street', index='Gold bullion',
         since=2004, cls='commodity', focus='gold',
         idea='Physical gold, held in a London vault, divided into shares.',
         strategy='Each share represents a fraction of an ounce of gold held in allocated storage. '
                  'There is no income and no earnings — the return is the gold price minus the '
                  'storage cost, which is deducted by selling a small amount of gold each year, so '
                  'the gold per share slowly declines. Tax treatment in the US differs from shares, '
                  'which matters for taxable accounts.',
         ucits=dict(ticker='SGLN / IGLN', name='iShares Physical Gold ETC',
                    note='European equivalents are exchange-traded commodities, not UCITS funds.')),
    dict(t='IAU', name='iShares Gold Trust', issuer='BlackRock', index='Gold bullion', since=2005,
         cls='commodity', focus='gold',
         idea='The same physical gold as GLD, at a lower annual cost.',
         strategy='Identical in substance to GLD — allocated physical gold, no income, cost '
                  'deducted in metal — but charges less, which compounds into a meaningful '
                  'difference over a decade. GLD retains more trading volume and a deeper options '
                  'market.',
         ucits=dict(ticker='SGLN / IGLN', name='iShares Physical Gold ETC')),
    dict(t='IBIT', name='iShares Bitcoin Trust', issuer='BlackRock', index='Bitcoin', since=2024,
         cls='crypto', focus='bitcoin',
         idea='Bitcoin held by a custodian, bought and sold like a share.',
         strategy='Holds bitcoin directly with an institutional custodian, so the share price '
                  'tracks the bitcoin price less the fee. It removes the need to manage private '
                  'keys or use a crypto exchange, which is the entire reason it gathered assets '
                  'faster than any ETF launch in history. The underlying asset produces no cash '
                  'flow, so there is nothing to value it against.',
         ucits=dict(name='European investors use exchange-traded products rather than UCITS funds',
                    note='UCITS rules do not permit a single-asset crypto fund.')),
]

BY = {e['t']: e for e in ETFS}
TICKERS = [e['t'] for e in ETFS]

assert len(ETFS) == 50, len(ETFS)
assert len(BY) == 50, 'duplicate ticker in the list'

if __name__ == '__main__':
    import collections
    print(len(ETFS), 'ETFs')
    for k, v in sorted(collections.Counter(e['focus'] for e in ETFS).items(), key=lambda x: -x[1]):
        print('  %-28s %d' % (k, v))
    print('with a named UCITS ticker:', sum(1 for e in ETFS if e['ucits'].get('ticker')))
