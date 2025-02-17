import easyocr
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import pymysql
from PIL import Image
import numpy as np
import re

# Read image
def read_image(file):
    reader = easyocr.Reader(['en'])
    image = Image.open(file)
    result = reader.readtext(np.array(image), detail=0)
    return result

# Establish SQL connection
def connect_database():
    try:
        myconnection = pymysql.connect(host='127.0.0.1', user='root', passwd='sairam19', database='Bizcard')
        return myconnection
    except Exception as e:
        st.error(f"An error occurred while connecting to the database: {e}")
        exit(1)

myconnection = connect_database()
cursor = myconnection.cursor()

# Convert image data to binary format
def image_to_binary(file):
    file.seek(0)
    binary_data = file.read()
    return binary_data

# Extract data
def extract_data(result, input_image):
    data = {
        'Company_name': [],
        'Cardholder_name': '',
        'Designation': '',
        'Phone_number': '',
        'Email': '',
        'Website': [],
        'Area': [],
        'City': [],
        'State': [],
        'Pincode': '',
        'Image': image_to_binary(input_image)
    }
    data['Designation'] = result[1]
    if data['Designation'] in result:
        result.remove(data['Designation'])
    
    for text in result:
        text_lower = text.lower()
        if '@' in text_lower:
            data['Email'] = text
        elif text_lower.startswith('www') or text_lower.startswith('http') or text_lower.endswith('.com'):
            data['Website'].append(text)
        elif '-' in text:
            data['Phone_number'] = text
        elif 'st' in text_lower and ',' in text:
            parts = [part.strip() for part in text.split(',') if part.strip()]
            if len(parts) >= 3:
                data['Area'].append(parts[0].strip())
                data['City'].append(parts[1].strip())
                data['State'] = parts[2].replace(';', ' ').strip()
            elif len(parts) >= 2:
                data['Area'].append(parts[0].strip())
                data['City'].append(parts[1].replace(';',' ').strip())        
        elif re.findall('^[0-9].+, [a-zA-Z]+', text):
            data['Area'].append(text.split(',')[0])
        elif re.findall('[0-9] [a-zA-Z]+', text):
            data['Area'].append(text)
            data['Area'].append(result[-1].replace(',',' ').strip())
        elif re.findall('^[E].*', text):
            data['City'].append(text.replace(',',' ').strip())
        elif re.findall('[a-zA-Z]{9} +[0-9]', text):
            data['State'].append(text[:9])
            data['Pincode'] = text[10:]
        elif re.search(r'\b\d{6,7}\b', text_lower):
            data['Pincode'] = re.search(r'\b\d{6,7}\b', text_lower).group()    
        else:
            if not data['Cardholder_name']:
                data['Cardholder_name'] = text
            else:
                data['Company_name'].append(text)
    
    # Join list items to make them a single string
    data['Company_name'] = ' '.join(data['Company_name']).strip()
    data['Website'] = ' '.join(data['Website']).strip()
    data['Area'] = ' '.join(data['Area']).strip()
    data['City'] = ' '.join(data['City']).strip()
    data['State'] = ' '.join(data['State']).strip() 
 

    return data

# Create table and insert data into the database
def card_table(data):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BizCard (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Company_name VARCHAR(255),
            Cardholder_name VARCHAR(255),
            Designation VARCHAR(255),
            Phone_number VARCHAR(50),
            Email VARCHAR(255) UNIQUE,
            Website VARCHAR(255),
            Area VARCHAR(255),
            City VARCHAR(255),
            State VARCHAR(255),
            Pincode INT,
            Image LONGBLOB       
        )
    ''')
    
    query = '''
    INSERT INTO BizCard (Company_name, Cardholder_name, Designation, Phone_number, Email, Website, Area, City, State, Pincode, Image)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        Company_name = VALUES(Company_name),
        Cardholder_name = VALUES(Cardholder_name),
        Designation = VALUES(Designation),
        Phone_number = VALUES(Phone_number),
        Website = VALUES(Website),
        Area = VALUES(Area),
        City = VALUES(City),
        State = VALUES(State),
        Pincode = VALUES(Pincode),
        Image = VALUES(Image)
    '''
    
    cursor.execute(query, (
        data['Company_name'], data['Cardholder_name'], data['Designation'], 
        data['Phone_number'], data['Email'], data['Website'], 
        data['Area'], data['City'], data['State'], data['Pincode'], data['Image']
    ))
    myconnection.commit()

# Check if the card details already exist in the database
def check_card(email):
    try:
        # Check if the table exists
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'Bizcard' AND table_name = 'BizCard'")
        if cursor.fetchone()[0] == 1:
            cursor.execute('SELECT * FROM BizCard WHERE Email = %s', (email,))
            result = cursor.fetchone()
            return result
        else:
            return []
    except Exception as e:
        st.error(f"An error occurred while fetching existing channel IDs: {e}")
        return []

# Streamlit code
st.set_page_config(page_title="Bizcard", layout="wide")
st.header(':orange[BizCardX: Extracting Business Card Data with OCR]')

with st.sidebar:
    selected = option_menu("Menu", ["Home", "Upload & Extract", "Alter Data"], 
        icons=['house', 'cloud-upload', 'crop'], menu_icon="menu-button"
       )

if selected == "Home":
    st.write(" ")
    st.markdown("### :blue[Tools Used:] Pandas, MySQL, Streamlit, OCR")
    st.markdown("### :blue[About the Project:] This project allows users to upload business card images, extract text data, and store it in a MySQL database. Users can also view, edit, and delete the stored data through the application.")

if selected == "Upload & Extract":
    input_card = st.file_uploader(accept_multiple_files=False, label='Select an image to proceed', type=['png', 'jpg', 'jpeg'])
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        button1 = st.button(':blue[Upload to SQL]')
    with col2:
        button2 = st.button(':blue[View Card]')    
    with col3:
        button3 = st.button(':blue[View Extracted Data]')

    if input_card is None and button1:
        st.warning("Please upload a business card to continue")
    elif input_card is not None:
        extracted_text = read_image(input_card)
        extracted_data = extract_data(extracted_text, input_card)
        if button1:
            result = check_card(extracted_data['Email'])
            if result:
                st.warning("The card details already exist in the database.")
            else:
                card_table(extracted_data)
                st.success("Data uploaded to SQL successfully!")
        if button2:
            st.image(input_card, caption="Uploaded Business Card", use_column_width=True)
        if button3:
            st.dataframe(pd.DataFrame([extracted_data]))
            st.write(extracted_text)

if selected == "Alter Data":
    option = st.radio("Select an option:", ['View Details', 'Edit Details', 'Delete Details'])
       
    if option == 'View Details':
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'Bizcard' AND table_name = 'BizCard'")
        if cursor.fetchone()[0] == 1:
            cursor.execute('SELECT * FROM BizCard')
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['id','Company_name', 'Cardholder_name', 'Designation', 'Phone_number', 'Email', 'Website', 'Area', 'City', 'State', 'Pincode', 'Image'])
            # Convert Pincode column to string to avoid comma formatting
            df['Pincode'] = df['Pincode'].astype(str)  
            st.dataframe(df)  
        else:
            st.warning('No details available')        

    elif option == 'Edit Details':
        email = st.text_input('Enter the email of the card to edit')
        field = st.selectbox('Select the field to edit', ('Company_name', 'Cardholder_name', 'Designation', 'Phone_number', 'Website', 'Area', 'City', 'State', 'Pincode'))
        new_value = st.text_input(f'Enter new value for {field}')
        if st.button('Update'):
            cursor.execute(f'UPDATE BizCard SET {field} = %s WHERE Email = %s', (new_value, email))
            myconnection.commit()
            st.success('Details updated successfully')
    elif option == 'Delete Details':
        email = st.text_input('Please enter registered email to proceed')
        if st.button('Delete'):
            cursor.execute('DELETE FROM BizCard WHERE Email = %s', (email,))
            myconnection.commit()
            st.success('Bizcard is deleted successfully')

myconnection.close()
