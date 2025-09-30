# Data Sorter

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
│   docker-compose.yml
│   Dockerfile
│   requirements.txt
│   README.md
│
├── app/
│   ├── db/
│   │   ├── models.py
│   │   └── session.py
│   ├── routes/
│   │   └── csv_routes.py
│   ├── services/
│   │   └── csv_services.py
│   └── utils/
│       └── helpers.py
│   └── main.py
│
├── static/
│   ├── script.js
│   └── style.css
│
└── templates/
    ├── index.html
    └── result.html
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

## 📄 License

This project is licensed under the MIT License.  
