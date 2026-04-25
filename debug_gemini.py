import google.generativeai as genai
import inspect
print('module file:', genai.__file__)
print('version:', getattr(genai, '__version__', 'unknown'))
print('has responses:', hasattr(genai, 'responses'))
print('has GenerativeModel:', hasattr(genai, 'GenerativeModel'))
print('has TextGenerationModel:', hasattr(genai, 'TextGenerationModel'))
print('has ChatCompletion:', hasattr(genai, 'ChatCompletion'))
print('has generate_content:', hasattr(genai, 'generate_content'))
print('has generate_text:', hasattr(genai, 'generate_text'))
print('has list_models:', hasattr(genai, 'list_models'))
print('dir responses:', dir(genai.responses) if hasattr(genai, 'responses') else 'no responses')
