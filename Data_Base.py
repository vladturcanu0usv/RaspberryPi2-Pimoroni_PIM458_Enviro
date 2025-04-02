import psycopg2

# Example list
my_list = [1, 2, 3, 4, 5]

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(
    dbname="your_database_name",
    user="your_username",
    password="your_password",
    host="your_host",
    port="your_port"
)

# Create a cursor object
cur = conn.cursor()

def add_to_table():
# Assuming you have a table named 'my_table' with a column 'my_coRlumn' of an appropriate type (e.g., integer)
    insert_query = "INSERT INTO my_table (my_column) VALUES (%s)"

    # Insert each element of the list into the table
    for item in my_list:
        cur.execute(insert_query, (item,))

    # Commit the transaction
    conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
