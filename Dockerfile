FROM python:3.11.9-slim
# Set the working directory in the container
WORKDIR /app
COPY . /app/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]