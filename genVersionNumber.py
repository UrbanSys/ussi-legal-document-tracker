import subprocess

"""
Checks if the code has been modified at all
"""
def is_code_modified():
    status_output = subprocess.check_output(['git', 'status', '--porcelain']).decode('utf-8')
    if status_output.strip():
        return True

"""
Describes the current git to be used as a version number
"""
def get_git_hash():
    try:
        git_hash = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=99']).strip().decode('utf-8')

        if is_code_modified():
            git_hash += "-modified"

        return git_hash
    except subprocess.CalledProcessError:
        return "***Code not tracked by github!***"

"""
Generates a version_info.py file to have the current version number
"""
def gen_version_info():
    current_git_hash = get_git_hash()
    with open("version_info.py", "w") as f:
        f.write(f'__VERSION_TEXT__ = "{current_git_hash}"\n')
    print("Succesfully generated git version! %s"%current_git_hash)
    
if __name__ == "__main__":
    gen_version_info()