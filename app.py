import customtkinter as ctk
import joblib
import re
import string
import webbrowser
from tkinter import messagebox
import threading
import os
from pathlib import Path

# ===================== IMPORT ONLINE VERIFIER =====================
from online_verifier import verify_news_online

# ===================== CONFIGURATION =====================

DESKTOP = Path(os.path.expanduser("~/Desktop"))
SYSTEM_FOLDER = DESKTOP / "system"

MODEL_FILE = SYSTEM_FOLDER / "fake_news_model.pkl"
VECTORIZER_FILE = SYSTEM_FOLDER / "tfidf_vectorizer.pkl"

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

# ===================== LOAD MODEL =====================

try:
    model = joblib.load(MODEL_FILE)
    vectorizer = joblib.load(VECTORIZER_FILE)
    print("✅ Model and vectorizer loaded successfully.")
except FileNotFoundError as e:
    print(f"❌ Error: Could not find model files.\n{e}")
    root = ctk.CTk()
    root.withdraw()
    messagebox.showerror(
        "Model Files Missing",
        f"Could not find the model files.\n\n"
        f"Please ensure:\n"
        f"1. The folder 'system' exists on your Desktop.\n"
        f"2. It contains 'fake_news_model.pkl' and 'tfidf_vectorizer.pkl'.\n\n"
        f"Expected path: {SYSTEM_FOLDER}"
    )
    exit(1)

# ===================== TEXT CLEANING =====================

def clean_text(text):
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ===================== MAIN APPLICATION =====================

class FakeNewsDetectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Fake News Detector & Reporting System")
        self.geometry("1000x850")
        self.minsize(900, 750)

        self.main_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=20,
            fg_color="transparent"
        )
        self.main_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # ===== Header =====
        self.header_frame = ctk.CTkFrame(self.main_frame, corner_radius=20, fg_color="transparent")
        self.header_frame.pack(pady=20, padx=30, fill="x")

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="📰 Fake News Detector & Reporting System",
            font=ctk.CTkFont(size=36, weight="bold", family="Segoe UI")
        )
        self.title_label.pack(pady=(10, 5))

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Detect fake news and report it to social media platforms",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.subtitle_label.pack(pady=(0, 10))

        # ===== Input Section =====
        self.input_frame = ctk.CTkFrame(self.main_frame, corner_radius=20)
        self.input_frame.pack(pady=10, padx=30, fill="x")

        self.input_label = ctk.CTkLabel(
            self.input_frame,
            text="News Title & Content",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.input_label.pack(pady=(15, 5), padx=20, anchor="w")

        self.text_input = ctk.CTkTextbox(
            self.input_frame,
            height=150,
            font=ctk.CTkFont(size=14),
            corner_radius=15,
            border_width=1,
            border_color="#3b4d6b",
            wrap="word"
        )
        self.text_input.pack(pady=10, padx=20, fill="x")

        self.text_input.insert("1.0", "Paste the news article here...")
        self.text_input.bind("<FocusIn>", self.clear_placeholder)
        self.text_input.bind("<FocusOut>", self.restore_placeholder)

        # Sample buttons frame
        self.sample_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.sample_frame.pack(pady=10, padx=20)

        self.real_sample_btn = ctk.CTkButton(
            self.sample_frame,
            text="✅ Sample REAL News",
            command=self.load_real_sample,
            width=200,
            height=40,
            corner_radius=20,
            fg_color="#2e7d32",
            hover_color="#1e5a23"
        )
        self.real_sample_btn.pack(side="left", padx=10)

        self.fake_sample_btn = ctk.CTkButton(
            self.sample_frame,
            text="❌ Sample FAKE News",
            command=self.load_fake_sample,
            width=200,
            height=40,
            corner_radius=20,
            fg_color="#c62828",
            hover_color="#9a1f1f"
        )
        self.fake_sample_btn.pack(side="left", padx=10)

        # ===== Predict Button =====
        self.predict_btn = ctk.CTkButton(
            self.main_frame,
            text="🔎 Verify Authenticity",
            command=self.predict,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=30,
            fg_color="#2b3a55",
            hover_color="#3b4d6b"
        )
        self.predict_btn.pack(pady=20, padx=30, fill="x")

        # ===== Mode Toggle Switch =====
        self.mode_frame = ctk.CTkFrame(self.main_frame, corner_radius=20)
        self.mode_frame.pack(pady=5, padx=30, fill="x")

        self.mode_label = ctk.CTkLabel(
            self.mode_frame,
            text="🔧 Verification Mode:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.mode_label.pack(side="left", padx=(20, 15), pady=10)

        self.mode_switch = ctk.CTkSwitch(
            self.mode_frame,
            text="",
            command=self.toggle_mode,
            progress_color="#2b3a55",
            onvalue="online",
            offvalue="offline"
        )
        self.mode_switch.pack(side="left", pady=10)

        self.mode_status_label = ctk.CTkLabel(
            self.mode_frame,
            text="🔵 Offline Mode (ML Only)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray"
        )
        self.mode_status_label.pack(side="left", padx=15, pady=10)

        self.mode_description_label = ctk.CTkLabel(
            self.mode_frame,
            text="Uses only the machine learning model. No internet search.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.mode_description_label.pack(side="left", padx=10, pady=10)

        # ===== Result Section =====
        self.result_frame = ctk.CTkFrame(self.main_frame, corner_radius=20)
        self.result_frame.pack(pady=10, padx=30, fill="x")

        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.result_label.pack(pady=(20, 5))

        self.confidence_bar_frame = ctk.CTkFrame(self.result_frame, height=10, fg_color="#e0e0e0", corner_radius=5)
        self.confidence_bar_frame.pack(pady=10, padx=30, fill="x")

        self.confidence_bar = ctk.CTkFrame(self.confidence_bar_frame, height=10, corner_radius=5, fg_color="#2b3a55")
        self.confidence_bar.place(x=0, y=0, relwidth=0, relheight=1)

        self.probability_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.probability_frame.pack(pady=(10, 20), padx=30, fill="x")

        self.real_prob_label = ctk.CTkLabel(
            self.probability_frame,
            text="REAL: 0%",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.real_prob_label.pack(side="left")

        self.fake_prob_label = ctk.CTkLabel(
            self.probability_frame,
            text="FAKE: 0%",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.fake_prob_label.pack(side="right")

        # ===== Verification Status Section =====
        self.verification_frame = ctk.CTkFrame(self.main_frame, corner_radius=20)
        self.verification_frame.pack(pady=5, padx=30, fill="x")

        self.verification_status_label = ctk.CTkLabel(
            self.verification_frame,
            text="🌐 Online Verification: Idle",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.verification_status_label.pack(pady=(10, 5), padx=20)

        self.verification_detail_label = ctk.CTkLabel(
            self.verification_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=800
        )
        self.verification_detail_label.pack(pady=(0, 10), padx=20)

        # ===== Organization Report Button =====
        self.org_report_frame = ctk.CTkFrame(self.main_frame, corner_radius=20)
        self.org_report_frame.pack(pady=5, padx=30, fill="x")
        self.org_report_frame.pack_forget()

        self.org_report_label = ctk.CTkLabel(
            self.org_report_frame,
            text="🏢 Report to Organization:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.org_report_label.pack(side="left", padx=20, pady=10)

        self.org_report_btn = ctk.CTkButton(
            self.org_report_frame,
            text="🚨 Report to Organization",
            command=self.report_to_organization,
            height=40,
            corner_radius=20,
            fg_color="#ff6b6b",
            hover_color="#ff5252",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.org_report_btn.pack(side="left", padx=15, pady=10)

        self.org_report_url_label = ctk.CTkLabel(
            self.org_report_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.org_report_url_label.pack(side="left", padx=10, pady=10)

        # ===== Reporting Section =====
        self.reporting_frame = ctk.CTkFrame(self.main_frame, corner_radius=20)
        self.reporting_frame.pack(pady=20, padx=30, fill="x")

        self.reporting_label = ctk.CTkLabel(
            self.reporting_frame,
            text="📢 Report Suspicious Content",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.reporting_label.pack(pady=(15, 15))

        # URL Input Frame
        self.url_frame = ctk.CTkFrame(self.reporting_frame, fg_color="transparent")
        self.url_frame.pack(pady=10, padx=20, fill="x")

        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="Enter any URL to report to...",
            height=45,
            corner_radius=25,
            border_width=2,
            border_color="#3b4d6b",
            font=ctk.CTkFont(size=14)
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.report_btn = ctk.CTkButton(
            self.url_frame,
            text="🚀 Report Now",
            command=self.report_to_url,
            width=150,
            height=45,
            corner_radius=25,
            fg_color="#ff6b6b",
            hover_color="#ff5252",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.report_btn.pack(side="right")

        # Quick Report Platforms
        self.quick_label = ctk.CTkLabel(
            self.reporting_frame,
            text="Quick Report to Platforms:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="gray"
        )
        self.quick_label.pack(pady=(20, 10))

        # Row 1
        self.social_frame1 = ctk.CTkFrame(self.reporting_frame, fg_color="transparent")
        self.social_frame1.pack(pady=5, padx=20, fill="x")

        self.fb_btn = ctk.CTkButton(
            self.social_frame1,
            text="📘 Facebook",
            command=lambda: self.open_social("facebook"),
            width=220,
            height=50,
            corner_radius=25,
            fg_color="#1877f2",
            hover_color="#166fe5",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.fb_btn.pack(side="left", padx=8, expand=True, fill="x")

        self.x_btn = ctk.CTkButton(
            self.social_frame1,
            text="🐦 X (Twitter)",
            command=lambda: self.open_social("x"),
            width=220,
            height=50,
            corner_radius=25,
            fg_color="#000000",
            hover_color="#333333",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.x_btn.pack(side="left", padx=8, expand=True, fill="x")

        # Row 2
        self.social_frame2 = ctk.CTkFrame(self.reporting_frame, fg_color="transparent")
        self.social_frame2.pack(pady=5, padx=20, fill="x")

        self.ig_btn = ctk.CTkButton(
            self.social_frame2,
            text="📷 Instagram",
            command=lambda: self.open_social("instagram"),
            width=220,
            height=50,
            corner_radius=25,
            fg_color="#e4405f",
            hover_color="#d13b57",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.ig_btn.pack(side="left", padx=8, expand=True, fill="x")

        self.blog_btn = ctk.CTkButton(
            self.social_frame2,
            text="📝 Blog/WordPress",
            command=lambda: self.open_social("blog"),
            width=220,
            height=50,
            corner_radius=25,
            fg_color="#ff7b00",
            hover_color="#e66a00",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.blog_btn.pack(side="left", padx=8, expand=True, fill="x")

        # Row 3
        self.social_frame3 = ctk.CTkFrame(self.reporting_frame, fg_color="transparent")
        self.social_frame3.pack(pady=5, padx=20, fill="x")

        self.yt_btn = ctk.CTkButton(
            self.social_frame3,
            text="▶️ YouTube",
            command=lambda: self.open_social("youtube"),
            width=220,
            height=50,
            corner_radius=25,
            fg_color="#ff0000",
            hover_color="#cc0000",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.yt_btn.pack(side="left", padx=8, expand=True, fill="x")

        self.tt_btn = ctk.CTkButton(
            self.social_frame3,
            text="🎵 TikTok",
            command=lambda: self.open_social("tiktok"),
            width=220,
            height=50,
            corner_radius=25,
            fg_color="#000000",
            hover_color="#333333",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.tt_btn.pack(side="left", padx=8, expand=True, fill="x")

        self.reddit_btn = ctk.CTkButton(
            self.social_frame3,
            text="👽 Reddit",
            command=lambda: self.open_social("reddit"),
            width=220,
            height=50,
            corner_radius=25,
            fg_color="#ff4500",
            hover_color="#e03d00",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.reddit_btn.pack(side="left", padx=8, expand=True, fill="x")

        # ===== ADSU Reporting Button =====
        self.adsu_frame = ctk.CTkFrame(self.reporting_frame, corner_radius=20)
        self.adsu_frame.pack(pady=10, padx=20, fill="x")

        self.adsu_label = ctk.CTkLabel(
            self.adsu_frame,
            text="🏫 Report Fake News About ADSU:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.adsu_label.pack(side="left", padx=15, pady=10)

        self.adsu_btn = ctk.CTkButton(
            self.adsu_frame,
            text="🚨 Report to ADSU",
            command=self.report_to_adsu,
            height=40,
            corner_radius=20,
            fg_color="#8B0000",
            hover_color="#5C0000",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.adsu_btn.pack(side="left", padx=15, pady=10)

        self.adsu_url_label = ctk.CTkLabel(
            self.adsu_frame,
            text="URL: https://www.adsu.edu.ng/contact",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.adsu_url_label.pack(side="left", padx=10, pady=10)

        # Tips
        self.tips_frame = ctk.CTkFrame(self.main_frame, corner_radius=20)
        self.tips_frame.pack(pady=20, padx=30, fill="x")

        self.tips_label = ctk.CTkLabel(
            self.tips_frame,
            text="💡 Reporting Tips",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.tips_label.pack(pady=(15, 5))

        self.tips_text = ctk.CTkLabel(
            self.tips_frame,
            text="• Click any platform button to open it in your browser\n"
                 "• A tip box will appear with step-by-step reporting instructions\n"
                 "• Enter any custom URL and click 'Report Now' to open it\n"
                 "• If an organization is detected, use 'Report to Organization' button\n"
                 "• Use the 'Report to ADSU' button for any fake news about Adamawa State University\n"
                 "• Always verify content before reporting",
            font=ctk.CTkFont(size=13),
            justify="left",
            text_color="gray"
        )
        self.tips_text.pack(pady=(0, 15), padx=20)

        # Footer
        self.footer_label = ctk.CTkLabel(
            self.main_frame,
            text="Powered by Machine Learning • Report responsibly",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.footer_label.pack(pady=(10, 20))

        # Initialize
        self.hide_result()
        self.placeholder_active = True
        self.current_prediction = None
        self.current_confidence = None
        self.current_proba = None
        self.verification_mode = "offline"
        self.current_organization = None
        self.current_organization_url = None

    # ===================== UI Helpers =====================

    def clear_placeholder(self, event):
        if self.placeholder_active:
            self.text_input.delete("1.0", "end")
            self.placeholder_active = False

    def restore_placeholder(self, event):
        if not self.text_input.get("1.0", "end-1c").strip():
            self.text_input.insert("1.0", "Paste the news article here...")
            self.placeholder_active = True

    def hide_result(self):
        self.result_label.configure(text="")
        self.confidence_bar.place_forget()
        self.real_prob_label.configure(text="REAL: 0%")
        self.fake_prob_label.configure(text="FAKE: 0%")
        self.verification_status_label.configure(text="🌐 Online Verification: Idle", text_color="gray")
        self.verification_detail_label.configure(text="")
        self.org_report_frame.pack_forget()
        self.current_organization = None
        self.current_organization_url = None

    def show_result(self, label, confidence, proba_real, proba_fake):
        if label == "REAL":
            self.result_label.configure(text="✅ REAL", text_color="#2e7d32")
            bar_color = "#2e7d32"
        else:
            self.result_label.configure(text="⚠️ FAKE", text_color="#c62828")
            bar_color = "#c62828"

        self.confidence_bar.configure(fg_color=bar_color)
        self.confidence_bar.place(x=0, y=0, relwidth=confidence/100, relheight=1)
        self.real_prob_label.configure(text=f"REAL: {proba_real:.1f}%")
        self.fake_prob_label.configure(text=f"FAKE: {proba_fake:.1f}%")

    # ===================== Mode Toggle =====================

    def toggle_mode(self):
        if self.mode_switch.get() == "online":
            self.verification_mode = "online"
            self.mode_status_label.configure(text="🟢 Online Mode (Pure Web Search)", text_color="#2e7d32")
            self.mode_description_label.configure(text="Uses ONLY DuckDuckGo web search. No machine learning.")
            self.verification_status_label.configure(text="🌐 Online Verification: Ready", text_color="#2e7d32")
            self.verification_detail_label.configure(text="Switch is ON. System will search the web for verification ONLY.")
        else:
            self.verification_mode = "offline"
            self.mode_status_label.configure(text="🔵 Offline Mode (ML Only)", text_color="gray")
            self.mode_description_label.configure(text="Uses only the machine learning model. No internet search.")
            self.verification_status_label.configure(text="🌐 Online Verification: Disabled (Offline Mode)", text_color="gray")
            self.verification_detail_label.configure(text="Switch is OFF. System will use ML model only.")

    # ===================== SAMPLE DATA =====================

    def load_real_sample(self):
        sample = (
            "Dangote Petroleum Refinery Announces Significant Price Reduction\n\n"
            "Dangote Petroleum Refinery has announced a reduction in the ex-depot (gantry) price of "
            "Premium Motor Spirit (PMS), commonly referred to as petrol, by N65.00, from N890 to N825 "
            "per litre, effective from 27th February 2025. This strategic price adjustment is designed "
            "to provide essential relief to Nigerians in anticipation of the upcoming Ramadan season, "
            "while also supporting President Bola Ahmed Tinubu's economic recovery policy by alleviating "
            "the financial burden on the Nigerian populace. This marks the second price reduction of PMS "
            "in February 2025, following a previous decrease of N60.00 earlier in the month."
        )
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", sample)
        self.placeholder_active = False

    def load_fake_sample(self):
        sample = (
            "BREAKING: President Tinubu Resigns Unexpectedly\n\n"
            "In a shocking development, President Bola Ahmed Tinubu has reportedly "
            "resigned from office effective immediately. According to an anonymous "
            "source within the State House, the President submitted his resignation "
            "letter to the National Assembly earlier today. The source claims that "
            "the President cited 'personal reasons' for his sudden departure. This "
            "comes just days after the President returned from a foreign trip. The "
            "Presidency has not issued any official statement regarding this claim, "
            "but speculations are already spreading across social media. Constitutional "
            "experts say this would be unprecedented in Nigeria's democratic history."
        )
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", sample)
        self.placeholder_active = False

    # ===================== Prediction =====================

    def predict(self):
        raw_text = self.text_input.get("1.0", "end-1c").strip()

        if not raw_text or self.placeholder_active:
            messagebox.showwarning("Empty Input", "Please enter some text to analyze.")
            return

        self.predict_btn.configure(state="disabled", text="Analyzing...")
        self.hide_result()

        def run():
            try:
                if self.verification_mode == "online":
                    print("🔍 Online Mode: Pure Web Search")
                    verification = verify_news_online(raw_text)
                    self.current_organization = verification.get("organization")
                    self.current_organization_url = verification.get("organization_report_url")
                    self.after(0, lambda: self.show_online_verification_result(verification))
                else:
                    print("🔍 Offline Mode: Machine Learning Only")
                    cleaned = clean_text(raw_text)
                    vec = vectorizer.transform([cleaned])
                    pred = model.predict(vec)[0]
                    proba = model.predict_proba(vec)[0]

                    label = "REAL" if pred == 0 else "FAKE"
                    confidence = proba[pred] * 100
                    proba_real = proba[0] * 100
                    proba_fake = proba[1] * 100

                    self.current_prediction = label
                    self.current_confidence = confidence
                    self.current_proba = proba

                    self.after(0, lambda: self.show_result(label, confidence, proba_real, proba_fake))
                    self.after(0, lambda: self.verification_status_label.configure(
                        text="🌐 Online Verification: Disabled (Offline Mode)",
                        text_color="gray"
                    ))
                    self.after(0, lambda: self.verification_detail_label.configure(
                        text="System is in OFFLINE mode. Only machine learning model used."
                    ))
                    self.after(100, lambda: self._scroll_to_result())

            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Prediction failed:\n{str(e)}"))
            finally:
                self.after(0, lambda: self.predict_btn.configure(state="normal", text="🔎 Verify Authenticity"))

        threading.Thread(target=run, daemon=True).start()

    def show_online_verification_result(self, verification):
        if verification.get("verified", False):
            self.result_label.configure(text="🔍 VERIFIED ONLINE", text_color="#2e7d32")
            bar_color = "#2e7d32"
            confidence = 85
        else:
            self.result_label.configure(text="⚠️ NOT VERIFIED ONLINE", text_color="#c62828")
            bar_color = "#c62828"
            confidence = 50

        self.confidence_bar.configure(fg_color=bar_color)
        self.confidence_bar.place(x=0, y=0, relwidth=confidence/100, relheight=1)
        self.real_prob_label.configure(text="REAL: 0%")
        self.fake_prob_label.configure(text="FAKE: 0%")

        sources_count = len(verification.get("sources", []))
        topic = verification.get("topic", "General")
        org_domain = verification.get("organization_domain", "")
        recency = verification.get("recency", "Recent")
        confidence_score = verification.get("confidence_score", 0)

        # Build detail text
        detail_text = f"📅 {recency}\n"
        if org_domain:
            detail_text += f"🔍 Searched: {org_domain} (OFFICIAL WEBSITE ONLY)\n"
        else:
            detail_text += f"🔍 Searched: Trusted News Sources Only\n"
        detail_text += f"📂 Topic: {topic}\n"
        detail_text += f"🎯 Analysis Confidence: {confidence_score:.1f}%\n"
        detail_text += verification.get('message', '')

        # Show sources with analysis
        sources = verification.get("sources", [])
        if sources:
            source_text = "\n📄 Sources Analyzed:\n"
            for i, source in enumerate(sources[:3]):
                title = source.get("title", "Untitled")[:70]
                analysis = source.get("analysis", {})
                supports = "✅ Supports" if analysis.get("supports_claim", False) else "⚠️ Not Supported"
                source_text += f"   {i+1}. {title}... ({supports})\n"
            detail_text += source_text

        self.verification_status_label.configure(
            text=f"✅ Online Verification: Complete",
            text_color="#2e7d32"
        )
        self.verification_detail_label.configure(text=detail_text)

        # ===== SHOW ORGANIZATION REPORT BUTTON =====
        org_name = verification.get("organization")
        org_url = verification.get("organization_report_url")

        if org_name and org_url:
            self.current_organization = org_name
            self.current_organization_url = org_url
            self.org_report_frame.pack(pady=5, padx=30, fill="x")
            self.org_report_label.configure(text=f"🏢 Report to: {org_name.title()}")
            self.org_report_url_label.configure(text=f"URL: {org_url}")
        else:
            self.org_report_frame.pack_forget()

        self.after(100, lambda: self._scroll_to_result())

    def _scroll_to_result(self):
        self.main_frame._parent_canvas.yview_moveto(0.3)

    # ===================== Report to Organization =====================

    def report_to_organization(self):
        if self.current_organization_url:
            webbrowser.open(self.current_organization_url)
            messagebox.showinfo(
                "Opening Organization Report Page",
                f"Opening {self.current_organization.title()}'s report/contact page in your browser.\n\n"
                f"URL: {self.current_organization_url}\n\n"
                "Please fill out the form or send a report directly."
            )
        else:
            messagebox.showwarning(
                "No Organization Detected",
                "No organization was detected in this news. Please use the social media reporting buttons instead."
            )

    # ===================== Report to ADSU =====================

    def report_to_adsu(self):
        adsu_url = "https://www.adsu.edu.ng/contact"
        webbrowser.open(adsu_url)
        messagebox.showinfo(
            "Report Fake News About ADSU",
            f"Opening ADSU's contact page in your browser.\n\n"
            f"URL: {adsu_url}\n\n"
            "Please provide details about the fake news content so the university can take appropriate action."
        )

    # ===================== Reporting System =====================

    def open_social(self, platform):
        urls = {
            "facebook": "https://www.facebook.com",
            "x": "https://twitter.com",
            "instagram": "https://www.instagram.com",
            "blog": "https://www.blogger.com",
            "youtube": "https://www.youtube.com",
            "tiktok": "https://www.tiktok.com",
            "reddit": "https://www.reddit.com"
        }

        if platform in urls:
            webbrowser.open(urls[platform])
            messagebox.showinfo("Opening Browser", f"Opening {platform.title()} in your default browser.")
            self.show_reporting_tip(platform)

    def report_to_url(self):
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showwarning("Empty URL", "Please enter a URL to report to.")
            return

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            webbrowser.open(url)
            messagebox.showinfo("Opening Browser", f"Opening:\n{url}\n\nin your default browser.")
            self.url_entry.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open URL:\n{str(e)}")

    def show_reporting_tip(self, platform):
        tips = {
            "facebook": (
                "📘 How to report on Facebook:\n\n"
                "1. Go to the post containing fake news\n"
                "2. Click the three dots (...) on the top right of the post\n"
                "3. Select 'Find support or report post'\n"
                "4. Choose 'False information' as the reason\n"
                "5. Follow the on-screen instructions"
            ),
            "x": (
                "🐦 How to report on X (Twitter):\n\n"
                "1. Go to the tweet containing fake news\n"
                "2. Click the three dots icon on the tweet\n"
                "3. Select 'Report Tweet'\n"
                "4. Choose 'It's misleading'\n"
                "5. Follow the reporting process"
            ),
            "instagram": (
                "📷 How to report on Instagram:\n\n"
                "1. Go to the post containing fake news\n"
                "2. Tap the three dots above the post\n"
                "3. Select 'Report'\n"
                "4. Choose 'False information'\n"
                "5. Complete the reporting form"
            ),
            "blog": (
                "📝 How to report on Blogging Platforms:\n\n"
                "Blogger/Blogspot:\n"
                "• Look for a 'Report Abuse' link\n"
                "• Fill out the abuse report form\n\n"
                "WordPress.com:\n"
                "• Use the 'Report this post' feature\n"
                "• Contact the site administrator"
            ),
            "youtube": (
                "▶️ How to report on YouTube:\n\n"
                "1. Go to the video containing misinformation\n"
                "2. Click the three dots below the video\n"
                "3. Select 'Report'\n"
                "4. Choose 'Spam or misleading'\n"
                "5. Select 'Misleading content' and submit"
            ),
            "tiktok": (
                "🎵 How to report on TikTok:\n\n"
                "1. Go to the video containing fake news\n"
                "2. Press and hold on the video\n"
                "3. Select 'Report'\n"
                "4. Choose 'Misleading information'\n"
                "5. Complete the reporting process"
            ),
            "reddit": (
                "👽 How to report on Reddit:\n\n"
                "1. Go to the post containing misinformation\n"
                "2. Click the 'Report' button below the post\n"
                "3. Select 'Misinformation'\n"
                "4. Add details if required\n"
                "5. Submit the report"
            )
        }

        if platform in tips:
            messagebox.showinfo(f"Reporting on {platform.title()}", tips[platform])

# ===================== RUN THE APP =====================

if __name__ == "__main__":
    app = FakeNewsDetectorApp()
    app.mainloop()