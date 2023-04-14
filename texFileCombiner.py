#This file will replace the input command in main.tex with the content of the input tex file to create one single tex file.
import os

working_folder = "/workspace/Cross-Sensor Auditing"


def replace_input_with_content(file_path):
    with open(file_path) as f:
        lines = f.readlines()
    for i in range(len(lines)):
        if not lines[i].strip().startswith("%") and "\\input{" in lines[i]:
            print(lines[i])
            folder_name = lines[i].split("{")[1].split("/")[0]
            file_name = lines[i].split("{")[1].split("/")[1].split("}")[0]
            with open(f"{working_folder}/{folder_name}/{file_name}.tex") as f2:
                content = f2.read()
            lines[i] = content
    with open(working_folder+"/one.tex", "w") as f:
        f.writelines(lines)


replace_input_with_content(working_folder + "/main.tex")
