# Smart AI Job-Shop Scheduler for SMEs

An AI-powered job-shop scheduling optimization tool designed for Small and Medium Enterprises (SMEs). This application helps optimize task allocation and machine utilization using constraint programming and AI techniques.

## Features

- 📊 Job-shop scheduling optimization using Google OR-Tools
- 📈 Interactive visualization of schedules via Gantt charts
- 📉 Machine utilization analysis
- 📁 CSV-based job data input
- 🎯 Priority-based scheduling suggestions
- 💻 User-friendly Streamlit interface

## Project Structure

```
.
├── data/               # Sample and user CSV files
├── scheduler/          # Core scheduling logic
├── app/               # Streamlit application
├── visualization/     # Plotting and charting utilities
├── requirements.txt   # Project dependencies
└── README.md         # Project documentation
```

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Streamlit app:
   ```bash
   streamlit run app/app.py
   ```
2. Upload your job data CSV file
3. Click "Run Optimizer" to generate the optimal schedule
4. View the results in the interactive dashboard

## CSV Format

The input CSV should follow this structure:
| JobID | TaskID | MachineID | Duration |
|-------|--------|-----------|----------|
| 1     | 1      | M1        | 3        |
| 1     | 2      | M2        | 2        |
| 2     | 1      | M2        | 4        |

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License 