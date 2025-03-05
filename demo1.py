from IR.remote import IRRemote

def main():
    """
    Main function to create an IRRemote instance and start reading IR codes.
    """
    ir_remote = IRRemote(pin=17, ir_code_file="./config/ir_code_ff.txt", private_key="UGjIlhTTfcfjwmK6XJWM")  # Replace with your actual private key
    ir_remote.read_ir_code()

if __name__ == "__main__":
    main()