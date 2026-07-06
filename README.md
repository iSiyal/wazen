# ⚖️ Wazen | وازن

An Arabic-first, culturally aware conversational AI assistant that simplifies personal budgeting for Saudi individuals. Built using advanced multi-agent workflows and LangGraph to provide precise, secure, and smart financial insights.

**وازن** هو مساعد مالي ذكي مدعوم بالذكاء الاصطناعي التفاعلي، مصمم خصيصاً ليتناسب مع الثقافة والأنظمة المالية في المجتمع السعودي. يعتمد المشروع على بنية العُملاء المتعددين (Multi-Agent Architecture) لتوفير تحليلات وجدولة مالية دقيقة وآمنة.

---

## 🚀 Features | الميزات الأساسية

- **Culturally Aware AI:** Understands Saudi financial dialects, local banking terminologies, and monthly salary cycles (e.g., 27th of each Gregorian month).
- **Multi-Agent Architecture:** Powered by **LangGraph**, dividing tasks between dedicated agents (Data Analyst Agent, Budgeting Agent, and Advisor Agent) for maximum accuracy.
- **Secure Data Management:** Integrated with **Supabase** for secure user session persistence and encrypted financial logs.
- **Interactive Insights:** Provides automated expense tracking, smart budgeting recommendations, and predictive saving alerts.

---

## 🛠️ Tech Stack | التقنيات المستخدمة

- **Core Logic & AI Framework:** Python, LangChain, LangGraph
- **Database & Authentication:** Supabase
- **Frontend Platform:** Flutter / Dart (or your specific UI choice)
- **Environment & Dependency Management:** `uv` / `pip`

---

## 📁 Repository Structure | هيكلة المستودع

```text
wazen/
├── data/                  # Evaluation datasets & analytics
├── docs/                  # Project documentation & architecture diagrams
├── supabase/              # Database schema & migrations
├── tests/                 # Unit tests for agents and backend
└── src/                   # Source code
    ├── agent/             # LangGraph state machine & AI agent logic
    ├── backend/           # FastAPI backend endpoints
    └── frontend/          # User Interface (Web/Mobile)

    ##  Agentic Workflow | مخطط تدفق النظام الذكي

```mermaid
graph TD
    A[ User Input / رسالة المستخدم] --> B{ Router Agent}
    
    B -- الاستفسار عن الميزانية والمصاريف --> C[ Budgeting Agent]
    B -- طلب تحليل مالي متقدم --> D[ Data Analyst Agent]
    B -- استشارة مالية أو نصيحة --> E[ Financial Advisor Agent]
    
    C --> F[ Tools: Calculate Expenses / Fetch Logs]
    D --> G[ Tools: Analytics Models]

    F --> H[ Database Checkpointer / Supabase]
    G --> H
    E --> H
    
    H --> I[ Formulate Response / صياغة الرد المالي الثقافي]
    I --> J[ Output to User / إرسال الإجابة لـ وازن]