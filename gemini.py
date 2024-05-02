"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""

from pathlib import Path
import hashlib
import google.generativeai as genai
import json
import csv

genai.configure(api_key="AIzaSyDx5Xz5NG8aqO4aVgD9I2xuXtgO2rLsDZY")

# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

system_instruction = "for each row in the file, clean the row if there are errors and respond as a comma separated row with each entry corresponding to the clean attribute in the input row"

def compare_csvs(clean_dataset, test_dataset, cleaned_dataset):
  """
  Compares two CSV files element by element and identifies any differences.

  Args:
      csv_file1: Path to the first CSV file.
      csv_file2: Path to the second CSV file.
  """

  with open(clean_dataset, 'r', newline='') as clean, open(test_dataset, 'r', newline='') as test, open(cleaned_dataset, 'r', newline='') as cleaned:
    clean_reader = csv.reader(clean)
    test_reader = csv.reader(test)
    cleaned_reader = csv.reader(cleaned)

    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0

    # Compare each row element by element
    for clean_row, test_row, cleaned_row in zip(clean_reader, test_reader, cleaned_reader):
      for clean_element, test_element, cleaned_element  in zip(clean_row, test_row, cleaned_row):
        if clean_element != test_element:
          if clean_element == cleaned_element:
            true_positive += 1
          else:
              false_negative += 1
        else:
          if clean_element == cleaned_element:
            true_negative += 1
          else:
            print(clean_element, cleaned_element)
            false_positive += 1

    precision = true_positive / (true_positive+false_positive)
    recall = true_positive / (true_positive+false_negative)
    print(f'TP: {true_positive}, FP: {false_positive}, TN: {true_negative}, FN: {false_negative}')
    print("Precision: ", precision)
    print("Recall: ", recall)        

def get_model_output(cleaned_dataset):
  model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                generation_config=generation_config,
                                system_instruction=system_instruction,
                                safety_settings=safety_settings)

  convo = model.start_chat(history=[
    {
      "role": "user",
      "parts": ["Consider a dataset with the following columns: row_id,age,workclass,education,maritalstatus,occupation,relationship,race,sex,hoursperweek,country,income.\nHere are some examples of clean rows: 0,31-50,Private,Prof-school,Never-married,Prof-specialty,Not-in-family,White,Female,40,United-States,MoreThan50K \n1,>50,Private,HS-grad,Married-civ-spouse,Craft-repair,Husband,White,Male,16,United-States,LessThan50K \n2,>50,Private,Some-college,Married-civ-spouse,Exec-managerial,Husband,White,Male,55,United-States,MoreThan50K \n3,22-30,Private,HS-grad,Never-married,Handlers-cleaners,Own-child,White,Male,40,United-States,LessThan50K.\n\n Errors can be common typos on a qwerty keyboard, missing values and implicitly missing values ex: age = 0, as well as values replaced with values from other columns"]
    },
  ])

  prompt = "for each row in the file,check if there is an error in the row and give a clean version of the row. ? always means an error and should be replced"
  with open(test_dataset, "r") as f:
      file_content = f.read()

  prompt += file_content

  convo.send_message(prompt)
  # print(convo.last.text)

  json_data = json.loads(convo.last.text)

  with open(cleaned_dataset, 'w') as f:
      for line in json_data:
          f.write(f"{line}\n")


if __name__ == "__main__":
  cleaned_dataset = 'adults-cleaned-10.csv'
  test_dataset = "adults-dirty-10.csv"
  clean_dataset = "adults-clean-10.csv"
  # get_model_output(cleaned_dataset)
  compare_csvs(clean_dataset, test_dataset, cleaned_dataset)