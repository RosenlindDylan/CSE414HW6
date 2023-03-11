from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import random

'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # delimit tokens and pass individually
    # throw exceptions starting with length
    if len(tokens) != 3:
        print("Failed to create user.")
        return
    
    username = tokens[1]
    password = tokens[2]

    if (username_exists_patient(username)):
        print("Username taken, try again!")
        return
    
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return
    
    if not passwordCheck: return 

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)

def passwordCheck(password):
    # At least 8 characters.
    # A mixture of both uppercase and lowercase letters.
    # A mixture of letters and numbers.
    # Inclusion of at least one special character, from “!”, “@”, “#”, “?”.
    containsUpper == False
    containsLower == False
    for char in password:
        if char.isupper():
            containsUpper = True
        if char.islower():
            containsLower = True

    containsInt = False
    containsChar = False
    for char in password:
        if char.isdigit():
            containsInt = True
        if char.isalpha():
            containsChar = True

    specialcharacters = "!@#?"
    containsSC = False
    for char in password:
        if char in specialcharacters:
            containsSC = True
    
    if len(password) < 8:
        print('Please write a password of at least 8 characters')
        return False
    elif (not containsUpper):
        print('Please include an uppercase letter')
        return False
    elif (not containsLower):
        print('Please include a lowercase letter')
        return False
    elif (not containsInt):
        print('Please include an integer')
        return False
    elif (not containsChar):
        print('Please include a character')
        return False
    elif (not containsSC):
        print('Please include a special character')
        return False
    else:
        return True




def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

# check if there exists a patient with the inputted username
def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

# login functionality for patient
def login_patient(tokens):
    # login_patient <username> <password>
    # check if someones already logged in
    # !! doesn't it have to be both? they dont have this in caregiver but right?
    global current_patient
    global current_caregiver
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check token length
    if len(tokens) != 3:
        print("Login failed.")
        return
    
    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient

def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver

    # search caregiver and vaccine to determine when caregivers and vaccines available
    # params: date, vaccine name
    # returns: caregiver_username and number of doses available
def search_caregiver_schedule(tokens):
    global current_patient
    global current_caregiver

    # prelim check user login
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    
    #  check the length of tokens
    if len(tokens) != 2:
        print("Please try again!")
        return
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    
    # fixing the tokens parameter
    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    d = datetime.datetime(year, month, day)
    
    # querying the availabilities db
    select_username = "SELECT Username AS Caregiver_Username FROM Availabilities WHERE Time = %s" + " ORDER BY Username"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, d)
        for row in cursor:
            print(row)
    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error:", e)
        quit()
    except Exception as e: # do i need this exception?? write incorrect format exception?
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()

    # do i not close it earlier or is this chill
    cm = ConnectionManager()
    conn = cm.create_connection()
    
    # printing out the vaccine db
    select_doses = "SELECT Name AS Vaccine_Name, Doses FROM Vaccines"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_doses)
    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error:", e)
        quit()
    except Exception as e: # do i need this exception??
        print("Please try again!")
        print("Error:", e)
    finally:
        for row in cursor:
            print(row)
        # print the projected tuples
        cm.close_connection()

# params: date, vaccine name
# allow patient to reserve a vaccine of the name param on date param
# update the doses of that vaccine and availability of caregiver on date
# choose caregiver by alphabetical order
# insert into Appointments table
# return assigned caregiver and the appointment ID for the reservation
def reserve(tokens):
    # prelim check if patient logged in, not caregiver
    global current_patient
    global current_caregiver
    if current_patient is None and current_caregiver is not None:
        print('Please login as a patient!')
        return
    elif current_patient is None:
        print('Please login first!')
        return
    
    #  check the length of tokens
    if len(tokens) != 3:
        print("Please try again g!")
        return
    
    # establish db connection
    cm = ConnectionManager()
    conn = cm.create_connection()

    # delimit the tokens
    date = tokens[1]
    vaccine_name = tokens[2]

    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    d = datetime.datetime(year, month, day)

    vaccine = None
    day_availability = "SELECT Username FROM Availabilities WHERE Time = %s" + " ORDER BY Username"

    cursor = conn.cursor(as_dict=True)
    cursor.execute(day_availability, d)
    username = ""

    # sorry this is terrible lol
    for row in cursor:
        username = row.get('Username')
        break

    if len(username) == 0:
        print("No caregivers available!")
        return
    
    doses = 0
    get_vaccine = "SELECT Doses FROM Vaccines WHERE Name = %s"
    try:
        cursor.execute(get_vaccine, vaccine_name)
        for row in cursor:
            print(row)
            doses = row.get('Doses')
    except pymssql.Error:
        print("Error occurred when getting Vaccine")
        raise
    
    if doses == 0:
        print("No doses available p!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()

    # after this point everythings chill so you can make any adjustments
    update = ("DELETE FROM Availabilities WHERE Username = %s" + " AND Time = %s")
    cursor.execute(update, (username, d))
    conn.commit()
    
    vaccine = Vaccine(vaccine_name, doses)
    vaccine.decrease_available_doses(1)

    randID = random.randint(100,999)

    appointment_id = username + current_patient.username + str(randID)
    patient_username = current_patient.username
    caregiver_username = username
    Time = d

    # update appts
    update_appts = ("INSERT INTO Appointments VALUES (%s, %s, %s, %s, %s)")
    cursor.execute(update_appts, (appointment_id, patient_username, caregiver_username, Time, vaccine_name))
    conn.commit()

    # print reciept
    print('Appointment ID: {' + appointment_id + '}, Caregiver username: {'+ username + '}')


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")

def show_appointments(tokens):
    global current_caregiver
    global current_patient

    # prelim checks
    if current_patient is None and current_caregiver is None:
        print('Please login first!')
        return
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    
    if current_caregiver is not None:
        # query db for all
        caregiver_appointments = "SELECT appointment_id, patient_username, Time, vaccine_name FROM Appointments WHERE caregiver_username = %s"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(caregiver_appointments, current_caregiver.username)
        except pymssql.Error as e:
            print("Please try again!")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Please try again!")
            print("Error:", e)
        finally:
            for row in cursor:
                print(row)
            cm.close_connection()

    cm = ConnectionManager()
    conn = cm.create_connection()
    
    if current_patient is not None:
        # query db for all
        patient_appointments = "SELECT appointment_id, caregiver_username, Time, vaccine_name FROM Appointments WHERE patient_username = %s"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(patient_appointments, current_patient.username)
            for row in cursor:
                print(f"{row['appointment_id']} {row['vaccine_name']} {row['Time']} {row['patient_username']}")
        except pymssql.Error as e:
            print("Please try again!")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Please try again!")
            print("Error:", e)
        finally:
            cm.close_connection()

# theres no parameters why is there tokens?? swag
def logout(tokens):
    global current_patient
    global current_caregiver

    if current_caregiver is None:
        print('Please login first')
        return
    if current_patient is None:
        print('Please login first!')
        return
    
    current_caregiver = None
    current_patient = None
    print("Successfully logged out!")


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)done 
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1) done
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2) just test some more/reread spec
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2) done
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
