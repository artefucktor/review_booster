import json
import streamlit as st
import pandas as pd

st.header('Ревью за 5 минут')
st.markdown('''*На что обратить внимание при беглой оценке работы*

    - как оформлены описания, структура проекта, есть ли визуализация данных
    - проведен ли EDA, насколько тщательная предобработка, есть ли фичеинжиниринг
    - качество кода, стиль, читаемость, отсутствие повторяющихся фрагментов, использование нативных методов
    - какие технологии используются (например пайплайны)
    - достигнута ли цель проекта
''')

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
            option_group['group_name'] = row.group_name
            option_group['group_weight'] = row.group_weight
            option_group['items'] = [row[col] for col in range(start_items, num_items) 
                                     if type(row[col])==str]
            groups.append(option_group)
        schema.append({'title': section,
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
schema = read_template(st.file_uploader('Загрузите свой шаблон', type='csv') or 'template.csv')
with st.form("my_form", clear_on_submit=False):
    rate = 0
    for i in range(len(schema)):
        section = schema[i]
        st.subheader(section['title'].upper())
        group = section['option_group']
        for k in range(len(group)):
            option = group[k]
            st.radio(option['group_name'],
                     ['',] + option['items'],
                     key='section'+str(i)+'_group'+str(k)+'run_'+str(st.session_state.run_id)
                     )
    submit = st.form_submit_button('ИТОГО', use_container_width=True)

st.subheader('SUMMARY')

summary = '\n\n'.join(v for k,v in sorted(st.session_state.items())
                       if k.startswith('section') and len(v)>0) + ' 🤓'
st.write(summary)
st.write('---')
st.write('*При необходимости – доработать ревью напильником*')

st.button('ОЧИСТИТЬ ФОРМУ', on_click=clear_form, use_container_width=True)

