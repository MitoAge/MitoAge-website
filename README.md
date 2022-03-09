The MitoAge website
===================

[MitoAge website](http://www.mitoage.info) provides basic tools for the comparative analysis of mtDNA, particularly focusing on animal longevity.

This project is a valuable tool for researchers and enthusiasts. MitoAge already used and cited multiple times in peer-reviewed journals. We believe that such a database needs constant development and improvements in order to stay relevant and support aging research in this field. The project has maximum availability to the public and possibly will attract more contributors for both development and research. An intuitive and easy-to-use interface enables access to the data for users with less computational skills.

Setting up
==========

MitoAge website is written in python and based on Django.
There are two options of running mitoage website localy: with docker container and with micromamba/conda environment

To install MitoAge with micromamba or conda you should:
```
micromamba env create -n mitoage python=3.9 pip
micromamba activate mitoage
pip install -r requirements.txt 
```
You should define SECRET_KEY environment variable. 
You can use latest.dump to initialize the database.

Usage
=====

Visit the website or read the [UserGuide](https://mitoage.info/user_guide/)