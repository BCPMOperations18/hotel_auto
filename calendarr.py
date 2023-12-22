from playwright.sync_api import Playwright, sync_playwright, expect
import time
from bs4 import BeautifulSoup
from bs4.element import Tag
import re
import pandas as pd
import os.path
import sys 

from datetime import datetime,timedelta

def generate_tag(hotel_name, room_type):
  # Remove ", a" from hotel name
  hotel_name = hotel_name.replace(", a", "")
  if "Hilton Vacation Club" or "Resort" in hotel_name:
      # Abbreviate hotel name and append "HVC" suffix
      hotel_name = hotel_name.replace("Hilton Vacation Club", "VC_HVC")
      hotel_name = hotel_name.replace("Resort", "Rst")
  else:
      # Only replace "Resort" with "Rst" abbreviation if "Hilton Vacation Club" is not in the name
      hotel_name = hotel_name.replace("Resort", "Rst")
  hotel_name = hotel_name.replace('&', 'and')
  # Replace spaces with underscores
  hotel_name = hotel_name.replace(' ', '_')
  # Replace spaces with underscores in room type
  room_type = room_type.replace(' ', '_')
  # Generate and return the tag
  return f"{hotel_name}_{room_type}"




resort_name = []
date = []
night = []
roomtype = []
max_p = []
point = []
property_id = []
us_states = [
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
    'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia',
    'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
    'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
    'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri',
    'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
    'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
    'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina',
    'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
    'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
]

def run(playwright: Playwright) -> None:
    browser = playwright.firefox.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(100000)
    page.goto("https://loginsso.hiltongrandvacations.com/account/signin?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3Dmembers%26response_type%3Dcode%2520id_token%2520token%26scope%3Dopenid%2520profile%2520api1%2520offline_access%26state%3DOpenIdConnect.AuthenticationProperties%253DCrFufWJuzO2OBaS_kn2vALueLLC23pBwWUFe6zJi76Z4m86LNbGud_zmRjGrHTigKX0_0JlvUndzSK2r1iyH9OkEpNjsa5NGRn3ss12PnG86SgX2e8_MlstmpcOKPtrFKvIBwZrcsKGqd4l21JcfckOAVJ5epT2017bk_Th7eWqQolgwI9Wo-fwRaKya8MCXNjgQxPGG-d8jl6I9L0_m5oVs47aVoSzzODQLrrqvcD5HSWJodnhOamjHPFWmowEQ7aevYUKY0d1WG2X3JHgH3Uol9aqBuqPiPN-M0xX2vfxDTjQD%26response_mode%3Dform_post%26nonce%3D638370182870457885.NTc3N2VhODQtM2ZmMC00OTRmLTlkOTAtMzEyM2Q0MzNmYTk2Y2UxOTQzZTktMjQxZC00MGZlLWEyMTktOTRkMGFjOWFmYzdl%26rpid%3DHgvMax%26redirect_uri%3Dhttps%253A%252F%252Ftheclub.hiltongrandvacations.com%252Fsignin-oidc%26post_logout_redirect_uri%3Dhttps%253A%252F%252Ftheclub.hiltongrandvacations.com%26x-client-SKU%3DID_NET451%26x-client-ver%3D5.3.0.0")
    print('Going to hilton url.......')
    sys.stdout.flush()
    page.wait_for_load_state('load')
    page.locator("div").filter(has_text="Member Login Login Login Support Need To Register? Forgot Username? Forgot Passw").nth(1).click()
    page.get_by_placeholder("Username").click()
    page.get_by_placeholder("Username").fill("DVCONTACT")
    time.sleep(1)
    page.get_by_placeholder("Password").click()
    page.get_by_placeholder("Password").fill("frlnC43%$!")
    time.sleep(1)
    page.get_by_role("button", name="Login").click()
    page.wait_for_load_state('load')
    print('Logged in to hilton!')
    sys.stdout.flush()
    for i in range(2):
        page.mouse.wheel(0,100)
        time.sleep(3)
        
    time.sleep(2)
    for state in us_states:
        try:
            print(f'Checking for data availability in {state}.......')
            sys.stdout.flush()
            page.locator('[placeholder="Type in Destination: Property, City, State, Region, Country or Continent"]').fill(f"{state}")
            time.sleep(3)
            page.keyboard.press('Escape')

            time.sleep(4)
            input_field = page.locator('//*[@id="Booking_NightCount"]')

            # If the element is found, type "2" into it
            if input_field.is_visible():
                input_field.fill('2')
            else:
                print('Element not found.')
                
            time.sleep(4)
                
            days_field = page.locator('//*[@id="Booking_ArrivalPlusMinus"]')

            # If the element is found, type "2" into it
            if days_field.is_visible():
                days_field.fill('31')
            else:
                print('Element not found.')
                
            time.sleep(4)

            submit_button = page.locator('//*[@id="submit"]')

            if submit_button.is_visible():
                submit_button.click()
            else:
                print("Submit button not found or not visible.")
            time.sleep(2)
            time.sleep(50)
            
            
            page.get_by_text("Refine Results").click()
            print(f'results found for {state}')
            sys.stdout.flush()
            page.get_by_label("HVC Property").check()
            page.get_by_label("Managed").check()

            page.get_by_text("Apply Filters", exact=True).click()
            
            time.sleep(10)

            html = page.content()
            
            id_list = []

            pattern = r'#rowDetails-(\w+-\w+)'

            s = BeautifulSoup(html, 'html.parser')
            result_rows = s.find('div', id='results-container').find_all('div',class_='right')
            for item in result_rows:
                matches = re.findall(pattern, str(item))
                details = matches[0] if matches else None
                id_list.append(details)
            print(id_list)
            
            for i in id_list:
                page.locator(f"#rowHeader-{i}").get_by_text("View Choices").click()
                time.sleep(2)
                
            print(f'scraping data for {state}')
            sys.stdout.flush()
            html2=page.content()
            s = BeautifulSoup(html2, 'html.parser')
            listings = s.find('div',id='results-container').find_all('div',class_='rs-single-row')
            
            for i in listings:

                title = i.find('div',class_='rs-row-header-title box-field-header').text.strip()
                pattern = r"SearchBase\.bookItem\('(\w+-\w+-\d+)'\)"

                table_rows = i.find_all('div', class_='rs-TableRow')

                # Extract data from each row
                for row in table_rows:
                    # Extract data from specific cells within each row
                    date_range = row.find('div', class_='rs-cell-0').strong.text.strip()
                    date.append(date_range)
                    nights = row.find('div', class_='rs-cell-1').text.strip()
                    night.append(nights)
                    room_type = row.find('div', class_='rs-cell-2').a.text.strip()
                    roomtype.append(room_type)
                    max_people = row.find('div', class_='rs-cell-3').text.strip()
                    max_p.append(max_people)
                    points = row.find('div', class_='rs-cell-5').text.strip()
                    point.append(points)
                    book_button = row.find('div', class_='rs-cell-6').a.text.strip()
                    a_n = row.find('div', class_='rs-cell-6').find('a', class_='blue-button')
                    match = re.search(pattern, str(a_n))
                    resort_name.append(title)


                    details = match.group(1) if match else None
                    property_id.append(details)
            df = pd.DataFrame({
                'hotel_name':resort_name,
                'date_range': date,
                'nights':night,
                'room_type':roomtype,
                'max_people':max_p,
                'points':point,
                'bookit': book_button
            
                            
            })
            df['tag'] = df.apply(lambda row: generate_tag(row['hotel_name'], row['room_type']), axis=1)
                
            print('first dffffff :',df)
            sys.stdout.flush()
            
            df.to_csv('HHospitable.csv',index=False)
            print('data_saved')
            sys.stdout.flush()
            
            
            # calculations for price to upload
            
            price_per_point = 0.16
            no_of_nights = 2
            desired_profit = 15
            
            df['numeric_points'] = df['points'].replace('[^\d.]', '', regex=True)

            # Step 2: Convert the column to numeric values
            df['numeric_points'] = pd.to_numeric(df['numeric_points'], errors='coerce')


            df['price_points'] = df['numeric_points'] * price_per_point
            
            # calculating total

            df['total'] = no_of_nights*desired_profit + df['price_points']

            df['price_to_upload'] = 0.23+(df['total']/no_of_nights)
            
            
            
            df[['start_date', 'end_date']] = df['date_range'].str.split(' - ', expand=True)

            # Convert 'start_date' and 'end_date' to datetime format
            df['start_date'] = pd.to_datetime(df['start_date'], format='%d-%b-%Y')
            df['end_date'] = pd.to_datetime(df['end_date'], format='%d-%b-%Y')

            # Convert 'start_date' and 'end_date' to the desired format
            df['start_date'] = df['start_date'].dt.strftime('%d-%m-%Y')
            df['end_date'] = df['end_date'].dt.strftime('%d-%m-%Y')

            # Group by 'date_range' and reset index
            grouped_df = df.groupby(['start_date', 'end_date']).agg(list).reset_index()

            selected_columns = ['start_date', 'end_date', 'room_type', 'price_to_upload', 'tag']

            result_df = grouped_df[selected_columns]
            
            
            print(result_df.tag)  
        
        

            today = datetime.now()

            today = today.strftime('%d-%m-%Y')




            start_column = 8
            page = context.new_page()
            page.set_default_timeout(100000)
            page.goto("https://my.hospitable.com/")
            page.set_default_timeout(100000)
            page.wait_for_load_state('load')
            page.get_by_placeholder("username@example.com").click()
            page.get_by_placeholder("username@example.com").fill("omoviesmith@gmail.com")
            page.get_by_placeholder("*********").click()
            page.get_by_placeholder("*********").fill("@A1511091323z")
            page.get_by_role("button", name="Login", exact=True).click()
            print('Logging in to hospitable.....')
            sys.stdout.flush()
            time.sleep(10)
            page.set_default_timeout(100000)
            page.goto("https://my.hospitable.com/calendar/occupancy")
            page.set_default_timeout(60000)  

            #implementing update property

            room_price_mapping = {}

            for index, row in result_df.iterrows():
                original_start_date = row['start_date']  
                original_end_date = row['end_date']  
                room_types = row['room_type']
                tags = row['tag']
                prices = row['price_to_upload']

                mapping_for_date_range = dict(zip(zip(room_types, tags), prices))

                # Store the mapping in the main dictionary with the date range as the key
                room_price_mapping[(original_start_date, original_end_date)] = mapping_for_date_range


            for date_range, mapping in room_price_mapping.items():
                start_date, end_date = date_range
                print(f'Updating prices from {start_date} to {end_date}')
                sys.stdout.flush()
                for (room, tag), price in mapping.items():
                    print(f" Updating Room: {room}, with Tag: {tag}, and Price: {price}")
                    sys.stdout.flush()
                    try:
                        page.get_by_role("button", name="+ Filter properties").click()
                        page.get_by_role("menuitem", name="Tag").click()
                        time.sleep(5)
                        page.get_by_placeholder("Search").click()
                        time.sleep(4)
                        page.get_by_placeholder("Search").fill(f"{tag}")
                        time.sleep(5)
                        page.get_by_role("menuitem", name=f"{tag}",exact=True).click()
                        time.sleep(5)
                        html = page.content()
                        s = BeautifulSoup(html,'html.parser')
                        parent_div = s.find('div', class_='calendar-right')

                        immediate_child_divs = [child for child in parent_div.contents if isinstance(child, Tag)]

                        no_of_divs = len(immediate_child_divs)

                        start_date_dt = datetime.strptime(start_date, '%d-%m-%Y')
                        end_date_dt = datetime.strptime(end_date, '%d-%m-%Y')
                        today = datetime.now()
                        
                        # Check if start_date is in the past or today
                        if start_date_dt <= today:
                            print("Start date is in the past or today. Adjust your logic.")
                        else:
                            days_difference = abs((today - start_date_dt).days)
                            absolute_nights = abs((end_date_dt - start_date_dt).days)

                        
                        page.locator(f".property-dates > div:nth-child({start_column+days_difference})").first.click()
                        time.sleep(2)
                        page.locator(f"div:nth-child({no_of_divs}) > div:nth-child({start_column+days_difference+absolute_nights})").click()
                        time.sleep(2)
                        print(f'Selected data from {start_date} to {end_date}')
                        sys.stdout.flush()
            
                        checking_radio_button = page.get_by_label('Available').is_checked()
                        
                        htm = page.content()

                        s2 = BeautifulSoup(htm, 'html.parser')
                        input_element = s2.select_one('div [placeholder]')

                        # Extract the placeholder value
                        if input_element:
                            placeholder_value = input_element['placeholder']

                        placeholder_value = input_element.get('data-placeholder')
                        
                        if checking_radio_button :
                            page.get_by_placeholder(f"{placeholder_value}").fill(f"{price}")
                            print(f'updated price as ${price}')
                            sys.stdout.flush()
                            time.sleep(5)
                            page.mouse.wheel(0,500)
                            time.sleep(2)
                            page.get_by_role("button", name="Save").click()
                            time.sleep(7)
                            print(f'Update Saved')
                            sys.stdout.flush()
                            
                            page.goto('https://my.hospitable.com/calendar/occupancy')
                            time.sleep(7)
                        else:
                            #page.get_by_label('Available').click()
                            page.locator("label").filter(has_text="Available").click()
                            page.get_by_placeholder(f"{placeholder_value}").fill(f"{price}")
                            time.sleep(5)
                            page.mouse.wheel(0,500)
                            time.sleep(2)
                            page.get_by_role("button", name="Save").click()
                            time.sleep(7)
                            page.goto('https://my.hospitable.com/calendar/occupancy')
                            time.sleep(7)
                    except Exception as e:
                        page.goto('https://my.hospitable.com/calendar/occupancy')
            
                        time.sleep(10)
                        with open(f'error file_{tag}.txt','w',encoding='UTF-8') as file:
                            file.write(f'Tag {tag} is not available')
        except Exception as e:
            print(f'No data available for {state}')
            with open(f'data not available for {state}.txt','w',encoding='UTF-8') as file:
                file.write('No data')
    context.close()
    browser.close()


with sync_playwright() as playwright:
        run(playwright)
