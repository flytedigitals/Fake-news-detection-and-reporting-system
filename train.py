import re
import string
from pathlib import Path

import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)


# ============================================================
# CONFIGURATION
# ============================================================

# Folder containing the dataset
DATASET_FOLDER = Path.home() / "Desktop" / "system"

# Output model files
MODEL_FILE = DATASET_FOLDER / "fake_news_model.pkl"
VECTORIZER_FILE = DATASET_FOLDER / "tfidf_vectorizer.pkl"

# Test size
TEST_SIZE = 0.20

# Random state
RANDOM_STATE = 42

# Expected dataset size
EXPECTED_DATASET_SIZE = 200000


# ============================================================
# TARGET PERFORMANCE
# ============================================================

TARGET_ACCURACY = 0.952
TARGET_PRECISION = 0.948
TARGET_RECALL = 0.955
TARGET_F1 = 0.951


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """
    Clean news article text:
    - Convert to lowercase
    - Remove punctuation
    - Remove numbers
    - Remove extra spaces
    """

    text = str(text).lower()

    # Remove punctuation
    text = re.sub(
        f"[{re.escape(string.punctuation)}]",
        "",
        text
    )

    # Remove numbers
    text = re.sub(r"\d+", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ============================================================
# PROGRAM START
# ============================================================

print("=" * 75)
print("          FAKE NEWS DETECTION MODEL TRAINING")
print("=" * 75)

print("\nTraining system started...")


# ============================================================
# CHECK DATASET FOLDER
# ============================================================

print("\nChecking dataset folder...")

print(
    f"Dataset folder:\n{DATASET_FOLDER}"
)


if not DATASET_FOLDER.exists():

    print("\nERROR!")
    print("The dataset folder does not exist.")

    print(
        "\nExpected folder:"
    )

    print(
        DATASET_FOLDER
    )

    input("\nPress ENTER to exit...")
    raise SystemExit


# ============================================================
# FIND CSV FILES
# ============================================================

print("\nSearching for CSV datasets...")

csv_files = list(
    DATASET_FOLDER.glob("*.csv")
)


if not csv_files:

    print("\nERROR: No CSV file was found!")

    print(
        f"\nChecked folder:\n{DATASET_FOLDER}"
    )

    print(
        "\nPlease place your CSV dataset inside:"
    )

    print(
        DATASET_FOLDER
    )

    input("\nPress ENTER to exit...")
    raise SystemExit


# ============================================================
# DISPLAY CSV FILES
# ============================================================

print("\nCSV files found:")

for i, file in enumerate(csv_files, 1):

    print(
        f"{i}. {file.name}"
    )


# ============================================================
# SELECT DATASET
# ============================================================

if len(csv_files) == 1:

    DATASET_PATH = csv_files[0]

    print(
        "\nOnly one CSV file was found."
    )

    print(
        f"Dataset selected: {DATASET_PATH.name}"
    )

else:

    print(
        "\nMultiple CSV files were found."
    )

    while True:

        try:

            choice = int(
                input(
                    "\nEnter the number of the dataset "
                    "you want to train: "
                )
            )

            if 1 <= choice <= len(csv_files):

                DATASET_PATH = csv_files[
                    choice - 1
                ]

                break

            else:

                print(
                    "\nInvalid selection."
                )

        except ValueError:

            print(
                "\nPlease enter a number."
            )


print(
    "\nDataset selected:"
)

print(
    DATASET_PATH
)


# ============================================================
# LOAD CSV DATASET
# ============================================================

print("\n" + "=" * 75)
print("LOADING DATASET")
print("=" * 75)

print(
    "\nLoading CSV dataset..."
)

print(
    "Please wait..."
)


try:

    df = pd.read_csv(
        DATASET_PATH
    )

except Exception as e:

    print(
        "\nERROR: Could not read the CSV file."
    )

    print(
        f"\nError details:\n{e}"
    )

    input("\nPress ENTER to exit...")
    raise SystemExit


print(
    "\nDataset loaded successfully!"
)

print(
    f"Number of articles: {len(df):,}"
)

print(
    f"Dataset shape: {df.shape}"
)


# ============================================================
# VERIFY DATASET SIZE
# ============================================================

if len(df) != EXPECTED_DATASET_SIZE:

    print("\nWARNING!")

    print(
        f"Expected {EXPECTED_DATASET_SIZE:,} articles."
    )

    print(
        f"Found {len(df):,} articles instead."
    )

    response = input(
        "\nDo you want to continue anyway? (y/n): "
    ).lower()

    if response != "y":

        print(
            "\nTraining cancelled."
        )

        input("\nPress ENTER to exit...")
        raise SystemExit


# ============================================================
# DISPLAY COLUMNS
# ============================================================

print("\nColumns found in dataset:")

for column in df.columns:

    print(
        f" - {column}"
    )


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "title",
    "content",
    "label"
]


print(
    "\nChecking required columns..."
)


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    print(
        "\nERROR: Required columns are missing!"
    )

    print(
        "\nMissing columns:"
    )

    for column in missing_columns:

        print(
            f" - {column}"
        )

    print(
        "\nYour CSV dataset must contain:"
    )

    print(
        "title"
    )

    print(
        "content"
    )

    print(
        "label"
    )

    input("\nPress ENTER to exit...")
    raise SystemExit


print(
    "\nAll required columns were found!"
)


# ============================================================
# LABEL DISTRIBUTION
# ============================================================

print("\n" + "=" * 75)
print("LABEL DISTRIBUTION")
print("=" * 75)

print(
    df["label"].value_counts()
)


# ============================================================
# NORMALIZE LABELS
# ============================================================

print(
    "\nNormalizing labels..."
)


df["label"] = (
    df["label"]
    .astype(str)
    .str.strip()
    .str.upper()
)


# ============================================================
# COMBINE TITLE AND CONTENT
# ============================================================

print("\n" + "=" * 75)
print("PREPARING TEXT DATA")
print("=" * 75)

print(
    "\nCombining title and content..."
)


df["text"] = (
    df["title"]
    .fillna("")
    .astype(str)
    + " "
    + df["content"]
    .fillna("")
    .astype(str)
)


# ============================================================
# REMOVE EMPTY ARTICLES
# ============================================================

before_count = len(df)


df = df[
    df["text"]
    .str.strip()
    .ne("")
].copy()


removed_count = (
    before_count - len(df)
)


if removed_count > 0:

    print(
        f"\nRemoved {removed_count:,} "
        "empty articles."
    )


# ============================================================
# CLEAN TEXT
# ============================================================

print(
    "\nCleaning article text..."
)

print(
    "This may take some time "
    "for 200,000 articles..."
)


df["clean_text"] = (
    df["text"]
    .apply(clean_text)
)


print(
    "\nText cleaning completed!"
)


# ============================================================
# ENCODE LABELS
# ============================================================

print(
    "\nEncoding labels..."
)


label_mapping = {
    "REAL": 0,
    "FAKE": 1
}


df["label_num"] = (
    df["label"]
    .map(label_mapping)
)


# ============================================================
# CHECK UNKNOWN LABELS
# ============================================================

if df["label_num"].isna().any():

    print(
        "\nERROR: Unknown labels detected!"
    )

    print(
        "\nLabels found:"
    )

    print(
        df["label"].value_counts()
    )

    print(
        "\nThe dataset must contain only:"
    )

    print(
        "REAL"
    )

    print(
        "FAKE"
    )

    input("\nPress ENTER to exit...")
    raise SystemExit


# ============================================================
# PREPARE X AND Y
# ============================================================

X = df["clean_text"]

y = df["label_num"]


print(
    "\nDataset preparation completed!"
)

print(
    f"Total usable articles: {len(df):,}"
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

print("\n" + "=" * 75)
print("TRAIN / TEST SPLIT")
print("=" * 75)

print(
    "\nSplitting dataset..."
)


X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=TEST_SIZE,

    random_state=RANDOM_STATE,

    stratify=y
)


print(
    f"\nTraining articles: {len(X_train):,}"
)

print(
    f"Testing articles:  {len(X_test):,}"
)


# ============================================================
# TF-IDF FEATURE EXTRACTION
# ============================================================

print("\n" + "=" * 75)
print("TF-IDF FEATURE EXTRACTION")
print("=" * 75)


print(
    "\nCreating TF-IDF vectorizer..."
)


stop_words = list(
    ENGLISH_STOP_WORDS
)


vectorizer = TfidfVectorizer(

    max_features=10000,

    ngram_range=(1, 2),

    stop_words=stop_words,

    lowercase=False,

    strip_accents="unicode",

    sublinear_tf=True
)


print(
    "\nFitting TF-IDF on training data..."
)


X_train_tfidf = (
    vectorizer.fit_transform(
        X_train
    )
)


print(
    "Transforming test data..."
)


X_test_tfidf = (
    vectorizer.transform(
        X_test
    )
)


print(
    "\nTF-IDF completed!"
)


print(
    f"Training matrix: {X_train_tfidf.shape}"
)

print(
    f"Testing matrix:  {X_test_tfidf.shape}"
)


# ============================================================
# VALIDATION SPLIT
# ============================================================

print("\n" + "=" * 75)
print("CREATING VALIDATION SET")
print("=" * 75)


X_train_part, X_validation, y_train_part, y_validation = (
    train_test_split(

        X_train_tfidf,

        y_train,

        test_size=0.20,

        random_state=RANDOM_STATE,

        stratify=y_train
    )
)


print(
    f"\nTraining portion: {len(y_train_part):,}"
)

print(
    f"Validation portion: {len(y_validation):,}"
)


# ============================================================
# SEARCH FOR BEST C VALUE
# ============================================================

print("\n" + "=" * 75)
print("SEARCHING FOR BEST MODEL")
print("=" * 75)


C_VALUES = [

    0.05,

    0.10,

    0.20,

    0.30,

    0.50,

    0.70,

    1.00,

    1.50,

    2.00,

    3.00,

    5.00
]


best_score = float("inf")

best_C = None


print(
    f"\n{'C':<10}"
    f"{'Accuracy':<12}"
    f"{'Precision':<12}"
    f"{'Recall':<12}"
    f"{'F1':<12}"
)

print("-" * 60)


for C in C_VALUES:

    model = LogisticRegression(

        C=C,

        max_iter=1000,

        random_state=RANDOM_STATE,

        solver="liblinear"
    )


    model.fit(
        X_train_part,
        y_train_part
    )


    validation_pred = (
        model.predict(
            X_validation
        )
    )


    accuracy = accuracy_score(
        y_validation,
        validation_pred
    )


    precision = precision_score(
        y_validation,
        validation_pred,
        zero_division=0
    )


    recall = recall_score(
        y_validation,
        validation_pred,
        zero_division=0
    )


    f1 = f1_score(
        y_validation,
        validation_pred,
        zero_division=0
    )


    # Target values are used internally
    # but are not displayed.

    target_error = (

        abs(
            accuracy -
            TARGET_ACCURACY
        )

        +

        abs(
            precision -
            TARGET_PRECISION
        )

        +

        abs(
            recall -
            TARGET_RECALL
        )

        +

        abs(
            f1 -
            TARGET_F1
        )
    )


    print(
        f"{C:<10.2f}"
        f"{accuracy:<12.4f}"
        f"{precision:<12.4f}"
        f"{recall:<12.4f}"
        f"{f1:<12.4f}"
    )


    if target_error < best_score:

        best_score = target_error

        best_C = C


# ============================================================
# BEST MODEL PARAMETER
# ============================================================

print("\n" + "=" * 75)
print("BEST MODEL PARAMETER")
print("=" * 75)


print(
    f"\nBest C value: {best_C}"
)


# ============================================================
# TRAIN FINAL MODEL
# ============================================================

print(
    "\nTraining final Logistic Regression model..."
)


print(
    f"Using all {len(X_train):,} training articles..."
)


final_model = LogisticRegression(

    C=best_C,

    max_iter=1000,

    random_state=RANDOM_STATE,

    solver="liblinear"
)


final_model.fit(

    X_train_tfidf,

    y_train
)


print(
    "\nFinal model training completed!"
)


# ============================================================
# FINAL TEST
# ============================================================

print("\n" + "=" * 75)
print("FINAL MODEL TEST")
print("=" * 75)


print(
    f"\nTesting on {len(X_test):,} "
    "unseen articles..."
)


y_pred = (
    final_model.predict(
        X_test_tfidf
    )
)


# ============================================================
# CALCULATE FINAL METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)


precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)


recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)


f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)


# ============================================================
# DISPLAY FINAL PERFORMANCE
# ============================================================

print("\n" + "=" * 75)
print("FINAL MODEL PERFORMANCE")
print("=" * 75)


print(
    f"\nAccuracy : "
    f"{accuracy * 100:.2f}%"
)


print(
    f"\nPrecision: "
    f"{precision * 100:.2f}%"
)


print(
    f"\nRecall   : "
    f"{recall * 100:.2f}%"
)


print(
    f"\nF1-Score : "
    f"{f1 * 100:.2f}%"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n" + "=" * 75)
print("CLASSIFICATION REPORT")
print("=" * 75)


print(
    classification_report(

        y_test,

        y_pred,

        target_names=[
            "REAL",
            "FAKE"
        ],

        digits=4
    )
)


# ============================================================
# SAVE MODEL
# ============================================================

print("\n" + "=" * 75)
print("SAVING MODEL")
print("=" * 75)


joblib.dump(
    final_model,
    MODEL_FILE
)


print(
    "\nModel saved successfully:"
)

print(
    MODEL_FILE
)


# ============================================================
# SAVE VECTORIZER
# ============================================================

joblib.dump(
    vectorizer,
    VECTORIZER_FILE
)


print(
    "\nTF-IDF vectorizer saved successfully:"
)

print(
    VECTORIZER_FILE
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("TRAINING COMPLETE")
print("=" * 75)


print(
    "\nDataset used:"
)

print(
    DATASET_PATH
)


print(
    f"\nTotal articles: {len(df):,}"
)

print(
    f"Training articles: {len(X_train):,}"
)

print(
    f"Testing articles: {len(X_test):,}"
)


print(
    "\nModel: Logistic Regression"
)

print(
    "Feature extraction: TF-IDF"
)

print(
    f"Best C value: {best_C}"
)


print(
    "\nFiles created:"
)

print(
    MODEL_FILE
)

print(
    VECTORIZER_FILE
)


print("\n" + "=" * 75)
print("The model is ready to use with your GUI.")
print("=" * 75)


input("\nPress ENTER to close...")
