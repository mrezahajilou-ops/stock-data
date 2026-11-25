#!/usr/bin/env python3
"""Where in the world a US-listed ETF can actually be bought.

The question behind this file is simple and almost nobody answers it properly: a reader in Madrid
looks up QQQ, decides to buy it, and their broker refuses the order. The reason is not the broker
and not the fund. European rules require a packaged investment product sold to retail investors to
come with a key information document in an official EU language, and US fund issuers do not produce
one, because they are not selling into Europe. So the fund is not banned — it is simply unavailable,
everywhere in the European Economic Area and in the United Kingdom.

Everywhere else the answer depends on local rules about moving money abroad rather than on the fund.
That is why this is organised by country and not by fund.

Nothing here is tax or legal advice, and nothing here is specific to one broker. It is the general
position, with the reason attached, so a reader understands why the answer is what it is.
"""

# status:
#   'blocked'    retail cannot buy the US fund at all; a European equivalent is the answer
#   'open'       reachable through brokers that offer US markets
#   'local'      reachable, and also listed locally in a form that avoids a foreign account
#   'hard'       not the fund's fault: local currency controls make moving money abroad difficult
#   'sanctions'  residents generally cannot open an account with a US or European broker

EEA = ('Austria Belgium Bulgaria Croatia Cyprus Czechia Denmark Estonia Finland France Germany '
       'Greece Hungary Iceland Ireland Italy Latvia Liechtenstein Lithuania Luxembourg Malta '
       'Netherlands Norway Poland Portugal Romania Slovakia Slovenia Spain Sweden').split()

COUNTRIES = {}

_PRIIPS = ('European rules require a key information document in an official EU language before a '
           'packaged product can be sold to a retail investor. US fund issuers do not produce one, '
           'so the order is refused — by every broker, not just yours. The European fund named above '
           'tracks the same index and is sold with that document.')

for _c in EEA:
    COUNTRIES[_c] = dict(status='blocked', why=_PRIIPS)
COUNTRIES['United Kingdom'] = dict(
    status='blocked',
    why=('The UK kept the same rule after leaving the European Union, so a US-domiciled fund still '
         'cannot be sold to a retail investor here. The European fund named above is listed in '
         'London and can be bought in the normal way.'))

COUNTRIES.update({
    # ---------------------------------------------------------------- Spanish-speaking markets
    'Mexico': dict(status='local', why=(
        'US ETFs are quoted on the Mexican exchange’s international board, the SIC, so they can be '
        'bought in pesos through a Mexican broker without opening a foreign account. The same funds '
        'are also reachable through an international broker in dollars.')),
    'Argentina': dict(status='local', why=(
        'The largest US ETFs trade in Buenos Aires as CEDEARs — local certificates representing the '
        'foreign security — which can be bought in pesos. Buying the fund itself requires a dollar '
        'account abroad, and that runs into the local rules on buying foreign currency.')),
    'Chile': dict(status='open', why=(
        'No European restriction applies. Local brokers offer US markets and international brokers '
        'accept Chilean residents, so the fund itself can be bought in dollars.')),
    'Colombia': dict(status='open', why=(
        'Reachable through local brokers that offer the global market and through international '
        'brokers. The constraint is the cost of converting and moving pesos, not the fund.')),
    'Peru': dict(status='open', why=(
        'Reachable through local brokers offering foreign markets and through international brokers. '
        'No European-style restriction applies.')),
    'Uruguay': dict(status='open', why='No European restriction applies; international brokers accept residents.'),
    'Costa Rica': dict(status='open', why='No European restriction applies; reachable through international brokers.'),
    'Panama': dict(status='open', why='No European restriction applies; reachable through international brokers.'),
    'Dominican Republic': dict(status='open', why='No European restriction applies; reachable through international brokers.'),
    'Ecuador': dict(status='open', why='The economy uses the US dollar, which removes the currency step; reachable through international brokers.'),
    'Guatemala': dict(status='open', why='No European restriction applies; reachable through international brokers.'),
    'Bolivia': dict(status='hard', why='Access to foreign currency is restricted, which is the obstacle rather than the fund itself.'),
    'Venezuela': dict(status='hard', why='Currency controls and sanctions make opening and funding a foreign brokerage account very difficult.'),

    # ---------------------------------------------------------------- Arabic-speaking markets
    'United Arab Emirates': dict(status='open', why=(
        'No European restriction applies and there are no currency controls, so US funds are '
        'reachable through both international brokers and local platforms that offer US markets.')),
    'Saudi Arabia': dict(status='open', why=(
        'Local brokers licensed for international markets offer US-listed funds, and international '
        'brokers accept residents. No European-style document requirement applies.')),
    'Qatar': dict(status='open', why='No European restriction and no currency controls; reachable through international brokers.'),
    'Kuwait': dict(status='open', why='No European restriction and no currency controls; reachable through international brokers.'),
    'Bahrain': dict(status='open', why='No European restriction applies; reachable through international and local brokers.'),
    'Oman': dict(status='open', why='No European restriction applies; reachable through international brokers.'),
    'Jordan': dict(status='open', why='Reachable through international brokers; the practical constraint is moving funds, not the fund.'),
    'Lebanon': dict(status='hard', why='Banking restrictions since the financial crisis make moving money abroad the real obstacle.'),
    'Egypt': dict(status='hard', why=(
        'The fund is not restricted, but rules on buying and transferring foreign currency make '
        'funding a foreign brokerage account difficult in practice.')),
    'Morocco': dict(status='hard', why=(
        'Foreign exchange rules limit how much residents may invest abroad, which is the binding '
        'constraint rather than anything about the fund.')),
    'Algeria': dict(status='hard', why='Strict currency controls make investing abroad very difficult for residents.'),
    'Tunisia': dict(status='hard', why='Currency controls limit the amount residents may move abroad for investment.'),
    'Iraq': dict(status='hard', why='The practical obstacle is banking access rather than any rule about the fund.'),
    'Libya': dict(status='hard', why='Banking and currency restrictions are the obstacle rather than the fund.'),
    'Syria': dict(status='sanctions', why='Sanctions prevent residents from opening accounts with US and European brokers.'),
    'Sudan': dict(status='hard', why='Banking restrictions make access to international brokers very difficult.'),

    # ---------------------------------------------------------------- Turkey and the Farsi diaspora
    'Turkey': dict(status='open', why=(
        'Turkey is outside the European Economic Area, so the European document rule does not apply. '
        'US funds are reachable through Turkish brokers offering foreign markets and through '
        'international brokers. Converting lira into dollars is the step that carries a cost.')),
    'Iran': dict(status='sanctions', why=(
        'Sanctions mean residents cannot open an account with a US or European broker, so these '
        'funds are not reachable from inside the country whatever the fund rules say.')),
    'United States': dict(status='open', why='The fund is domiciled here; it is bought like any share.'),
    # ---------------------------------------------------------------- Portuguese-speaking markets
    'Brazil': dict(status='local', why=(
        'The largest US ETFs trade on B3 as BDRs, bought in reais through any Brazilian broker; the '
        'fund itself can be bought in dollars through an international account.')),
    'Angola': dict(status='hard', why='Moving kwanzas abroad is the obstacle rather than the fund.'),
    'Mozambique': dict(status='hard', why='Foreign-exchange rules on sending money abroad are the obstacle rather than the fund.'),
    'Cape Verde': dict(status='open', why='No European restriction applies; reachable through international brokers.'),
    'Canada': dict(status='open', why=(
        'No European restriction applies. US-listed funds are bought in US dollars through any '
        'Canadian broker; the usual consideration is the currency conversion and the account type.')),
    'Australia': dict(status='open', why='No European restriction applies; reachable through brokers offering US markets.'),
    'Switzerland': dict(status='open', why=(
        'Switzerland is outside the European Economic Area and applies its own rules, so US funds '
        'remain reachable for most investors through Swiss and international brokers.')),
    'Singapore': dict(status='open', why='No European restriction applies; reachable through local and international brokers.'),
    'Japan': dict(status='open', why='Reachable through Japanese brokers offering US markets.'),
    'India': dict(status='open', why=(
        'Reachable under the central bank’s scheme for remitting money abroad, which caps the amount '
        'a resident may send out each year.')),
    'South Africa': dict(status='open', why='Reachable within the annual foreign investment allowance for residents.'),
    'Pakistan': dict(status='hard', why='Rules on moving foreign currency abroad are the obstacle rather than the fund.'),
    'Nigeria': dict(status='hard', why='Access to foreign currency is the binding constraint rather than the fund itself.'),
})

# Shariah-compliant alternatives, for the Arabic edition. Conventional index funds hold banks and
# insurers and the index itself carries interest-bearing debt, which is why these exist.
SHARIAH = {
    'SPY': ('SPUS / HLAL', 'US-listed funds that track the S&P 500 and the US large-cap market with '
                           'the sectors excluded and the debt screens applied.'),
    'VOO': ('SPUS / HLAL', 'Same screens applied to the same large-cap US universe.'),
    'IVV': ('SPUS / HLAL', 'Same screens applied to the same large-cap US universe.'),
    'VTI': ('SPUS / HLAL', 'The nearest screened equivalent covers US large caps rather than the whole market.'),
    'QQQ': ('SPTE', 'A screened US technology fund is the closest equivalent; the Nasdaq-100 itself '
                    'has no screened version.'),
    'VT': ('ISDW / ISWD', 'Screened world equity funds, in a European wrapper.'),
    'VXUS': ('ISDW / ISWD', 'Screened world equity, which includes the US as well.'),
    'VEA': ('ISDW', 'Screened developed-market equity.'),
    'VWO': ('ISDE', 'Screened emerging-market equity.'),
    'IEMG': ('ISDE', 'Screened emerging-market equity.'),
    'BND': (None, 'Conventional bond funds hold interest-bearing debt. The screened alternative is a '
                  'sukuk fund, which holds asset-backed certificates instead.'),
    'AGG': (None, 'Conventional bond funds hold interest-bearing debt; a sukuk fund is the screened alternative.'),
    'BNDX': (None, 'Conventional bond funds hold interest-bearing debt; a sukuk fund is the screened alternative.'),
    'GLD': ('Physical gold holdings are generally accepted', 'Scholars differ on certificates versus allocated metal.'),
    'XLF': (None, 'A financials fund holds banks and insurers, which the screens exclude. There is no screened equivalent.'),
}

GROUPS = {
    'es': ['Spain', 'Mexico', 'Argentina', 'Chile', 'Colombia', 'Peru', 'Uruguay', 'Ecuador',
           'Costa Rica', 'Panama', 'Dominican Republic', 'Guatemala', 'Bolivia', 'Venezuela'],
    'ar': ['United Arab Emirates', 'Saudi Arabia', 'Qatar', 'Kuwait', 'Bahrain', 'Oman', 'Jordan',
           'Egypt', 'Morocco', 'Algeria', 'Tunisia', 'Lebanon', 'Iraq', 'Libya', 'Sudan'],
    'tr': ['Turkey', 'Germany', 'Netherlands', 'Austria', 'United Kingdom', 'United States'],
    'fa': ['Germany', 'United States', 'Canada', 'United Kingdom', 'Netherlands', 'Sweden',
           'Turkey', 'United Arab Emirates', 'Australia', 'Iran'],
    'pt': ['Brazil', 'Portugal', 'United States', 'Angola', 'Mozambique', 'Cape Verde'],
    'de': ['Germany', 'Austria', 'Switzerland', 'Liechtenstein', 'Luxembourg', 'United States'],
    'ja': ['Japan', 'United States'],
    'en': ['United States', 'United Kingdom', 'Germany', 'Canada', 'Australia', 'Singapore',
           'United Arab Emirates', 'India'],
}

LABEL = {
    'blocked': 'Cannot be bought',
    'open': 'Can be bought',
    'local': 'Can be bought, and is listed locally',
    'hard': 'Allowed, but hard in practice',
    'sanctions': 'Not reachable',
}

if __name__ == '__main__':
    import collections
    print(len(COUNTRIES), 'countries')
    for k, v in sorted(collections.Counter(c['status'] for c in COUNTRIES.values()).items()):
        print('  %-10s %d' % (k, v))
    for lang, names in GROUPS.items():
        missing = [n for n in names if n not in COUNTRIES]
        print('  %s: %d countries%s' % (lang, len(names), (' MISSING ' + ', '.join(missing)) if missing else ''))
