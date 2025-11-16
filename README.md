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
```

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
4. Run ruff and fix minor issues.
5. Update pre-commit periodically.
6. Run pre-commit quality checks on all code files (**twice if needed**, the first pass may fix things).
7. Run tests.

In VS Code, open your repository, then open a terminal (Terminal / New Terminal) and run the following commands one at a time to check the code.

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

NOTE: The second `git add .` ensures any automatic fixes made by Ruff or pre-commit are included before testing or committing.

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

- After running the serve command, the local URL of the docs will be provided. To open the site, press **CTRL and click** the provided link (at the same time) to view the documentation. On a Mac, use **CMD and click**.
- Press **CTRL c** (at the same time) to stop the hosting process.

### 3.4 Execute

This project includes demo code.
Run the demo Python modules to confirm everything is working.

In VS Code terminal, run:

```shell
uv run python -m analytics_project.demo_module_basics
uv run python -m analytics_project.demo_module_languages
uv run python -m analytics_project.demo_module_stats
uv run python -m analytics_project.demo_module_viz
```

You should see:

- Log messages in the terminal
- Greetings in several languages
- Simple statistics
- A chart window open (close the chart window to continue).

If this works, your project is ready! If not, check:

- Are you in the right folder? (All terminal commands are to be run from the root project folder.)
- Did you run the full `uv sync --extra dev --extra docs --upgrade` command?
- Are there any error messages? (ask for help with the exact error)

---

### 3.5 Git add-commit-push to GitHub

Anytime we make working changes to code is a good time to git add-commit-push to GitHub.

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

Each time forward progress is made, remember to git add-commit-push.

## 4. P2 Notes — Reading raw data into DataFrames

- Created `src/analytics_project/data_prep.py` to read raw CSVs into pandas DataFrames.
- Ran the module and logged shapes to `project.log`.

**Command used**
```powershell
$env:PYTHONPATH="src"; python -m analytics_project.data_prep

## P4 – Create and Populate Data Warehouse (DW)

### Overview

In P4, I designed and implemented a small star-schema data warehouse for the smart-store project.
The DW is built with SQLite and populated from the prepared CSV files created in earlier modules.

- DW database file: `data/dw/smart_store_dw.db`
- ETL script: `src/analytics_project/dw/etl_to_dw.py`
- Source data:
  - `data/prepared/customers_data_prepared.csv`
  - `data/prepared/products_data_prepared.csv`
  - `data/prepared/sales_data_prepared.csv`

The ETL script:
1. Creates the DW schema (dimension and fact tables).
2. Loads customers, products, and sales from the prepared CSVs.
3. Logs progress and any errors to `project.log`.

---

### Schema Design

I used a **star schema** with:

- **Fact table**
  - `sale` – one row per transaction.

- **Dimension tables**
  - `customer`
  - `product`

#### customer (dimension)

```text
customer_id        INTEGER  PRIMARY KEY
name               TEXT     NOT NULL
region             TEXT
join_date          TEXT     -- ISO 8601 date string
loyalty_points_qty INTEGER
contact_method     TEXT

#### product (dimension)

```text
product_id   INTEGER  PRIMARY KEY
product_name TEXT     NOT NULL
category     TEXT
unit_price   REAL
stock_qty    INTEGER
supplier     TEXT

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

How to Run the ETL and Build the DW

From the project root (smart-store-lynzie):

uv run python -m analytics_project.dw.etl_to_dw


This will:

Connect (or create) data/dw/smart_store_dw.db

Create the customer, product, and sale tables if they do not exist

Load data from the prepared CSVs into the DW

Log details to project.log

Verifying the DW

I used the VS Code SQLite extension (alexcvzz.vscode-sqlite) to confirm the DW was created and populated.

Open smart_store_dw.db in the SQLite Explorer panel.

Check that:

customer has 198 rows (one per customer)

product has 99 rows

sale has 1650 rows

Screenshots

(Replace these image paths with your actual screenshot files.)

![Customer table](docs/img/dw_customer_table.png)
![Product table](docs/img/dw_product_table.png)
![Sale fact table](docs/img/dw_sale_table.png)

Challenges and Notes

Column name mismatches
I had to carefully map CSV headers to DW column names (e.g., CustomerID → customer_id, ProductName → product_name).
A couple of early runs failed with key/NOT NULL errors until the mappings were fixed.

NOT NULL constraints
The name and product_name columns are NOT NULL, so the ETL code skips any rows that are missing those values to avoid constraint errors.

Date handling
Dates are kept as ISO 8601 strings (YYYY-MM-DD) in SQLite for simplicity, which matches the prepared CSVs.

Overall, the DW now supports querying sales by customer, product, region, category, date, and other attributes for future BI and analytics tasks.
