
# Pro Analytics 02 Python Starter Repository

> Use this repo to start a professional Python project.

- Additional information: <https://github.com/denisecase/pro-analytics-02>
- Project organization: [STRUCTURE](./STRUCTURE.md)
- Build professional skills:
  - **Environment Management**: Every project in isolation
  - **Code Quality**: Automated checks for fewer bugs
  - **Documentation**: Use modern project documentation tools
  - **Testing**: Prove your code works
  - **Version Control**: Collaborate professionally

---

## WORKFLOW 1. Set Up Your Machine

Proper setup is critical.
Complete each step in the following guide and verify carefully.

- [SET UP MACHINE](./SET_UP_MACHINE.md)

---

## WORKFLOW 2. Set Up Your Project

After verifying your machine is set up, set up a new Python project by copying this template.
Complete each step in the following guide.

- [SET UP PROJECT](./SET_UP_PROJECT.md)

It includes the critical commands to set up your local environment (and activate it):

```shell
uv venv
uv python pin 3.12
uv sync --extra dev --extra docs --upgrade
uv run pre-commit install
uv run python --version
````

**Windows (PowerShell):**

```shell
.\.venv\Scripts\activate
```

**macOS / Linux / WSL:**

```shell
source .venv/bin/activate
```

---

## WORKFLOW 3. Daily Workflow

Please ensure that the prior steps have been verified before continuing.
When working on a project, we open just that project in VS Code.

### 3.1 Git Pull from GitHub

Always start with `git pull` to check for any changes made to the GitHub repo.

```shell
git pull
```

### 3.2 Run Checks as You Work

This mirrors real work where we typically:

1. Update dependencies (for security and compatibility).
2. Clean unused cached packages to free space.
3. Use `git add .` to stage all changes.
4. Run Ruff and fix minor issues.
5. Update pre-commit periodically.
6. Run pre-commit quality checks on all code files (**twice if needed** – the first pass may fix things).
7. Run tests.

In VS Code, open your repository, then open a terminal (**Terminal → New Terminal**) and run the following commands one at a time to check the code.

```shell
uv sync --extra dev --extra docs --upgrade
uv cache clean
git add .
uvx ruff check --fix
uvx pre-commit autoupdate
uv run pre-commit run --all-files
git add .
uv run pytest
```

> NOTE: The second `git add .` ensures any automatic fixes made by Ruff or pre-commit are included before testing or committing.

<details>
<summary>Click to see a note on best practices</summary>

`uvx` runs the latest version of a tool in an isolated cache, outside the virtual environment.
This keeps the project light and simple, but behavior can change when the tool updates.
For fully reproducible results, or when you need to use the local `.venv`, use `uv run` instead.

</details>

### 3.3 Build Project Documentation

Make sure you have current doc dependencies, then build your docs, fix any errors, and serve them locally to test.

```shell
uv run mkdocs build --strict
uv run mkdocs serve
```

* After running the serve command, the local URL of the docs will be provided. To open the site, press **CTRL + click** the provided link (CMD + click on Mac) to view the documentation.
* Press **CTRL + C** (or CMD + C) to stop the hosting process.

### 3.4 Execute

This project includes demo code. Run the demo Python modules to confirm everything is working.

In VS Code terminal, run:

```shell
uv run python -m analytics_project.demo_module_basics
uv run python -m analytics_project.demo_module_languages
uv run python -m analytics_project.demo_module_stats
uv run python -m analytics_project.demo_module_viz
```

You should see:

* Log messages in the terminal
* Greetings in several languages
* Simple statistics
* A chart window open (close the chart window to continue)

If this works, your project is ready! If not, check:

* Are you in the right folder? (All terminal commands are to be run from the root project folder.)
* Did you run the full `uv sync --extra dev --extra docs --upgrade` command?
* Are there any error messages? (Ask for help with the exact error.)

---

### 3.5 Git add-commit-push to GitHub

Anytime we make working changes to code is a good time to `git add-commit-push` to GitHub.

1. Stage your changes with git add.
2. Commit your changes with a useful message in quotes.
3. Push your work to GitHub.

```shell
git add .
git commit -m "describe your change in quotes"
git push -u origin main
```

This will trigger the GitHub Actions workflow and publish your documentation via GitHub Pages.

### 3.6 Modify and Debug

With a working version safe in GitHub, start making changes to the code.

Before starting a new session, remember to do a `git pull` and keep your tools updated.
Each time forward progress is made, remember to `git add-commit-push`.

---

## P2 Notes — Reading Raw Data into DataFrames

* Created `src/analytics_project/data_prep.py` to read raw CSVs into pandas DataFrames.
* Ran the module and logged shapes to `project.log`.

**Command used:**

```powershell
$env:PYTHONPATH="src"; python -m analytics_project.data_prep
```

---

## P4 – Create and Populate Data Warehouse (DW)

### Overview

In P4, I designed and implemented a small star-schema data warehouse for the smart-store project.
The DW is built with SQLite and populated from the prepared CSV files created in earlier modules.

* DW database file: `data/dw/smart_store_dw.db`
* ETL script: `src/analytics_project/dw/etl_to_dw.py`
* Source data:

  * `data/prepared/customers_data_prepared.csv`
  * `data/prepared/products_data_prepared.csv`
  * `data/prepared/sales_data_prepared.csv`

The ETL script:

1. Creates the DW schema (dimension and fact tables).
2. Loads customers, products, and sales from the prepared CSVs.
3. Logs progress and any errors to `project.log`.

---

### Schema Design

I used a **star schema** with:

* **Fact table**

  * `sale` – one row per transaction.
* **Dimension tables**

  * `customer`
  * `product`

#### customer (dimension)

```text
customer_id        INTEGER  PRIMARY KEY
name               TEXT     NOT NULL
region             TEXT
join_date          TEXT     -- ISO 8601 date string
loyalty_points_qty INTEGER
contact_method     TEXT
```

#### product (dimension)

```text
product_id   INTEGER  PRIMARY KEY
product_name TEXT     NOT NULL
category     TEXT
unit_price   REAL
stock_qty    INTEGER
supplier     TEXT
```

#### sale (fact)

```text
sale_id      INTEGER  PRIMARY KEY
customer_id  INTEGER  -- FK to customer.customer_id
product_id   INTEGER  -- FK to product.product_id
store_id     INTEGER
campaign_id  INTEGER
sale_amount  REAL     NOT NULL
discount_pct REAL
payment_type TEXT
sale_date    TEXT     -- ISO 8601 date string

FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
FOREIGN KEY (product_id)  REFERENCES product(product_id)
```

---

### How to Run the ETL and Build the DW

From the project root (`smart-store-lynzie`):

```shell
uv run python -m analytics_project.dw.etl_to_dw
```

This will:

1. Connect to (or create) `data/dw/smart_store_dw.db`.
2. Create the `customer`, `product`, and `sale` tables if they do not exist.
3. Load data from the prepared CSVs into the DW.
4. Log details to `project.log`.

### Verifying the DW

I used the VS Code SQLite extension (`alexcvzz.vscode-sqlite`) to confirm the DW was created and populated.

* Open `smart_store_dw.db` in the SQLite Explorer panel.
* Check that:

  * `customer` has 198 rows (one per customer)
  * `product` has 99 rows
  * `sale` has 1650 rows

### Screenshots

(Replace these image paths with your actual screenshot files.)

* ![Customer table](docs/img/dw_customer_table.png)
* ![Product table](docs/img/dw_product_table.png)
* ![Sale fact table](docs/img/dw_sale_table.png)

### Challenges and Notes

**Column name mismatches**
I had to carefully map CSV headers to DW column names (e.g., `CustomerID` → `customer_id`, `ProductName` → `product_name`).
A couple of early runs failed with key/NOT NULL errors until the mappings were fixed.

**NOT NULL constraints**
The `name` and `product_name` columns are NOT NULL, so the ETL code skips any rows that are missing those values to avoid constraint errors.

**Date handling**
Dates are kept as ISO 8601 strings (`YYYY-MM-DD`) in SQLite for simplicity, which matches the prepared CSVs.

Overall, the DW now supports querying sales by customer, product, region, category, date, and other attributes for future BI and analytics tasks.

---

## P5. Reporting with Power BI

### Operating system and tools

* Operating system: Windows 10
* Reporting tool: Power BI Desktop (connected to my SQLite data warehouse via ODBC using the SQLite3 ODBC driver and a DSN named `SmartSalesDSN`).

### SQL queries and reports

For this phase, I focused on reporting from the warehouse rather than changing the warehouse design.

* I used a custom SQL query in Power BI (`Odbc.Query` with `dsn=SmartSalesDSN`) to create a **Top Customers** dataset that joins `sale` and `customer`, groups by customer name, and calculates `total_spent` using `SUM(sale_amount)`, ordered from highest to lowest.
* In Power BI I built several visuals based on the warehouse tables (`customer`, `product`, `sale`) and the Top Customers query:

  * A **Top Customers bar chart** showing the customers with the highest total spending.
  * A **matrix** showing **product category (rows)** by **customer region (columns)** with **Sum of sale_amount** for dicing across two categorical dimensions.
  * A **time-series chart** using the derived `Year`, `Quarter`, and `Month Name` columns from `sale_date` to support drilldown.
  * A **date slicer** on `sale_date` to filter all visuals by date.

### Screenshots

I captured and committed screenshots to show the key operations:

1. **Model view** – Power BI Model view showing relationships from `sale` to `customer` (on `customer_id`) and from `sale` to `product` (on `product_id`), plus the `Top Customers` query.
2. **Slice** – Report page showing the `sale_date` slicer controlling the visuals.
3. **Dice** – Matrix visual with product `category` on rows, customer `region` on columns, and `Sum of sale_amount` in the cells.
4. **Drilldown** – Line or column chart with a date hierarchy (Year > Quarter > Month Name) and drilldown enabled, along with an example of the drilled level.

```
::contentReference[oaicite:0]{index=0}
```
# P7 Custom BI Project – Blossoms & Bees Lavender Farm

## Section 1. The Business Goal

This custom BI project uses a hypothetical lavender farm, **Blossoms & Bees**, as the business context.
Business question:

**Which products and sales channels generate the most revenue and value per transaction over time, and how could Blossoms & Bees adjust future production and sales strategy?**

This matters because a small farm has limited time, land, and budget. Knowing which “products” and “channels” perform best helps plan what to make more of, where to sell it, and when demand is strongest.

---

## Section 2. Data Source

I used the prepared sales file from earlier modules:

- `data/prepared/sales_data_prepared.csv`

Key fields used:

- `TransactionID` – individual sale
- `ProductID` – represents a lavender product line
- `StoreID` – represents a sales channel (farm stand, market, online, etc.)
- `SaleAmount` – revenue for the transaction

For this project, I generated a synthetic `YearMonth` field in Python to simulate seasonal patterns for Blossoms & Bees.

---

## Section 3. Tools Used

- **Python + pandas** – to load the prepared sales data, engineer a YearMonth field, and aggregate to a summary table.
- **Power BI Desktop** – to build measures, create visualizations, and explore insights.

---

## Section 4. Workflow & Logic

1. **Python data prep**
   - Read `data/prepared/sales_data_prepared.csv` into pandas.
   - Created a fake date sequence (`2024-01-01` forward, every 7 days) to assign a `YearMonth` value to each row for a more realistic seasonal pattern.
   - Grouped by `ProductID`, `StoreID`, and `YearMonth`.
   - Calculated:
     - `total_revenue = sum(SaleAmount)`
     - `transaction_count = count(TransactionID)`
   - Saved the result to `data/analysis/blossoms_bees_summary.csv`.

2. **Power BI model**
   - Loaded `data/analysis/blossoms_bees_summary.csv` as table **BlossomsBeesSummary**.
   - Created measures:
     - `Total Revenue = SUM(BlossomsBeesSummary[total_revenue])`
     - `Transaction Count = SUM(BlossomsBeesSummary[transaction_count])`
     - `Avg Revenue per Transaction = DIVIDE([Total Revenue], [Transaction Count])`.

3. **Visualizations**
   - Built visuals to compare revenue over time by channel and average revenue per transaction by product.

---

## Section 5. Results (narrative + visualizations)

Key visuals:

1. **Stacked column chart – Total Revenue by YearMonth and StoreID**
   - Shows total revenue over time with each StoreID as a different color stack.
   - I interpreted StoreID as different Blossoms & Bees sales channels.

2. **Clustered bar chart – Avg Revenue per Transaction by ProductID**
   - Shows which products generate the highest value per sale.

_Screenshot of the final dashboard would go here in a full report._

Key findings:

- Some channels (e.g., a specific StoreID) consistently generate higher total revenue across many months.
- Certain ProductIDs stand out with much higher average revenue per transaction, acting like “hero” products.
- Revenue varies across months, suggesting that planning around seasonal peaks would be important for a real lavender farm.

---

## Section 6. Suggested Business Action

If these patterns represented the real Blossoms & Bees farm, I would recommend:

- **Prioritize high-value products** (top ProductIDs by average revenue per transaction) in production, marketing, and display space.
- **Focus on the strongest channels** (top StoreIDs by total revenue) when scheduling events, stocking inventory, or planning promotions.
- Use lower-performing products or channels for experiments: bundles, samples, or targeted promotions instead of heavy production.

---

## Section 7. Challenges

- **Python environment / path issues** – I had to use the virtual environment executable directly
  (`.\.venv\Scripts\python.exe`) instead of the plain `python` command.
- **Column naming differences** – the prepared file did not have `order_date` or `product_category`; I adjusted the script to use the actual fields (`SaleDate`, `ProductID`, `StoreID`, `SaleAmount`, `TransactionID`).
- **Date variety** – the original data did not have nice monthly variety for this story, so I created synthetic dates to spread the data across multiple months.

---

## Section 8. Ethical Considerations

For this hypothetical Blossoms & Bees project, I considered several ethical issues. First, if the data represented real customers, it would need to be stored securely and used only for legitimate business purposes (no unnecessary sharing or selling of personal information). Second, the analysis could reinforce bias if I treated one “channel” or customer group as more valuable without checking whether all customers have equal opportunity to buy. Third, the results are based on a limited snapshot of transactions and a simplified model, so I would avoid making major production or staffing decisions without validating the data and checking for missing or bad records. Finally, I used AI (ChatGPT) to help design the analysis and code, but the business is still responsible for reviewing the logic, validating results, and not blindly automating decisions without human judgment.
