import csv
import datetime
import os

# CONFIGURATION
# In a real pilot, you would point this to the client's actual file.
DATA_FILE = "sample_data.csv"
REPORT_FILE = "fragility_report.txt"

# ANOMALY THRESHOLDS
CRITICAL_COLUMNS = ["email", "order_total", "shipping_address"]

def scan_data(filename):
    """
    Scans a CSV file for basic data fragility issues:
    - Null/Empty values in critical columns
    - Duplicates
    - Negative values in positive-only fields
    """
    print(f"[{datetime.datetime.now()}] AGENT STARTED: Scanning {filename}...")
    
    issues = []
    row_count = 0
    seen_rows = set()
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader):
                row_count += 1
                row_id = i + 2 # Adjust for header and 0-index
                
                # Check for Duplicates
                row_tuple = tuple(row.values())
                if row_tuple in seen_rows:
                    issues.append(f"Row {row_id}: Duplicate Record detected.")
                seen_rows.add(row_tuple)

                # Check Critical Columns for Nulls
                for col in CRITICAL_COLUMNS:
                    if col in row and not row[col].strip():
                        issues.append(f"Row {row_id}: Critical Data Missing in '{col}'.")
                
                # Check Logic (e.g., Order Total must be positive)
                if "order_total" in row:
                    try:
                        val = float(row["order_total"])
                        if val < 0:
                            issues.append(f"Row {row_id}: Negative Value in 'order_total' (${val}).")
                    except ValueError:
                        issues.append(f"Row {row_id}: Invalid Format in 'order_total' ('{row['order_total']}').")

    except FileNotFoundError:
        return ["CRITICAL ERROR: Data file not found."]

    print(f"[{datetime.datetime.now()}] SCAN COMPLETED: {row_count} rows analyzed.")
    return issues

def generate_report(issues):
    """Generates a text report of the findings."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(REPORT_FILE, "w") as f:
        f.write("==================================================\n")
        f.write(f"LOGICFLOW SYSTEMS: FRAGILITY REPORT\n")
        f.write(f"Generated: {timestamp}\n")
        f.write("==================================================\n\n")
        
        if not issues:
            f.write("STATUS: HEALTHY. No anomalies detected.\n")
        else:
            f.write(f"STATUS: FRAGILE. {len(issues)} anomalies detected.\n")
            f.write(f"ESTIMATED REVENUE RISK: ${len(issues) * 50} (Est. $50 friction/error)\n\n")
            f.write("DETAILED FINDINGS:\n")
            for issue in issues:
                f.write(f"[ALERT] {issue}\n")
                
    print(f"[{datetime.datetime.now()}] REPORT GENERATED: Saved to {REPORT_FILE}")

if __name__ == "__main__":
    # Create a dummy file if it doesn't exist for test purposes
    if not os.path.exists(DATA_FILE):
        print("Creating sample data for demonstration...")
        with open(DATA_FILE, "w", newline='') as f:
            f.write("order_id,email,order_total,shipping_address\n")
            f.write("1001,chuck@example.com,120.50,123 Main St\n")
            f.write("1002,,50.00,456 Oak Ave\n") # Missing email
            f.write("1003,dave@example.com,-20.00,789 Pine St\n") # Negative total
            f.write("1001,chuck@example.com,120.50,123 Main St\n") # Duplicate
    
    found_issues = scan_data(DATA_FILE)
    generate_report(found_issues)
