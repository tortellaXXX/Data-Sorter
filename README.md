# Data Sorter
<img width="707" height="473" alt="image" src="https://github.com/user-attachments/assets/3ff87fb5-55e5-454a-a777-3ea41fa96b51" />

A web application for uploading, sorting, and downloading CSV files.  
Built with **FastAPI**, **PostgreSQL**, and **Docker**.

---

## 🚀 Features

- Upload CSV files  
- Sort data by a given column  
- Download the sorted CSV  
- Persistent storage via PostgreSQL  
- Runs in Docker containers  

---

## 📁 Project Structure

```
Data-Sorter/
│   docker-compose.yml       # Docker Compose config (Postgres + FastAPI app)
│   Dockerfile               # Dockerfile for building the FastAPI app
│   requirements.txt         # Python dependencies
│   README.md                # Project documentation
│
├── app/                     # Main application package
│   ├── db/                  # Database layer
│   │   ├── models.py        # SQLAlchemy models (tables structure)
│   │   └── session.py       # Database session/engine setup
│   ├── routes/              # API routes
│   │   └── csv_routes.py    # Endpoints for CSV upload, sorting, download
│   ├── services/            # Business logic layer
│   │   └── csv_services.py  # CSV processing and database interaction
│   └── utils/               # Helper utilities
│       └── helpers.py       # Misc helper functions (temp files, IDs, etc.)
│   └── main.py              # FastAPI application entry point
│
├── static/                  # Static assets (frontend)
│   ├── script.js            # Client-side JavaScript
│   └── style.css            # Styles for HTML templates
│
└── templates/               # Jinja2 templates for HTML rendering
    ├── index.html           # Main upload form
    └── result.html          # Sorted CSV preview page

```

---

## 🛠 Prerequisites

- Docker  
- Docker Compose  

---

## 🔧 Installation & Run

1. Clone the repo:  
   ```bash
   git clone https://github.com/tortellaXXX/Data-Sorter.git
   cd Data-Sorter
   ```

2. Build and run containers:  
   ```bash
   docker-compose up --build
   ```

3. Open in browser:  
   ```
   http://localhost:8000
   ```

---

## ⚙️ Configuration

Set environment variables in `docker-compose.yml`:  

- `POSTGRES_USER` — username for PostgreSQL  
- `POSTGRES_PASSWORD` — password  
- `POSTGRES_DB` — database name  
- `DATABASE_URL` — e.g. `postgresql+psycopg2://user:password@db:5432/dbname`

---

## 🔍 API Endpoints

- **POST /sort** – upload a CSV and preview sorted data  
- **GET /download** – download the sorted CSV  

---

## 🛠 Troubleshooting

- **Connection refused to DB**  
  Web might start before DB is ready. Use `depends_on` + `healthcheck` in `docker-compose.yml`.  
- **Old schema conflict**  
  If `user_tables` exists with wrong columns, you may need to drop it or recreate DB volume.

--- 
