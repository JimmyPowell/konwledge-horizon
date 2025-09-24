# FastAPI Project Template

This is a comprehensive template for building FastAPI applications, featuring a robust user authentication and management system.

## Features

- **User Registration**: Secure user registration flow with email verification.
- **User Login**: JWT-based authentication (`access_token` and `refresh_token`).
- **Token Refresh**: Endpoint to refresh an expired `access_token` using a `refresh_token`.
- **Secure Logout**: Server-side logout by blacklisting `refresh_token` in Redis.
- **Password Management**: Secure endpoint for changing passwords with validation.
- **Database Integration**: SQLAlchemy for ORM, with support for MySQL.
- **Cache & Blacklist**: Redis for caching and token blacklisting.
- **Configuration Management**: Centralized settings using Pydantic.
- **Email Service**: Integrated email service for sending verification codes.

## Dependencies

The project relies on the following main dependencies:

- `fastapi`: The main web framework.
- `uvicorn[standard]`: ASGI server for running the application.
- `pydantic` & `pydantic-settings`: For data validation and settings management.
- `SQLAlchemy`: For database object-relational mapping (ORM).
- `pymysql`: MySQL driver.
- `redis`: For connecting to the Redis server.
- `python-jose[cryptography]`: For handling JSON Web Tokens (JWT).
- `passlib[bcrypt]`: For hashing and verifying passwords.
- `email-validator`: For validating email formats.
- `fastapi-mail`: For sending emails.
- `python-multipart`: For handling form data (required for Swagger UI auth).

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/JimmyPowell/fastapi-project-template.git
    cd fastapi-project-template
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Configure environment variables:**
    -   Copy the `.env.example` to `.env` in the `backend` directory.
    -   Fill in your database, Redis, and email credentials in `backend/.env`.

5.  **Run the application:**
    ```bash
    cd backend
    uvicorn app.main:app --reload
    ```
    The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Authentication (`/auth`)

-   `POST /request-code`: Request a verification code to be sent to an email.
-   `POST /verify-code`: Verify the code and get a session token for registration.
-   `POST /register`: Complete the user registration process.
-   `POST /login`: Log in with username/email and password to get tokens.
-   `POST /token`: (For Swagger UI) Log in with form data to get tokens.
-   `POST /refresh`: Refresh the `access_token` using a `refresh_token`.
-   `POST /logout`: Log out by blacklisting the `refresh_token`.
-   `POST /change-password`: Change the current user's password (requires `access_token`).
