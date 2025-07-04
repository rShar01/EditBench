import streamlit as st

# Создаем две формы для ввода данных
# В первой форме значения сохраняются в словарь form1_dict напрямую
# Во второй форме значения сохраняются в session_state и затем копируются в form2_dict

form1_dict = {}
with st.form('form1'):
    form1_dict['a'] = st.text_input('a')
    form1_dict['b'] = st.text_input('b') 
    st.form_submit_button('Submit Form 1')
st.write(form1_dict)

with st.form('form2'):
    st.text_input('a', key='form2_a')
    st.text_input('b', key='form2_b')
    st.form_submit_button('Submit Form 2')

# Создаем словарь form2_dict и копируем в него значения из session_state,
# убирая префикс 'form2_' из ключей
form2_dict = {}
for key in st.session_state:
    if key.startswith('form2_'):
        form2_dict[key.removeprefix('form2_')] = st.session_state[key]

st.write(form2_dict)

# Добавляем вывод в консоль результатов сабмита формы
print("Form 1 submission:", form1_dict)
print("Form 2 submission:", form2_dict)
