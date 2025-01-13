# app/Dockerfile

FROM python:3.9-slim

WORKDIR /home/ubuntu/Genes_from_Space_interface

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY streamlit.py streamlit_map.py questions.py api_calls.py requirements.txt config.toml /home/ubuntu/Genes_from_Space_interface/
COPY images /home/ubuntu/Genes_from_Space_interface/images/

RUN pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit.py", "--server.port=8080", "--server.address=0.0.0.0"]