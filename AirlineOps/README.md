# ✈️ Airline Operations Efficiency Dashboard

An interactive supply chain / operations analytics dashboard built to answer:
**"Which routes, airlines, and airports cause the most operational disruptions — and why?"**

Built as a portfolio project demonstrating end-to-end data engineering and visualization skills using Python, Pandas, and Streamlit.

---

## Key Findings

After analyzing **~1M+ US domestic flights in 2019**:

- **Late aircraft cascades** are the single largest source of delay minutes, accounting for ~38% of total delay time — a systemic ripple effect where one late plane disrupts subsequent flights.
- **Carrier-attributed delays** rank second, suggesting scheduling and crew management are the biggest controllable levers for airlines.
- **Weather delays**, while unpredictable, are responsible for the highest *average* delay duration per incident.
- Certain high-traffic routes (e.g., ORD → EWR, ATL → LAX) show disproportionately high average delays despite being well-staffed, pointing to airport congestion as a root cause.
- **Friday and Thursday** see the highest average arrival delays — likely due to peak travel demand straining ground operations.

---

## Dashboard Features

| Tab | What you can explore |
|-----|----------------------|
| **Delay Causes** | Breakdown of delay minutes by cause (Carrier, Weather, NAS/ATC, Security, Late Aircraft) + cancellation reasons |
| **Carrier Performance** | On-time rate, average delay, and cancellation rate by airline — sortable and color-coded |
| **Routes** | Top N most disruption-prone city-pair routes with average delay and cancellation rate |
| **Airports** | Top 20 departure airports by average departure delay |
| **Time Patterns** | Day-of-week and month-over-month delay trends |

All views respond to **sidebar filters** for airline selection and month range.

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Data wrangling | Python 3.11, Pandas 2.2 |
| Visualization | Plotly Express |
| Dashboard framework | Streamlit 1.41 |
| Dataset | [Airline Delay and Cancellation Data — Kaggle](https://www.kaggle.com/) |

---

## Project Structure

```
AirlineOps/
├── data/
│   └── Flight_delay.csv        # Raw dataset (not committed — see below)
├── src/
│   ├── data_loader.py          # Cached data ingestion
│   └── preprocessing.py        # Cleaning, feature engineering, aggregations
├── app.py                      # Streamlit dashboard entry point
├── requirements.txt
└── README.md
```

---

## Running Locally

```bash
# 1. Clone the repo
git clone https://github.com/your-username/AirlineOps.git
cd AirlineOps

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add the dataset
# Download Flight_delay.csv from Kaggle and place it in data/

# 4. Launch the dashboard
streamlit run app.py
```

The first load takes ~15–20 seconds while Pandas reads the full CSV. Subsequent filter interactions are near-instant thanks to Streamlit's `@st.cache_data`.

---

## Dataset

**Source:** Kaggle — Airline Delay and Cancellation Data  
**Period:** 2019 US domestic flights  
**Size:** ~93 MB / ~1M+ rows, 29 columns  
**Key columns:** `ArrDelay`, `DepDelay`, `Cancelled`, `CancellationCode`, `CarrierDelay`, `WeatherDelay`, `NASDelay`, `LateAircraftDelay`, `UniqueCarrier`, `Origin`, `Dest`

> The raw CSV is excluded from version control (see `.gitignore`). Download it from Kaggle and place it at `data/Flight_delay.csv`.

---

## Design Decisions

- **Caching:** `@st.cache_data` on the data load layer means the 93 MB CSV is parsed only once per session — all filter interactions operate on the in-memory DataFrame.
- **Route filtering:** Routes with fewer than 50 recorded flights are excluded from the route analysis to avoid misleading averages from low-sample-size city pairs.
- **On-time definition:** A flight is "on-time" if it arrives with ≤ 0 minutes of arrival delay AND was not cancelled — matching the FAA/BTS standard definition.
- **Delay cause attribution:** Only applied to flights that actually departed (non-cancelled), since cancelled flights don't accumulate delay minutes.

---

## Skills Demonstrated

- Exploratory data analysis with Pandas (groupby, aggregation, categorical dtypes for memory efficiency)
- Interactive multi-view dashboard design with Streamlit tabs and sidebar filters
- Data storytelling: framing raw delay data as operational insights for business stakeholders
- Clean, modular Python project structure separating data loading, transformation, and presentation layers

---

*Built by [Vince Arguelles](https://github.com/vin-arg) · May 2026*
