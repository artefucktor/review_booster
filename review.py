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
    for num_section in range(len(schema)):
        section = schema[num_section]
        st.subheader(section['title'])
        group = section['option_group']
        for num_group in range(len(group)):
            option = group[num_group]
            args = [option['group_name'], ['',] + option['items']]
            kwargs = {'key': f'item_{st.session_state.run_id:03d}_{num_section:03d}_{num_group:03d}'}
            if option['control_type']=='select':
                st.selectbox(*args, **kwargs)
            else:
                st.radio(*args, **kwargs)
    submit = st.form_submit_button('ИТОГО', use_container_width=True)




# summary calculation
summary = '\n\n'.join(v for k,v in sorted(st.session_state.items())
                       if k.startswith('item') and len(v)>0) + '\n\n🤓'

rating = {}
for section in schema:
    section_name = section['title']
    rating[section_name] = {'current' : 0,
                            'max_rate': sum(w['group_weight'] for w in section['option_group'])
                           }

for k,v in st.session_state.items():
    if k.startswith('item') and len(v)>0:
        
        _, _, num_section, num_group = k.split('_')
        num_section, num_group = int(num_section), int(num_group)
        
        section_name = schema[num_section]['title']
        
        group = schema[num_section]['option_group'][num_group]
        items = schema[num_section]['option_group'][num_group]['items']

        reverse_index = len(items)-items.index(v)
        weight = group['group_weight']/(len(items)-1)*(reverse_index-1)

        rating[section_name]['current'] += weight



summary_rating = pd.DataFrame(rating).T
last_row = len(summary_rating)

summary_rating.loc[last_row] = summary_rating[['current', 'max_rate']].sum(axis=0)
summary_rating['Доля от максимального'] = summary_rating['current']/summary_rating['max_rate']

summary_rating = summary_rating.rename(
    index={last_row: 'ИТОГО'}, 
    columns={'current': 'Набрано баллов',
             'max_rate': 'Максимально возможный балл'}
)




# summary output
st.subheader('SUMMARY')

st.write(summary)
st.caption('*При необходимости – доработать ревью напильником*')

st.subheader('Результаты')
st.dataframe(summary_rating, use_container_width=True)

st.button('ОЧИСТИТЬ ФОРМУ', on_click=clear_form, use_container_width=True)

