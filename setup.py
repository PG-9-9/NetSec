from setuptools import find_packages, setup
from typing import List

def get_requirements()->List[str]:
    """
    Get the requirements from the requirements.txt file
    """
    requirement_lst:List[str]=[]
    try:
        with open('requirements.txt','r') as file:
            # Read lines from the file
            lines=file.readlines()
            for line in lines:
                # Remove the newline character
                requirement=line.strip()
                # ignore the empty lines and -e .
                if requirement and requirement!='-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print('requirements.txt file not found')
    
    return requirement_lst

# To setup the META information about the package
setup(
    name="NetSec",
    version="0.0.1",
    author="PG-9-9",
    author_email="vishaals0507@gmail.com",
    packages=find_packages(), # Find all the packages in the directory
    install_requires=get_requirements(),
)