# deployment is used to list available models
# for Azure API, specify model name as a key and deployment name as a value
# for OpenAI API, specify model name as a key and a value
credentials = {
    "deployments": {"gpt-3.5-turbo": "gpt-3.5-turbo"},
    "api_key": "************************************",
    "requests_per_second_limit": 1
}