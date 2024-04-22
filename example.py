from flowvisor import FlowVisor

def deposit(amount):
    if exit:
        return
    print(f"Depositing ${amount}")
    balance = check_balance()
    print(f"New balance after deposit: ${balance + amount}")

def withdraw(amount):
    print(f"Withdrawing ${amount}")
    balance = check_balance()
    if balance >= amount:
        print(f"Withdrawal successful. New balance: ${balance - amount}")
    else:
        print("Insufficient funds!")

def check_balance():
    balance = 1000  # Assume initial balance is $1000
    print(f"Current balance: ${balance}")
    deposit(0)
    return balance

def transfer(amount):
    print(f"Transferring ${amount}")
    withdraw(amount)
    deposit(amount)

def main():
    print("Welcome to the bank!")
    transfer(200)
    check_balance()
    print("Thank you for banking with us!")

if __name__ == "__main__":
    FlowVisor.visualize_all()
    main()
    FlowVisor.generate_graph()
