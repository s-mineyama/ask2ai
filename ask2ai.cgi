#!/home/user/anaconda3/envs/py312/bin/python
import cgi
import asyncio
from google import genai
from openai import AsyncOpenAI

api = "gemini-2.5-flash"
api2 = "gpt-4o-mini"
apikey = "gemini-apikey"
api2key = "openai-apikey"

async def ask_gemini():
    global question, api, answer
    client = genai.Client(api_key=apikey)
    response = await client.aio.models.generate_content(
        model=api,
        contents=question)
    answer = response.text

async def ask_openai():
    global question, api2, answer2
    client2 = AsyncOpenAI(api_key=api2key)
    completion = await client2.chat.completions.create(
        model=api2,
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": question},
        ]
    )
    answer2 = completion.choices[0].message.content

async def main() -> None:
    global question, api, api2, answer, answer2
    print("Content-Type: text/html") # CGIヘッダーを出力

    form = cgi.FieldStorage() # フォームデータを取得
    question = form.getvalue("question", "") # question = "1+1は?"
    oldques = '−'

    if question: # 質問がある場合
        oldques = question

        chkgem = form.getvalue("nogem", "")
        chkgpt = form.getvalue("nogpt", "")
        chkedgem = chkedgpt = "checked"

        if chkgem != 'on' and chkgpt != 'on':
            chkedgem = chkedgpt = ""
            await asyncio.gather(ask_gemini(), ask_openai())
        else: # 2個同時でないとき
            answer = answer2 = ""
            if chkgem != 'on':
                await asyncio.gather(ask_gemini())
                chkedgem = ""
            if chkgpt != 'on':
                await asyncio.gather(ask_openai())
                chkedgpt = ""
    else:
        chkedgem = chkedgpt = ""
        answer = answer2 = ""

    print(f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>AIにまとめて質問</title>
    <script>
    height = window.innerHeight;
    wheight = Math.round(height / 6 * 5);
    </script>
</head>
<body style="background-color:#aaa">
<form method="post" action="">
<table style="width:100%">
    <tr>
    <td style="width:15%">
    <h2>AIに質問</h2>
    </td>
    <td style="width:85%">
        <label for="question">質問:</label>
        <input type="text" id="question" name="question" required style="width:85%;background-color:#cccccc;" placeholder="何か質問してください。">
        <input type="submit" value="Enter">
        <p>現在の質問: <span style="font-weight:bold">{oldques}</span></p>
    </td>
    </tr>
</table>
<table style="width:100%;margin-top:-20px">
    <tr>
    <td style="width:33%">
    <h3><a href="https://gemini.google.com/app?hl=ja" target="_blank">{api}</a>の回答: <input type="checkbox" id="nogem" name="nogem" {chkedgem}> スルー</h3>
    <textarea style="width:99%;height:25%;background-color:#cccccc;" id="ta">{answer}</textarea>
    </td>
    <td style="width:33%">
    <h3><a href="https://chatgpt.com/" target="_blank">{api2}</a>の回答: <input type="checkbox" id="nogpt" name="nogpt" {chkedgpt}> スルー</h3>
    <textarea style="width:99%;height:25%;background-color:#cccccc;" id="ta2">{answer2}</textarea>
    </td>
    <td style="width:33%;vertical-align:top">
    <h3>その他のサイトへのリンク</h3>
    <a href="https://felo.ai/ja/search" target="_blank">Felo</a><br>
    <a href="https://claude.ai/new" target="_blank">claude</a><br>
    </td>
    </tr>
</table>
</form>
    <script>
    document.getElementById("ta").style.height = wheight + "px";
    document.getElementById("ta2").style.height = wheight + "px";
    </script>
</body>
</html>
""")

asyncio.run(main())
