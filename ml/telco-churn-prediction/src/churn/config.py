"""Project-wide constants: paths, seeds and feature lists."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "Telco_customer_churn.xlsx"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"

SEED = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

# Business requirement: catch at least this share of customers who will leave.
TARGET_RECALL = 0.80

TARGET_COLUMN = "Churn_Label"

NUMERIC_FEATURES = ["Tenure_Months", "Monthly_Charges", "Total_Charges", "CLTV"]

CATEGORICAL_FEATURES = [
    "Gender",
    "Senior_Citizen",
    "Partner",
    "Dependents",
    "Phone_Service",
    "Multiple_Lines",
    "Internet_Service",
    "Online_Security",
    "Online_Backup",
    "Device_Protection",
    "Tech_Support",
    "Streaming_TV",
    "Streaming_Movies",
    "Contract",
    "Paperless_Billing",
    "Payment_Method",
]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# Columns that must never be used as features:
# - Churn_Label / Churn_Value: the target itself
# - Churn_Score: a ready-made risk score shipped with the dataset
# - Churn_Reason: known only for customers who already left
LEAKY_COLUMNS = ["Churn_Label", "Churn_Value", "Churn_Score", "Churn_Reason"]
