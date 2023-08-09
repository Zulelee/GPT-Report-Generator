import streamlit as st
import pandas as pd
from langchain import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
import os
import openai

openai.api_key = "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"


# llm = OpenAI(openai_api_key="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", model="gpt-3.5-turbo-16k",
#              temperature=0.5)
# llm = ChatOpenAI(openai_api_key="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", model="gpt-3.5-turbo-16k",
#                  temperature=0.5)


def filter_data(dataDF, s_date, e_date, c_id):
    dataDF['session_date'] = dataDF['session_date'].dt.date
    condition = (dataDF['session_date'] >= s_date) \
                & (dataDF['session_date'] <= e_date) \
                & (dataDF['EI_number'] == c_id)
    filtered_data = dataDF[condition]
    return filtered_data


st.title("Report Generator")
st.divider()
start_date = st.date_input("Enter start date")
end_date = st.date_input("Enter end date")
client_id = st.text_input("Enter client ID")

button1 = st.button("Question 2")
button5 = st.button("Question 5")

# You are an expert assistant that can answer questions based on the child session data of 3 months.

template = '''
Question : Based on your on-going assessment of the child, what is the overall progress in this child’s functional abilities since the last IFSP
meeting or Progress Report? How was progress determined (e.g. standardized instrument, checklist, non-standardized 
assessments, observation & informed clinical opinion)?


The 3 months' data is as following:
{data}

The response should be according to the following instructions:
- Give a detailed description or specific examples of the child's current skills.
- Mention any new skills that have been achieved in the last 3 months.
- Have the parents' expressed any new concerns or priorities for the next IFSP period?

'''
# prompt = PromptTemplate(
#     input_variables=["data"],
#     template=template,
# )

template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert assistant that can answer questions based on the child session data of 3 months."),
    ("human", "{data}")
])
if start_date and end_date and client_id:
    client_id = int(client_id)
    if button1:
        df = pd.read_excel('data.xlsx')
        # filtering data
        data = filter_data(df, start_date, end_date, client_id)
        # st.write(df.dtypes)
        st.write("Answer to question 2:")
    elif button5:
        st.write("Answer to question 5:")
        df = pd.read_excel('data.xlsx')
        # filtering data
        data = filter_data(df, start_date, end_date, client_id)
        information = ''
        for index, row in data.iterrows():
            information = information + "Date: " + str(row['session_date']) + "\n" + "Describe: " + \
                          str(row['describe']) + "\n" + " Additional: " + str(row['additional'])

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert assistant that can answer questions based on the child session data of 3 months."
                },
                {
                    "role": "user",
                    "content": '''Question : Based on your on-going assessment of the child, what is the overall
                               progress in this child’s functional abilities since the last IFSP meeting or Progress
                               Report? How was progress determined (e.g. standardized instrument, checklist,
                               non-standardized assessments, observation & informed clinical opinion)?'''
                },
                {
                    "role": "user",
                    "content": "The 3 months' data is as following:" + information
                },
                {
                    "role": "user",
                    "content": '''The response should be according to the following instructions:
                    - Give a detailed description or specific examples of the child's current skills.
                    - Mention any new skills that have been achieved in the last 3 months.
                    - Have the parents' expressed any new concerns or priorities for the next IFSP period?
                    '''
                }
            ]
        )
        response = completion.choices[0].message
        st.write(response)

else:
    st.error("All the fields are required!")
