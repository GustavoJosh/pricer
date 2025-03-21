"""
SQL queries and database operations for the Sign Business application.
"""
from .connection import DatabaseConnection

# Get the database connection instance
db = DatabaseConnection.get_instance()

# Signs CRUD operations
def get_all_signs():
    """Get all signs ordered by creation date"""
    query = """
    SELECT SignID, SignName, CustomerInfo, CreationDate, Status, TotalCost 
    FROM Signs 
    ORDER BY CreationDate DESC
    """
    return db.execute_query(query, fetchall=True)

def get_sign_by_id(sign_id):
    """Get a sign by its ID"""
    query = "SELECT * FROM Signs WHERE SignID = %s"
    return db.execute_query(query, (sign_id,), fetchone=True)

def create_sign(name, description, customer_info, status):
    """Create a new sign"""
    query = """
    INSERT INTO Signs (SignName, Description, CustomerInfo, Status) 
    VALUES (%s, %s, %s, %s)
    """
    result = db.execute_query(query, (name, description, customer_info, status), commit=True)
    if result is not None:  # None indicates error
        return db.get_connection().cursor().lastrowid
    return None

def update_sign(sign_id, name, description, customer_info, status):
    """Update a sign"""
    query = """
    UPDATE Signs 
    SET SignName = %s, Description = %s, CustomerInfo = %s, Status = %s 
    WHERE SignID = %s
    """
    return db.execute_query(query, (name, description, customer_info, status, sign_id), commit=True)

def delete_sign(sign_id):
    """Delete a sign"""
    query = "DELETE FROM Signs WHERE SignID = %s"
    return db.execute_query(query, (sign_id,), commit=True)

# Components CRUD operations
def get_components_by_sign_id(sign_id):
    """Get all components for a sign"""
    query = """
    SELECT * FROM Components 
    WHERE SignID = %s 
    ORDER BY ComponentID
    """
    return db.execute_query(query, (sign_id,), fetchall=True)

def create_component(sign_id, component_name):
    """Create a new component"""
    query = """
    INSERT INTO Components (SignID, ComponentName) 
    VALUES (%s, %s)
    """
    result = db.execute_query(query, (sign_id, component_name), commit=True)
    if result is not None:  # None indicates error
        return db.get_connection().cursor().lastrowid
    return None

def update_component(component_id, component_name):
    """Update a component"""
    query = """
    UPDATE Components 
    SET ComponentName = %s 
    WHERE ComponentID = %s
    """
    return db.execute_query(query, (component_name, component_id), commit=True)

def delete_component(component_id):
    """Delete a component"""
    query = "DELETE FROM Components WHERE ComponentID = %s"
    return db.execute_query(query, (component_id,), commit=True)

# Jobs CRUD operations
def get_jobs_by_component_id(component_id):
    """Get all jobs for a component"""
    query = """
    SELECT * FROM Jobs 
    WHERE ComponentID = %s 
    ORDER BY JobID
    """
    return db.execute_query(query, (component_id,), fetchall=True)

def get_job_by_id(job_id):
    """Get a job by its ID"""
    query = "SELECT * FROM Jobs WHERE JobID = %s"
    return db.execute_query(query, (job_id,), fetchone=True)

def get_job_by_details(job_name, unit_cost):
    """Get a job by its name and unit cost"""
    query = "SELECT JobID FROM Jobs WHERE JobName = %s AND UnitCost = %s"
    return db.execute_query(query, (job_name, unit_cost), fetchone=True)

def create_job(component_id, job_name, unit_cost, quantity):
    """Create a new job"""
    query = """
    INSERT INTO Jobs (ComponentID, JobName, UnitCost, Quantity) 
    VALUES (%s, %s, %s, %s)
    """
    result = db.execute_query(query, (component_id, job_name, unit_cost, quantity), commit=True)
    if result is not None:  # None indicates error
        return db.get_connection().cursor().lastrowid
    return None

def update_job(job_id, job_name, unit_cost, quantity):
    """Update a job"""
    query = """
    UPDATE Jobs 
    SET JobName = %s, UnitCost = %s, Quantity = %s 
    WHERE JobID = %s
    """
    return db.execute_query(query, (job_name, unit_cost, quantity, job_id), commit=True)

def delete_job(job_id):
    """Delete a job"""
    query = "DELETE FROM Jobs WHERE JobID = %s"
    return db.execute_query(query, (job_id,), commit=True)