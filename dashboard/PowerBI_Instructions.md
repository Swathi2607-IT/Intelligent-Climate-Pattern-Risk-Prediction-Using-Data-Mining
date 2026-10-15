# Climate Change Dashboard - Power BI Instructions

## Overview
This document provides instructions for creating a comprehensive Climate Change Analysis dashboard in Microsoft Power BI.

## Prerequisites
- Microsoft Power BI Desktop (latest version)
- Climate dataset: `climate_sample.csv` or `climate_processed_latest.csv`

## Data Model Setup

### 1. Import Data
1. Open Power BI Desktop
2. Click "Get Data" → "Text/CSV"
3. Navigate to `/data/sample/climate_sample.csv`
4. Click "Load"

### 2. Create Date Table (DAX)
```DAX
DateTable = 
ADDCOLUMNS(
    CALENDAR(
        DATE(1924, 1, 1),
        DATE(2053, 12, 31)
    ),
    "Year", YEAR([Date]),
    "Decade", ROUNDDOWN(YEAR([Date]), -1)
)
```

### 3. Create Calculated Measures

#### Temperature Metrics
```DAX
Avg_Temperature = AVERAGE(climate_sample[global_temp_anomaly])

Max_Temperature = MAX(climate_sample[global_temp_anomaly])

Min_Temperature = MIN(climate_sample[global_temp_anomaly])

Temp_Change_Rate = 
VAR FirstYear = CALCULATE(AVERAGE(climate_sample[global_temp_anomaly]), climate_sample[year] = 1924)
VAR LastYear = CALCULATE(AVERAGE(climate_sample[global_temp_anomaly]), climate_sample[year] = 2023)
RETURN (LastYear - FirstYear) / 99
```

#### CO₂ Metrics
```DAX
Avg_CO2 = AVERAGE(climate_sample[co2_ppm])

CO2_Growth_Rate = 
VAR FirstYear = CALCULATE(AVERAGE(climate_sample[co2_ppm]), climate_sample[year] = 1924)
VAR LastYear = CALCULATE(AVERAGE(climate_sample[co2_ppm]), climate_sample[year] = 2023)
RETURN (LastYear - FirstYear) / 99

Current_CO2 = CALCULATE(AVERAGE(climate_sample[co2_ppm]), climate_sample[year] = MAX(climate_sample[year]))
```

#### Sea Level Metrics
```DAX
Current_Sea_Level = CALCULATE(AVERAGE(climate_sample[sea_level_mm]), climate_sample[year] = MAX(climate_sample[year]))

Sea_Level_Rise_Total = MAX(climate_sample[sea_level_mm]) - MIN(climate_sample[sea_level_mm])
```

#### Methane Metrics
```DAX
Avg_Methane = AVERAGE(climate_sample[methane_ppb])

Methane_Growth = MAX(climate_sample[methane_ppb]) - MIN(climate_sample[methane_ppb])
```

## Dashboard Layout

### Page 1: Executive Overview

#### KPI Cards (Top Row)
1. **Current Temperature Anomaly**
   - Visual: Card
   - Field: Last temperature value
   - Format: +X.XX°C
   - Background: Red gradient

2. **Current CO₂ Level**
   - Visual: Card
   - Field: Current_CO2
   - Format: XXX.X ppm
   - Background: Green gradient

3. **Sea Level Rise**
   - Visual: Card
   - Field: Sea_Level_Rise_Total
   - Format: XXX mm
   - Background: Blue gradient

4. **Temperature Change Rate**
   - Visual: Card
   - Field: Temp_Change_Rate
   - Format: +X.XXXX°C/year
   - Background: Orange gradient

#### Main Visuals
1. **Temperature Trend Line Chart**
   - X-axis: year
   - Y-axis: global_temp_anomaly
   - Add trend line
   - Color: Red
   - Add zero reference line

2. **CO₂ Concentration Area Chart**
   - X-axis: year
   - Y-axis: co2_ppm
   - Fill: Green with transparency
   - Show data labels for recent years

3. **Multi-Line Chart: All Indicators (Normalized)**
   - X-axis: year
   - Y-axes: Normalized values of all 4 indicators
   - Different colors for each line
   - Legend on right

### Page 2: Detailed Analysis

#### Correlation Matrix
1. Create measures for correlations between all variables
2. Use Matrix visual
3. Conditional formatting: Color scale (red to blue)

#### Scatter Plots
1. **CO₂ vs Temperature**
   - X-axis: co2_ppm
   - Y-axis: global_temp_anomaly
   - Play axis: year
   - Size: sea_level_mm

2. **Methane vs Temperature**
   - X-axis: methane_ppb
   - Y-axis: global_temp_anomaly

#### Decade Comparison
1. Use clustered column chart
2. X-axis: decade
3. Y-axis: Average values
4. Multiple series: All indicators

### Page 3: Forecasting

#### Historical + Forecast Line Chart
1. Create forecast using Power BI's built-in forecasting
2. Settings:
   - Forecast length: 30 years
   - Confidence interval: 95%
   - Seasonality: Auto

#### Projection Tables
1. Show projected values for 2030, 2040, 2050
2. Include confidence intervals

## Color Scheme
- Temperature: #FF4444 (Red)
- CO₂: #22AA44 (Green)
- Methane: #FF8800 (Orange)
- Sea Level: #0066CC (Blue)
- Background: #F5F5F5 (Light gray)
- Text: #333333 (Dark gray)

## Filters and Slicers

### Global Filters
1. **Year Slicer** (Range slider)
   - Min: 1924
   - Max: 2023
   - Default: All years

2. **Decade Slicer** (Dropdown)
   - Options: 1920s, 1930s, ..., 2020s

3. **Data Source** (for future multi-source data)

## Publishing

### Steps to Publish
1. File → Publish → Publish to Power BI
2. Select workspace
3. Open in Power BI Service
4. Pin visuals to dashboard
5. Set up automatic refresh (if using live data)

### Refresh Schedule
- Frequency: Daily at 6:00 AM
- Data source: Update path if using processed data

## Export Options
1. **PDF Report**: File → Export to PDF
2. **PowerPoint**: File → Export to PowerPoint
3. **Web Publishing**: Publish → Embed in web

## Advanced Features

### Bookmarks
Create bookmarks for:
1. Overview view
2. Temperature focus
3. CO₂ focus
4. Comparison view

### Drill-Through
1. Create drill-through page for year details
2. Show all indicators for selected year
3. Compare to previous/next year

### Tooltips
Custom tooltip pages showing:
- Year-over-year change
- Decade comparison
- Statistical details

## File Naming
- Save as: `Climate_Change_Dashboard.pbix`
- Location: `/dashboard/Climate_Change_Dashboard.pbix`

## Maintenance
- Update data source monthly
- Review calculated measures quarterly
- Update forecast parameters annually

## Support Resources
- Power BI Documentation: https://docs.microsoft.com/power-bi/
- DAX Reference: https://dax.guide/
- Climate Data Sources: See main README.md
