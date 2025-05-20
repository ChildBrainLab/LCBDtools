import subprocess

# Path to NDA validation tool and Image03.csv file
vtu_path = "path/to/nda-validation-tool"
csv_file = "/storage1/fs1/perlmansusan/Active/moochie/study_data/P-CAT/R56/Image03.csv"

with open("/home/claytons/.nda_creds", "r") as file:
    lines = file.readlines()
    username = lines[0].strip()  # Remove newline characters
    password = lines[1].strip()

# Run the validation tool
subprocess.run([vtu_path, "--validate", csv_file])

subprocess.run([vtu_path, "--upload", csv_file, "--username", nda_username, "--password", nda_password])