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
- **Environment & Dependency Management:** `uv` / `pip`

---
## 🔄 Project Architecture | مخطط تدفق النظام الذكي
```mermaid
graph TD
    __start__([Start]) --> init
    
    init["init Node<br>• Setup DB Candidate & Session UUIDs<br>• Load program requirements"] 
    --> router_node
    
    router_node{"node_router Router"}
    
    router_node -- "evaluate" --> evaluation
    router_node -- "generate_question" --> interviewer
    router_node -- "wrap_up" --> wrap_up
    
    evaluation["Evaluation Agent<br>• Scores answer (1-5)<br>• Flags needs_probe<br>• Extracts skills/facts"]
    --> profile_builder["Profile Builder Agent<br>• Updates candidate_profiles JSONB<br>• Updates covered topics"]
    
    profile_builder --> router_node
    
    interviewer["Interviewer Agent<br>• Generates fresh question or probing follow-up<br>• Logs question to DB"] 
    -- "Interrupt boundary (Wait for last_answer)" --> evaluation
    
    wrap_up["Decision Support Agent<br>• Compiles overall scores<br>• Synthesizes strengths/weaknesses<br>• Generates recommendations"] 
    --> __end__([End])```


## 📁 Repository Structure | هيكلة المستودع


wazen/
├── data/                  # Evaluation datasets & analytics
├── docs/                  # Project documentation
├── supabase/              # Database schema & migrations
├── tests/                 # Unit tests for agents and backend
└── src/                   # Source code
    ├── agent/             # LangGraph state machine & AI agent logic
    └── backend/           # FastAPI backend endpoints


    ##  Agentic Workflow | مخطط تدفق النظام الذكي

