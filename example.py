from flowvisor import FlowVisor
from ok import bla
import ok


def deposit(amount, exit = False):
    if exit:
        return
    print(f"Depositing ${amount}")
    balance = check_balance()  # Function 1
    print(f"New balance after deposit: ${balance + amount}")
    deposit(0, True)

def withdraw(amount):
    print(f"Withdrawing ${amount}")
    balance = check_balance()  # Function 2
    if balance >= amount:
        print(f"Withdrawal successful. New balance: ${balance - amount}")
    else:
        print("Insufficient funds!")

def check_balance():
    balance = 1000  # Assume initial balance is $1000
    print(f"Current balance: ${balance}")
    deposit(0, True)
    return balance

def transfer(amount):
    print(f"Transferring ${amount}")
    withdraw(amount)  # Function 3
    deposit(amount)  # Function 4

def main():
    print("Welcome to the bank!")
    transfer(200)  # Function 5
    check_balance()
    print("Thank you for banking with us!")

def test():
    print("Test function")
    deposit(100)
    withdraw(50)
    check_balance()
    bla.this_is_a_very_long_method()

if __name__ == "__main__":
    FlowVisor.visualize_all()
    FlowVisor.exclude_function("__init__")
    main()
    test()
    FlowVisor.CONFIG.logo = "mas.png"
    FlowVisor.CONFIG.node_scale = 3
    FlowVisor.generate_graph()
