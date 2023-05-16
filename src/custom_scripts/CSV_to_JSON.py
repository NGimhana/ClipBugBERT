import csv
import json

# Open the CSV file and create a new JSON file
# with open('questions.csv', 'r') as csv_file, open('output.jsonl', 'w') as json_file:
#     # Create a CSV reader and skip the header row
#     csv_reader = csv.reader(csv_file)
#     next(csv_reader)

#     # Loop through each row in the CSV file
#     for row in csv_reader:
#         # Create a dictionary to hold the data
#         data = {
#             'video_id': row[0],
#             'question': row[1],
#             'answer': row[2],
#             'answer_type': row[3]
#         }

#         # convert all the characters to lowercase
#         data['question'] = data['question'].lower()
#         data['answer'] = data['answer'].lower()
#         data['answer_type'] = data['answer_type'].lower()
#         # Write the data as a JSON object to the output file
#         json.dump(data, json_file)
#         json_file.write('\n')


 
import pandas as pd

# # Read the CSV file into a pandas DataFrame
# df = pd.read_csv('questions.csv')

# # Get the unique values in the "answer" column
# unique_answers = df['answer'].unique()

# # Create a dictionary to map each unique answer to a unique integer
# answer_to_int = {answer: i for i, answer in enumerate(unique_answers)}

# # Create a JSON object from the dictionary
# json_obj = json.dumps(answer_to_int)

# # write the JSON object to a file
# with open('train_ans2label.json', 'w') as json_file:
#     json.dump(answer_to_int, json_file)

## read the file jsonl file 
PATH="/home/nadeeshan/ASE/ClipBERT/data/txt_db/rico/vqa_k_trainval.jsonl"
with open(PATH, 'r') as json_file:
    json_file = json_file.readlines()
    unique_answers = set()
    for line in json_file:
        data = json.loads(line)
        ## read  the json's labels
        answers = data['labels'].keys()
        for answer in answers:
            unique_answers.add(answer)
 
## create a dictionary to map each unique answer to a unique integer
answer_to_int = {answer: i for i, answer in enumerate(unique_answers)}   
 
## write the JSON object to a file
with open('/home/nadeeshan/ASE/ClipBERT/data/txt_db/rico/trainval_ans2label.json', 'w') as json_file:
    json.dump(answer_to_int, json_file)