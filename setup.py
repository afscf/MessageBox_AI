from setuptools import setup
import py2app

setup(
    app=["def.py"],
    data_files=["assets"],  # Add the image file here
    options={"py2app": {"resources": ["assets"]}},
)