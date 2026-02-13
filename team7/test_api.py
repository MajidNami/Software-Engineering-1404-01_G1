from openai import OpenAI
client = OpenAI(api_key="g4a-1rcT4Qz2aq7XJT_qGXaoPavi8YyDzpuYfzHPzmEa8so", base_url="https://api.gpt4-all.xyz/v1")
print(client.models.list())
