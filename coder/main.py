from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.core.embeddings import resolve_embed_model
from pydantic import BaseModel
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.query_pipeline import QueryPipeline
from dotenv import load_dotenv
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from prompts import context, code_parser_template
from code_reader import code_reader

load_dotenv()

llm = Ollama(model="mistral", request_timeout=180.0)
parser = LlamaParse(result_type="markdown")
file_extractor = {".pdf": parser}
documents = SimpleDirectoryReader("./data", file_extractor=file_extractor).load_data()
embed_model = resolve_embed_model("local:BAAI/bge-m3")
vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
query_engine = vector_index.as_query_engine(llm=llm)

tools = [
    QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="api_documentation",
            description="this gives documentation about code for an API. Use this for reading docs for the API",
        ),
    ),
    code_reader
]

code_llm = Ollama(model="codellama")
agent = ReActAgent.from_tools(tools, llm=code_llm, verbose=True, context=context)

class CodeOutput(BaseModel):
    code: str
    description: str
    filename: str

parser = PydanticOutputParser(CodeOutput)
json_prompt_str = parser.format(code_parser_template)
json_prompt_template = PromptTemplate(json_prompt_str)
output_pipeline = QueryPipeline(chain=[json_prompt_template, llm])




result = agent.query("read the contents of test.py and write a python script that calls the post endpoint to make a new item")
# next_result= output_pipeline.run(response=result)
print(result)



# response = llm.complete("What is the capital of France?")
# print(response)


