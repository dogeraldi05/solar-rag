# Photovoltaic basics (demo corpus)

Short explanatory notes written for this demo. They are general knowledge, not taken from any publication.

## Performance ratio

The performance ratio (PR) compares the energy a photovoltaic plant delivered with the energy it would deliver under ideal conditions for the irradiation it received. A PR of 80 percent means 20 percent of the theoretical energy was lost to temperature, soiling, wiring, inverter conversion, shading and downtime. PR is useful because it removes the effect of weather, so two plants in different climates can be compared.

## Temperature effect

Crystalline silicon modules lose power as they heat up. The temperature coefficient of power is typically around minus 0.3 to minus 0.4 percent per degree Celsius above 25 degrees. On a hot afternoon a module can run 30 degrees above ambient, which costs roughly 10 percent of its nameplate output. Good ventilation behind the modules reduces this loss.

## Soiling

Dust, pollen, bird droppings and agricultural residue reduce the light reaching the cells. Losses build up slowly during dry periods and drop suddenly after heavy rain or cleaning. Soiling is hard to see in daily totals because it looks like a slow drift, so it is usually detected by comparing a plant or an inverter against its own weather-corrected baseline.

## Inverter clipping

When the DC array can produce more power than the inverter can convert, the inverter limits its output. This is called clipping. Designers accept some clipping on purpose by choosing a DC to AC ratio above 1.0, because the extra modules produce more energy in the morning and evening for a small cost. A ratio between 1.1 and 1.4 is common.

## Degradation

Modules lose a small amount of output each year. A typical value is 0.5 percent per year, with a larger drop in the first year caused by light-induced degradation. After 25 years a module is often expected to deliver around 85 percent of its original power. Yearly degradation is best measured on the performance ratio, not on raw energy, which also depends on the weather of each year.

## Net metering and distributed generation

In a net metering scheme, a consumer with a small solar system injects surplus energy into the grid and receives credits that offset later consumption. Rules differ by country: some credit the full retail tariff, others credit only the energy component and charge for grid use separately. Before sizing a system it is important to read the current rule, because it changes the payback time.

## Grid connection and protection

A distributed solar plant must disconnect when the grid goes down, to avoid feeding an isolated section of network. This is called anti-islanding protection. Inverters also monitor voltage and frequency and trip when values leave the allowed window, then reconnect after a waiting time once the grid is stable again.

## What an inverter does

An inverter converts the direct current (DC) produced by the modules into alternating current (AC) at the grid voltage and frequency. It also tracks the maximum power point of the array, monitors the grid, and disconnects when conditions are unsafe. String inverters serve a group of modules, while central inverters serve large plants and microinverters serve a single module.
