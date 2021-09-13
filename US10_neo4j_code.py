###
#Query 01 
#Input: Address
#Output:hospital_name,Distance(Meter),street,house_number,postcode,city,email,tel,url
#cap_bed,rating
# Example_address: Krankenhausstraße 2, Amstetten

###
import numpy as np
import pandas as pd
from neo4j import GraphDatabase, basic_auth
import streamlit as st

st.set_page_config(page_title='SearchNearestHospital', page_icon="🖖")
st.title('Looking for a Hospital near by')
st.markdown('               __Get start with our App now at a finger click.__             ')
import base64

main_bg = "v870-tang-36.jpg" #Hospital Image Background
main_bg_ext = "jpg"

side_bg =  "v870-tang-36.jpg"
side_bg_ext = "jpg"
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

st.markdown(
    f"""
    <style>
    .reportview-container {{
        background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()})
    }}
   .sidebar .sidebar-content {{
        background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()})
    }}
    </style>
    """,
    unsafe_allow_html=True
)

query01 = '''
as myLocation
CALL apoc.spatial.geocodeOnce(myLocation) YIELD location
WITH point({longitude: location.longitude, latitude: location.latitude}) as myPosition,100 as distanceInKm
MATCH (t:HospitalType)<-[r:HAS_TYPE]-(h:Hospital)
WHERE h.lat IS NOT NULL and distance(myPosition, point({longitude:h.lon,latitude:h.lat})) < (distanceInKm * 100)
RETURN h.hospital_name as `Hospital Name`,toInteger(distance(myPosition,
       point({longitude:h.lon,latitude:h.lat}))) as `Distance(Meter)` ,h.street as Street,h.house_number as `House Number`,h.postcode as Postcode,h.city as City,h.email as Email,h.tel as Telephone, h.url as Website,h.cap_beds as `Bed Capacity`, h.geo_qual as Rating,t.name as `Hospital Type`
ORDER BY `Distance(Meter)` LIMIT 
'''
query021 = '''
MATCH (t:HospitalType)<-[r:HAS_TYPE]-(h:Hospital)-[:IS_IN]->(c:City) 
where c.name="'''
query022 = ''' RETURN h.hospital_name as `Hospital Name` ,h.street as Street,h.house_number as `House Number`,h.postcode as Postcode,h.city as City,h.email as Email,h.tel as Telephone, h.url as Website,h.cap_beds as `Bed Capacity`, h.geo_qual as Rating,t.name as `Hospital Type` LIMIT  '''
list1=['Search by Current Location','Search by Country & City','Search by Insurance Type','Hospital Statistics in Europe']


st.sidebar.title('Hospital Directory')
st.sidebar.header('')
st.sidebar.subheader("It's quick, easy and free")
st.sidebar.write('Select Option')
option = st.sidebar.selectbox(
   label='',
    options=list1
)

'You selected:', option


driver = GraphDatabase.driver(
   "bolt://3.231.105.190:7687",
  auth=basic_auth("neo4j", "rudders-weld-fluid"))
cypher_query_country= '''MATCH (c:Country) RETURN c.name order by c.name;'''
with driver.session(database="neo4j") as session:
    results = session.read_transaction(lambda tx: tx.run(cypher_query_country,limit="10").data())
    data_country=pd.DataFrame.from_dict(results)

if option=='Search by Current Location':
    # Using the "with" syntax
    submit_button01=False
    data=pd.DataFrame()
    address=st.text_input(label= ' Please Enter you address to find the nearest hospital :- ')
    with st.form(key='my_form'):
        submit_button01 = st.form_submit_button(label='Submit')
        if submit_button01==True:
            NumOfResult= 25
            cypher_query=  ''.join([ 'WITH "', address,'" ', query01, str(NumOfResult)])
            with driver.session(database="neo4j") as session:
                results = session.read_transaction(lambda tx: tx.run(cypher_query,limit="10").data())
                data=pd.DataFrame.from_dict(results)
                blankIndex=[''] * len(data)
                data.index=blankIndex
                if data.empty!=True:
                    st.write(data)
                else:
                    st.write("Sorry no result found !")
elif option=='Search by Insurance Type':
     #Final
    data=pd.DataFrame()
    submit_button01=False
    HospitalType=[]
    CountryNameI=''
    data_cityI=''
    HospitalType = st.selectbox(label='Please select the Insurance type',options=['All','Only Public','Only Private','Public','Private','Only Public & Private'] )
    CountryNameI  = st.selectbox(label='Please select the Country',options=data_country)
        
    cypher_query_cityI= ''.join([ 'MATCH (co:Country)<-[:IS_IN]-(c:City) WHERE co.name = "', CountryNameI,'" RETURN c.name order by c.name;'])
    with driver.session(database="neo4j") as session:
        results = session.read_transaction(lambda tx: tx.run(cypher_query_cityI,limit="10").data())
        data_cityI=pd.DataFrame.from_dict(results)
        CityNameI = st.selectbox(label='Please select the City',options=data_cityI)
    with st.form(key='my_form'): 
        submit_button01 = st.form_submit_button(label='Submit')
        if submit_button01==True:
            NumOfResult= 25
            if HospitalType == "Public":
                cypher_query=  ''.join([ query021,CityNameI,'" and t.name <> "private"',query022, str(NumOfResult)])
            elif HospitalType == "Private":
                cypher_query=  ''.join([ query021,CityNameI,'" and t.name <> "public"',query022, str(NumOfResult)])
            elif HospitalType == "Only Public":
                cypher_query=  ''.join([ query021,CityNameI,'" and t.name = "public"',query022, str(NumOfResult)])
            elif HospitalType == "Only Private":
                cypher_query=  ''.join([ query021,CityNameI,'" and t.name = "private"',query022, str(NumOfResult)])
            elif HospitalType == "Only Public & Private":
                cypher_query=  ''.join([ query021,CityNameI,'" and t.name = "public & private"',query022, str(NumOfResult)])
            elif HospitalType == "All":
                cypher_query=  ''.join([ query021,CityNameI,'"',query022, str(NumOfResult)])
            with driver.session(database="neo4j") as session:
                results = session.read_transaction(lambda tx: tx.run(cypher_query,limit="10").data())
                data=pd.DataFrame.from_dict(results)
                blankIndex=[''] * len(data)
                data.index=blankIndex
                if data.empty!=True:
                    st.write(data)
                else:
                    st.write("Sorry no result found. Please change the Insurance Type")
elif option=='Search by Country & City':
    #Final
    data=pd.DataFrame()
    submit_button02=False
    CountryName=''
    data_city=''
    CountryName = st.selectbox(label='Please select the Country',options=data_country)
    cypher_query_city= ''.join([ 'MATCH (co:Country)<-[:IS_IN]-(c:City) WHERE co.name = "', CountryName,'" RETURN c.name order by c.name;'])
    with driver.session(database="neo4j") as session:
        results = session.read_transaction(lambda tx: tx.run(cypher_query_city,limit="10").data())
        data_city=pd.DataFrame.from_dict(results)
        CityName = st.selectbox(label='Please select the City',options=data_city)
    
    with st.form(key='my_form'): 
        submit_button02 = st.form_submit_button(label='Submit')
        if submit_button02==True:
            cypher_query=  ''.join([ 'MATCH (t:HospitalType)<-[r:HAS_TYPE]-(h:Hospital)-[:IS_IN]->(c:City) WHERE c.name = "', CityName,'" RETURN h.hospital_name as `Hospital Name` ,h.street as Street,h.house_number as `House Number`,h.postcode as Postcode,h.city as City,h.email as Email,h.tel as Telephone, h.url as Website,h.cap_beds as `Bed Capacity`, h.geo_qual as Rating,t.name as `Hospital Type` '])
            with driver.session(database="neo4j") as session:
                results = session.read_transaction(lambda tx: tx.run(cypher_query,limit="10").data())
                data=pd.DataFrame.from_dict(results)
                blankIndex=[''] * len(data)
                data.index=blankIndex
                if data.empty!=True:
                    st.write(data)
                else:
                    st.write("Sorry no result found !")
elif option=='Hospital Statistics in Europe':  

    cypher_query= '''MATCH (h:Hospital)-[:IS_IN]->(City)-[:IS_IN]->(Country)
    RETURN Country.name as Country,count(h) as `Number Of Hospitals` 
    ORDER BY `Number Of Hospitals` desc'''
#print(cypher_query)
    with driver.session(database="neo4j") as session:
        results = session.read_transaction(lambda tx: tx.run(cypher_query,limit="10").data())
        data=pd.DataFrame.from_dict(results)
        blankIndex=[''] * len(data)
        data.index=blankIndex
#print(df)
        st.write(data)  
driver.close()





