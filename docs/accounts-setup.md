# 📋 User/Account Authentication Setup Guide

This guide will walk you through setting up account/device authentication for the application using a `users.csv` file. Follow the steps below to securely manage user credentials. These credentials should be treated more like device authentication than users, to prevent confusing with the acutal end-users using the app on the tablets.

## 📄 Step 1: Create the `users.csv` File

1. **Create a new file** named `users.csv` in the root directory of the application (or another location that is accessible by the app).
2. **Structure** the file as follows:

   ```
   username,hashed_password
   admin,pbkdf2:sha256:600000$example1$hashedpasswordexample1
   user1,pbkdf2:sha256:600000$example2$hashedpasswordexample2
   ```

   - Each row should represent a user.
   - The first column is the **username**.
   - The second column is the **hashed password**.

## 🔒 Step 2: Generate a Hashed Password

For security, passwords should not be stored in plain text. Instead, hash them using the following method:

1. Open a Python shell and run the following commands:

   ```python
   from werkzeug.security import generate_password_hash
   print(generate_password_hash("your_plain_text_password"))
   ```

2. Replace `"your_plain_text_password"` with the actual password you want to hash.
3. Copy the generated hash output. It will look something like this:

   ```
   pbkdf2:sha256:600000$example$9ff99db5eb881e688f8b9eb7429c4eeb2fa91a004d909bb2f1c4d46bdf16334e
   ```

4. Paste the hashed password into the `users.csv` file, like so:

   ```
   username,hashed_password
   admin,pbkdf2:sha256:600000$example$9ff99db5eb881e688f8b9eb7429c4eeb2fa91a004d909bb2f1c4d46bdf16334e
   ```

## 📦 Step 3: Make Sure the App Can Access `users.csv`

Store the `users.csv` file in the `/env` directory to ensure the conatiner has access to it.

- Restart the application to ensure the new users are loaded.

## 🚀 Step 4: Restart the Application

After setting up or updating `users.csv`, restart the application so that the new credentials take effect.

- **To restart locally:** Simply stop and start the application.
- **To restart in Docker:**

  ```bash
  docker-compose down
  docker-compose up --build
  ```

## 🛠 Example Workflow

1. **Generate a hashed password**:

   ```python
   from werkzeug.security import generate_password_hash
   print(generate_password_hash("securePassword123"))
   ```

2. **Add the user to `users.csv`**:

   ```
   admin,pbkdf2:sha256:600000$example$hashedpasswordexample
   ```

3. **Restart the app**, and you're done!

## ✨ Additional Tips

- 🔐 **Keep `users.csv` secure!** Ensure this file is not publicly accessible.
- 🔄 **Regularly update passwords** and ensure they are strong.
- 🆘 **Having issues?** Make sure the file is correctly formatted, and double-check the usernames and hashed passwords.
