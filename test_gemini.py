import google.generativeai as genai

genai.configure(api_key="AQ.Ab8RN6KoDteaPWPr-YtfrTxsqWHandURxPfebl_CAYVFWw3PrQ")
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Say hi in one sentence")
print(response.text)