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
    """read schema"""
    df = pd.read_csv(template)
    schema = list()
    item_list = [col for col in df if col.startswith('item')]
    item_idx = [df.columns.tolist().index(item) for item in item_list]
    
    for section in df.section.unique():
        groups = list()
        for row in df[df.section==section].itertuples(index=False):
            option_group = {}
            option_group['group_name'] = row.group_name
            option_group['control_type'] = row.control_type
            option_group['group_weight'] = row.group_weight
            if 'group_class' in df:
                option_group['group_class'] = row.group_class
            option_group['items'] = [row[col] for col in item_idx if type(row[col])==str]
            groups.append(option_group)
        schema.append({'title': section,
                       'option_group': groups
                      })
    return schema

def calc_rating(dd_summary):
    """calc summary"""
    df_summary = pd.DataFrame(dd_summary).T
    last_row = len(df_summary)
    if last_row>0:
        df_summary.loc[last_row] = df_summary[['current', 'max_rate']].sum(axis=0)
        df_summary['Доля от максимального'] = df_summary['current']/df_summary['max_rate']
        
        df_summary = df_summary.rename(
            index={last_row: 'ИТОГО'}, 
            columns={'current': 'Набрано баллов',
                     'max_rate': 'Максимально возможный балл'}
        )
    return df_summary

def process_rate():
    rating = {}
    class_score = {}
    for section in schema:
        section_name = section['title']
        rating[section_name] = {'current' : 0,
                                'max_rate': sum(w['group_weight'] for w in section['option_group'])
                               }
    
        for group in section['option_group']:
            if 'group_class' in group:
                group_class = group['group_class']
                class_score[group_class] = {'current': 0,
                                            'max_rate': (group['group_weight'] if group_class not in class_score
                                                         else class_score[group_class]['max_rate']+group['group_weight'])
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
            if len(class_score)>0:
                group_class = group['group_class']
                class_score[group_class]['current'] += weight
    return rating, class_score

def clear_form():
    run_id = st.session_state.run_id
    st.session_state.clear()
    st.session_state.run_id = run_id+1

if 'run_id' not in st.session_state:
    st.session_state.run_id = 0





# user interface
schema = read_template(st.file_uploader('Загрузите свою схему оценки', type='csv', on_change=clear_form) or DEFAULT_SCHEMA)
with st.form("my_form", clear_on_submit=False):
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
    submit = st.form_submit_button('ИТОГО', use_container_width=True, help='Обновить результаты')



# summary calculation
summary = '\n\n'.join(v for k,v in sorted(st.session_state.items())
                       if k.startswith('item') and len(v)>0) + '\n\n🤓'

rating, class_score = process_rate()

summary_rating = calc_rating(rating)
summary_class = calc_rating(class_score)


# summary output
st.subheader('SUMMARY')

st.write(summary)
st.caption('*При необходимости – доработать ревью напильником*')

st.subheader('Результаты')
st.dataframe(summary_rating, use_container_width=True)
if len(class_score)>0:
    st.subheader('Скиллы')
    st.dataframe(summary_class, use_container_width=True)

st.button('ОЧИСТИТЬ ФОРМУ', on_click=clear_form, use_container_width=True)

