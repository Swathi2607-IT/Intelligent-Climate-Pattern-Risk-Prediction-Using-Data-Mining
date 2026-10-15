@echo off
echo ===================================
echo Climate Change Data Analysis
echo ===================================
echo.

echo [1/4] Running Data Transformation...
python pipeline/transformation/data_transformer.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Data transformation failed!
    pause
    exit /b 1
)
echo.

echo [2/4] Training ML Models...
cd pipeline/ml
python climate_ml_models.py
cd ../..
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: ML model training failed!
    pause
    exit /b 1
)
echo.

echo [3/4] Generating Visualizations...
cd visualizations
python climate_visualizer.py
cd ..
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Visualization generation failed!
    pause
    exit /b 1
)
echo.

echo [4/4] Opening Results...
start website/index.html
start visualizations/output/climate_dashboard.html
echo.

echo ===================================
echo Analysis Complete!
echo ===================================
echo.
echo Website: website/index.html
echo Dashboard: visualizations/output/climate_dashboard.html
echo Processed Data: data/processed/
echo ML Models: pipeline/ml/models/
echo.
pause
