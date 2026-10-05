from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI(title="Skin Clinic Campaign Analysis API")

# Load the dataset
df = pd.read_csv("skin clinic campaign.csv")

# ---------- Analysis Functions ----------

def gender_response():
    table = df.groupby("Gender")["Response_to_Campaign"].apply(
        lambda x: (x == "Yes").mean() * 100
    ).round(2).reset_index()
    table.columns = ["Gender", "Response Rate (%)"]
    return table


def age_response():
    table = df.groupby("AgeGroup")["Response_to_Campaign"].apply(
        lambda x: (x == "Yes").mean() * 100
    ).round(2).reset_index()
    table.columns = ["Age Group", "Response Rate (%)"]
    # Order the age groups
    order = ["<30", "30-50", ">50"]
    table["Age Group"] = pd.Categorical(table["Age Group"], categories=order, ordered=True)
    table = table.sort_values("Age Group").reset_index(drop=True)
    return table


def purchase_response():
    table = df.groupby("Purchase_Last_Quarter")["Response_to_Campaign"].apply(
        lambda x: (x == "Yes").mean() * 100
    ).round(2).reset_index()
    table.columns = ["Purchase Last Quarter", "Response Rate (%)"]
    return table


def product_usage_response():
    def categorize(n):
        if 1 <= n <= 4:
            return "1-4"
        elif 5 <= n <= 8:
            return "5-8"
        else:
            return ">8"

    df["Product_Category"] = df["Unique_Products_Purchased"].apply(categorize)
    table = df.groupby("Product_Category")["Response_to_Campaign"].apply(
        lambda x: (x == "Yes").mean() * 100
    ).round(2).reset_index()
    table.columns = ["Product Usage Category", "Response Rate (%)"]
    order = ["1-4", "5-8", ">8"]
    table["Product Usage Category"] = pd.Categorical(
        table["Product Usage Category"], categories=order, ordered=True
    )
    table = table.sort_values("Product Usage Category").reset_index(drop=True)
    return table


# ---------- FastAPI Endpoint ----------

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head><title>Skin Clinic Campaign Analysis</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>Skin Clinic Campaign Analysis API</h1>
            <p>Go to <a href="/campaign-analysis">/campaign-analysis</a> to view the results.</p>
        </body>
    </html>
    """


@app.get("/campaign-analysis", response_class=HTMLResponse)
def campaign_analysis():
    gender_tbl = gender_response()
    age_tbl = age_response()
    purchase_tbl = purchase_response()
    product_tbl = product_usage_response()

    html = """
    <html>
    <head>
        <title>Campaign Analysis</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background: #f7f9fc; }
            h1 { color: #2c3e50; }
            h2 { color: #34495e; margin-top: 30px; }
            table { border-collapse: collapse; width: 60%; margin-bottom: 20px; background: #fff; }
            th, td { border: 1px solid #ccc; padding: 10px; text-align: center; }
            th { background: #2980b9; color: white; }
            tr:nth-child(even) { background: #f2f2f2; }
            .container { max-width: 900px; margin: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Skin Clinic Campaign Analysis</h1>
            <p>Response rates across different customer segments.</p>
    """

    html += "<h2>1. Gender vs Campaign Response</h2>"
    html += gender_tbl.to_html(index=False, border=0)

    html += "<h2>2. Age Group vs Campaign Response</h2>"
    html += age_tbl.to_html(index=False, border=0)

    html += "<h2>3. Purchase in Last Quarter vs Campaign Response</h2>"
    html += purchase_tbl.to_html(index=False, border=0)

    html += "<h2>4. Product Usage vs Campaign Response</h2>"
    html += product_tbl.to_html(index=False, border=0)

    html += """
        </div>
    </body>
    </html>
    """
    return html