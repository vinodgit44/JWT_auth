

# 🔐 JWT Authentication Module (FastAPI + Streamlit)

A production-ready **JSON Web Token (JWT) authentication system** implemented using **FastAPI** (backend) and **Streamlit** (client UI).
Designed to act as an **API Gateway authentication layer** for microservice-based systems such as **AeroSense RAG**.

---

## ✨ Features

* Stateless authentication using **JWT**
* Secure password hashing using **Argon2**
* Token-based authorization via `Authorization: Bearer <token>`
* Token expiration handling
* Client-side persistence using **encrypted browser cookies**
* Works across browser refreshes and multiple tabs
* Gateway-friendly design (single auth boundary)
* Easy integration with downstream microservices

---

## 🧠 Why JWT?

JWT enables **portable trust** in distributed systems:

* No server-side session storage
* Horizontally scalable
* Works across:

  * Web UIs
  * APIs
  * Microservices
  * AI / RAG pipelines
* Ideal for cloud deployments (ECS, EKS, API Gateway)

In AeroSense, JWT is enforced **only at the Gateway**, keeping internal services clean and focused.

---

## 🏗 Architecture Overview

```
Client (Streamlit / Web / API)
        |
        |  Authorization: Bearer <JWT>
        v
┌──────────────────────────┐
│  API Gateway (FastAPI)   │
│  - Verifies JWT          │
│  - Extracts user/role    │
│  - Enforces permissions  │
└───────────┬──────────────┘
            |
            v
   Internal Microservices
   (RAG, LLM, Retrieval )
```

---

## 🔐 Authentication Flow

1. User logs in with username & password
2. Password is verified using **Argon2**
3. Gateway issues a signed JWT
4. Client stores JWT securely (encrypted cookie)
5. JWT is sent with every API request
6. Gateway verifies token & allows access

No session storage. No per-request DB lookup.

---

## 🧾 JWT Payload Structure

Example payload:

```json
{
  "sub": "vinod",
  "role": "engineer",
  "permissions": ["query", "telemetry"],
  "exp": 1700000000
}
```

* `sub` → user identity
* `role` → access level
* `permissions` → fine-grained control
* `exp` → token expiration (mandatory)

---

## 📁 Project Structure

```
jwt-auth/
├── main.py        # FastAPI backend (JWT, login, protected routes)
├── app.py         # Streamlit client UI
└── README.md
```

---

## 🚀 Getting Started

### 1️⃣ Install dependencies

```bash
pip install fastapi uvicorn passlib[argon2] python-jose
pip install streamlit requests streamlit-cookies-manager
```

---

### 2️⃣ Run backend (Gateway)

```bash
uvicorn main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

---

### 3️⃣ Run frontend (Client UI)

```bash
streamlit run app.py
```

Streamlit runs at:

```
http://127.0.0.1:8501
```

---

## 🔑 Demo Credentials

```
Username: admin
Password: password123
```

*(For demo only — production systems should use a real database.)*

---

## 🔒 Security Decisions

### Passwords

* Hashed using **Argon2**
* Raw passwords are never stored or logged

### Tokens

* Short-lived access tokens
* Signed using `HS256`
* Verified on every request

### Client Storage

* JWT stored in **encrypted browser cookies**
* Survives refresh and multiple tabs
* Safer than `localStorage` for internal tools

---

## 🧩 Integration with AeroSense RAG

In AeroSense:

* JWT is enforced **only at the Gateway**
* Microservices trust the Gateway
* Identity and permissions are forwarded as headers if needed

Example Gateway protection:

```python
@router.post("/rag/query")
def query_rag(request: dict, user=Depends(get_current_user)):
    if "query" not in user["permissions"]:
        raise HTTPException(status_code=403)
    return rag_pipeline.run(request)
```

This keeps RAG, LLM, and telemetry services **auth-free and scalable**.

---

## ❓ JWT vs Session-Based Auth

| Feature              | Sessions | JWT       |
| -------------------- | -------- | --------- |
| Server state         | Required | None      |
| Horizontal scaling   | Hard     | Easy      |
| Microservices        | Poor fit | Excellent |
| Mobile / API clients | Limited  | Native    |
| Cloud readiness      | ⚠️       | ✅         |

---

## 🔮 Future Enhancements

* Refresh tokens
* Role-based access control (RBAC)
* Database-backed users
* Audit logging
* OAuth / SSO integration
* API Gateway + AWS Cognito
* Zero-trust internal service auth

---

## 🧠 Key Takeaway

> **JWT is not just “login” — it is distributed trust.**
