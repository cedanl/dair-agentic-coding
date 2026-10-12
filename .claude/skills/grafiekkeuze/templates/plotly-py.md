# plotly.py-snippets per uitkomst

Python-gebruik (notebook / Streamlit / FastAPI). `import plotly.graph_objects as go`
(en `import plotly.express as px` waar handig). Toon met `fig.show()`, of in Streamlit met
`st.plotly_chart(fig, use_container_width=True)`. Vervang placeholderdata door echte cijfers.

## Enkel getal
```python
import plotly.graph_objects as go
fig = go.Figure(go.Indicator(mode="number", value=72, number={"suffix": "%"}))
```

## Enkel getal geschaald (gauge t.o.v. norm/maximum)
```python
fig = go.Figure(go.Indicator(
    mode="gauge+number", value=72, number={"suffix": "%"},
    gauge={"axis": {"range": [0, 100]},
           "threshold": {"value": 80, "line": {"color": "red", "width": 3}}}))  # threshold = norm
```

## Cirkeldiagram (deel-van-geheel, één periode)
```python
fig = go.Figure(go.Pie(labels=["A", "B", "C"], values=[45, 35, 20]))  # hole=0.4 voor donut
```

## Lijndiagram (trend in tijd)
```python
fig = go.Figure(go.Scatter(x=["2020", "2021", "2022", "2023"], y=[120, 135, 150, 168],
                           mode="lines+markers"))
fig.update_layout(xaxis_title="Jaar", yaxis_title="Aantal")
```

## Kolomdiagram (verticaal — vergelijken op tijd-/getalas)
```python
fig = go.Figure(go.Bar(x=["2020", "2021", "2022"], y=[120, 135, 150]))
fig.update_layout(yaxis_title="Aantal")
```

## Staafdiagram (horizontaal — vergelijken van categorieën)
```python
inst, score = ["Inst. A", "Inst. B", "Inst. C"], [7.2, 6.8, 8.1]
paren = sorted(zip(score, inst))                       # sorteren = beter leesbaar
fig = go.Figure(go.Bar(x=[s for s, _ in paren], y=[i for _, i in paren], orientation="h"))
fig.update_layout(xaxis_title="Score")
```

## Gestapelde staafdiagram (deel-van-geheel over categorieën, absoluut)
```python
cats = ["Opl. A", "Opl. B", "Opl. C"]
fig = go.Figure([
    go.Bar(name="Vmbo", y=cats, x=[40, 30, 50], orientation="h"),
    go.Bar(name="Havo", y=cats, x=[25, 35, 20], orientation="h"),
    go.Bar(name="Mbo",  y=cats, x=[15, 20, 18], orientation="h"),
])
fig.update_layout(barmode="stack")
```

## 100% gestapelde staafdiagram (categorieën, procentueel aandeel)
```python
cats = ["Opl. A", "Opl. B", "Opl. C"]
reeksen = {"Vmbo": [40, 30, 50], "Havo": [25, 35, 20], "Mbo": [15, 20, 18]}
totaal = [sum(r[i] for r in reeksen.values()) for i in range(len(cats))]
fig = go.Figure([
    go.Bar(name=naam, y=cats, orientation="h",
           x=[100 * v / totaal[i] for i, v in enumerate(r)],
           customdata=r, hovertemplate="%{y} – " + naam + ": %{x:.1f}% (%{customdata})<extra></extra>")
    for naam, r in reeksen.items()
])
fig.update_layout(barmode="stack", xaxis=dict(ticksuffix="%", range=[0, 100]))
```

## Gestapelde kolomdiagram (deel-van-geheel over tijd, absoluut)
```python
jaren = ["2020", "2021", "2022", "2023"]
fig = go.Figure([
    go.Bar(name="Vmbo", x=jaren, y=[40, 42, 45, 48]),
    go.Bar(name="Havo", x=jaren, y=[25, 27, 26, 30]),
    go.Bar(name="Mbo",  x=jaren, y=[15, 16, 18, 17]),
])
fig.update_layout(barmode="stack", xaxis_title="Cohort")
```

## 100% gestapelde kolomdiagram (over tijd, procentueel aandeel)
```python
jaren = ["2020", "2021", "2022", "2023"]
reeksen = {"Vmbo": [40, 42, 45, 48], "Havo": [25, 27, 26, 30], "Mbo": [15, 16, 18, 17]}
totaal = [sum(r[i] for r in reeksen.values()) for i in range(len(jaren))]
fig = go.Figure([
    go.Bar(name=naam, x=jaren,
           y=[100 * v / totaal[i] for i, v in enumerate(r)],
           customdata=r, hovertemplate="%{x} – " + naam + ": %{y:.1f}% (%{customdata})<extra></extra>")
    for naam, r in reeksen.items()
])
fig.update_layout(barmode="stack", yaxis=dict(ticksuffix="%", range=[0, 100]), xaxis_title="Cohort")
```

## Correlatie-analyse (scatter)
```python
fig = go.Figure(go.Scatter(x=[3.1, 4.0, 5.2, 6.1, 7.4], y=[120, 150, 165, 180, 210],
                           mode="markers", marker=dict(size=10)))
fig.update_layout(xaxis_title="Variabele X", yaxis_title="Variabele Y")
```

## Lijst / tabel
```python
fig = go.Figure(go.Table(
    header=dict(values=["Instelling", "Score"], fill_color="#e8eef5", align="left"),
    cells=dict(values=[["Inst. A", "Inst. B", "Inst. C"], [7.2, 6.8, 8.1]], align="left"),
))
```
