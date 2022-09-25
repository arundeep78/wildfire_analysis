
import os
from src import utils

import streamlit as st
import sqlalchemy as sa

# Set page confiuration. Must be the first execution in the app/page
st.set_page_config(
   page_title="US Wildfire analysis",
   page_icon="🧊",
   layout="wide",
   initial_sidebar_state="expanded",
)


# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():

    # return psycopg2.connect(**st.secrets["postgres"])

    return sa.create_engine(f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}/{os.environ['POSTGRES_DB']}")

# Initialize Db connection
conn = init_connection()

# Load CSS to hide dataframe index column
# utils.load_css()

def main():
    """
    Sentiment analysis app based on reviews of the daily popular movies list on The moview database
    """

    
    st.title("US Wildfire analysis based on [Kaggle dataset](https://www.kaggle.com/datasets/rtatman/188-million-us-wildfires?resource=download)")
    st.markdown("---")

    #Get overall US wildfire info    
    wf_info = utils.get_us_wf_stats(conn = conn)    
    # Get county based info
    county_info = utils.get_county_stats(conn,3)
    
    # get states
    list_states = utils.get_states(conn)
  

   # -------Side bar information-----------#
    st.sidebar.write(f"#### Total US Wildfires between {wf_info['start_year']}-{wf_info['end_year']} : ",f'\n{wf_info["total_fire"]:,.2f}')
    st.sidebar.write("#### Fires per year:" ,f'\n{int(wf_info["total_fire"]/(wf_info["end_year"] - wf_info["start_year"])):,}')
    st.sidebar.write("#### Avg burned area per year:", f"\n{wf_info['total_area']/(wf_info['end_year']-wf_info['start_year']):,.2f} acres ")
    st.sidebar.write(f"#### {county_info['missing_county_pct']:,.2f} % events do not have county information!")
    st.sidebar.write("---")

    sel_state = st.sidebar.selectbox(label='Select state for individual trends', options=list_states,format_func=utils.get_state_name)

    # get start and end year for selected state
    state_years = utils.get_state_years(conn=conn, state=sel_state)
    sel_year = st.sidebar.selectbox(label = 'Year',
                                                options= list(range(*state_years))
                                        )
    
    # get fire locations info for the map component
    df_state_locs = utils.get_state_fire_locs(conn, sel_state, sel_year)

    # get state wildfire trends data
    state_wf_info = utils.get_state_wf_trend(conn, sel_state)
    df_trend = state_wf_info['data_table']
    area_rate = state_wf_info['area_coef'][0]
    count_rate = state_wf_info['count_coef'][0]

    #Build headline row
    r0c1, r0c2 = st.columns([1,1])
    
    with r0c1:
        st.write(f"""### Wildfires trend for {utils.get_state_name(sel_state)}""")
    
    with r0c2:
        st.write("### Wildfire information for all counties")
        

    #Build 1st row   
    r1c1,r1c2, r1c3 = st.columns([2,1,1])
   
    with r1c1:
                
        st.write(f"Wildfires {utils.slope_text(count_rate)} at annual rate of {count_rate:,.2f} """)

        st.line_chart(df_trend['count'],)


    with r1c2:
        st.write("Least impacted counties by count")
        st.write(county_info['bottom_by_count'].style.highlight_min(subset='count',color='green'))
        st.write("Most impacted counties by count")
        st.write(county_info['top_by_count'].style.highlight_max(subset='count',color='red'))


    # Build 2nd row
    with r1c3:
        st.write("Least impacted counties by area")
        st.write(county_info['bottom_by_area'].style.highlight_min(subset='area',color='green'))
        st.write("Most impacted counties by area")
        st.write(county_info['top_by_area'].style.highlight_max(subset='area',color='red'))


    r2c1,r2c2 = st.columns([1,1])

    with r2c1:
        st.write(f'Area burned {utils.slope_text(area_rate)} {area_rate:,.2f} acres annually')
        st.line_chart(df_trend['area'])

    with r2c2:
        st.write(f'{len(df_state_locs):,} fires happened in {utils.get_state_name(sel_state)} in year {sel_year}')
        st.map(data=df_state_locs,)

            
    st.write("----")
    # st.write("### US wildfire analysis by counties")


    
if __name__ == "__main__":
    main()

