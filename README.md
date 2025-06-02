# README for STR2025 Finance Application

## Project Overview
STR2025 is a web-based finance application built using Flask. It allows users to manage their stock portfolio, including functionalities for buying and selling shares, viewing transaction history, and checking stock quotes.

## Features
- User registration and login
- Buy and sell shares of stocks
- View portfolio with current cash and total cash
- Transaction history display
- Stock quote lookup

## Technologies Used
- Flask: A lightweight WSGI web application framework.
- MySQL: A relational database management system for storing user and stock data.
- HTML/CSS: For front-end design and layout.
- Bootstrap: For responsive design.

## Setup Instructions

### Prerequisites
- Python 3.x
- MySQL Server
- MySQL Connector for Python

### Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd STR2025
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the MySQL database:
   - Ensure that your MySQL server is running.
   - Create a database named `finance`.
   - Update the database connection settings in `app.py` to match your MySQL configuration.

### Running the Application
1. Start the Flask application:
   ```
   python app.py
   ```

2. Open your web browser and go to `http://127.0.0.1:5000`.

## Usage
- Register a new account or log in with an existing account.
- Use the navigation bar to access different functionalities such as buying stocks, viewing your portfolio, and checking stock quotes.

## Notes
- Ensure that the MySQL server is running and the database is created before running the application.
- Modify the `requirements.txt` to include `mysql-connector-python` for MySQL support.

## License
This project is licensed under the MIT License.