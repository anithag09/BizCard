# BizCardX: Extracting Business Card Data with OCR

## Project Overview
BizCardX is a Streamlit application designed to extract and manage business card data using Optical Character Recognition (OCR) technology. The project leverages EasyOCR for text extraction, MySQL for database management, and Streamlit for the interactive user interface.

## Tools Used
- **Pandas**: Data manipulation and analysis
- **MySQL**: Database management
- **Streamlit**: Interactive web applications
- **OCR**: Optical Character Recognition for text extraction

## About the Project
This project allows users to upload business card images, extract text data, and store it in a MySQL database. Users can also view, edit, and delete the stored data through the application.

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- MySQL server
- Required Python packages: easyocr, streamlit, pandas, pymysql, numpy

### Step-by-Step Guide

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
    ```
2. **Install the required Python packages as listed in Prerequisites**:
    ```bash
    pip install -r required packages
    ```
3. **MySQL Setup**
    ```bash
    CREATE DATABASE Bizcard;
    ```
4. **Configure MySQL Connection**    
    Update the MySQL connection parameters (host, user, password, database) in the connect_database function within the script.

5. **Run the Streamlit Application**   
    Run the Streamlit app using the following command:
    ```bash
    streamlit run Bizcard.py
    ```

## Usage

**Home Page**   
    The home page provides an overview of the tools used and information about the project.

**Upload & Extract**

1. Upload an Image

- Select an image file (PNG, JPG, JPEG) to upload.
- Click Upload to SQL to extract and store the data in the database.
- Click View Card to view the uploaded image.
- Click View Data to view the extracted data.

2. Data Extraction and Storage

- The uploaded image is processed using EasyOCR to extract text.
- The extracted data is then stored in the MySQL database.

**Alter Data**

    1. View Details

    - View all stored business card details in a tabular format.
    
    2. Edit Details

    - Enter the email of the card to edit.
    - Select the field to edit and provide the new value.
    - Click Update to save the changes.
    
    3. Delete Details

    - Enter the registered email to delete the corresponding card details.
    - Click Delete to remove the card from the database.    


## Code Overview

**Reading Image**
- The read_image function uses EasyOCR to read text from the uploaded image.

**SQL Connection**
- The connect_database function establishes a connection to the MySQL database.

**Extract Data**
- The extract_data function processes the OCR results and maps them to the appropriate fields.

**Create Table and Insert Data**
- The card_table function creates the BizCard table if it doesn't exist and inserts or updates data in the table.

**Streamlit Application**
- The Streamlit application provides an interactive interface for uploading images, viewing extracted data, and managing stored data.

## Closing the Database Connection
Ensure to close the database connection after completing operations:
```python
myconnection.close()