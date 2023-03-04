
CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);


CREATE TABLE Patients (
    Username VARCHAR(255),
    Salt BINARY(16),
    Hash BINARY (16),
    PRIMARY KEY (Username)
);

CREATE TABLE Appointments (
    appointment_id VARCHAR(50) PRIMARY KEY,
    patient_username VARCHAR(255) REFERENCES Patients(Username),
    caregiver_username VARCHAR(255) REFERENCES Caregivers(Username),
    Time date,
    vaccine_name VARCHAR(255) REFERENCES Vaccines(Name)
);