# Climate Change Dashboard - Tableau Instructions

## Overview
This document provides step-by-step instructions for creating an interactive Climate Change Analysis dashboard in Tableau.

## Prerequisites
- Tableau Desktop (version 2021.1 or later recommended)
- Climate dataset: `climate_sample.csv`

## Data Connection

### 1. Connect to Data
1. Launch Tableau Desktop
2. Click "Connect" → "To a File" → "Text file"
3. Navigate to `/data/sample/climate_sample.csv`
4. Click "Open"

### 2. Data Source Configuration
- Data Interpreter: Enable if needed
- Field Types:
  - year: Number (whole) - Convert to Date if needed
  - global_temp_anomaly: Number (decimal)
  - co2_ppm: Number (decimal)
  - methane_ppb: Number (decimal)
  - sea_level_mm: Number (decimal)

### 3. Create Calculated Fields

#### Decade
```
INT([year] / 10) * 10
```

#### Normalized Temperature
```
([global_temp_anomaly] - WINDOW_MIN([global_temp_anomaly])) / 
(WINDOW_MAX([global_temp_anomaly]) - WINDOW_MIN([global_temp_anomaly]))
```

#### Normalized CO₂
```
([co2_ppm] - WINDOW_MIN([co2_ppm])) / 
(WINDOW_MAX([co2_ppm]) - WINDOW_MIN([co2_ppm]))
```

#### Temperature Change (Year-over-Year)
```
[global_temp_anomaly] - LOOKUP([global_temp_anomaly], -1)
```

#### CO₂ Growth Rate
```
[co2_ppm] - LOOKUP([co2_ppm], -1)
```

#### Trend Line Equation (for Temperature)
```
TREND_LINE([global_temp_anomaly], [year])
```

## Dashboard Design

### Dashboard 1: Executive Overview (1920x1080)

#### Layout Grid: 4 Rows x 4 Columns

#### Row 1: KPI Cards

**Card 1: Current Temperature**
- Worksheet Name: "Current Temp KPI"
- Calculation: `MAX([global_temp_anomaly])`
- Format: Number (Custom) → +0.00°C
- Color: Red (#FF4444)
- Add title: "Current Temperature Anomaly"

**Card 2: Current CO₂**
- Calculation: `MAX([co2_ppm])`
- Format: 0.0 "ppm"
- Color: Green (#22AA44)
- Title: "Current CO₂ Level"

**Card 3: Sea Level Rise**
- Calculation: `MAX([sea_level_mm])`
- Format: 0 "mm"
- Color: Blue (#0066CC)
- Title: "Total Sea Level Rise"

**Card 4: Warming Rate**
- Calculation: `(MAX([global_temp_anomaly]) - MIN([global_temp_anomaly])) / (MAX([year]) - MIN([year]))`
- Format: +0.0000 "°C/yr"
- Color: Orange (#FF8800)
- Title: "Avg Warming Rate"

#### Row 2-3: Main Trend Charts

**Chart 1: Temperature Anomaly Timeline**
- Type: Line Chart
- Columns: YEAR([year])
- Rows: AVG([global_temp_anomaly])
- Marks:
  - Type: Line + Circle
  - Color: Red (#FF4444)
  - Size: 2
- Analytics:
  - Add Reference Line at 0 (Baseline)
  - Add Trend Line (Show Equation)
- Title: "Global Temperature Anomaly (1924-2023)"
- Axes:
  - X: Year
  - Y: Temperature Anomaly (°C)

**Chart 2: CO₂ Concentration**
- Type: Area Chart
- Columns: YEAR([year])
- Rows: AVG([co2_ppm])
- Marks:
  - Type: Area
  - Color: Green (#22AA44) with 40% transparency
- Title: "Atmospheric CO₂ Concentration"

**Chart 3: Methane Levels**
- Type: Line Chart
- Columns: YEAR([year])
- Rows: AVG([methane_ppb])
- Color: Orange (#FF8800)
- Title: "Atmospheric Methane (CH₄)"

**Chart 4: Sea Level Rise**
- Type: Area Chart
- Columns: YEAR([year])
- Rows: AVG([sea_level_mm])
- Color: Blue (#0066CC)
- Title: "Global Sea Level Rise"

#### Row 4: Combined View

**Multi-Indicator Chart**
- Type: Line Chart
- Columns: YEAR([year])
- Rows: Multiple measures (normalized)
- Measure Names on Color
- Use dual axis if needed
- Title: "Climate Indicators (Normalized)"

### Dashboard 2: Correlation Analysis

#### Correlation Matrix
1. Create calculated field for each correlation pair
2. Use Highlight Table
3. Color: Red-Blue Diverging
4. Center: 0
5. Show values in cells

#### Scatter Plots

**CO₂ vs Temperature**
- Columns: AVG([co2_ppm])
- Rows: AVG([global_temp_anomaly])
- Color: YEAR([year]) - Continuous
- Size: AVG([sea_level_mm])
- Add Trend Line
- Title: "CO₂ Impact on Temperature"

**Methane vs Temperature**
- Columns: AVG([methane_ppb])
- Rows: AVG([global_temp_anomaly])
- Color: YEAR([year])
- Add Trend Line

### Dashboard 3: Decade Comparison

**Decade Bar Chart**
- Columns: [Decade]
- Rows: Multiple measures
- Measure Names on Color
- Sorted by decade
- Title: "Climate Change by Decade"

**Decade Table**
- Show summary statistics for each decade
- Columns: All indicators
- Rows: Decade
- Number format: 2 decimal places

### Dashboard 4: Forecast & Projections

**Temperature Forecast**
1. Create line chart with historical data
2. Analytics → Forecast
3. Settings:
   - Forecast: 30 periods
   - Model: Automatic
   - Show prediction interval: 95%
4. Color: Blue for forecast, Red for actual

**CO₂ Projection**
- Same configuration as temperature
- Green color scheme

## Formatting & Design

### Color Palette
Create custom palette:
- Name: "Climate Change"
- Colors:
  ```
  Temperature: #FF4444
  CO2: #22AA44
  Methane: #FF8800
  Sea Level: #0066CC
  Neutral: #888888
  Background: #F5F5F5
  ```

### Fonts
- Titles: Tableau Bold, 16pt
- Subtitles: Tableau Regular, 12pt
- Body: Tableau Light, 10pt
- KPIs: Tableau Bold, 32pt

### Dashboard Background
- Color: #FFFFFF or #F8F9FA
- Border: None
- Padding: 10px

## Interactivity

### Filters
Add to all dashboards:
1. **Year Range Filter**
   - Type: Range Slider
   - Show: Start and End values
   - Position: Top of dashboard

2. **Decade Filter**
   - Type: Single Value (dropdown)
   - Include "All"
   - Position: Top right

### Actions
1. **Highlight Action**
   - Source: Any chart
   - Target: All charts
   - Trigger: Hover
   - Clear: On menu

2. **Filter Action**
   - Source: Decade chart
   - Target: Detail charts
   - Trigger: Select

3. **URL Action**
   - Link to data sources
   - Link to methodology

### Tooltips
Custom tooltip showing:
- Year
- All indicator values
- Year-over-year change
- Mini trend line (last 10 years)

## Dashboard Navigation

### Create Story
1. Story Point 1: Overview
2. Story Point 2: Temperature Focus
3. Story Point 3: Greenhouse Gases
4. Story Point 4: Sea Level
5. Story Point 5: Correlations
6. Story Point 6: Forecast

### Navigation Buttons
- Add image objects as buttons
- Use dashboard actions to navigate
- Icons: ←  →  ⌂  ⟲

## Parameters

### Create Parameters
1. **Reference Year**
   - Data type: Integer
   - Current value: 2023
   - Allowable values: Range (1924-2023)

2. **Forecast Period**
   - Data type: Integer
   - Current value: 30
   - Range: 10-50 years

3. **Confidence Level**
   - Data type: Float
   - Current value: 0.95
   - List: 0.90, 0.95, 0.99

## Performance Optimization

### Data Extracts
1. Data → Extract Data
2. Filters: None (use all data)
3. Aggregation: Visible dimensions
4. Refresh: Schedule daily

### Tips
- Use data extracts instead of live connections
- Limit number of marks to < 10,000 per view
- Use fixed LOD calculations when possible
- Hide unused fields

## Publishing

### Tableau Server/Online
1. Server → Publish Workbook
2. Project: Climate Analysis
3. Permissions: Set appropriately
4. Data Source: Embed or publish separately
5. Show sheets as tabs: Checked

### Tableau Public (if applicable)
1. Save to Tableau Public
2. URL: https://public.tableau.com/profile/[username]/climate-dashboard

## Export Options
- **PDF**: File → Print to PDF
- **Image**: Dashboard → Export Image (PNG)
- **PowerPoint**: Dashboard → Export to PowerPoint
- **Crosstab**: Worksheet → Export → Crosstab to Excel

## File Naming
- Workbook: `Climate_Change_Analysis.twbx`
- Extract: `climate_data.hyper`
- Location: `/dashboard/Climate_Change_Analysis.twbx`

## Best Practices
1. Use consistent color scheme across all views
2. Label axes clearly
3. Include data source citations
4. Add last updated timestamp
5. Test on different screen sizes
6. Ensure color accessibility (color blind friendly)

## Maintenance Checklist
- [ ] Update data source monthly
- [ ] Verify calculations quarterly
- [ ] Review performance annually
- [ ] Update forecast parameters as needed
- [ ] Check for Tableau software updates

## Support Resources
- Tableau Help: https://help.tableau.com/
- Tableau Public Gallery: https://public.tableau.com/gallery/
- Climate Data Sources: See main README.md
