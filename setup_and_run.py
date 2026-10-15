#!/usr/bin/env python3
"""
Quick Setup and Run Script for Climate Change Data Analysis Platform
"""
import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def run_command(cmd, description, cwd=None):
    """Run a command and handle errors."""
    print(f"[Running] {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            cwd=cwd,
            capture_output=False,
            text=True
        )
        print(f"[Success] {description} completed\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[Error] {description} failed with code {e.returncode}\n")
        return False

def install_dependencies():
    """Install required Python packages."""
    print_header("Installing Dependencies")
    
    packages = [
        "pandas", "numpy", "scipy", "scikit-learn", 
        "statsmodels", "plotly", "matplotlib", "seaborn", 
        "requests", "jupyter"
    ]
    
    cmd = f"{sys.executable} -m pip install {' '.join(packages)}"
    return run_command(cmd, "Package Installation")

def run_transformation():
    """Run data transformation pipeline."""
    print_header("Data Transformation")
    
    script_path = Path(__file__).parent / "pipeline" / "transformation" / "data_transformer.py"
    cmd = f"{sys.executable} {script_path}"
    return run_command(cmd, "Data Transformation")

def run_ml_models():
    """Train ML models."""
    print_header("Machine Learning Models")
    
    script_path = Path(__file__).parent / "pipeline" / "ml" / "climate_ml_models.py"
    cmd = f"{sys.executable} {script_path}"
    return run_command(cmd, "ML Model Training")

def generate_visualizations():
    """Generate visualizations."""
    print_header("Visualization Generation")
    
    script_path = Path(__file__).parent / "visualizations" / "climate_visualizer.py"
    cmd = f"{sys.executable} {script_path}"
    return run_command(cmd, "Visualization Generation")

def open_results():
    """Open website and dashboard."""
    print_header("Opening Results")
    
    base_dir = Path(__file__).parent
    website_path = base_dir / "website" / "index.html"
    dashboard_path = base_dir / "visualizations" / "output" / "climate_dashboard.html"
    
    try:
        if sys.platform == "win32":
            os.startfile(website_path)
            os.startfile(dashboard_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(website_path)])
            subprocess.run(["open", str(dashboard_path)])
        else:  # Linux
            subprocess.run(["xdg-open", str(website_path)])
            subprocess.run(["xdg-open", str(dashboard_path)])
        
        print("[Success] Opened website and dashboard\n")
        return True
    except Exception as e:
        print(f"[Error] Could not open files: {e}\n")
        return False

def main():
    """Main execution function."""
    print_header("Climate Change Data Analysis Platform")
    print("This script will:")
    print("  1. Install dependencies (if needed)")
    print("  2. Transform climate data")
    print("  3. Train ML models")
    print("  4. Generate visualizations")
    print("  5. Open results in browser\n")
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Aborted.")
        return
    
    # Check if packages are installed
    try:
        import pandas
        import plotly
        print("\n[Info] Dependencies already installed, skipping installation...\n")
    except ImportError:
        if not install_dependencies():
            print("Failed to install dependencies. Please install manually:")
            print("pip install pandas numpy scipy scikit-learn statsmodels plotly matplotlib seaborn requests jupyter")
            return
    
    # Run pipeline
    steps = [
        (run_transformation, "Data Transformation"),
        (run_ml_models, "ML Model Training"),
        (generate_visualizations, "Visualization Generation"),
        (open_results, "Opening Results")
    ]
    
    for i, (func, name) in enumerate(steps, 1):
        print(f"\n[Step {i}/{len(steps)}] {name}")
        if not func():
            print(f"\n[Failed] Pipeline stopped at: {name}")
            return
    
    # Summary
    print_header("Analysis Complete!")
    print("Results:")
    print("  📊 Website: website/index.html")
    print("  📈 Dashboard: visualizations/output/climate_dashboard.html")
    print("  💾 Processed Data: data/processed/")
    print("  🤖 ML Models: pipeline/ml/models/")
    print("\nAll visualizations: visualizations/output/")
    print("\nThank you for using the Climate Change Data Analysis Platform!")

if __name__ == "__main__":
    main()
