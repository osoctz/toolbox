from transformers import AutoTokenizer

# 加载Qwen2.5-72B-Instruct-AWQ模型对应的分词器
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-72B-Instruct-AWQ")

def count_tokens(text):
    # 对输入文本进行编码，并计算tokens的数量
    encoded_input = tokenizer(text, return_tensors="pt")
    num_tokens = len(encoded_input["input_ids"][0])
    return num_tokens

if __name__ == "__main__":
    message = "你的消息内容"
    num_tokens = count_tokens(message)
    print(f"Message: {message}",flush=True)
    print(f"Number of tokens: {num_tokens}")