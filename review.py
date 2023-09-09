import streamlit as st
import pandas as pd

DEFAULT_SCHEMA = 'template.csv'

st.header('Ревью за 5 минут')
st.markdown("""
<style>
    div[role="radiogroup"] > :first-child{display: none !important;}
</style>
""", unsafe_allow_html=True)

def read_template(template):
    df = pd.read_csv(template)
    schema = list()
    start_items, num_items = 4, df.shape[1]
    for section in df.section.unique():
        groups = list()
        for row in df[df.section==section].itertuples(index=False):
            option_group = {}
            option_group['group_name'] = row.group_name.upper()
            option_group['group_weight'] = row.group_weight
            option_group['control_type'] = row.control_type
            option_group['items'] = [row[col] for col in range(start_items, num_items) 
                                     if type(row[col])==str]
            groups.append(option_group)
        schema.append({'title': section.upper(),
                       'option_group': groups})
    return schema

def clear_form():
    run_id = st.session_state.run_id
    st.write(run_id)
    st.session_state.clear()
    st.session_state.run_id = run_id+1

if 'run_id' not in st.session_state:
    st.session_state.run_id = 0


# user interface
schema = read_template(st.file_uploader('Загрузите свою схему оценки', type='csv') or DEFAULT_SCHEMA)
with st.form("my_form", clear_on_submit=False):
    rate = 0
    for i in range(len(schema)):
        section = schema[i]
        st.subheader(section['title'])
        group = section['option_group']
        for k in range(len(group)):
            option = group[k]
            if option['control_type']=='select':
                st.selectbox(
                    option['group_name'],
                    ['',] + option['items'],
                    key='section'+str(i)+'_group'+str(k)+'run_'+str(st.session_state.run_id))
            else:
                st.radio(
                    option['group_name'],
                    ['',] + option['items'],
                    key='section'+str(i)+'_group'+str(k)+'run_'+str(st.session_state.run_id))
    submit = st.form_submit_button('ИТОГО', use_container_width=True)

st.subheader('SUMMARY')

summary = '\n\n'.join(v for k,v in sorted(st.session_state.items())
                       if k.startswith('section') and len(v)>0) + '\n\n🤓'
st.write(summary)
st.write('---')
st.write('*При необходимости – доработать ревью напильником*')

st.button('ОЧИСТИТЬ ФОРМУ', on_click=clear_form, use_container_width=True)

