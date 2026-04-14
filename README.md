# nepal-dhs-2022-dashboard
An interactive Streamlit dashboard built directly from the Nepal Demographic and Health Survey (NDHS) 2022 microdata. This tool computes and visualises key maternal and child health indicators—ANC visits, facility delivery, child stunting, and fertility—using proper DHS sampling weights and recode standards.

## ⚠️ Data Privacy & Demo Mode

This public deployment uses **synthetic sample data** for demonstration purposes. The real NDHS 2022 microdata files are not included in this repository.

To run the dashboard with actual DHS data:
1. Obtain the official datasets from the [DHS Program](https://dhsprogram.com).
2. Place `NPIR82FL.dta` and `NPKR82FL.dta` in the project root.
3. The app will automatically detect and use the real data.

The synthetic data produces results similar to the official NDHS 2022 report but should **not** be used for actual analysis.