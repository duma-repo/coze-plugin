from runtime import Args
from typings.video2audio.video2audio import Input, Output

import requests
from moviepy.editor import VideoFileClip
import os
from openai import OpenAI

"""
Each file needs to export a function named `handler`. This function is the entrance to the Tool.

Parameters:
args: parameters of the entry function.
args.input - input parameters, you can get test input value by args.input.xxx.
args.logger - logger instance used to print logs, injected by runtime.

Remember to fill in input/output in Metadata, it helps LLM to recognize and use tool.

Return:
The return data of the function, which should match the declared output parameters.
"""


def handler(args: Args[Input]) -> Output:
    url = args.input.url
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }

    response = requests.get(url, headers=headers, stream=True)

    # 临时视频文件路径
    temp_video_file = "video.mp4"

    if response.status_code == 200:
        with open(temp_video_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print("Download complete!")
    else:
        return {"message": response.status_code}
        print(f"Failed to download video. Status code: {response.status_code}")

    # 输出音频文件路径
    audio_file = "output_audio.mp3"
    # 加载视频文件
    video = VideoFileClip(temp_video_file)
    # 提取音频
    audio = video.audio
    # 保存音频文件
    audio.write_audiofile(audio_file)
    # 删除临时视频文件
    os.remove(temp_video_file)
    print("音频提取完成！")
    # 这里用openai接口转文本，你也可以换成别的
    client = OpenAI(base_url='你的base_url', api_key='你自己的key')
    audio_file = open(audio_file, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

    return {"message": transcription.text}