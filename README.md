\# Water Leakage and Loss Analyzer



A Python and Oracle Database application for recording leakage incidents, calculating water loss, identifying recurring locations, and supporting maintenance decisions.



\## Overview



Water leakage causes water wastage and increases maintenance costs. This project records leakage incidents, calculates estimated water loss, and generates reports to help identify locations that need attention.



\## Features



\- Record water leakage incidents.

\- Calculate leakage duration and estimated water loss.

\- Classify incidents by priority.

\- Analyze water loss by location.

\- Identify recurring leakage locations.

\- Display high-priority incidents.

\- Generate maintenance recommendations.

\- Store and retrieve records using Oracle Database.

\- Validate user input and handle overnight repair times.



\## Technology Stack



\- Python

\- Oracle Database

\- SQL

\- python-oracledb



\## Project Structure



```text

Water-Leakage-Analyzer/

├── README.md

├── database.sql

└── console/

&#x20;   ├── water\_leakage\_pro.py

&#x20;   ├── requirements.txt

&#x20;   └── .gitignore

```



\## Prerequisites



\- Python 3.10 or later

\- Oracle Database

\- An Oracle database user with the required permissions

\- The python-oracledb Python package



\## Installation and Setup



\### 1. Clone the repository



Replace `YOUR\_USERNAME` with your GitHub username.



```bash

git clone https://github.com/YOUR\_USERNAME/water-leakage-analyzer-console.git

cd water-leakage-analyzer-console

```



\### 2. Install dependencies



```bash

python -m pip install -r console/requirements.txt

```



\### 3. Create the database table



Connect to the appropriate Oracle database schema and execute the `database.sql` script.



This creates the `leakage\_records` table used by the application.



\### 4. Configure the database connection



The application uses these connection settings:



\- Username: `water\_user`

\- Database service: `localhost:1521/FREEPDB1`



Ensure the database service is running and the database user has the required permissions.



The application prompts for the database password when it starts. Never publish database passwords or other secrets.



\### 5. Run the application



```bash

python console/water\_leakage\_pro.py

```



Use the interactive menu to add leakage incidents, view analysis reports, or exit.



\## Database Schema



The `leakage\_records` table contains:



| Column | Description |

|---|---|

| incident\_id | Unique incident identifier |

| location | Leakage location |

| leak\_start | Leakage start timestamp |

| repair\_time | Repair completion timestamp |

| duration\_hours | Calculated leakage duration |

| loss\_rate | Estimated leakage rate in liters per hour |

| water\_loss | Estimated water loss in liters |

| leak\_type | Type of leakage |

| priority | Incident priority |



\## Available Reports



1\. View all leakage records

2\. Analyze water loss by location

3\. Identify recurring leakage locations

4\. View high-priority incidents

5\. Review maintenance recommendations



\## Water Loss Calculation



Water loss is estimated using:



\*\*Water Loss (liters) = Duration (hours) x Leakage Rate (liters/hour)\*\*



For example, a leak lasting 5 hours at 200 liters per hour results in an estimated loss of 1,000 liters.



\## Security



\- Do not commit passwords or credentials.

\- Use a dedicated database account with appropriate permissions.

\- Keep local backups and private data out of the public repository.

\- Review all files before pushing them to GitHub.



\## Future Improvements



\- Add a web dashboard with charts and filters.

\- Visualize leakage locations on a map.

\- Analyze monthly water-loss trends.

\- Use Oracle sequences for safer concurrent incident ID generation.

\- Add alerts for recurring and high-priority incidents.



\## Author



\*\*Hasini Mekala\*\*



B.Tech, Computer Science and Engineering



GitHub: \[@hasinimekala-22](https://github.com/hasinimekala-22)



\---



Academic project focused on water-loss analysis and maintenance decision support.



