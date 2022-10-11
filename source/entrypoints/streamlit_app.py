import streamlit as st
from helpsk.database import Sqlite
from source.service.database import load_job_infos

db = Sqlite(path='data/jobs.db')
jobs = load_job_infos(database=db)
job_dict = {f"{j.company} - {j.title} - {j.location}": j for j in jobs}
jobs_to_view = job_dict

st.title('Job Openings')
with st.sidebar:
    companies_selection = st.sidebar.multiselect(
        "Companies",
        set([j.company for j in jobs])
    )
    if companies_selection:
        jobs_to_view = {k: v for k, v in jobs_to_view.items() if v.company in companies_selection}

    job_title_search = st.sidebar.text_input(
        "Job Title",
    )
    if job_title_search:
        jobs_to_view = {k: v for k, v in jobs_to_view.items() if job_title_search in v.title}

    jobs_selection = st.sidebar.selectbox(
        "Jobs",
        tuple(jobs_to_view.keys())
    )

selected_job = jobs_to_view[jobs_selection]
st.header(f"{selected_job.title}")
st.subheader(f"{selected_job.company} ({selected_job.location})")
st.markdown(f'[{selected_job.url}]({selected_job.url})')
st.markdown("""---""")
st.markdown(selected_job.description, unsafe_allow_html=True)

