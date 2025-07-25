import subprocess
import time

def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    """Wait for PostgreSQL to become available."""
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                # capture output of command as text
                # # check=True : throws an exception if we get an error 
                ["pg_isready", "-h", host], check=True, capture_output=True, text=True)
            if "accepting connections" in result.stdout:
                print("Successfully connected to PostgreSQL")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            retries += 1
            print(f"retrying in {delay_seconds} seconds... tried {retries} so far")
        time.sleep(delay_seconds)
    print(f"reached max retries of {max_retries}, exiting")
    return False

# Use the function before running the ELT process
if not wait_for_postgres(host="source_postgres"):
    # exit(1) is used to terminate the program immediately and return an exit status code to the operating system
    exit(1)

print("Starting ELT script...")

# Configuration for the source PostgreSQL database
source_config = {
    'dbname': 'source_db',
    'user': 'postgres',
    'password': 'secret',
    # Use the service name from docker-compose as the hostname
    'host': 'source_postgres'
}

# Configuration for the destination PostgreSQL database
destination_config = {
    'dbname': 'destination_db',
    'user': 'postgres',
    'password': 'secret',
    # Use the service name from docker-compose as the hostname
    'host': 'destination_postgres'
}

# get all data from the src database into the data_dump.sql file
# Use pg_dump to dump the source database to a SQL file
# 'pg_dump' is the PostgreSQL utility used to dump (i.e., export) a database into a file
# '-h' specifies the host (the server where the PostgreSQL instance is running).
dump_command = [
    'pg_dump',
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d', source_config['dbname'],
    '-f', 'data_dump.sql',
    '-w' # Do not prompt for password
]

# Set the PGPASSWORD environment variable for src database to avoid password prompt
subprocess_env = dict(PGPASSWORD=source_config['password'])

# Execute the dump command
subprocess.run(dump_command, env=subprocess_env, check=True)

# Use psql to load the dumped SQL file into the destination database
load_command = [
    'psql',
    '-h', destination_config['host'],
    '-U', destination_config['user'],
    '-d', destination_config['dbname'],
    '-a',
    '-f', 'data_dump.sql'
]

# Set the PGPASSWORD environment variable for the dest database
subprocess_env = dict(PGPASSWORD=destination_config['password'])

# Execute the load command
subprocess.run(load_command, env=subprocess_env, check=True)

print("Ending ELT script...")