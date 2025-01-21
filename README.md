# AI Agent for SEO Reporting

This project features an AI agent designed for generating SEO reports, using tools like **LangChain** and **RapidAPI**. The agent interacts with users, fetches live SEO data, and provides actionable insights for businesses.

---

## **Setup Instructions**

### **Step 1: Clone the Repository**

Clone the GitHub repository to your local machine:

```bash
git clone https://github.com/B-Ismail/AgentAI_SEO.git
cd AgentAI_SEO
```

---

### **Step 2: Create a Virtual Environment**

Create and activate a Python virtual environment:

#### On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### **Step 3: Install Dependencies**

Install the required libraries:

```bash
pip install -r requirements.txt
```

---

### **Step 4: Set Up Environment Variables**

Create a `.env` file in the project root and configure the following variables:

```
RAPIDAPI_KEY=your_rapidapi_key_here
OPENAI_API_KEY=your_openai_api_key_here
SENDER_EMAIL=your_sender_email@example.com
SENDER_PASSWORD=your_email_password_here
```

- **`RAPIDAPI_KEY`**: Your RapidAPI key for accessing SEO-related APIs.
- **`OPENAI_API_KEY`**: Your OpenAI API key for accessing GPT-based functionality.
- **`SENDER_EMAIL`**: The email address used for sending reports.
- **`SENDER_PASSWORD`**: The app-specific password for the sender email.

#### **How to Obtain the RapidAPI Key**
1. Go to the [RapidAPI SimilarWeb Insights API](https://rapidapi.com/opendatapoint-opendatapoint-default/api/similarweb-insights/playground/apiendpoint_349e6b92-24b8-4f38-8563-f9a856872fb6).
2. Sign up for a free account if you don’t already have one.
3. Once signed in, subscribe to the API and generate your unique API key.
4. Use this key as the value for `RAPIDAPI_KEY` in your `.env` file.

#### **How to Generate the App-Specific Password**

1. Go to your Google Account settings and navigate to the **Security** tab.
2. Under the **Signing in to Google** section, locate **App Passwords**.
3. Follow the instructions to generate a 16-character app-specific password for the application.
4. Use this generated password as the value for `SENDER_PASSWORD` in your `.env` file.

Ensure the `.env` file is not tracked by Git by adding it to `.gitignore`.

---

### **Step 5: Run the Application**

Start the application:

```bash
streamlit run app.py
```

This command will launch the app in your default web browser.

---

## **Additional Notes**

- Ensure you have Python 3.8 or higher installed.
- If you encounter issues with SMTP, ensure the sender email allows third-party app access or use an app-specific password.

Thank you for checking in 🚀

