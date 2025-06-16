import datasets

from ast import literal_eval
import json

if __name__ == "__main__":
    data = datasets.load_dataset("waynechi/project-edit", split="test")
    print(data.column_names)

    other_files = data[106]['other_files']
    for file_name, file_content in other_files.items():
        print(file_name)
        print(file_content)
        print("===" * 20)