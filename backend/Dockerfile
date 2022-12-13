FROM python
WORKDIR /app
COPY requirements.txt /app
RUN  pip install --upgrade pip &&  python -m pip install -r requirements.txt

COPY . /app
EXPOSE 5000

CMD [ "python", "app.py" ]