import google.generativeai as genai

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Say hi in one sentence")
print(response.text)
