# Finance PM (Personal Finance Manager)

## Video Demo
https://youtu.be/IaupHlegp_o


## Overview

Finance PM is a personal finance management web application designed to help users track their incomes, expenses, transfers, and view summarized financial reports. The project focuses on simplicity, clarity, and usability while covering core financial management functionality. It allows users to organize their financial data by accounts and categories, monitor recent transactions, and analyze reports based on stored data.

This project was built as a learning-oriented yet practical application, emphasizing clean architecture, clear separation of concerns, and persistent state management using local storage and a lightweight database. Finance PM demonstrates how a small but complete finance system can be implemented using a structured backend and a responsive frontend.

---

## Features

- Account management with balances and currencies
- Income and expense tracking with categories
- Transfers between accounts
- Recent transactions overview
- Reports section with multiple report types
- Persistent filtering using localStorage
- Clean and responsive UI
- SQLite database for lightweight persistence

---

## Technology Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, Jinja2 templates, Bootstrap
- **State Persistence:** localStorage (for UI filters and dates)

The choice of SQLite was intentional due to its simplicity, zero-configuration nature, and suitability for small to medium-sized applications. Flask was selected as the backend framework because it provides flexibility and clarity without unnecessary overhead.

---

## Project Structure and File Descriptions

### `app.py`

This is the main Flask application file. It defines all routes, initializes the SQLite database connection, and controls the overall application flow. Routes are separated by responsibility, such as accounts, incomes, expenses, transfers, and reports. The dashboard route aggregates data and passes it to templates.

Key responsibilities:
- Application initialization
- Route definitions
- Database queries
- Passing data to templates

---

### `templates/layout.html`

This file serves as the base layout for all pages. It contains the shared HTML structure, including the header, navigation, and Bootstrap imports. Other templates extend this file to ensure consistency across the application.

Design choice:
Using a base layout avoids duplication and ensures a unified look and feel across all pages.

---

### `templates/index.html`

The main dashboard view. It displays:
- A list of accounts and their balances
- Action cards for incomes, expenses, and transfers
- A table of recent transactions
- A link to the reports section

Recent transactions are styled dynamically based on transaction type (income or expense), improving visual clarity.

---

### `templates/incomes.html` and `templates/expenses.html`

These files handle listing and managing incomes and expenses respectively. Each transaction includes:
- Name
- Amount
- Category
- Date
- Type indicator

The `type` field is used to differentiate incomes and expenses at both the database and UI level, simplifying queries and styling logic.

---

### `templates/transfers.html`

This template manages transfers between accounts. Transfers update balances in two accounts simultaneously, ensuring consistency. Special care was taken to validate inputs and prevent invalid transfers.

Design consideration:
Transfers are handled separately from incomes and expenses to avoid ambiguity and maintain accurate reporting.

---

### `templates/reports.html`

The reports page provides access to four different report types, each linked via a card-based UI. Filters such as owners and register dates are stored in `localStorage` to persist user selections across page reloads.

This approach avoids unnecessary backend complexity while maintaining a smooth user experience.

---

### `static/`

Contains CSS styles and icons used throughout the application. Custom classes such as `text-green` and `text-red` are used to visually distinguish transaction types.

---

## Database Design

The SQLite database includes the following core tables:
- `accounts`
- `incomes`
- `expenses`
- `categories`
- `transfers`

Each transaction record contains a `type` field to clearly identify whether it is an income or an expense. This design simplifies reporting and recent transaction queries.

Design choice:
Instead of separate tables for every transaction type, shared fields were normalized where possible to reduce redundancy.

---

## Design Decisions and Trade-offs

One important design decision was to use `localStorage` for UI-level state such as filters and selected dates. This avoids excessive backend calls and keeps the interface responsive. While this approach is not suitable for multi-user synchronization, it is appropriate for a personal finance manager.

Another decision was keeping the UI logic simple and explicit. Function names in the frontend and backend were kept consistent to prevent UI breakage and improve maintainability.

The application intentionally avoids overengineering. Features such as authentication or advanced analytics were excluded to keep the scope focused and the codebase understandable.

---

## Conclusion

Finance PM is a complete and functional personal finance management system that demonstrates practical full-stack development principles. It balances simplicity with real-world usability and provides a solid foundation for further expansion, such as user authentication, cloud storage, or advanced financial analytics.

This project reflects careful planning, clear structure, and thoughtful design choices, making it both a strong learning exercise and a useful application.
