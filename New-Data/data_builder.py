import os
import json
import subprocess

count = 0
def count_files_in_dir(dir_path):
    count = 0
    for root, dirs, files in os.walk(dir_path):
        count += len(files)
    return count 

json_template = {"caption": "", "clip_name": "", "retrieval_key": ""}


def search_json_files(file_name):
    for root, dirs, files in os.walk("src/experiments/final_json"):
        for file in files:
            if file_name in file:    
                with open(os.path.join(root, file), 'r') as f:
                    json_data = json.load(f)
                    return json_data

## match the video and json files
def match_json_video_files():
    index = 0
    retrieval_key = "ret"
    for root, dirs, files in os.walk("src/experiments/videos"):
        for file in files:
            if validate_mp4_file(os.path.join(root, file)):
                common_file_name = '_'.join(file.split('.')[0].split('_')[0:3])
                if common_file_name.__contains__("issue"):
                    # load corresponding issue json file
                    issue_json = search_json_files(common_file_name)
                    ## fill the template
                    json_template["caption"] = issue_json["title"]
                    json_template["clip_name"] = ''.join(file.split('.')[0])
                    json_template["retrieval_key"] = retrieval_key + str(index)
                    index+=1
                    ## write to file
                    with open(f"src/experiments/all.jsonl", 'a') as f:
                        f.write(json.dumps(json_template) + "\n")


def copy_videos():
    for root, dirs, files in os.walk("src/experiments/videos"):
        for file in files:
            common_file_name = '_'.join(file.split('.')[0].split('_')[0:3])
            if common_file_name.__contains__("issue"):
                os.system(f"cp {os.path.join(root, file)} src/experiments/final_videos")




def validate_mp4_file(file_path):
    isValid = True
    command = ["ffmpeg", "-v", "error", "-i", file_path, "-f", "null", "-"]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        isValid = True
    except subprocess.CalledProcessError as e:
        print(f"Validation failed. Error message: {e.stderr.decode('utf-8')}")
        isValid = False
    finally:
        return isValid    

match_json_video_files()
copy_videos()
# print(count_files_in_dir("src/experiments/json"))
# print(count_files_in_dir("src/experiments/videos"))
# print(count_files_in_dir("src/experiments/final_videos"))