# Database Schema - ATM Maintenance Management System

## Overview

The ATM Maintenance Management System uses PostgreSQL as the database with a normalized relational schema. The schema consists of five main tables designed to handle user management, device tracking, technician assignments, maintenance submissions, and photo storage.

---

## Schema Design Principles

- **Normalization**: 3rd Normal Form (3NF) to eliminate data redundancy
- **Relationships**: Proper foreign key constraints with cascade rules
- **Indexing**: Strategic indexes on frequently queried fields
- **Timestamps**: `created_at` and `updated_at` for audit trails
- **Constraints**: Unique constraints and check constraints for data integrity

---

## Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────────┐
│    User     │       │   Technician    │
│             │       │    Device       │
│ - id (PK)   │◄──────┼─────────────────┼──────┐
│ - username  │       │ - id (PK)       │      │
│ - password  │       │ - technician (FK)│      │
│ - role      │       │ - device (FK)   │      │
│ - city      │       │                 │      │
│ - created_at│       └─────────────────┘      │
└─────────────┘                               │
                                              │
                                              │
┌─────────────┐       ┌─────────────────┐      │
│   Device    │       │   Submission    │      │
│             │       │                 │      │
│ - id (PK)   │◄──────┼─────────────────┼──────┼────┐
│ - interaction│       │ - id (PK)       │      │    │
│   _id        │       │ - technician (FK)│      │    │
│ - gfm_cost_ │       │ - device (FK)   │      │    │
│   center    │       │ - type          │      │    │
│ - status    │       │ - visit_date    │      │    │
│ - gfm_prob_ │       │ - half_month    │      │    │
│   type      │       │ - status        │      │    │
│ - gfm_prob_ │       │ - pdf_url       │      │    │
│   date      │       │ - remarks       │      │    │
│ - city      │       │ - created_at    │      │    │
│ - region    │       └─────────────────┘      │    │
│ - type      │                               │    │
│ - created_at│                               │    │
└─────────────┘                               │    │
                                              │    │
                                              │    │
┌─────────────┐       ┌─────────────────┐      │    │
│    Photo    │       │                 │      │    │
│             │       │                 │      │    │
│ - id (PK)   │◄──────┤                 │      │    │
│ - submission│       │                 │      │    │
│   (FK)      │       │                 │      │    │
│ - section   │       │                 │      │    │
│ - file_url  │       │                 │      │    │
│ - order_    │       │                 │      │    │
│   index     │       └─────────────────┘      │    │
└─────────────┘                               │    │
                                              │    │
                                              └────┘
```

---

## Table Definitions

### 1. User Table

**Purpose**: Stores user accounts with role-based access control.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing primary key |
| username | VARCHAR(150) | UNIQUE, NOT NULL | Unique username for login |
| password | VARCHAR(128) | NOT NULL | Hashed password |
| role | VARCHAR(20) | NOT NULL, CHECK(role IN ('host', 'technician', 'supervisor')) | User role |
| city | VARCHAR(100) | NULL | City assignment (NULL for host/supervisor) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

**Indexes**:
- UNIQUE index on `username`
- Index on `role` for role-based queries

---

### 2. Device Table

**Purpose**: Stores ATM device information imported from Excel files.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing primary key |
| interaction_id | VARCHAR(50) | UNIQUE, NOT NULL | Unique device identifier |
| gfm_cost_center | VARCHAR(100) | NOT NULL | Cost center information |
| status | VARCHAR(50) | NOT NULL | Device status |
| gfm_problem_type | VARCHAR(100) | NOT NULL | Problem classification |
| gfm_problem_date | DATE | NOT NULL | Problem report date |
| city | VARCHAR(100) | NOT NULL | Device location city |
| region | VARCHAR(100) | NOT NULL | Device location region |
| type | VARCHAR(20) | NOT NULL, CHECK(type IN ('Cleaning', 'Electrical')) | Maintenance type |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Indexes**:
- UNIQUE index on `interaction_id`
- Index on `city` for city-based filtering
- Index on `type` for type-based filtering
- Composite index on `(city, type)` for technician queries

---

### 3. TechnicianDevice Table

**Purpose**: Links technicians to their assigned devices.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing primary key |
| technician_id | INTEGER | FOREIGN KEY → User.id, ON DELETE CASCADE | Reference to technician |
| device_id | INTEGER | FOREIGN KEY → Device.id, ON DELETE CASCADE | Reference to device |

**Indexes**:
- UNIQUE index on `(technician_id, device_id)` to prevent duplicate assignments
- Index on `technician_id` for technician device queries

---

### 4. Submission Table

**Purpose**: Tracks maintenance submissions with approval workflow.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing primary key |
| technician_id | INTEGER | FOREIGN KEY → User.id, ON DELETE CASCADE | Submitting technician |
| device_id | INTEGER | FOREIGN KEY → Device.id, ON DELETE CASCADE | Target device |
| type | VARCHAR(20) | NOT NULL, CHECK(type IN ('Cleaning', 'Electrical')) | Maintenance type |
| visit_date | DATE | NOT NULL | Date of maintenance visit |
| half_month | INTEGER | NOT NULL, CHECK(half_month IN (1, 2)) | Half-month period (1 or 2) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'Pending', CHECK(status IN ('Pending', 'Approved', 'Rejected')) | Approval status |
| pdf_url | VARCHAR(500) | NULL | Generated PDF report URL |
| remarks | TEXT | NULL | Supervisor remarks |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Submission timestamp |

**Indexes**:
- UNIQUE index on `(technician_id, device_id, half_month)` to prevent duplicate submissions
- Index on `status` for filtering submissions
- Index on `created_at` for chronological ordering
- Composite index on `(status, created_at)` for dashboard queries

---

### 5. Photo Table

**Purpose**: Stores photo metadata for maintenance submissions.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing primary key |
| submission_id | INTEGER | FOREIGN KEY → Submission.id, ON DELETE CASCADE | Parent submission |
| section | INTEGER | NOT NULL, CHECK(section BETWEEN 1 AND 3) | Photo section (1-3) |
| file_url | VARCHAR(500) | NOT NULL | Photo file URL |
| order_index | INTEGER | NOT NULL | Photo order within section |

**Indexes**:
- Index on `submission_id` for submission photo queries
- Composite index on `(submission_id, section)` for section-based photo retrieval

---

## Data Integrity Constraints

### Unique Constraints
- `User.username`: Ensures unique usernames
- `Device.interaction_id`: Prevents duplicate device entries
- `TechnicianDevice.(technician_id, device_id)`: One assignment per technician-device pair
- `Submission.(technician_id, device_id, half_month)`: One submission per device per half-month

### Foreign Key Constraints
- All foreign keys use `ON DELETE CASCADE` to maintain referential integrity
- Ensures orphaned records are automatically cleaned up

### Check Constraints
- `User.role`: Limited to valid role values
- `Device.type`: Limited to 'Cleaning' or 'Electrical'
- `Submission.type`: Must match device type
- `Submission.half_month`: Limited to 1 or 2
- `Submission.status`: Limited to valid status values
- `Photo.section`: Limited to 1-3

---

## Performance Optimizations

### Indexing Strategy
- **Primary Keys**: Automatically indexed by PostgreSQL
- **Foreign Keys**: Automatically indexed for referential integrity
- **Query-Specific Indexes**: Added for frequently filtered fields
- **Composite Indexes**: For multi-column WHERE clauses

### Query Optimization
- Use `SELECT *` only when all columns are needed
- Implement pagination for large result sets
- Use `EXPLAIN ANALYZE` to optimize slow queries
- Consider partial indexes for status-based filtering

---

## Migration Strategy

### Initial Setup
```sql
-- Create database
CREATE DATABASE atm_maintenance;

-- Create user with permissions
CREATE USER atm_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE atm_maintenance TO atm_user;
```

### Django Migrations
- Use Django's migration system for schema changes
- Test migrations on development database first
- Backup production data before applying migrations
- Use atomic migrations for data integrity

---

## Backup and Recovery

### Backup Strategy
- Daily automated backups of production database
- Point-in-time recovery capability
- Store backups in secure, encrypted storage
- Test backup restoration regularly

### Data Retention
- Keep submission data indefinitely for audit purposes
- Implement data archiving for old photo files
- Regular cleanup of temporary files

---

This schema provides a solid foundation for the ATM Maintenance Management System with proper normalization, indexing, and constraints to ensure data integrity and performance.