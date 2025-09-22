import pandas as pd
import requests
from langchain.prompts import PromptTemplate
from langchain_experimental.utilities import PythonREPL
import streamlit as st
import matplotlib.pyplot as plt
import os

class PandasAgent():
    
    import pandas as pd
    import requests
    from langchain.prompts import PromptTemplate
    from langchain_experimental.utilities import PythonREPL
    
    def __init__(self, api_key: str, model: str, df: pd.DataFrame):
        self._model = model
        self._api_key = api_key
        self._df = df

        os.makedirs('data', exist_ok=True)

        self._df_path = f"data/{st.session_state['session_id']}.csv"
        self._df.to_csv(self._df_path, index=False)
        self.response = None 

        self._prompt = PromptTemplate.from_template(
            template = """
            You are a data scientist assistant and must strictly answer only those queries that are related to the data. In case of any unnecessary queries reply "I don't know"
            From the given dataframe: `{df}`
            Reason the following query: {query}
            Include code as well. (code given should be compatabile with markdown format).
            Your response to the query should be strictly in the form of as follows:
            1. Code Snippet (Assume that the dataset is already imported and is contained by the variable `df`, Make necessary imports except `pandas`)
            2. Short description about the code snippet
            3. Sample Output
            """
        )
        
        self.runner = PythonREPL()
        
    @staticmethod
    def list_available_models(api_key):
        try:
            response = requests.get(
                url="https://aihub-vvitu.social/api/ollama-api/models",
                headers={
                    'API-KEY': api_key
                }
            )
            response.raise_for_status() # Raise an exception for bad status codes
            return [model['name'] for model in response.json().get('models', [])] 
            
        except requests.exceptions.RequestException as e:
            print(f"Error occurred during API request: {e}")
            return f"Error occurred: {e}"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return f"An unexpected error occurred: {e}"
    
    def set_df(self, df: pd.DataFrame):
        self._df = df
        self._df.to_csv(self._df_path, index=False)
    
    def set_model(self, model: str):
        self._model = model
    
    def update_df(self):
        self._df = pd.read_csv(self._df_path)
        st.session_state['content'] = self._df.to_string()
        
    def chat(self, query: str):
        try:
            prompt_str = self._prompt.invoke({'df': self._df.head().to_string(), 'query': query}).to_string().strip()
            response = requests.post(
                url="https://aihub-vvitu.social/api/ollama-api/generate/",
                headers={
                    'API-KEY': self._api_key
                },
                json={
                    "model": self._model,
                    "prompt": prompt_str
                }
            )
            response.raise_for_status()
            self.response = str(response.json().get('response', 'No response field in result.'))
            return self.response
            
        except requests.exceptions.RequestException as e:
            print(f"Error occurred during API request: {e}")
            return f"Error occurred: {e}"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return f"An unexpected error occurred: {e}"
    
    def get_code(self):
        if self.response: 
            code_blocks = self.response.split("```")
            return ''.join([code.strip("python") for code in code_blocks if code.startswith('python')])
            
    def run_code(self):
        imports_code = f"""import pandas as pd
df = pd.read_csv('{self._df_path}')"""
        code_to_run = imports_code + self.get_code() + f"\ndf.to_csv('{self._df_path}', index=False)"
        output = self.runner.run(code_to_run)

        if len(output) == 0:
            output = "Executed Successfully"

        if "plt.show()" in code_to_run:
            plt.savefig(f"data/{st.session_state['session_id']}.png")
            output = None        

        self.update_df()
        return output
