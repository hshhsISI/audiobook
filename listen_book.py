import asyncio
import edge_tts
import os
import glob

# ========== 新手可直接修改的配置 ==========
# 语音选择（二选一，#注释掉不用的）
VOICE = "zh-CN-YunxiNeural"   # 温柔男声
# VOICE = "zh-CN-XiaoxiaoNeural"  # 温柔女声

WORDS_PER_MINUTE = 260  # 每分钟读的字数（默认语速，不用乱改）
MINUTES_PER_CHUNK = 5   # 每段音频的时长（分钟），想要几分钟就改几
# ==========================================

# 自动计算每段的字数（无需手动修改）
CHUNK_SIZE = int(WORDS_PER_MINUTE * MINUTES_PER_CHUNK)

# 自动找文件夹里的第一个txt小说文件
def find_first_txt():
    txt_files = glob.glob("*.txt")
    if not txt_files:
        print("❌ 错误：没找到小说文件！请把 .txt 格式的小说放到这个文件夹里")
        return None
    print(f"✅ 成功找到小说：{txt_files[0]}")
    return txt_files[0]

# 读取小说内容
def read_book(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().replace("\n", " ").strip()
        return content
    except Exception as e:
        print(f"❌ 读取小说失败：{str(e)}")
        return ""

# 按设定的时长分段
def split_text(text):
    chunks = [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
    return chunks

# 文字转语音生成音频
async def text_to_speech(text, output_file):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_file)

# 主程序
async def main():
    # 1. 自动识别小说
    book_file = find_first_txt()
    if not book_file:
        os.system("pause")
        return

    # 2. 读取并分段
    print("⌛ 正在读取小说内容...")
    book_content = read_book(book_file)
    if not book_content:
        os.system("pause")
        return

    chunks = split_text(book_content)
    total_chunks = len(chunks)
    print(f"📖 小说已按每段{MINUTES_PER_CHUNK}分钟分段，共 {total_chunks} 段")
    print("="*50)

    # 3. 循环生成：仅输入Y生成下一段，无任何播放相关操作
    current_index = 0
    while current_index < total_chunks:
        current_num = current_index + 1
        output_file = f"第{current_num}段.mp3"

        # 仅等待生成确认，无其他提问
        while True:
            user_input = input(f"\n请输入 Y 生成第 {current_num}/{total_chunks} 段，输入 Q 退出程序：").strip().lower()
            if user_input == "y":
                break
            elif user_input == "q":
                print("\n👋 已退出程序")
                return
            else:
                print("❌ 输入无效！请输入 Y 继续，或输入 Q 退出")

        # 仅生成音频，不播放、不提问
        print(f"🔄 正在生成第 {current_num}/{total_chunks} 段音频（约{MINUTES_PER_CHUNK}分钟）...")
        try:
            await text_to_speech(chunks[current_index], output_file)
            print(f"✅ 第 {current_num}/{total_chunks} 段生成完成！已保存为：{output_file}")
        except Exception as e:
            print(f"❌ 生成音频失败：{str(e)}")
        
        current_index += 1

    # 全部生成完成提示
    print("\n🎉 恭喜！全书已经全部生成完毕！")
    os.system("pause")

if __name__ == "__main__":
    asyncio.run(main())
