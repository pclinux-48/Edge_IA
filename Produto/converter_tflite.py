import os
import tensorflow as tf

# Força o uso da CPU para evitar bugs no plugin Metal do Mac
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# 1. Carrega o modelo
model = tf.keras.models.load_model('modelo_ambiental.h5')

# 2. Converte para uma função concreta (evita o erro de MLIR/LLVM)
run_model = tf.function(lambda x: model(x))
concrete_func = run_model.get_concrete_function(
    tf.TensorSpec(model.inputs[0].shape, model.inputs[0].dtype)
)

# 3. Configura o conversor usando a função concreta
converter = tf.lite.TFLiteConverter.from_concrete_functions([concrete_func])
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# 4. Gera o arquivo .h para o seu Produto de TCC
def hex_to_c_array(hex_data, var_name):
    c_str = f"unsigned char {var_name}[] = {{\n  "
    for i, val in enumerate(hex_data):
        c_str += f"0x{val:02x}, "
        if (i + 1) % 12 == 0:
            c_str += "\n  "
    c_str += "\n};\n"
    c_str += f"unsigned int {var_name}_len = {len(hex_data)};"
    return c_str

with open("model_data.h", "w") as f:
    f.write(hex_to_c_array(tflite_model, "modelo_ia"))

print("Sucesso! O arquivo 'model_data.h' foi gerado no seu MacBook Pro.")