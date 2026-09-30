# B2B Lead Generator (Directory Scraper)

A CLI Python tool that queries the **Google Places API (New)** to extract local business leads directly into structured CSV files.

## Objectives

- Extracts **Business Name**, **Phone Number**, and **Website URL**.
- Automates exports into individual files inside a `/leads` directory.

## Critical Constraints & Quotas

- **Daily API Limit:** Capped strictly at **165 queries per day** inside `config.py` to remain entirely within Google's free usage tier (\$0 billing).
- **Usage Logging:** Tracks API calls across separate executions using a local `api_usage_log.json` file. It automatically resets based on the **SAST (GMT+2)** timezone.
- **Email Placeholder:** The `email` field currently returns `"N/A"`. Website crawling logic is not yet implemented.

## Directory Structure

```text
.
├── api_usage_log.json      # Tracks daily API call totals
├── config.py               # Houses the MAX_QUERIES_PER_DAY limit
├── leads/                  # Output folder for generated CSV files
├── main.py                 # Script entry point (Run this)
├── requirements.txt        # Third-party dependencies
└── scraper.py              # Core API and file writing logic
```

## How to Set Up & Run

### 1. Configure the Environment

Rename `.example.env` file to `.env` in the root directory and insert your key:

```env
GOOGLE_PLACES_API_KEY=your_actual_google_places_api_key
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Scraper

```bash
python main.py
```

Type your query when prompted (e.g., `plumbers pretoria`). The tool automatically formats the name and writes the output directly to `leads/plumbers-pretoria.csv`.
