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

    tp = fp = tn = fn = 0
    imputation_tp = imputation_fn = 0

    # Compare each row element by element
    for clean_row, test_row, cleaned_row in zip(clean_reader, test_reader, cleaned_reader):
      for clean_element, test_element, cleaned_element  in zip(clean_row, test_row, cleaned_row):
        if clean_element != test_element: # actual error 
          if test_element != cleaned_element: # error detected            
            tp += 1
            if clean_element == cleaned_element: # error corrected
              imputation_tp += 1
            else:
              imputation_fn += 1
          else: # error not detected
            fn += 1
        else: # no error
          if clean_element == cleaned_element: # left unchanged
            tn += 1
          else: # error detected incorrectly
            # print(clean_element, cleaned_element)
            fp += 1

    # error detection
    precision = tp / (tp+fp)
    recall = tp / (tp+fn)
    # imputation
    imputation_accuracy = (imputation_tp+tn)/(tp+tn+fn+fp)
    print('Error Detection: ')
    print(f'TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}')
    print("Precision: ", precision)
    print("Recall: ", recall)
    print('Imputataion')
    print('TP:', imputation_tp, 'FN:', imputation_fn)
    print("Accuracy: ", imputation_accuracy)
          

def get_model_output(chat_start, test_dataset, cleaned_dataset, start_index):
  print(start_index)
  model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                generation_config=generation_config,
                                system_instruction=system_instruction,
                                safety_settings=safety_settings)

  convo = model.start_chat(history=[
    {
      "role": "user",
      "parts": [chat_start]
    },
  ])

  prompt = "for each row in the file,check if there is an error in the row and give a clean version of the row. ? always means an error and should be replaced"
  with open(test_dataset, "r") as f:
      file_content = ''.join(f.readlines()[start_index:start_index+20]) #.split('\n')

  # print(file_content)
  prompt += file_content

  convo.send_message(prompt)
  # print(convo.last.text)

  json_data = json.loads(convo.last.text)

  with open(cleaned_dataset, 'a') as f:
      for line in json_data:
          f.write(f"{line}\n")


if __name__ == "__main__":
  data = 'adults'
  data = 'hospital'
  folder = '../data_clean_datasets/datasets/'+data+'/'
  cleaned_dataset = data+'-cleaned.csv'
  test_dataset = data+"_dirty.csv"
  clean_dataset = data+"_clean.csv"
  # chat_start = "Consider a dataset with the following columns: row_id,age,workclass,education,maritalstatus,occupation,relationship,race,sex,hoursperweek,country,income.\nHere are some examples of clean rows: 0,31-50,Private,Prof-school,Never-married,Prof-specialty,Not-in-family,White,Female,40,United-States,MoreThan50K \n1,>50,Private,HS-grad,Married-civ-spouse,Craft-repair,Husband,White,Male,16,United-States,LessThan50K \n2,>50,Private,Some-college,Married-civ-spouse,Exec-managerial,Husband,White,Male,55,United-States,MoreThan50K \n3,22-30,Private,HS-grad,Never-married,Handlers-cleaners,Own-child,White,Male,40,United-States,LessThan50K.\n\n Errors can be common typos on a qwerty keyboard, missing values and implicitly missing values ex: age = 0, as well as values replaced with values from other columns"
  chat_start = "Consider a dataset with the following columns: ProviderNumber,HospitalName,Address1,Address2,Address3,City,State,ZipCode,CountyName,PhoneNumber,HospitalType,HospitalOwner,EmergencyService,Condition,MeasureCode,MeasureName,Score,Sample,Stateavg\nHere are some examples of clean rows:\n10018,callahan eye foundation hospital,1720 university blvd,,,birmingham,al,35233,jefferson,2053258100,acute care hospitals,voluntary non-profit - private,yes,surgical infection prevention,scip-card-2,surgery patients who were taking heart drugs called beta blockers before coming to the hospital who were kept on the beta blockers during the period just before and after their surgery,,,al_scip-card-2\n10018,callahan eye foundation hospital,1720 university blvd,,,birmingham,al,35233,jefferson,2053258100,acute care hospitals,voluntary non-profit - private,yes,surgical infection prevention,scip-inf-1,surgery patients who were given an antibiotic at the right time (within one hour before surgery) to help prevent infection,,,al_scip-inf-1\n10018,callahan eye foundation hospital,1720 university blvd,,,birmingham,al,35233,jefferson,2053258100,acute care hospitals,voluntary non-profit - private,yes,surgical infection prevention,scip-inf-2,surgery patients who were given the  right kind  of antibiotic to help prevent infection,,,al_scip-inf-2\n10018,callahan eye foundation hospital,1720 university blvd,,,birmingham,al,35233,jefferson,2053258100,acute care hospitals,voluntary non-profit - private,yes,surgical infection prevention,scip-inf-3,surgery patients whose preventive antibiotics were stopped at the right time (within 24 hours after surgery),,,al_scip-inf-3\n\nfor each row of the following rows, check if there is an error in the row and give a clean version of the row.\n10018,callahan eye foundation hospital,1720 university blvd,,,birmingham,al,35233,jefferson,2053258100,acute care hospitals,voluntary non-profit - private,yes,surgical infection prevention,scip-card-2,surgery patients who were taking heart drugs caxxed beta bxockers before coming to the hospitax who were kept on the beta bxockers during the period just before and after their surgery,,,al_scip-card-2\n10018,callahan eye foundation hospital,1720 university blvd,,,birmingham,al,35233,jefferson,2053258100,acute care hospitals,voluntary non-profit - private,yes,surgical infection prevention,scip-inf-1,surgery patients who were given an antibiotic at the right time (within one hour before surgery) to help prevent infection,,,al_scip-inf-1\n10018,callahan eye foundation hospital,1720 university blvd,,,birmingham,al,35233,jefferson,2053258100,acute care hospitals,voluntary non-profit - private,yes,surgical infection prevention,scip-inf-2,surgery patients who were given the  right kind  of antibiotic to help prevent infection,,,al_scip-inf-2\n10018,callahan eye foundation hospital,1720 university blvd,,,birminghxm,al,35233,jefferson,2053258100,acute care hospitals,voluntary non-profit - private,yes,surgical infection prevention,scip-inf-3,surgery patients whose preventive antibiotics were stopped at the right time (within 24 hours after surgery),,,al_scip-inf-3\n10018,callahan eye foundation hospital,1720 university blvd,,,birmingham,al,35233,jefferson,2053258100,acute care hospitals,voluntary non-profit - private,yes,surgical infection prevention,scip-inf-4,all heart surgery patients whose blood sugar (blood glucose) is kept under good control in the days right after surgery,,,al_scip-inf-4n\n Errors can be common typos on a qwerty keyboard, missing values and implicitly missing values ex: age = 0, as well as values replaced with values from other columns"

  [get_model_output(chat_start, folder+test_dataset, cleaned_dataset, i) for i in range(0, 1000, 20)]
  
  compare_csvs(folder+clean_dataset, folder+test_dataset, cleaned_dataset)