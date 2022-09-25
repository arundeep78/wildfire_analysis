#! /bin/bash 

# Simple helper script to download data file from kaggle.
# API token is configured in .json file.
# based on assumpton that this dataset has only 1 file
dataset_name="rtatman/188-million-us-wildfires"
t_file_name="wildfires_us.sqlite"

path="db/"

{
if [ -f "${path}${t_file_name}" ]; then
    echo "File already exists."
    exit 0
fi
}

kaggle datasets files "${dataset_name}" -v > names.txt

readarray -t names_csv < names.txt
# remove temporary file
# rm names.txt

IFS=","

read -ra names <<<  "${names_csv[1]}"

echo "Downloading file ${names[0]}"

kaggle datasets download -d ${dataset_name} -p ${path} --unzip

echo "rename file ${names[0]} to ${t_file_name}"

mv "${path}${names[0]}" "${path}${t_file_name}"
