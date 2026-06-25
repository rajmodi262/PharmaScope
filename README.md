<div align="center">

# 🧬 EconoScope · Pharma Intelligence
### *Live biopharma pipeline & competitive intelligence — type any drug or indication, get the analyst brief.*

<br>

[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Framer Motion](https://img.shields.io/badge/Framer_Motion-anim-0055FF?style=for-the-badge&logo=framer&logoColor=white)](https://www.framer.com/motion/)
[![Live Data](https://img.shields.io/badge/Data-ClinicalTrials.gov_%2B_openFDA-22d3ee?style=for-the-badge)](https://clinicaltrials.gov)

<br>

> Search a molecule or indication → EconoScope queries **ClinicalTrials.gov** and
> **openFDA** *live*, then structures the result into a competitive pipeline,
> sponsor leaderboard, regulatory profile, real-world safety signals, and an
> auto-generated **Insights / Opportunities / Threats** analyst brief.
>
> **Real data. No mock-ups.** Try `semaglutide` (736 trials, Novo Nordisk leads),
> `pembrolizumab` (11,500+ trials), or `obesity`.

<br>

</div>

---

## 🚀 Quickstart (full-stack)

**One click (Windows):** double-click **`start.bat`** — it frees ports 8900/5180,
installs backend + frontend dependencies, launches both servers, and opens the app
in your browser. `stop.bat` shuts it down.

<details><summary>Or run the two services manually</summary>

```bash
# 1 — Backend (FastAPI · live pharma APIs, no keys needed)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --port 8900

# 2 — Frontend (React + Vite + Tailwind + Framer Motion)
cd frontend
npm install
npm run dev          # → http://localhost:5180  (proxies /api to :8900)
```

</details>

## 🏗️ Architecture

```
React + TS + Tailwind + Framer Motion        FastAPI (async httpx)            Live public APIs
┌─────────────────────────────────┐   REST   ┌──────────────────────────┐    ┌──────────────────┐
│ search-driven dashboard          │ ───────> │ GET /api/intelligence    │ ─> │ ClinicalTrials.gov│
│ stat cards · pipeline · sponsors │ <─────── │ • concurrent asyncio.gather│ <─ │ openFDA (label +  │
│ momentum · safety · analyst brief│          │ • Pydantic-typed contract │    │   FAERS events)   │
│ animated, exportable brief       │          │ • 12h disk cache + fallback│    └──────────────────┘
└─────────────────────────────────┘          └──────────────────────────┘
```

**Engineering highlights:** concurrent live API calls (`asyncio.gather`), a single
Pydantic-typed response contract mirrored by the TypeScript client, a 12-hour disk
cache with **stale-fallback so a flaky upstream never blanks the screen**, and a
deterministic rule-based synthesis layer (no LLM dependency → demo-safe). The
analyst brief and trial data export to Markdown / CSV for hand-off.

> The original **Streamlit analytics console** (GDP ML forecasting + modelled
> pharma market sizing & patent-cliff analysis) remains in `app.py` as a secondary
> module — see below.

---

---

## 💊 Life-Sciences Commercial Analytics  *(flagship module)*

The first tab of the app — `pharma_analytics.py` — is a **US biopharma commercial-analytics
console** modelled on the work of a life-sciences analytics consultant:

| Capability | What it does |
|------------|--------------|
| 📈 **Market sizing & forecasting** | US net-sales trajectory 2019→2030 with a ±12% uncertainty band, per therapy area |
| ⏳ **Patent-cliff / LOE modelling** | Year-by-year sales-at-risk from loss of exclusivity, with distinct **generic vs biosimilar** erosion curves |
| 🏁 **Competitive landscape** | Share-vs-growth bubble map and company-level share table |
| 🌳 **Therapy-area treemap** | 2024 market value by area & brand, coloured by growth |
| 🚀 **Launch analog forecaster** | Bass-diffusion uptake to peak + patent-cliff erosion + **risk-adjusted NPV** for a pipeline asset — the core launch deliverable, fully interactive |
| 📝 **Auto-generated consulting brief** | Data-driven **Insights · Opportunities · Threats**, with one-click **CSV + Markdown export** for hand-off |

> ⚡ **Performance:** heavy artifacts (incl. a ~94MB Random Forest) and the pharma dataset are
> cached with `@st.cache_resource` / `@st.cache_data`, so they load once per session — widget
> interactions stay instant.

> Covers 18 leading brands — Keytruda, Ozempic, Dupixent, Mounjaro, Skyrizi, Eliquis, Biktarvy,
> Trikafta, Humira & more — across Oncology, Immunology, Cardiometabolic (incl. GLP-1),
> Infectious Disease, Rare Disease & Vaccines.
> **FY2024 net sales are actuals from company annual reports / 10-Ks;** prior-year history, forward
> forecast and LOE/erosion assumptions are modelled. Swap `build_market()` for an IQVIA / Evaluate
> feed for US-specific audited figures and the pipeline is production-ready.

**Why it maps to commercial life-sciences analytics roles:** *deep dive into datasets · extract
key insights, opportunities and threats · advanced analysis in the Life Sciences / Pharma domain ·
build visually rich, engaging analytical tools* — Python, pandas, Plotly, ML.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Project Architecture](#-project-architecture)
- [Dataset](#-dataset)
- [ML Pipeline](#-ml-pipeline)
- [Models Trained](#-models-trained)
- [Feature Selection](#-feature-selection)
- [Streamlit App](#-streamlit-app)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Technologies Used](#-technologies-used)
- [Future Improvements](#-future-improvements)

---

## 🧠 Overview

The **Global GDP Predictor** is an end-to-end machine learning project that leverages **World Bank Development Indicators** to forecast a country's **GDP (current US$)**. It covers the full data science lifecycle — from raw data ingestion and advanced imputation, to multi-model training and an interactive real-time dashboard.

The system trains **10 regression models** and serves predictions via a beautifully styled **Streamlit web app**, allowing users to tweak 25 economic indicators per country and instantly compare forecasts across all models.

---

## ✨ Features

- 🌐 **Global Coverage** — Predict GDP for any country in the World Bank dataset  
- 🤖 **10 ML Models** — From Linear Regression to XGBoost and Neural Networks  
- 🔬 **Smart Imputation** — 5-group hybrid imputation strategy for missing data  
- 📊 **4-Method Feature Selection** — Correlation + Mutual Info + RF Importance + RFE  
- 🎛️ **25 Selected Indicators** — Economically meaningful features for prediction  
- 💰 **Auto-Scale Results** — `log(1+GDP)` predictions auto-converted to real USD  
- 🆚 **Baseline Comparison** — Instantly see % change from country's latest real data  
- 🎨 **Glassmorphism UI** — Dark-theme Streamlit app with modern card design  

---

## 🏗️ Project Architecture

```
Raw World Bank CSV
        │
        ▼
┌──────────────────────────────┐
│      Data Preprocessing      │  ← data_preprocessing.ipynb
│  • Reshape Wide → Long → Wide│
│  • Missing data analysis     │
│  • 5-Group hybrid imputation │
│  • Hybrid scaling pipeline   │
│  • 4-Method feature selection│
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Model Training         │  ← 10 models saved as .pkl
│  • 80/20 train-test split    │
│  • log(1+GDP) target variable│
│  • Metrics saved to CSV      │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Streamlit App          │  ← app.py
│  • Load all .pkl artifacts   │
│  • Country + indicator grid  │
│  • Multi-model predictions   │
│  • Interactive metric charts │
└──────────────────────────────┘
```

---

## 📦 Dataset

| Property | Details |
|----------|---------|
| **Source** | [World Bank – World Development Indicators](https://databank.worldbank.org/source/world-development-indicators) |
| **File** | `World_data_GDP.csv` (1.39 MB) |
| **Format** | Wide CSV → reshaped Long → pivoted Wide for modeling |
| **Coverage** | Multiple countries × multiple years |
| **Target Variable** | `GDP (current US$)` |

### 📋 Indicator Categories

| Category | Examples |
|----------|---------|
| 🏦 **Economic** | GDP growth %, Inflation, Real interest rate, Exchange rate |
| 🚢 **Trade & External** | Exports, Imports, Current account balance, FDI net inflows |
| 🏛️ **Fiscal** | Govt. consumption, Gross capital formation, Gross savings % |
| 🏭 **Sectoral** | Agriculture, Industry, and Services value added |
| 👥 **Social** | Life expectancy, School enrollment GPI, Literacy rate |
| 🌆 **Demographics** | Total population, Urban population, Labor force participation |
| 💻 **Infrastructure** | Internet usage %, Mobile subscriptions, Energy consumption |
| 💳 **Debt & Reserves** | External debt stocks, Total reserves including gold |

---

## 🔄 ML Pipeline

### Stage 1 — Data Loading & Reshaping
```
Wide CSV  →  Melt to Long  →  Add Indicator Units  →  Pivot to Wide
```

### Stage 2 — Missing Data Analysis & Pruning
- Visualize missing % per column **before** and **after** pruning
- Drop columns with **> 50%** missing values
- Drop rows with **> 50%** missing values

### Stage 3 — Group-Wise Hybrid Imputation

| Group | Behavior | Best Method | Example Indicators |
|-------|----------|-------------|-------------------|
| **① Smooth Trend** | Gradual monotonic growth | Linear Interpolation | GDP, Population, Urban population |
| **② Volatile %** | Bounded, year-to-year jumps | Country Median + Iterative RF | Inflation, GDP growth %, Unemployment |
| **③ Cross-Country** | Correlated across similar economies | KNN Imputer (k=5) | Exports, Imports, Reserves, FDI |
| **④ Structurally Linked** | Mathematically related (GDP = C+I+G) | Iterative RF Imputer | Consumption, Govt spending, Capital formation |
| **⑤ Social / Demographic** | Slow-changing index values | Simple Median Imputer | Internet %, School enrollment, Energy use |

### Stage 4 — Hybrid Scaling Pipeline

| Scaler | Applied To |
|--------|-----------|
| **PowerTransformer** | Large magnitudes: GDP, Trade, Debt values |
| **StandardScaler** | Percentage & rate indicators |
| **MinMaxScaler** | Social and demographic indices |
| **RobustScaler** | Volatile financial indicators |

### Stage 5 — Feature Selection

Four methods combined to select the most impactful features:

```
① Correlation Filter      (country-aware mean correlation with GDP)
         +
② Mutual Information      (non-linear relationship scoring)
         +
③ RF Feature Importance   (model-based non-linear importance)
         +
④ RFE                     (Recursive Feature Elimination)
         ║
         ▼
    25 Final Selected Features
```

---

## 🤖 Models Trained

All models saved as `.pkl` files in `models/` directory.

| # | Model | File | Type |
|---|-------|------|------|
| 1 | Linear Regression | `Linear_Regression.pkl` | Linear |
| 2 | Ridge Regression | `Ridge_Regression.pkl` | Regularized Linear |
| 3 | LASSO | `LASSO.pkl` | Sparse Linear |
| 4 | Decision Tree | `Decision_Tree.pkl` | Tree-based |
| 5 | Random Forest | `Random_Forest.pkl` | Ensemble Bagging |
| 6 | K-Nearest Neighbors | `K-Nearest_Neighbors.pkl` | Instance-based |
| 7 | Support Vector Regression | `Support_Vector_Regression.pkl` | Kernel-based |
| 8 | Gradient Boosting | `Gradient_Boosting.pkl` | Sequential Boosting |
| 9 | LightGBM | `LightGBM.pkl` | Fast Gradient Boosting |
| 10 | XGBoost | `XGBoost.pkl` | Extreme Gradient Boosting |
| 11 | Neural Network MLP | `Neural_Network_MLP.pkl` | Deep Learning |

> 💡 **Target Transform:** All models trained on `log(1 + GDP)` for numerical stability. The app automatically applies `expm1()` to convert back to real USD.

### Saved Artifacts

| Artifact | Purpose |
|----------|---------|
| `best_model.pkl` | Top-performing model by metric |
| `encoder.pkl` | OneHotEncoder for Country Name |
| `scaling_pipeline.pkl` | Full hybrid scaler object |
| `df_imputed.pkl` | Preprocessed reference dataset |
| `X_columns.pkl` | Column index for prediction alignment |
| `log_target_flag.pkl` | Boolean — was log transform applied? |
| `model_metrics.csv` | R², RMSE, MAE for all models |

---

## 🎛️ Streamlit App

### Tab 1 — 🎯 Prediction Dashboard
- Select any **country** from the dropdown
- Auto-fills all **25 indicator fields** from the country's latest data
- Adjust any value to simulate economic scenarios
- Click **🚀 Run Prediction Models** — all 10 models predict instantly
- See 🥇🥈🥉 Top 3 predictions as metric cards
- View **% change from baseline** in a highlighted callout

### Tab 2 — 📈 Model Performance
- Horizontal bar charts for **R² score** and **RMSE (Billion USD)**
- Full sortable metrics table with R², RMSE, MAE
- Summary metrics: Best R² model, Lowest RMSE model, Average R²

### Tab 3 — ⚙️ System Information
- Count of models loaded, countries, total features, selected features
- Artifact health check (encoder, scaler, log flag status)
- Full list of 25 selected economic features

---

## ⚙️ Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/gdp-predictor.git
cd gdp-predictor
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

### Step 1 — Train the Models
Run the preprocessing and training notebook first:
```bash
jupyter notebook data_preprocessing.ipynb
```
> This creates the `models/` directory with all `.pkl` files.

### Step 2 — Launch the App
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501` 🎉

---

## 📁 Project Structure

```
GDP-Predictor/
│
├── 📓 data_preprocessing.ipynb              # Full ML pipeline notebook
├── 🖥️  app.py                               # Streamlit web application
├── 📋 requirements.txt                      # Python dependencies
├── 🔒 .gitignore
├── 📊 __GDP.xlsx                            # Supplementary GDP data
│
├── 📂 P_Data_Extract_From_World_Development_Indicators/
│   └── World_data_GDP.csv                   # Raw World Bank dataset (1.39 MB)
│
└── 📂 models/                               # Auto-generated after training
    ├── best_model.pkl
    ├── Linear_Regression.pkl
    ├── Ridge_Regression.pkl
    ├── LASSO.pkl
    ├── Decision_Tree.pkl
    ├── Random_Forest.pkl
    ├── K-Nearest_Neighbors.pkl
    ├── Support_Vector_Regression.pkl
    ├── Gradient_Boosting.pkl
    ├── LightGBM.pkl
    ├── XGBoost.pkl
    ├── Neural_Network_MLP.pkl
    ├── encoder.pkl
    ├── scaling_pipeline.pkl
    ├── df_imputed.pkl
    ├── X_columns.pkl
    ├── log_target_flag.pkl
    └── model_metrics.csv
```

---

## 🛠️ Technologies Used

| Library | Purpose |
|---------|---------|
| `pandas` | Data manipulation, reshaping, merging |
| `numpy` | Numerical operations, log transforms |
| `scikit-learn` | Models, imputers, scalers, feature selection |
| `xgboost` | XGBoost regression |
| `lightgbm` | LightGBM regression |
| `matplotlib` | Static charts and model plots |
| `seaborn` | Statistical visualization |
| `scipy` | Statistical utilities |
| `streamlit` | Interactive web dashboard |
| `joblib` | Model serialization / pickle |
| `jinja2` | HTML template support |
| `ipykernel` | Jupyter notebook execution |

---

## 🔮 Future Improvements

- [ ] Add LSTM / Prophet for **time-series GDP trajectory** forecasting
- [ ] Include **SHAP values** for per-feature explainability
- [ ] Enable **multi-country comparison** view on a world map
- [ ] Deploy on **Streamlit Cloud** or **Hugging Face Spaces**
- [ ] Add confidence intervals / prediction uncertainty bands
- [ ] Extend dataset to World Bank **2024 / 2025** updates
- [ ] Add scenario presets (e.g., "Recession Scenario", "High Growth")

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- **Data:** [World Bank — World Development Indicators](https://databank.worldbank.org)
- **Imputation strategy** inspired by domain-aware ML preprocessing best practices
- **Streamlit** for the elegant, fast dashboard framework

---

<div align="center">

Made with ❤️ using Python & Streamlit

⭐ *Star this repo if you found it useful!*

</div>
