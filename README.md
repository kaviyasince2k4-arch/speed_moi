# SPEED MOI - Contribution Recording Web App

Welcome to **SPEED MOI**! This application is designed to quickly record wedding and traditional function contributions (Moi), print individual receipts, and manage contributions without delay.

---

## 📋 What is Built in Stage 1 & Stage 2

### Stage 1:
1. **Clean Project Structure & SQLite Database (`speed_moi.db`)**: `users`, `functions`, and `contributions` tables.
2. **Admin Authentication**: Secure login, password hashing, and `reset_password.py` script.
3. **Function Setup & Management**: Setup new wedding/function and switch functions from the Previous Functions list.

### Stage 2:
4. **Add Contribution Page**:
   - Fast manual entry fields: **Contributor Name**, **Native Place**, and **Amount**.
   - Supports English, Tamil, and all Indian languages seamlessly.
   - Automatic local date (`DD-MM-YYYY`, e.g. `06-10-2026`) and time (`hh:mm AM/PM`, e.g. `09:30 AM`) from your laptop's clock.
   - **Anti Double-Click Protection**: The "✓ Confirm & Save" button disables instantly upon click to prevent creating duplicate bills.
   - **Voice Language Selector** (remembers your choice in local storage, ready for Stage 3).
   - "Clear" button to quickly reset fields for the next person.
   - **Recent Contributions Table**: Displays the last 5 saved entries with a quick "View Bill" button.
5. **Automatic Bill ID Generator**:
   - Bill ID counter restarts at `SM-0001` for each new function and increases automatically (`SM-0002`, `SM-0003`...).
   - Number counter is maintained atomically in the database.
6. **Individual Bill (Receipt)**:
   - Traditional Indian function design with Deep Burgundy and Champagne Gold border accents.
   - Clean details: Brand `SPEED MOI`, `CONTRIBUTION RECEIPT`, Bill ID, Date & Time, Function Name, Coordinator Name, Function Date, Contributor Name, Native Place.
   - Large prominent amount in Indian currency format (e.g. `₹2,000`, `₹50,000`).
   - Thank-you message: *"Thank You. Your contribution is greatly valued."*
   - Print-optimized CSS: Designed specifically for **A5 size** (half of an A4 page). When printed, hides header and buttons and prints with crisp high-contrast black borders for laser, inkjet, or receipt printers.
   - Instant workflow buttons: **"🖨️ Print Bill"**, **"➕ Add Another Contribution"**, **"📋 View All Contributions"**, and **"🏠 Dashboard"**.
7. **All Contributions Page**:
   - Lists all saved contributions for the current function with live total contributors and total amount.

---

## 💻 How to Run on Windows (Step-by-Step for Beginners)

Follow these exact steps on your Windows computer:

### Step 1: Open Command Prompt (CMD) or PowerShell
1. Press the **Windows Key** on your keyboard.
2. Type **`cmd`** and press **Enter**.
3. Navigate to your project folder:
   ```cmd
   cd path\to\your\folder
   ```

### Step 2: Install the Required Packages
Type the following command and press **Enter**:
```cmd
pip install -r requirements.txt
```
*(This installs Flask, Werkzeug, and openpyxl).*

### Step 3: Start the Application
Type this command and press **Enter**:
```cmd
python app.py
```
You will see:
```text
Starting SPEED MOI server on http://127.0.0.1:5000
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

### Step 4: Open in Google Chrome
1. Open Google Chrome (or your preferred web browser).
2. In the address bar, type:
   ```
   http://127.0.0.1:5000
   ```
   and press **Enter**.

---

## 🧪 How to Test Stage 1

1. **First-Time Setup**:
   - The browser will show **"First-Time Setup: Create Admin Account"**.
   - Enter a username (e.g. `admin`) and a password with at least 6 characters (e.g. `admin123`).
   - Click **"Create Admin Account"**.
2. **Function Setup**:
   - You will automatically be taken to the **"Setup Function"** page.
   - Enter:
     - **Function Name**: e.g., `Murugan & Valli Wedding`
     - **Coordinator / Host Name**: e.g., `K. Murugan`
     - **Function Date**: Today's date (selected by default)
   - Click **"START CONTRIBUTION"**.
3. **Verify Active Function**:
   - You will see the function created with active ID and next Bill ID `SM-0001`.
4. **Test Navigation & Previous Functions**:
   - In the top header bar, click **"Functions"**.
   - You will see your newly created function listed in the table with status **"Currently Active"**.
   - Click **"+ Setup New Function"** to test creating a second function (e.g., `Selvam Ear Piercing`).
   - Use the **"Open"** button to switch between functions.
5. **Test Logout & Login**:
   - Click **"Logout"** in the top right corner.
   - Notice that the first-time setup form is gone, and the normal **Login** form appears.
   - Enter your username and password to log back in.
6. **Test Password Reset (If you ever forget your password)**:
   - In your Windows Command Prompt window, open a new tab or stop the server (`Ctrl + C`).
   - Run:
     ```cmd
     python reset_password.py
     ```
   - Follow the prompts to enter your username and new password.
   - Start the server again (`python app.py`) and log in with your new password!

---

## 🖨️ Thermal Receipt Printing & Silent Kiosk Mode (Windows)

SPEED MOI supports narrow thermal rolls (**80 mm default**, **58 mm**, and **A5 paper**).

### How to Check Print Preview in Google Chrome (Save as PDF)
1. On the receipt page (`/receipt/<id>`), choose your desired bill size (**Thermal 80 mm**, **Thermal 58 mm**, or **A5**).
2. Click **"🖨️ Print Bill"** (or press `Ctrl + P`).
3. In the Chrome print dialog:
   - **Destination**: Choose **"Save as PDF"** (or your thermal printer model).
   - **Paper size**: If using 80 mm, select **80mm x Receipt** (or Roll Paper 80x297mm).
   - **Margins**: Set to **None** or **Minimum**.
   - **Options**: Uncheck **Headers and footers** (so URL and date are not printed by Chrome).
4. Notice that:
   - Everything is crisp black text on white with thin clean borders.
   - There are **no dark filled blocks** (preventing ink burn and paper overheating).
   - Only the receipt bill is printed; all website headers and action buttons are completely hidden!

---

### How to Print Instantly Without Print Dialog (Chrome `--kiosk-printing`)

In busy wedding/function halls, you want the thermal printer to cut the paper immediately when you click **"Print Bill"** without stopping to show the Windows print confirmation dialog every time.

Follow these steps to set up **Silent Kiosk Printing**:

#### Step 1: Set Your Thermal Printer as Windows Default
1. Open Windows **Settings** (Win + I).
2. Go to **Bluetooth & devices** > **Printers & scanners**.
3. Click your thermal printer (e.g. *POS-80* or *TVS RP 3200*).
4. Click **"Set as default"**.

#### Step 2: Create a Chrome Shortcut for Kiosk Printing
1. Go to your Windows Desktop.
2. Right-click on your **Google Chrome** desktop icon and select **Copy**, then right-click an empty space on the desktop and click **Paste** (this creates a copy like *Google Chrome - Copy*).
3. Rename the shortcut to **`SPEED MOI - Kiosk Chrome`**.
4. Right-click **`SPEED MOI - Kiosk Chrome`** and select **Properties**.
5. In the **Shortcut** tab, look at the **Target** box. It will look like:
   ```text
   "C:\Program Files\Google\Chrome\Application\chrome.exe"
   ```
6. Add a space and `--kiosk-printing` to the very end of the line:
   ```text
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk-printing
   ```
7. Click **Apply** and then **OK**.

#### Step 3: Test It First Safely
1. **Important:** Close all open Google Chrome windows completely.
2. Launch Chrome using your new **SPEED MOI - Kiosk Chrome** shortcut.
3. Open `http://127.0.0.1:5000` and record a test contribution.
4. Click **"🖨️ Print Bill"**.
5. The receipt will immediately print on your thermal roll without any dialog pop-up!

---

## 📂 Project Files Created in Stage 1, 2 & 3

- `app.py`: Main Flask application with routes and session management.
- `database.py`: SQLite database queries and table creation.
- `reset_password.py`: Command-line script to reset forgotten admin passwords.
- `requirements.txt`: Python dependencies (`Flask`, `Werkzeug`, `openpyxl`).
- `templates/`:
  - `base.html`: Common layout with Burgundy & Gold theme and navigation.
  - `login.html`: First-time admin creation and regular login.
  - `function_setup.html`: Function setup form.
  - `previous_functions.html`: Table of all recorded functions.
  - `add_contribution.html`: Contribution recording page shell.
  - `dashboard.html`: Function overview dashboard.
- `static/css/style.css`: Traditional Burgundy & Champagne Gold styling with Indian script typography support.
- `test_stage1.py`: Automated tests verifying all Stage 1 features.
