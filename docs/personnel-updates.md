# ✨ How to Update `personnel.csv` Using the Configuration Page

This guide will show you how to create and update the `personnel.csv` file using the **MySchool** platform and upload it through the app's configuration page.

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

## ⚙️ Step 3: Upload the CSV File Using the Configuration Page

Once your `personnel.csv` file is ready, you can update it directly through the app's configuration page.

1. **Go to the Configuration Page**:
   - Navigate to the `/config` page of the app.
   - Example: `http://your-app-url/config`
   
2. **Select the New `personnel.csv` File**:
   - Use the file upload feature on the page.
   - Click **Choose File** and select your updated `personnel.csv` file.

⚠️ **NOTE**: The following UI elements don't yet exist!
3. **Confirm Overwriting**:
   - A warning will inform you that the new file will **overwrite** the existing `personnel.csv`.
   - Confirm the action and click **Upload**.

4. **Success Message**:
   - Once the upload is complete, you will see a success message confirming that the new `personnel.csv` has been uploaded.

---

## 🎉 You’re Done!

Your app is now using the latest `personnel.csv` file. If you need to update the file again in the future, simply repeat these steps.
