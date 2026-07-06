# Wazen | وازن

An Arabic-first, culturally aware conversational AI assistant that simplifies personal budgeting for Saudi individuals. Built using advanced multi-agent workflows and LangGraph to provide precise, secure, and smart financial insights.

**وازن** هو مساعد مالي ذكي مدعوم بالذكاء الاصطناعي التفاعلي، مصمم خصيصاً ليتناسب مع الثقافة والأنظمة المالية في المجتمع السعودي. يعتمد المشروع على بنية العُملاء المتعددين (Multi-Agent Architecture) لتوفير تحليلات وجدولة مالية دقيقة وآمنة.

---

##  Features | الميزات الأساسية

- **Culturally Aware AI:** Understands Saudi financial dialects, local banking terminologies, and monthly salary cycles (e.g., 27th of each Gregorian month).
- **Multi-Agent Architecture:** Powered by **LangGraph**, dividing tasks between dedicated agents (Data Analyst Agent, Budgeting Agent, and Advisor Agent) for maximum accuracy.
- **Secure Data Management:** Integrated with **Supabase** for secure user session persistence and encrypted financial logs.
- **Interactive Insights:** Provides automated expense tracking, smart budgeting recommendations, and predictive saving alerts.

---

##  Tech Stack | التقنيات المستخدمة

- **Core Logic & AI Framework:** Python, LangChain, LangGraph
- **Database & Authentication:** Supabase
- **Environment & Dependency Management:** `uv` / `pip`

---
##  Project Architecture | مخطط تدفق النظام الذكي

```mermaid
flowchart TD
    classDef default fill:#2d3748,stroke:#4a5568,stroke-width:1px,color:#fff;
    classDef router fill:#3182ce,stroke:#2b6cb0,stroke-width:2px,color:#fff;
    classDef agent fill:#805ad5,stroke:#6b46c1,stroke-width:1px,color:#fff;
    classDef tool fill:#319795,stroke:#2c7a7b,stroke-width:1px,color:#fff;
    classDef db fill:#38a169,stroke:#2f855a,stroke-width:1px,color:#fff;
    classDef ui fill:#dd6b20,stroke:#c05621,stroke-width:1px,color:#fff;

    A["👤 User Input / رسالة المستخدم"]:::ui --> B{"🔀 Router Agent"}:::router
    
    B -- "الاستفسار عن الميزانية والمصاريف" --> C["💼 Budgeting Agent"]:::agent
    B -- "طلب تحليل مالي متقدم" --> D["📊 Data Analyst Agent"]:::agent
    B -- "استشارة مالية أو نصيحة" --> E["💡 Advisor Agent"]:::agent
    
    C --> F["🔧 Tools: Calculate Expenses / Fetch Logs"]:::tool
    D --> G["🔧 Tools: Analytics Models"]:::tool

    F --> H[("🗄️ Database Checkpointer / Supabase")]:::db
    G --> H
    E --> H
    
    H --> I["📝 Formulate Response / صياغة الرد المالي الثقافي"]:::ui
    I --> J["📤 Output to User / إرسال الإجابة لـ وازن"]:::ui
```

##  Repository Structure | هيكلة المستودع

```text
wazen/
├── data/                  # Evaluation datasets & analytics
├── docs/                  # Project documentation
├── supabase/              # Database schema & migrations
├── tests/                 # Unit tests for agents and backend
├── src/                   # Source code
    ├── agent/             # LangGraph state machine & AI agent logic
    ├── backend/           # FastAPI backend endpoints
    └── frontend/          # User Interface (Web/Mobile)
```
