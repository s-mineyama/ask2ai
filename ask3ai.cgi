#!/home/user/anaconda3/envs/py312/bin/python # 要変更
import cgi
import asyncio
from google import genai
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

api = "gemini-2.5-flash"
api2 = "gpt-4o-mini"
api3 = "claude-sonnet-4-20250514" # "claude-3-haiku-20240307"
apikey = "gemni-apikey" # 要変更
api2key = "openai-apikey" # 要変更
api3key = 'claude-apikey' # 要変更

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

async def ask_claude():
    global question, api3, answer3
    client3 = AsyncAnthropic(api_key=api3key)
    message = await client3.messages.create(
        model=api3,
        max_tokens=1000,
        system="",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question
                    }
                ]
            }
        ]
    )
    answer3 = str(message.content) # コードを文字化。前後の不要な文字列を削除
    answer3 = answer3.replace('[TextBlock(citations=None, text=\'','')
    answer3 = answer3.replace('\', type=\'text\')]','')
    answer3 = answer3.replace('\\n','&#13;') # 改行コードを修正

async def main() -> None:
    global question, api, api2, api3, answer, answer2, answer3
    print("Content-Type: text/html") # CGIヘッダーを出力

    form = cgi.FieldStorage() # フォームデータを取得
    question = form.getvalue("question", "") # question = "1+1は?"
    oldques = '−'

    if question: # 質問がある場合
        oldques = question

        chkgem = form.getvalue("nogem", "")
        chkgpt = form.getvalue("nogpt", "")
        chkcla = form.getvalue("nocla", "")
        chkedgem = chkedgpt = "checked"

        if chkgem != 'on' and chkgpt != 'on' and chkcla != 'on':
            chkedgem = chkedgpt = chkedcla = ""
            await asyncio.gather(ask_gemini(), ask_openai(), ask_claude())
        else: # 3個同時でないとき
            answer = answer2 = answer3 = ""
            if chkgem != 'on':
                await asyncio.gather(ask_gemini())
                chkedgem = ""
            if chkgpt != 'on':
                await asyncio.gather(ask_openai())
                chkedgpt = ""
            if chkcla != 'on':
                await asyncio.gather(ask_claude())
                chkedcla = ""
    else:
        chkedgem = chkedgpt = chkedcla = ""
        answer = answer2 = answer3 = ""

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
        <input type="text" id="question" name="question" required style="width:85%;background-color:#cccccc;" placeholder="何か質問してください。" autocomplete="off">
        <input type="submit" value="Enter">
        <p>現在の質問: <span style="font-weight:bold">{oldques}</span></p>
    </td>
    </tr>
</table>
<div>その他のサイト:&nbsp;&nbsp;<a href="https://felo.ai/ja/search" target="_blank">Felo</a>&nbsp;&nbsp;
<a href="https://x.com/i/grok" target="_blank">Grok</a>
</div>
<table style="width:100%;margin-top:-20px">
    <tr>
    <td style="width:33%">
    <h3><a href="https://gemini.google.com/app?hl=ja" target="_blank">{api}</a>の回答: <input type="checkbox" id="nogem" name="nogem" {chkedgem}> スルー</h3>
    <textarea style="width:99%;height:25%;background-color:#cccccc;" id="ta">{answer}</textarea>
    </td>
    <td style="width:33%">
    <h3><a href="https://chatgpt.com/" target="_blank">{api2}</a>: <input type="checkbox" id="nogpt" name="nogpt" {chkedgpt}> スルー</h3>
    <textarea style="width:99%;height:25%;background-color:#cccccc;" id="ta2">{answer2}</textarea>
    </td>
    <td style="width:33%">
    <h3><a href="https://claude.ai/new" target="_blank">{api3}</a>: <input type="checkbox" id="nocla" name="nocla" {chkedcla}> スルー</h3>
    <textarea style="width:99%;height:25%;background-color:#cccccc;" id="ta3">{answer3}</textarea>
    </td>
    </tr>
</table>
</form>
    <script>
    document.getElementById("ta").style.height = wheight + "px";
    document.getElementById("ta2").style.height = wheight + "px";
    document.getElementById("ta3").style.height = wheight + "px";
    </script>
</body>
</html>
""")

asyncio.run(main())
