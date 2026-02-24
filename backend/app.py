from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

# -----------------------------
# LOAD DATASET
# -----------------------------
df = pd.read_csv("D:\Data Analysis\Clothing Sales Transactions Dataset\sales-dashboard\data\Clothing Sales Data_UTF.csv")  # make sure file name is correct
df["saleDate"] = pd.to_datetime(df["saleDate"], format="mixed", errors="coerce")

# -----------------------------
# FASTAPI APP
# -----------------------------

app = FastAPI(title="Clothing Sales Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # change to Netlify URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

def extract_month(q: str):
    months = [
        "january","february","march","april","may","june",
        "july","august","september","october","november","december"
    ]
    for m in months:
        if m in q:
            return m
    return None


def extract_category(q: str):
    for cat in df["productCategory"].dropna().unique():
        if cat.lower() in q:
            return cat
    return None


def extract_product(q: str):
    for prod in df["productName"].dropna().unique():
        if prod.lower() in q:
            return prod
    return None

def total_sales_logic(q: str):
    q = q.lower()

    # Start with full dataset
    filtered_df = df.copy()

    # -------------------------
    # Extract filters
    # -------------------------
    month = extract_month(q)
    category = extract_category(q)
    product = extract_product(q)

    # -------------------------
    # Apply filters
    # -------------------------
    if month:
        filtered_df = filtered_df[filtered_df["month"] == month]

    if category:
        filtered_df = filtered_df[
            filtered_df["productCategory"].str.lower() == category.lower()
        ]

    if product:
        filtered_df = filtered_df[
            filtered_df["productName"].str.lower() == product.lower()
        ]

    # -------------------------
    # Calculate sales
    # -------------------------
    sales = filtered_df["totalAmount"].sum()

    if sales == 0 or filtered_df.empty:
        return {
            "answer": "❌ I can't find sales data for your request."
        }

    # -------------------------
    # Build dynamic response
    # -------------------------
    response_parts = []

    if product:
        response_parts.append(product)
    elif category:
        response_parts.append(f"{category} category")
    else:
        response_parts.append("all products")

    if month:
        response_parts.append(f"in {month.title()}")

    response = " ".join(response_parts)

    return {
        "answer": f"🛍️ Total sales for {response} is ₹{sales:,.2f}."
    }

# -----------------------------
# CHAT ENDPOINT
# -----------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    q = req.message.lower()

    # -----------------------------
    # TOTAL SALES
    # -----------------------------
    if "total" in q and ("sales" in q or "revenue" in q or "sale" in q):
        return total_sales_logic(q)

    # -----------------------------
    # TOP CATEGORY
    # -----------------------------
    elif (
        "category" in q and
        any(word in q for word in ["top", "highest", "best", "max"])
    ):
        data = (
            df.groupby("productCategory")["totalAmount"]
              .sum()
              .sort_values(ascending=False)
        )

        return {
            "answer": f"Top category by sales is {data.index[0]} with revenue ₹{data.iloc[0]:,.2f}"
        }

    # -----------------------------
    # TOP PRODUCTS
    # -----------------------------
    elif (
        "product" in q and
        any(word in q for word in ["top", "highest", "best"])
    ):
        data = (
            df.groupby("productName")["totalAmount"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )

        lines = ["🏆 Top 5 Products by Sales:\n"]

        for i, (product, sales) in enumerate(data.items(), start=1):
            lines.append(f"{i}. {product} – ₹{sales:,.2f} \n")

        return {
            "answer": "\n".join(lines)
        }

    # -----------------------------
    # SALES BY CHANNEL
    # -----------------------------
    elif "channel" in q or "online" in q or "store" in q:
        data = (
            df.groupby("salesChannel")["totalAmount"]
              .sum()
        )

        return {
            "answer": "Sales by channel",
            "data": {
                channel: f"₹{amount:,.2f}"
                for channel, amount in data.items()
            }
        }

    # -----------------------------
    # MONTHLY TREND
    # -----------------------------
    elif "monthly" in q or "trend" in q:
        monthly = (
            df.groupby(df["saleDate"].dt.to_period("M"))["totalAmount"]
              .sum()
              .reset_index()
        )
        monthly["saleDate"] = monthly["saleDate"].astype(str)

        return {
            "answer": "Monthly sales trend",
            "data": monthly.to_dict(orient="records")
        }

    # -----------------------------
    # TOP LOCATIONS
    # -----------------------------
    elif "location" in q or "city" in q:
        data = (
            df.groupby("location")["totalAmount"]
              .sum()
              .sort_values(ascending=False)
              .head(5)
        )

        return {
            "answer": "Top locations by sales",
            "data": {
                loc: f"₹{amt:,.2f}"
                for loc, amt in data.items()
            }
        }

    # -----------------------------
    # FALLBACK
    # -----------------------------
    elif any(word in q for word in ["hi", "hello", "hey"]):
        return {
        "answer": "Hi 👋 I’m your sales analytics assistant. You can ask me about sales, products, trends, and performance."
        }

    elif any(word in q for word in ["thanks", "thank you"]):
        return {
        "answer": "You're welcome! 😊 Happy to help."
        }

    elif "help" in q or "what can you do" in q:
        return {
        "answer": (
            "I can help you with:\n"
            "• Top category by sales\n"
            "• Top products\n"
            "• Monthly sales trend\n"
            "• Online vs store sales\n"
            "• Total revenue\n"
            "• Top locations"
        )
        }
    elif any(phrase in q for phrase in [
        "how are you",
        "how r you",
        "how is it going",
        "how was doing",
        "how are things"
        ]):
        return {
        "answer": (
            "I’m doing great 😊 Thanks for asking! "
            "I’m ready to help you analyze sales, products, trends, or performance."
        )
        }
    elif any(phrase in q for phrase in [
        "ok", "okay", "done", "great",
        "cool", "fine", "awesome", "nice"
        ]):
        return {
        "answer": (
            "👍 Got it! What would you like to check next?\n\n"
        )
        }