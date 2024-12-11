FROM python:3.10
RUN apt update
RUN apt install -y libgl1-mesa-glx
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code
CMD ["python", "main.py"]