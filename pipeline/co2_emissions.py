def get_co2_emissions(geodf, co2_rates):
    co2 = co2_rates.loc[geodf.iloc[0]['country'].capitalize(),'co2/kWh']
    geodf['co2/a'] = geodf['kWh/a'] * co2
    geodf['opt_co2'] = geodf['kWh/a'] * min(co2_rates['co2/kWh'])
    geodf['diff'] = geodf['co2/a'] - geodf['opt_co2']
    return geodf
