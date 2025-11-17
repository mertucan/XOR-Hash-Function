from flask import Flask, render_template, request
import textwrap

app = Flask(__name__)

def xor_hash(message: str) -> dict:
    """
    Calculates a 128-bit hash and returns the detailed steps of the process.
    """
    steps = []
    block_size = 16  # 128 bits

    # Step 1: Encode the message into bytes
    data = message.encode('utf-8')
    char_hex_pairs = [{'char': char, 'hex': f"{byte:02x}"} for char, byte in zip(message, data)]
    steps.append({
        "title": "Adım 1: Mesajı Byte'lara Çevirme (UTF-8)",
        "explanation": "Girilen metindeki her karakter, standart bir karakter kodlaması olan UTF-8 formatında, onaltılık (hex) sistemdeki bir byte değerine karşılık gelir. Bu tablo, her karakterin bu dönüşümünü göstermektedir.",
        "char_hex_pairs": char_hex_pairs,
        "full_hex": data.hex(' ')
    })

    # Step 2: Apply padding
    padding_len = block_size - (len(data) % block_size)
    padding = bytes([padding_len] * padding_len)
    padded_data = data + padding
    steps.append({
        "title": "Adım 2: Dolgu (Padding) Ekleme",
        "explanation": f"Mesajın uzunluğunu 128 bitin (16 byte) tam katı yapmak için sonuna dolgu eklenir. Mesajın son bloğunda {block_size - padding_len} byte veri vardı, bu yüzden {padding_len} byte'lık dolgu (her biri {hex(padding_len)} değerinde) eklendi.",
        "original_data": data.hex(' '),
        "padding": padding.hex(' '),
        "padded_data": padded_data.hex(' ')
    })

    # Step 3: Split into blocks
    blocks = textwrap.wrap(padded_data.hex(' '), width=block_size * 3 - 1)
    steps.append({
        "title": "Adım 3: 128-bitlik Bloklara Ayırma",
        "explanation": f"Dolgulu veri, her biri 16 byte (128 bit) olan {len(blocks)} adet bloğa ayrılır. XOR işlemi bu bloklar üzerinde sırayla yapılacaktır.",
        "blocks": blocks
    })

    # Step 4: Perform XOR operation
    hash_result = bytearray(block_size)
    xor_steps = []
    for i, block_hex in enumerate(blocks):
        block = bytearray.fromhex(block_hex.replace(' ', ''))
        prev_hash = hash_result.copy()
        
        for j in range(block_size):
            hash_result[j] ^= block[j]
        
        xor_steps.append({
            "block_num": i + 1,
            "prev_hash": prev_hash.hex(' '),
            "block_data": block.hex(' '),
            "result_hash": hash_result.hex(' ')
        })
    
    steps.append({
        "title": "Adım 4: Bloklar Arası XOR İşlemi",
        "explanation": "Tüm bloklar sırayla birbiriyle XOR'lanır. Her bloğun her bir byte'ı, bir önceki işlemin sonucundaki hash'in ilgili byte'ı ile XOR'lanır. Başlangıç hash'i sıfırlardan oluşur.",
        "xor_steps": xor_steps
    })

    final_hash = hash_result.hex()
    steps.append({
        "title": "Adım 5: Nihai Hash Kodu",
        "explanation": "Tüm blokların XOR'lanmasından sonra elde edilen 128-bitlik sonuç, mesajın hash kodudur.",
        "hash_code": final_hash
    })
    
    return {"steps": steps, "final_hash": final_hash}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form['message']
        if message:
            result = xor_hash(message)
            return render_template('index.html', message=message, hash_code=result['final_hash'], steps=result['steps'])
    return render_template('index.html', message=None, hash_code=None, steps=None)

if __name__ == '__main__':
    app.run(debug=True)
