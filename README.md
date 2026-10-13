Fake News Detection and Reporting System

A dual-mode fake news detection system that combines offline machine learning with real-time online verification for higher accuracy.

**Author:** Naiwo Oluwaseyi | [LinkedIn](https://www.linkedin.com/in/naiwo-oluwaseyi-aa8563246)

Overview

This system tackles misinformation using two complementary approaches:

**1. Offline Mode (Machine Learning)**
- Uses TF-IDF vectorization and a trained classification model
- Works without internet for fast prediction
- Core files: `fake_news_model.pkl`, `tfidf_vectorizer.pkl`

**2. Online Mode (Real-time Verification)**
- Verifies news credibility against trusted sources in real-time
- Handles breaking and trending news
- Core file: `online_verifier.py`

Tech Stack
- Python, Scikit-learn, Pandas, NumPy
- NLP: TF-IDF Vectorization
- Machine Learning Classification

Project Structure
├── http://app.py                 # Main application
├── http://train.py               # Model training
├── online_verifier.py     # Online verification engine
├── test_verifier.py       # Verification tests
├── fake_news_model.pkl    # Trained model
├── tfidf_vectorizer.pkl   # TF-IDF vectorizer

How to Run

1. Clone repository:
   ```bash
   git clone https://github.com/flytedigitals/Fake-news-detection-and-reporting-system.git
2. Install dependencies:
   pip install scikit-learn pandas numpy
3. Run app:
   python app.py
How It Works
1. User inputs news text
2. Text is vectorized using TF-IDF
3. Offline model predicts REAL or FAKE
4. Online verifier cross-checks for confirmation
5. Final result with confidence score

Author
*Naiwo Oluwaseyi*
- Graduate, Computer Science
- Interests: AI/ML, Python Development
- GitHub: https://github.com/flytedigitals
- LinkedIn: https://www.linkedin.com/in/naiwo-oluwaseyi-aa8563246

Open to opportunities in ML Engineering and Software Development.
