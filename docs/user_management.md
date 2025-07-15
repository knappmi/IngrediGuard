# IngrediGuard User Management System Documentation

## Overview

The User Management System provides secure authentication, user account control, and role-based access for the IngrediGuard application. This system enables administrators to create, manage, and control access to the application's features based on user roles.

## Features

- Secure password storage using PBKDF2 with salting
- Role-based access control (Admin/Regular users)
- User account activation/deactivation
- Password management
- Database reset capability
- Session management

## Technical Architecture

### Database Schema

The user database consists of a single table with the following structure:

| Column        | Type    | Description                                  |
|---------------|---------|----------------------------------------------|
| id            | INTEGER | Primary key, auto-increment                  |
| username      | TEXT    | Unique user identifier                       |
| password_hash | TEXT    | PBKDF2 hashed password                       |
| salt          | TEXT    | Unique salt for password hashing             |
| is_admin      | INTEGER | Boolean flag for admin privileges (0 or 1)   |
| is_active     | INTEGER | Boolean flag for account status (0 or 1)     |

### Components

#### UserDatabase Class

Located in `models/user_database.py`, this class handles all database operations related to user management:

- User creation and authentication
- Password hashing and verification
- User privilege management
- Account status management
- Database initialization and reset

#### Login Screen

Located in `screens/login_screen.py`, this screen:

- Provides username and password input
- Validates credentials against the database
- Sets session information upon successful login
- Handles login errors and feedback

#### User Management Screen

Located in `screens/user_management_screen.py`, this admin-only screen provides:

- User account creation interface
- List of all users with their status and role
- Controls to toggle user admin privileges
- Controls to activate/deactivate user accounts
- Database reset functionality

## User Roles

### Admin Users

Administrators have access to:

- All regular user features
- User management screen
- Admin hub features
- Menu upload, edit, and management
- Database reset capability
- OCR settings (if enabled)

### Regular Users

Regular users have access to:

- Login screen
- Landing screen
- Menu allergen checking functionality

## Security Features

### Password Security

- Passwords are never stored in plaintext
- PBKDF2 algorithm with SHA256 for password hashing
- Unique salt generated for each password
- 100,000 iterations for increased security

### Access Control

- Screen-level access control based on user role
- Admin-only sections are not accessible to regular users
- Disabled accounts cannot authenticate

### Session Management

- User session maintained during application use
- Logout functionality with confirmation
- Session variables for user role and authentication status

## Usage Guide

### User Authentication

1. Launch the application
2. Enter username and password on the login screen
3. Application validates credentials
4. Upon successful login, users are directed to the landing screen

### Creating New Users (Admin only)

1. Navigate to Admin Hub → User Management
2. Enter username and password in the "Add New User" section
3. Toggle admin status if required
4. Click "Add User"
5. New user appears in the user list below

### Managing User Accounts (Admin only)

1. Navigate to Admin Hub → User Management
2. View list of all user accounts
3. Toggle admin status with "Make Admin"/"Remove Admin" buttons
4. Toggle account status with "Enable"/"Disable" buttons

### Logging Out

1. Click the "Log Out" button on the main screen
2. Confirm logout in the dialog
3. User is returned to the login screen

## Default Configuration

- A default admin account is created on first run with username "admin" and password "admin"
- It is recommended to change this default password after first login

## Implementation Notes

### Database Initialization

- Database is automatically created in the `app_data` directory
- Default admin user is created if no users exist
- Schema is created automatically on first run

### Security Considerations

- The system prevents disabling the last active admin account
- Database reset requires confirmation to prevent accidental data loss
- Password requirements are minimal but can be enhanced as needed

## Testing

The user management system includes a comprehensive test suite in `tests/test_user_database.py` that covers:

- User creation and authentication
- Password security
- Admin privilege management
- User status management
- Database reset functionality
- Edge cases like duplicate users and disabled accounts

## Future Enhancements

- Password complexity requirements
- Password expiration policy
- Multi-factor authentication
- User-specific allergen profiles
- Session timeout handling
