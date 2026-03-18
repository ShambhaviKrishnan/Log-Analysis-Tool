# Log Analysis Tool

A Python-based log analysis system that parses and analyzes system log files to detect errors, warnings and patterns. This tool helps in identifying frequent issues and summarizing log data efficiently.

---

## Features

-  Reads and processes log files
-  Counts log levels (ERROR, WARNING, INFO)
-  Detects repeated error messages
-  Extracts timestamps (if available)
-  Identifies most frequent errors
-  Generates a summary report
-  Optional: Saves results to a `report.txt` file

---

##  Tech Stack

- Python
- Regular Expressions (Regex)
- File Handling
- Collections (Dictionary, Counter)

---

##  Project Structure

```
log-analysis-tool/
│── log_analyzer.py
│── sample.log
│── report.txt (generated)
│── README.md
```
---

##  How to Run

1. Clone the repository:
   git clone https://github.com/ShambhaviKrishnan/Log-Analysis-Tool.git

2. Navigate to the project folder:
   cd Log-Analysis-Tool

3. Run the script:
   python log_analyzer.py

4. Enter the path of your log file when prompted.
---

##  Sample Input
```
2026-03-17 10:00:01 INFO User login successful
2026-03-17 10:05:23 ERROR Failed to connect to database
2026-03-17 10:06:45 WARNING Disk space low
2026-03-17 10:07:12 ERROR Failed to connect to database
```

---

##  Sample Output
```
Total Lines: 4
INFO: 1
WARNING: 1
ERROR: 2

Most Frequent Error:
"Failed to connect to database" occurred 2 times
```

---

##  Use Cases

- System monitoring
- Debugging application issues
- Analyzing server logs
- Detecting repeated failures

---

##  Future Enhancements

- Add graphical dashboard (using Streamlit)
- Real-time log monitoring
- Export reports in CSV/JSON format
- Web-based interface

---

##  Author

- Shambhavi Krishnan

---

## ⭐ If you found this useful, consider giving it a star!


