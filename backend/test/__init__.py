from flask_bcrypt import Bcrypt

# Initialize Bcrypt
bcrypt = Bcrypt()

# Example function to hash a password
def password(password):
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    print(password_hash)

# Call the function
password("11111111")
