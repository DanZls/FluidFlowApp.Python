Install Python with PIP and PATH registration
Resume MongoDB cluster cloud.mongodb.com/v2/65d76ef7fe0abc0175605f23#/overview

python -m pip install --upgrade pip
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

.venv\Scripts\activate
python main.py

deactivate