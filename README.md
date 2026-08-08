# 🎓 College Management System (CMS)

> **Phase 1 — Foundation & Core Architecture**

A modular, Django-powered **College Management System (CMS)** designed to digitize and streamline academic administration, user management, and campus workflows.

The project is being developed in multiple phases, with **Phase 1 focused on establishing the core architecture, authentication, database foundation, and application structure** required for future academic features.

---

## 📌 Phase 1 — Current Status

**Status:** 🟢 Foundation Completed / In Development

Phase 1 establishes the technical foundation of the College Management System, including the custom authentication system, role-based access structure, Django applications, and initial academic database architecture.

### ✅ Implemented in Phase 1

* 🔐 **Custom User Authentication**

  * Custom Django user model
  * User registration and authentication foundation
  * Role-based user structure

* 👥 **Role-Based Access Control (RBAC)**

  * 👨‍💼 Admin
  * 👨‍🏫 Teacher / Faculty
  * 👨‍🎓 Student

* 🏗️ **Modular Django Architecture**

  * `accounts` — Authentication and user management
  * `faculty` — Faculty-related functionality
  * `students` — Student-related functionality
  * `collegePortal` — Main Django project configuration
  * `templates` — Shared UI templates

* 🗄️ **Database Foundation**

  * Custom user architecture
  * Academic entities and relationships
  * Departments
  * Courses
  * Subjects
  * Student/Faculty profiles
  * Initial grade-related structures

* ⚙️ **Django Project Configuration**

  * Development environment setup
  * Database migration system
  * Static and template configuration
  * Application-level separation

---

## 🎯 Phase 1 Objectives

The primary objective of Phase 1 is to establish a **clean, scalable, and maintainable foundation** for the complete CMS.

### Core Goals

| Objective                        | Status          |
| -------------------------------- | --------------- |
| Django project initialization    | ✅               |
| Custom user model                | ✅               |
| Role-based user structure        | ✅               |
| Accounts application             | ✅               |
| Faculty application              | ✅               |
| Student application              | ✅               |
| Initial academic database design | ✅               |
| Migration setup                  | ✅               |
| Shared template structure        | ✅               |
| Advanced academic workflows      | 🔄 Future Phase |
| Analytics & reporting            | 🔄 Future Phase |
| QR attendance                    | 🔄 Future Phase |
| AI-powered features              | 🔄 Future Phase |

---

## 🚀 Development Roadmap

The CMS is planned as a multi-phase system.

### Phase 1 — Foundation

**Current Phase**

* Django architecture
* Custom authentication
* Role-based access
* Core database models
* Application structure
* Initial templates and configuration

### Phase 2 — Academic Management

Planned academic management features include:

* 📚 Course and subject management
* 👨‍🎓 Student academic profiles
* 👨‍🏫 Faculty management
* 📝 Internal assessment management
* 📊 Marks and grade management
* 📅 Academic/semester organization
* 🏫 Department and batch management

### Phase 3 — Attendance & Campus Workflows

Planned features:

* ⚡ Dynamic QR-based attendance
* ⏱️ Time-limited attendance sessions
* 📱 Student QR check-in
* 📊 Attendance analytics
* 🚨 Attendance threshold notifications
* 📅 Attendance history

### Phase 4 — Analytics & Intelligence

Planned features:

* 📊 Interactive academic dashboards
* 📈 GPA and grade analytics
* 📉 Attendance trend analysis
* 🏆 Student performance rankings
* 🤖 Local AI-assisted academic analysis
* 🖼️ Automated merit/poster generation using local LLM infrastructure such as Ollama

### Phase 5 — Digital Certification

Planned features:

* 🏅 Digital merit badges
* 📜 Certificate generation
* 🔐 QR-based certificate verification
* 🔎 Public verification pages
* 🛡️ Tamper-resistant verification workflow

---

## 🛠️ Technology Stack

### Backend

* **Python 3.11+**
* **Django 5.x**

### Database

* **SQLite3** — Development
* **PostgreSQL** — Production

### Frontend

* Django Templates
* HTML5
* CSS3
* JavaScript
* Tailwind CSS / Bootstrap 5

### Planned Technologies

* Chart.js — Analytics and visualization
* Ollama — Local AI/LLM integration
* QR Code technologies — Attendance and certificate verification
* PostgreSQL — Production database

---

## 📁 Project Structure

```text
collegePortal/
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── ...
│
├── faculty/
│   ├── models.py
│   ├── views.py
│   └── ...
│
├── students/
│   ├── models.py
│   ├── views.py
│   └── ...
│
├── collegePortal/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── templates/
│   ├── base.html
│   └── ...
│
├── manage.py
├── requirements.txt
└── README.md
```

> The structure may evolve as new modules are introduced in later development phases.

---

## ⚙️ Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/unni24061-ux/collegePortal.git
cd collegePortal
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

**Windows — PowerShell:**

```powershell
venv\Scripts\Activate.ps1
```

**Windows — Command Prompt:**

```cmd
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create an Administrator

```bash
python manage.py createsuperuser
```

Follow the prompts to configure the administrator account.

### 7. Start the Development Server

```bash
python manage.py runserver
```

The application will normally be available at:

```text
http://127.0.0.1:8000/
```

---

## 🔐 User Roles

The system is designed around three primary user roles.

### 👨‍💼 Administrator

Responsible for:

* User management
* Academic configuration
* Department/course management
* System administration

### 👨‍🏫 Faculty

Designed to support:

* Subject management
* Student evaluation
* Attendance
* Academic records
* Performance monitoring

### 👨‍🎓 Student

Designed to provide:

* Personal academic information
* Subjects and courses
* Attendance records
* Marks and grades
* Performance analytics

> Some of these capabilities are planned for subsequent phases and are not necessarily available in Phase 1.

---

## 🗄️ Database Architecture

The initial database architecture is designed to support an **APJ Abdul Kalam Technological University (KTU)-style academic workflow**.

The architecture is intended to accommodate entities such as:

```text
User
 │
 ├── Student Profile
 │
 └── Faculty Profile
       │
       └── Department
             │
             ├── Course
             │
             └── Subject
                    │
                    └── Academic Records
```

The database will be expanded incrementally as academic management features are implemented.

---

## 🔮 Planned System Architecture

The long-term architecture is intended to evolve into a modular platform:

```text
                    ┌─────────────────────┐
                    │       Users         │
                    │ Admin / Faculty /   │
                    │       Student       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Django Backend    │
                    │ Authentication/RBAC │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
    ┌───────────┐        ┌───────────┐        ┌───────────┐
    │ Students  │        │  Faculty  │        │ Academic  │
    │   Module  │        │   Module  │        │  Module   │
    └───────────┘        └───────────┘        └───────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │      Database       │
                    │ SQLite / PostgreSQL │
                    └─────────────────────┘
```

Future modules such as attendance, analytics, AI services, notifications, and digital certification can be integrated without restructuring the core system.

---

## 🧪 Development Status

| Component             |        Phase 1 |
| --------------------- | -------------: |
| Project Setup         |    ✅ Completed |
| Django Configuration  |    ✅ Completed |
| Custom Authentication |    ✅ Completed |
| User Roles            |    ✅ Completed |
| Accounts App          |    ✅ Completed |
| Faculty App           |  ✅ Initialized |
| Students App          |  ✅ Initialized |
| Database Foundation   |  ✅ Initialized |
| Academic Workflow     | 🔄 In Progress |
| Attendance System     |      ⏳ Planned |
| Analytics             |      ⏳ Planned |
| AI Integration        |      ⏳ Planned |
| Digital Certificates  |      ⏳ Planned |

**Legend:**

* ✅ Completed
* 🔄 In Progress
* ⏳ Planned

---

## 🤝 Contributors

### Development Team

* **Unnikrishnan UR**
* **Adil Zaman V**

---

## 📜 Project Status

This project is currently under active development.

**Current Release:** `Phase 1 — Foundation`

Future phases will progressively introduce academic management, attendance, analytics, AI-assisted functionality, notifications, and digital certification.

---

## ⭐ Contributing

Contributions, suggestions, and improvements are welcome as the project evolves.

If you would like to contribute:

```bash
git fork
git clone <your-fork>
git checkout -b feature/your-feature
```

Implement your changes, test them locally, and submit a pull request.

---

## 📄 License

License information will be added as the project progresses.
