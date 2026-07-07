# Selenium IDE to SmartRetry: Complete Walkthrough

This guide explains how to use the Selenium IDE Chrome extension to record your web interactions and automatically import them into the SmartRetry Framework without writing any code.

## Step 1: Install the Recorder
1. Open Google Chrome.
2. Go to the Chrome Web Store and search for **Selenium IDE** (or click [this link](https://chrome.google.com/webstore/detail/selenium-ide/mooikfkahbdckldjjndijceileamjick)).
3. Click **Add to Chrome** to install the extension.

## Step 2: Record Your Actions
1. Click the **Selenium IDE** extension icon in your Chrome toolbar (it looks like a blue "Se").
2. A popup window will appear. Select **"Record a new test in a new project"**.
3. Enter a project name (e.g., "Flipkart Tests") and click **OK**.
4. You will be prompted for a **Base URL**. Enter the starting URL, like `https://www.flipkart.com`, and click **Start Recording**.
5. A new Chrome window will open. Simply interact with the website naturally!
   - Search for a product.
   - Click links or buttons.
   - Wait for pages to load.
6. When you are finished, switch back to the Selenium IDE window and click the red **Stop Recording** button (top right).
7. Give your test a name (e.g., "Add to Cart Flow") and click **OK**.

## Step 3: Save the Recording (.side file)
1. In the Selenium IDE window, click the **Save** button (floppy disk icon) in the top right menu bar.
2. It will download a file ending in `.side` to your computer (e.g., `Flipkart_Tests.side`). This file contains all your recorded clicks and actions.

## Step 4: Import into SmartRetry
1. Open the SmartRetry application (`http://localhost:8080`).
2. Navigate to **Projects** and open your target project (e.g., Flipkart).
3. Click **New Test Case** (or edit an existing one).
4. On the right side of the Step Builder, look for the **Steps** panel and click the green **<i class="bi bi-upload"></i> Import .side** button.
5. Select the `.side` file you just downloaded.
6. **Magic!** The framework will instantly parse the file and translate all your recorded `open`, `click`, and `type` commands into native SmartRetry steps complete with locators and values.

## Step 5: Execute the Test
1. Save the Test Case.
2. Go to the **Dashboard** or **Quick Run** page.
3. Select your project and click **Execute**.
4. The SmartRetry Engine will now launch its automated browser and replay your recorded actions exactly as you performed them. If any steps fail, the framework's flaky detection engine will retry them and capture evidence automatically!
