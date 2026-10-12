# Plotly.js-snippets per uitkomst

Frontend-gebruik. Laad Plotly één keer: `<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>`
en render in een container: `<div id="chart"></div>`. Vervang de placeholderdata door echte cijfers.
Alle voorbeelden gebruiken `{responsive: true}` zodat ze meeschalen in een dashboard.

```js
const cfg = {responsive: true, displayModeBar: false, locale: 'nl'};
```

## Enkel getal
```js
Plotly.newPlot('chart', [{
  type: 'indicator', mode: 'number',
  value: 72, number: {suffix: '%', font: {size: 64}}
}], {margin: {t: 0, b: 0}}, cfg);
```

## Enkel getal geschaald (gauge t.o.v. norm/maximum)
```js
Plotly.newPlot('chart', [{
  type: 'indicator', mode: 'gauge+number', value: 72,
  number: {suffix: '%'},
  gauge: {axis: {range: [0, 100]}, threshold: {value: 80, line: {color: 'red', width: 3}}}
}], {margin: {t: 20, b: 0}}, cfg);   // threshold = norm
```

## Cirkeldiagram (deel-van-geheel, één periode)
```js
Plotly.newPlot('chart', [{
  type: 'pie', labels: ['A', 'B', 'C'], values: [45, 35, 20], hole: 0   // hole>0 = donut
}], {}, cfg);
```

## Lijndiagram (trend in tijd)
```js
Plotly.newPlot('chart', [{
  type: 'scatter', mode: 'lines+markers',
  x: ['2020', '2021', '2022', '2023'], y: [120, 135, 150, 168]
}], {xaxis: {title: 'Jaar'}, yaxis: {title: 'Aantal'}}, cfg);
```

## Kolomdiagram (verticaal — vergelijken op tijd-/getalas)
```js
Plotly.newPlot('chart', [{
  type: 'bar', x: ['2020', '2021', '2022'], y: [120, 135, 150]
}], {yaxis: {title: 'Aantal'}}, cfg);
```

## Staafdiagram (horizontaal — vergelijken van categorieën)
```js
const inst = ['Inst. A', 'Inst. B', 'Inst. C'], score = [7.2, 6.8, 8.1];
const order = score.map((_, i) => i).sort((a, b) => score[a] - score[b]);   // sorteren = beter leesbaar
Plotly.newPlot('chart', [{
  type: 'bar', orientation: 'h',
  x: order.map(i => score[i]), y: order.map(i => inst[i])
}], {xaxis: {title: 'Score'}, margin: {l: 120}}, cfg);
```

## Gestapelde staafdiagram (deel-van-geheel over categorieën, absoluut)
```js
const cats = ['Opl. A', 'Opl. B', 'Opl. C'];
Plotly.newPlot('chart', [
  {type: 'bar', orientation: 'h', name: 'Vmbo', y: cats, x: [40, 30, 50]},
  {type: 'bar', orientation: 'h', name: 'Havo', y: cats, x: [25, 35, 20]},
  {type: 'bar', orientation: 'h', name: 'Mbo',  y: cats, x: [15, 20, 18]}
], {barmode: 'stack', margin: {l: 100}}, cfg);
```

## 100% gestapelde staafdiagram (categorieën, procentueel aandeel)
Normaliseer per categorie naar 100% en toon het absolute getal in de tooltip.
```js
const cats = ['Opl. A', 'Opl. B', 'Opl. C'];
const reeksen = {Vmbo: [40, 30, 50], Havo: [25, 35, 20], Mbo: [15, 20, 18]};
const totaal = cats.map((_, i) => Object.values(reeksen).reduce((s, r) => s + r[i], 0));
const data = Object.entries(reeksen).map(([naam, r]) => ({
  type: 'bar', orientation: 'h', name: naam, y: cats,
  x: r.map((v, i) => 100 * v / totaal[i]),
  customdata: r, hovertemplate: '%{y} – ' + naam + ': %{x:.1f}% (%{customdata})<extra></extra>'
}));
Plotly.newPlot('chart', data, {barmode: 'stack', xaxis: {ticksuffix: '%', range: [0, 100]}, margin: {l: 100}}, cfg);
```

## Gestapelde kolomdiagram (deel-van-geheel over tijd, absoluut)
```js
const jaren = ['2020', '2021', '2022', '2023'];
Plotly.newPlot('chart', [
  {type: 'bar', name: 'Vmbo', x: jaren, y: [40, 42, 45, 48]},
  {type: 'bar', name: 'Havo', x: jaren, y: [25, 27, 26, 30]},
  {type: 'bar', name: 'Mbo',  x: jaren, y: [15, 16, 18, 17]}
], {barmode: 'stack', xaxis: {title: 'Cohort'}}, cfg);
```

## 100% gestapelde kolomdiagram (over tijd, procentueel aandeel)
```js
const jaren = ['2020', '2021', '2022', '2023'];
const reeksen = {Vmbo: [40, 42, 45, 48], Havo: [25, 27, 26, 30], Mbo: [15, 16, 18, 17]};
const totaal = jaren.map((_, i) => Object.values(reeksen).reduce((s, r) => s + r[i], 0));
const data = Object.entries(reeksen).map(([naam, r]) => ({
  type: 'bar', name: naam, x: jaren,
  y: r.map((v, i) => 100 * v / totaal[i]),
  customdata: r, hovertemplate: '%{x} – ' + naam + ': %{y:.1f}% (%{customdata})<extra></extra>'
}));
Plotly.newPlot('chart', data, {barmode: 'stack', yaxis: {ticksuffix: '%', range: [0, 100]}, xaxis: {title: 'Cohort'}}, cfg);
```

## Correlatie-analyse (scatter)
```js
Plotly.newPlot('chart', [{
  type: 'scatter', mode: 'markers',
  x: [3.1, 4.0, 5.2, 6.1, 7.4], y: [120, 150, 165, 180, 210],
  marker: {size: 10}
}], {xaxis: {title: 'Variabele X'}, yaxis: {title: 'Variabele Y'}}, cfg);
```

## Lijst / tabel
```js
Plotly.newPlot('chart', [{
  type: 'table',
  header: {values: ['Instelling', 'Score'], fill: {color: '#e8eef5'}, align: 'left'},
  cells:  {values: [['Inst. A', 'Inst. B', 'Inst. C'], [7.2, 6.8, 8.1]], align: 'left'}
}], {}, cfg);
```
