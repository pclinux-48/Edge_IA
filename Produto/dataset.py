import serial
import csv
import time

# Configure a porta conforme detectado anteriormente no seu Mac
ser = serial.Serial('/dev/cu.usbserial-1120', 115200)
time.sleep(2) # Aguarda a conexão estabilizar

print("Iniciando coleta de dados... Pressione Ctrl+C para parar.")

with open("dados_sensores.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["umidade", "temperatura"]) # Cabeçalho

    try:
        while True:
            line = ser.readline().decode('utf-8').strip()
            if "," in line:
                dados = line.split(",")
                writer.writerow(dados)
                print(f"Dados salvos: {dados}")
    except KeyboardInterrupt:
        print("\nColeta finalizada.")
        ser.close()