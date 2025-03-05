from IR.remote import IRRemote
from dotenv import load_dotenv
import os

load_dotenv()

secret_key = os.getenv('SECRET_KEY')

def main():
    """
    Main function to create an IRRemote instance and start reading IR codes.
    """
    ir_remote = IRRemote(pin=17, ir_code_file="./config/ir_code_ff.txt", private_key=secret_key)
    ir_remote.read_ir_code()

if __name__ == "__main__":
    main()