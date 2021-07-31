# Flask Demo Code - NCB Internship

To begin using this app you can do the following:

1. Clone the repository to your local machine.
2. Create a Python virtual environment e.g. `python -m venv venv` (You may need to use `python3` instead)
3. Enter the virtual environment using `source venv/bin/activate` (or `.\venv\Scripts\activate` on Windows)
4. Install the dependencies using Pip. e.g. `pip install -r requirements.txt`. Note: Ensure you have MySQL already installed and a database created.
5. Create a `.env` or `.flaskenv` (dotenv) file and enter your environmental variables (a sample file can be seen in `.env.sample`)
6. Run the migrations by typing `flask db upgrade`.
7. Start the development server using `flask run`.
