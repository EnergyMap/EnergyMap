from log import log

def get_co2_emissions(geodf, co2_rates):
    log(f'Calculating co2-emissions for country {geodf.loc[geodf.index[0], "country"]}...')
    co2 = co2_rates.loc[geodf.iloc[0]['country'].capitalize(),'co2/kWh']
    geodf['co2(t)/a'] = (geodf['kWh/a'] * co2) / 1000 #dividing for tonnes
    geodf['opt_co2(t)/a'] = (geodf['kWh/a'] * min(co2_rates['co2/kWh']))  /1000
    geodf['diff'] = geodf['opt_co2(t)/a'] - geodf['co2(t)/a']
    return geodf
