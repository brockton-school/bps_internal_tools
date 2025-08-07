# ✨ How to Generate and Setup `personnel.csv` on App Build

This guide will walk you through the steps to generate and update the `personnel.csv` file using **MySchool** and mount it correctly in the app.

---

## 📥 Step 1: Export Data from MySchool

To export the necessary data from MySchool, follow these steps:

1. **Login to MySchool** and navigate to the **Data Reports** section in the side bar.
2. Under **Data Reports**, select the **Export** function.
3. In the export settings, ensure the following options are selected:
    - **Report Type**: Leave "User Info" selected.
    - **Format**: `.csv`
    - **Filters/Target**: Click the folder icon, then select teachers, staff, and students, under each school level (Junior, Middle, and Senior).
    - **Content/Export**:
        - `Surname`
        - `Name`
        - `School Level`
        - `Grade`
4. **Export the File** from the button in the bottum right, and save it on your computer.

---

## 📝 Step 2: Format the CSV File

Once you have exported the file, ensure that it is properly formatted with the following columns:
- **SURNAME**
- **NAME**
- **SCHOOL LEVEL**
- **GRADE**

The data should look something like this:

```csv
"SURNAME","NAME","SCHOOL LEVEL","GRADE"
"Smith","John","Junior School","Grade 3"
"Johnson","Emily","Middle School","Grade 7"
"Doe","Jane","Senior School","Grade 12"
"Brown","Michael","Junior School","Grade 5"
"James","Bob",,
```
**NOTE**: Staff Names will simply have no grade or school level (see last line). The real file will likely be alphabetical by surname, but any order is fine.

---

## 📂 Step 3: Mount the CSV File in the App

Once your `personnel.csv` file is ready, you need to mount it in the app using the `env/` directory. Follow these steps:

1. **Place the `personnel.csv` file** inside the `env/` directory of your project:
   ```
   ./env/personnel.csv
   ```
2. Double check that the `env/` directory is mounted properly in the `docker-compose.yml` file (this should already be done by default):

```yaml
volumes:
  - ./env:/app/env  # Mount the env directory containing personnel.csv
```

3. **Restart the app** after placing the updated file. The new `personnel.csv` will be loaded automatically.

---

## 🎉 You're Done!

Your app is now using the latest `personnel.csv` file. Once the app is running its best to update from the GUI at `your-app-ulr/config`.
