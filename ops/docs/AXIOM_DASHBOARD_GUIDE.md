# Axiom Dashboard Guide for photographi (v2)

Use these APL (Axiom Processing Language) queries in your **photographi-mcp** dataset to build your dashboard. 

> [!IMPORTANT]
> **Bracket Notation**: Always use `['field.name']` for metrics containing dots.
> **Chart Rendering**: Run the query first, then click the **Chart** icon in the UI to select the recommended visualization.

---

## 🏗️ 1. Infrastructure & Usage
**Monitor growth and system scale.**

#### 📸 Total Images Processed
*Best for: Single Stat or Area Chart*
```apl
['photographi-mcp']
| where event_type == 'global_state'
| summarize Total = max(total_images_processed) by bin(_time, 1h)
```

#### ⚡ Processing Latency (Avg)
*Best for: Time Series*
```apl
['photographi-mcp']
| where event_type == 'global_state'
| summarize Latency = avg(['performance.avg_processing_time_ms']) by bin(_time, 1h)
```

#### 🛡️ Error Rate
*Best for: Bar Chart or Table*
```apl
['photographi-mcp']
| where event_type == 'distribution' and category == 'error_type'
| summarize Occurrences = max(value) by label
```

---

## 🧪 2. Science & Quality Efficacy
**Understand how well the AI is performing.**

#### 🏆 Qualitative Judgement Distribution
*Best for: Pie Chart*
```apl
['photographi-mcp']
| where event_type == 'distribution' and category == 'judgement'
| summarize max(value) by label
```

#### 📏 Score Trends (Technical vs Aesthetic)
*Best for: Time Series (Multi-line)*
```apl
['photographi-mcp']
| where event_type == 'global_state'
| summarize 
    Technical = avg(['quality_scores.avg_technical']), 
    Aesthetic = avg(['quality_scores.avg_aesthetic'])
  by bin(_time, 1h)
```

---

## 📷 3. Camera & Gear Insights
**See what hardware your users are actually using.**

#### 🥇 Top 10 Cameras
*Best for: Bar Chart*
```apl
['photographi-mcp']
| where event_type == 'distribution' and category == 'camera'
| summarize Samples = max(value) by label
| sort by Samples desc
| take 10
```

#### 🔭 Lens Popularity
*Best for: Horizontal Bar Chart*
```apl
['photographi-mcp']
| where event_type == 'distribution' and category == 'lens'
| summarize Count = max(value) by label
| sort by Count desc
```

#### 📁 File Format Distribution
*Best for: Pie Chart*
```apl
['photographi-mcp']
| where event_type == 'distribution' and category == 'format'
| summarize max(value) by label
```

---

## 🛠️ 4. Feature & Tool Adoption
**Discover which tools are "sticky".**

#### 🔧 Tool Invocation Volume
*Best for: Bar Chart*
```apl
['photographi-mcp']
| where event_type == 'distribution' and category == 'tool'
| summarize max(value) by label
```

#### ✨ AI Feature Adoption
*Best for: Table*
```apl
['photographi-mcp']
| where event_type == 'distribution' and category == 'feature'
| summarize max(value) by label
```

---

## 🌍 5. Environmental Context
**Identify platform-specific distributions.**

#### 🖥️ OS Distribution
*Best for: Pie Chart*
```apl
['photographi-mcp']
| where event_type == 'global_state'
| summarize count() by ['environment.os']
```

#### 🐍 Python Versioning
*Best for: Bar Chart*
```apl
['photographi-mcp']
| where event_type == 'global_state'
| summarize count() by ['environment.python']
```
