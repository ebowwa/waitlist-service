# Instructions to Use the Waitlist Service

This guide summarizes how to set up and run the waitlist microservice, based on the conversation with the LLM.

## 1. Clone and Set Up the Project
```bash
git clone https://github.com/ebowwa/waitlist-service.git
cd waitlist-service
```
Environment variables such as `DATABASE_URL`, `SUPABASE_URL`, and `SUPABASE_KEY` may be required. Refer to the README for details.

## 2. Install Dependencies
Install packages from `requirements.txt` or via `setup.py` using `pip`:
```bash
pip install -r requirements.txt
```

## 3. Provide Environment Variables
Create a `.env` file using `.env.example` as a reference. Example values:
```
DATABASE_URL=sqlite:///instance/waitlist.db
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

## 4. Run the Service
Run the FastAPI app with `uvicorn`, or use Docker Compose:
```bash
uvicorn waitlist_service.main:app --reload
```
Docker Compose exposes the service on port `3030` and provides a PostgreSQL backend.

## 5. Interact with the API
Use `POST /waitlist/register` to add users and `GET /waitlist/status/{email}` to check their status and position.

## 6. Optional Testing
Run `pytest` in the `tests/` directory to execute the included tests.

## Is This Repository a Library?
The project is primarily a FastAPI-based microservice. While it contains a `setup.py` file and can be installed, it is best viewed as an application service rather than a reusable library.
