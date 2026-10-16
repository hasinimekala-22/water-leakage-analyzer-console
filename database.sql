
CREATE TABLE leakage_records (
    incident_id NUMBER PRIMARY KEY,
    location VARCHAR2(100) NOT NULL,
    leak_start TIMESTAMP NOT NULL,
    repair_time TIMESTAMP NOT NULL,
    duration_hours NUMBER(10,2),
    loss_rate NUMBER(10,2),
    water_loss NUMBER(12,2),
    leak_type VARCHAR2(50),
    priority VARCHAR2(20)
);