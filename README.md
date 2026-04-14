# nepal-dhs-2022-dashboard
An interactive Streamlit dashboard built directly from the Nepal Demographic and Health Survey (NDHS) 2022 microdata. This tool computes and visualises key maternal and child health indicators—ANC visits, facility delivery, child stunting, and fertility—using proper DHS sampling weights and recode standards.

📊 Features
Weighted National Estimates for:

4+ Antenatal Care (ANC) Visits (%)

Facility Delivery (%)

Child Stunting (Height-for-age Z < -2 SD) (%)

Total Fertility (Children Ever Born per Woman)

Provincial Disparities – Bar charts comparing all 7 provinces

Wealth Quintile Analysis – Socioeconomic gradients from poorest to richest

Urban/Rural Breakdown (optional, easily added)

Built-in diagnostic expander to verify variable availability and data distributions

Fully reproducible with cached data loading for performance

📸 Screenshots
(Add screenshots of the Overview tab and a provincial chart here)

https://screenshots/overview.png
https://screenshots/province_chart.png

🧠 Methodology
All indicators follow DHS Program standard definitions:

Indicator	DHS Variable	Definition
4+ ANC Visits	m14 (KR)	≥4 visits for most recent live birth in last 5 years
Facility Delivery	m15 (KR)	Delivery in public (21–26) or private (31–36) facility
Child Stunting	hc70/hc72	Height-for-age Z-score < -2 SD (scaled by 100)
Fertility (TCEB)	v201 (IR)	Total children ever born to women 15–49
Weights: v005 / 1,000,000 applied to all percentages and means.

Most recent birth: Identified using midx (DHS‑8) or bidx (DHS‑7).

Missing values: Codes 98/99 are excluded from numerator and denominator.

🚀 Getting Started
Prerequisites
Python 3.8+

Required packages:

bash
pip install streamlit pandas numpy plotly pyreadstat
Data Files
Place the following DHS recode files in the project root:

NPIR82FL.dta – Women's Individual Recode

NPKR82FL.dta – Children's Recode

⚠️ Note: These files are not included in this repository. You must request access from the DHS Program.

Run the Dashboard
bash
streamlit run ndhs_dashboard.py
📁 Repository Structure
text
.
├── ndhs_dashboard.py        # Main Streamlit application
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── screenshots/             # Dashboard screenshots
✅ Expected Output (Based on NDHS 2022 Official Report)
Metric	National Value (approx)
4+ ANC Visits	81% – 82%
Facility Delivery	79% – 80%
Child Stunting	24% – 26%
Fertility (TCEB)	2.0 – 2.2 children
Provincial disparities are clearly visible (e.g., Bagmati performs best, Madhesh and Karnali lag on several indicators).

🛠️ Troubleshooting
If the dashboard shows unexpected numbers (e.g., ANC < 50%), open the 🔬 Diagnostic Info expander to inspect:

Number of most recent births (should be ~4,500–5,000)

Distribution of m14 and m15 – if mostly 99, the most-recent-birth filter may need adjustment (try midx instead of bidx).

📜 License
This project is for educational and research purposes. The NDHS 2022 microdata is property of the DHS Program and should be cited appropriately.

 Citation:

Ministry of Health and Population, Nepal; New ERA; and ICF. 2023. Nepal Demographic and Health Survey 2022. Kathmandu, Nepal: Ministry of Health and Population, Nepal.

🙏 Acknowledgements
The DHS Program for providing access to the microdata.

Built with Streamlit, Plotly, and Pyreadstat.

👤 Author
Prabhat Kumar Sardar
