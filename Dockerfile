FROM apache/airflow:2.5.0

# Run updates and install system packages as root
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev

# Switch to airflow user to install Python packages
USER airflow

# Copy the requirements.txt file into the container
COPY requirements.txt /opt/airflow/requirements.txt

# Install the Python dependencies listed in the requirements.txt file
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Switch back to root user to create folders and change permissions
USER root

# Copy the DAGs to the correct directory inside the container
COPY ./dags /opt/airflow/dags

# Set 777 permissions on the created folders to ensure full access
RUN chmod -R 777 /opt/airflow/dags/files