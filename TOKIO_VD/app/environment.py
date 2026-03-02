"""
Read execution arguments and environment variables.

This file can also be imported as a module and expose variables.
"""
import os
# from dotenv import load_dotenv, find_dotenv

# # Environment type
# CLOUD_EXECUTION = os.getenv('CLOUD_EXECUTION', False)

# if not CLOUD_EXECUTION:
#     # Load environment variables from a .env file
#     load_dotenv(find_dotenv())

# Strategy's Name
STRATEGY_NAME = os.getenv("STRATEGY_NAME","SEGMENTACIÓN DE AGENTES")
# Must end with .csv
FILE_NAME_TO_DOWNLOAD = os.getenv('FILE_NAME_TO_DOWNLOAD', 'Base agentes segmentada.csv')

# # Name of datbase's model S3  migi-test/auto/PREDICT/IN/...
# # TODO: Search rename database with the date.   
# PATH_ROUTH = os.getenv('PATH_ROUTH' , "sura_thec_dic_2024.csv")

# # Path of training model in S3 example "dev/Mac_independientes"
# PATH_MODEL  = os.getenv("PATH_MODEL", "sura_thec_dic_2024")

# #Contact_history 
# CH = os.getenv('CH' , None)
# #Flag new version migi
# NEW_VERSION=  os.getenv('NEW_VERSION' , True)

# # MIGI TEST'S url
# if NEW_VERSION:
#     URL_MIGI_TEST_START = os.getenv("URL_MIGI_TEST_START", "https://api-migi-back.analiticagrupokonectacloud.com/migi/v1/inference")
#     BUCKET= os.getenv("BUCKET", "s3-migi-v2-dev")
#     URL_MIGI_TEST_STATUS = os.getenv("URL_MIGI_TEST_STATUS", "https://api-migi-back.analiticagrupokonectacloud.com/migi/v1/inference/status")


# else:

#     URL_MIGI_TEST_START = os.getenv("URL_MIGI_TEST_START", "https://api-migi.analiticagrupokonectacloud.com/testMIGI")
#     BUCKET= os.getenv("BUCKET", "trained-models-predict")
#     URL_MIGI_TEST_STATUS =  None



