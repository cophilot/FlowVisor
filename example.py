from flowvisor import FlowVisor, vis


@vis  # Decorator to include the function in the graph
def deposit(amount):
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
def check_balance():
    balance = 1000
    print(f"Current balance: ${balance}")
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


if __name__ == "__main__":
    FlowVisor.CONFIG.show_flowvisor_settings = False  # Show the FlowVisor settings
    FlowVisor.CONFIG.show_system_info = False  # Show system information
    FlowVisor.CONFIG.show_function_time_percantage = (
        True  # Show Percentage of time spent in each function
    )
    FlowVisor.CONFIG.show_graph = True
    main()
    FlowVisor.CONFIG.output_file = (
        "example_flow"  # You can add some configureation with the CONFIG object
    )
    FlowVisor.graph()  # Generate the graph
    FlowVisor.export("example_flow", "json")  # Save the flow as json
