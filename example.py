import timeit
from flowvisor import FlowVisor, vis
from flowvisor.utils import get_time_as_string

@vis # Decorator to include the function in the graph
def deposit(amount):
    if exit:
        return
    print(f"Depositing ${amount}")
    balance = check_balance()
    print(f"New balance after deposit: ${balance + amount}")

@vis
def withdraw(amount):
    print(f"Withdrawing ${amount}")
    balance = check_balance()
    if balance >= amount:
        print(f"Withdrawal successful. New balance: ${balance - amount}")
    else:
        print("Insufficient funds!")

@vis
def make_timestamp():
    time.time()

@vis
def check_balance():
    balance = 1000  # Assume initial balance is $1000
    print(f"Current balance: ${balance}")
    deposit(0)
    for i in range(10):
        make_timestamp()
    return balance

@vis
def transfer(amount):
    print(f"Transferring ${amount}")
    withdraw(amount)
    deposit(amount)

@vis
def main():
    print("Welcome to the bank!")
    transfer(200)
    check_balance()
    print("Thank you for banking with us!")
    
import time

@vis
def take_100_micro_s():
    # sleep for 100 microseconds
    time.sleep(0.0001)

@vis
def new_main():
    take_100_micro_s()
    main()

if __name__ == "__main__":
    FlowVisor.enable_advanced_overhead_reduction()
    new_main()
    FlowVisor.CONFIG.output_file = "example_graph_true_s_2" # You can add some configureation with the CONFIG object
    FlowVisor.graph() # Generate the graph
    FlowVisor.export("example_flow", "json") # Save the flow as json
